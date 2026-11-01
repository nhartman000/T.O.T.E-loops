"""Bounded source preparation and admission. Semantic extraction belongs to an agent.

This module never executes instructions or operations found in a manual.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import html.parser
import json
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 8 * 1024 * 1024
MAX_CHUNKS = 200


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9_-]+', value):
        raise ValueError('Invalid identifier')
    return value


class ManualHTML(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript'):
            self.hidden += 1
        if tag in ('p', 'div', 'li', 'br', 'tr', 'h1', 'h2', 'h3', 'h4', 'pre'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript'):
            self.hidden = max(0, self.hidden - 1)
        if tag in ('p', 'div', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'pre'):
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def public_target(url):
    """Resolve once, deny mixed/private DNS answers, return pinned public IP."""
    import ipaddress
    import socket
    from urllib.parse import urlsplit
    p = urlsplit(url)
    if (p.scheme not in ('https', 'http') or not p.hostname or p.username or p.password
            or p.fragment or p.port not in (None, 80 if p.scheme == 'http' else 443)):
        raise ValueError('Only public HTTP(S) URLs on standard ports without credentials/fragments')
    answers = socket.getaddrinfo(p.hostname, p.port or (443 if p.scheme == 'https' else 80), type=socket.SOCK_STREAM)
    addresses = [ipaddress.ip_address(a[4][0]) for a in answers]
    if not addresses or any(not a.is_global or a.is_multicast or a.is_reserved for a in addresses):
        raise ValueError('Nonpublic network target denied')
    return p, str(answers[0][4][0])


@contextmanager
def fetch_deadline(seconds=30):
    """Hard Unix main-thread deadline, including DNS/TLS/headers/body.

    Fail closed where this guarantee is unavailable; offline admission is portable.
    """
    import signal
    import threading
    if not hasattr(signal, 'setitimer') or threading.current_thread() is not threading.main_thread():
        raise ValueError('Network fetch requires Unix main thread for its hard deadline')
    if signal.getitimer(signal.ITIMER_REAL)[0] > 0:
        raise ValueError('Cannot replace an existing process alarm')
    old = signal.getsignal(signal.SIGALRM)
    def expired(signum, frame):
        raise TimeoutError('Overall fetch deadline exceeded')
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def fetch_public(url):
    with fetch_deadline():
        return _fetch_public(url)


def _fetch_public(url):
    """No proxies, cookies, credentials or redirects; pin socket to vetted IP.

    A redirect must be separately reviewed and added as an exact manifest URL.
    """
    import http.client
    import socket
    import ssl
    import time
    p, ip = public_target(url)
    port = p.port or (443 if p.scheme == 'https' else 80)
    deadline = time.monotonic() + 30
    conn = http.client.HTTPConnection(p.hostname, port, timeout=10)
    sock = socket.create_connection((ip, port), timeout=10)
    try:
        if p.scheme == 'https':
            context = ssl.create_default_context()
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            sock = context.wrap_socket(sock, server_hostname=p.hostname)
        conn.sock = sock
        conn.request('GET', (p.path or '/') + ('?' + p.query if p.query else ''), headers={'User-Agent': 'TOTE-manual-source/1.0', 'Accept': 'text/html,text/plain', 'Accept-Encoding': 'identity'})
        response = conn.getresponse()
        if response.status != 200:
            raise ValueError(f'HTTP {response.status}; redirects/auth are not followed')
        if response.getheader('Content-Encoding', 'identity') != 'identity':
            raise ValueError('Compressed responses not supported')
        if response.getheader('Content-Type', '').split(';')[0] not in ('text/html', 'text/plain', 'application/xhtml+xml'):
            raise ValueError('Only HTML/plain text responses accepted')
        data = bytearray()
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ValueError('Fetch deadline exceeded')
            sock.settimeout(min(10, remaining))
            block = response.read1(min(65536, MAX_BYTES + 1 - len(data)))
            if not block:
                break
            data.extend(block)
            if len(data) > MAX_BYTES:
                raise ValueError('Source exceeds byte limit')
        return bytes(data)
    finally:
        conn.close()
        sock.close()


def select_source(manifest, source_id):
    sources = manifest['sources']
    ids = [s['source_id'] for s in sources]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate allowlist IDs')
    for source in sources:
        if source['source_id'] == source_id:
            return source
    raise ValueError('Unknown allowlisted source_id')


def check_source(source):
    identifier(source['source_id'])
    for key in ('url', 'publisher', 'domain', 'profession', 'license', 'access', 'review_needs', 'format'):
        if not source.get(key):
            raise ValueError('Missing source metadata: ' + key)
    if source['access'] != 'public' or source['format'] not in ('html', 'text'):
        raise ValueError('Only public HTML/text sources supported; PDF requires separately reviewed text extraction')


def extract_text(raw, source_format):
    decoded = raw.decode('utf-8', errors='strict')
    if source_format == 'html':
        parser = ManualHTML()
        parser.feed(decoded)
        decoded = ''.join(parser.parts)
    return '\n'.join(line for line in (' '.join(x.split()) for x in decoded.splitlines()) if line) + '\n'


def scan_source(source, output: Path, *, raw=None, chunk_chars=4000):
    check_source(source)
    if not 32 <= chunk_chars <= 16000:
        raise ValueError('chunk_chars must be 32..16000')
    if raw is None:
        raw = fetch_public(source['url'])
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ValueError('Source exceeds byte limit')
    text = extract_text(raw, source['format'])
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_chars, len(text))
        if end < len(text):
            split = text.rfind('\n', start, end)
            if split > start:
                end = split + 1
        chunks.append(dict(chunk_id=f'chunk-{len(chunks):04d}', start=start, end=end, text=text[start:end], line_start=text.count('\n', 0, start)+1))
        start = end
    if len(chunks) > MAX_CHUNKS or not text.strip():
        raise ValueError('Empty source or chunk budget exceeded; narrow the allowed manual section')
    metadata = dict(format_version='1.0', source=source, raw_sha256=digest(raw), snapshot_sha256=digest(text.encode()), chunks=chunks)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    target = output / source['source_id']
    # No replacement of existing source evidence. New versions need a new source_id.
    if target.exists():
        existing = read_snapshot(output, source['source_id'])
        if existing['raw_sha256'] == metadata['raw_sha256'] and existing['source'] == source:
            return existing
        raise ValueError('Snapshot already exists with different bytes or metadata')
    with tempfile.TemporaryDirectory(prefix='.snapshot-', dir=output) as temp:
        stage = Path(temp) / 'source'
        stage.mkdir()
        (stage/'original.bin').write_bytes(raw)
        (stage/'snapshot.txt').write_text(text, encoding='utf-8')
        (stage/'snapshot.json').write_bytes(encoded(metadata))
        stage.rename(target)
    return dict(metadata, text=text)


def read_snapshot(root, source_id):
    folder = Path(root)/identifier(source_id)
    meta = json.loads((folder/'snapshot.json').read_text(encoding='utf-8'))
    raw = (folder/'original.bin').read_bytes()
    text = (folder/'snapshot.txt').read_text(encoding='utf-8')
    check_source(meta['source'])
    if digest(raw) != meta['raw_sha256'] or digest(text.encode()) != meta['snapshot_sha256']:
        raise ValueError('Snapshot hash mismatch')
    if extract_text(raw, meta['source']['format']) != text:
        raise ValueError('Snapshot text is not derived from retained original bytes')
    for c in meta['chunks']:
        if c['text'] != text[c['start']:c['end']]:
            raise ValueError('Chunk locator mismatch')
    return dict(meta, text=text)


def validate_batch(*args, **kwargs):
    from .manual_admission import validate_batch as validate
    return validate(*args, **kwargs)


def main(argv=None):
    import argparse
    import sys
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    scan = sub.add_parser('scan', help='Fetch one exact allowlisted public source and prepare chunks; not semantic extraction')
    scan.add_argument('--manifest', type=Path, required=True)
    scan.add_argument('--source-id', required=True)
    scan.add_argument('--output', type=Path, required=True)
    scan.add_argument('--chunk-chars', type=int, default=4000)
    for name in ('validate', 'integrate-batch'):
        p = sub.add_parser(name)
        p.add_argument('--batch', type=Path, required=True)
        p.add_argument('--seed', type=Path, default=ROOT/'data/seed_loops.json')
        p.add_argument('--snapshots', type=Path, required=True)
        if name == 'integrate-batch':
            p.add_argument('--output', type=Path, required=True)
            p.add_argument('--prior-provenance', type=Path)
    audit = sub.add_parser('audit')
    audit.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'scan':
            source = select_source(json.loads(args.manifest.read_text()), args.source_id)
            result = scan_source(source, args.output, chunk_chars=args.chunk_chars)
            result = dict(source_id=source['source_id'], snapshot_sha256=result['snapshot_sha256'], chunks=len(result['chunks']))
        elif args.command == 'audit':
            from src.manual_admission import audit_output
            result = audit_output(args.output)
        else:
            batch = json.loads(args.batch.read_text())
            seed = json.loads(args.seed.read_text())
            if args.command == 'validate':
                result = validate_batch(batch, seed, args.snapshots)
            else:
                prior_path = args.prior_provenance or args.seed.parent/'provenance.json'
                if args.prior_provenance is not None and not prior_path.is_file():
                    raise ValueError('Explicit --prior-provenance path does not exist')
                prior = json.loads(prior_path.read_text()) if prior_path.exists() else None
                result = integrate_batch(batch, seed, args.snapshots, args.output, prior_provenance=prior)
                result = dict(output=result['output'], loops=len(result['seed']['loops']), candidates=len(result['provenance']['candidates']))
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2


def integrate_batch(*args, **kwargs):
    from .manual_admission import integrate_batch as integrate
    return integrate(*args, **kwargs)


if __name__ == '__main__':
    raise SystemExit(main())
