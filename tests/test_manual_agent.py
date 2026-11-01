from contextlib import closing
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from src import manual_agent as m


class ScanTests(unittest.TestCase):
    def test_snapshot_chunks_preserve_exact_quote_locators(self):
        with tempfile.TemporaryDirectory() as d:
            source = dict(source_id='fixture', url='https://example.org/manual', publisher='Fixture publisher', domain='testing', profession='tester', license='Fixture only', access='public', review_needs=['semantic', 'license'], format='html')
            m.scan_source(source, Path(d), raw=b'<h1>Check</h1><p>Inspect the indicator.</p><script>evil()</script><h2>Repair</h2><p>Adjust then inspect again.</p>', chunk_chars=64)
            snap = m.read_snapshot(Path(d), 'fixture')
            self.assertNotIn('evil', snap['text'])
            self.assertEqual(snap['raw_sha256'], hashlib.sha256((Path(d)/'fixture'/'original.bin').read_bytes()).hexdigest())
            self.assertTrue(snap['chunks'])
            for chunk in snap['chunks']:
                self.assertEqual(chunk['text'], snap['text'][chunk['start']:chunk['end']])
                self.assertLessEqual(len(chunk['text']), 64)
            (Path(d)/'fixture'/'snapshot.txt').write_text('tampered')
            with self.assertRaises(ValueError):
                m.read_snapshot(Path(d), 'fixture')


def fixture_batch(root):
    source = dict(source_id='fixture', url='https://example.org/manual', publisher='Fixture publisher', domain='testing', profession='tester', license='Fixture only', access='public', review_needs=['semantic', 'license'], format='text')
    snap = m.scan_source(source, root, raw=b'Inspect the indicator. Adjust the control. Inspect the indicator again. Stop when green.\n')
    seed = json.loads((m.ROOT/'data/seed_loops.json').read_text())
    admitted = seed.pop('manual_admission', {})
    seed['loops'] = [loop for loop in seed['loops'] if loop['loop_id'] not in admitted]
    loop = dict(loop_id='manual-fixture', name='Fixture control', domain='testing', objective='Set indicator green', initial_test='Inspect indicator state', exit_predicate='Fresh inspection shows green', max_iterations=3, epistemic_status='DERIVED', gestalts=[seed['gestalts'][0]['gestalt_id']])
    def claim(text, basis='authored_policy'):
        return dict(text=text, basis=basis, evidence=[0] if basis=='source_fact' else [])
    candidate = dict(loop=loop, procedure=dict(initial_test=claim(loop['initial_test']), operation=claim('Adjust the control.', 'source_fact'), fresh_retest=claim('Inspect indicator again using fresh evidence'), exit=claim(loop['exit_predicate']), iteration_policy=claim('At most 3 adjustments; stop unresolved on limit, missing evidence or unsafe conditions.')), evidence=[dict(source_id='fixture', snapshot_sha256=snap['snapshot_sha256'], chunk_id='chunk-0000', start=23, end=42, quote='Adjust the control.')], review=dict(reviewer='fixture reviewer', status='approved', notes='Synthetic fixture only; no real domain approval', safety='Do not execute', license='Fixture only'))
    return seed, dict(format_version='1.0', batch_id='fixture-batch', candidates=[candidate])


class SourceIntegrityTests(unittest.TestCase):
    def test_rehashed_text_must_still_derive_from_original(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fixture_batch(root)
            folder = root/'fixture'
            text = 'Invented source statements.\n'
            (folder/'snapshot.txt').write_text(text)
            meta = json.loads((folder/'snapshot.json').read_text())
            meta['snapshot_sha256'] = m.digest(text.encode())
            meta['chunks'] = [dict(chunk_id='chunk-0000', start=0, end=len(text), text=text, line_start=1)]
            (folder/'snapshot.json').write_bytes(m.encoded(meta))
            with self.assertRaises(ValueError):
                m.read_snapshot(root, 'fixture')


class AdmissionTests(unittest.TestCase):
    def test_grounded_batch_is_idempotent_and_preserves_seed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed, batch = fixture_batch(root/'sources')
            original = json.loads(json.dumps(seed))
            m.validate_batch(batch, seed, root/'sources')
            result = m.integrate_batch(batch, seed, root/'sources', root/'out')
            second = m.integrate_batch(batch, result['seed'], root/'sources', root/'out2', prior_provenance=result['provenance'])
            self.assertEqual(result['seed'], second['seed'])
            self.assertEqual(seed, original)
            self.assertEqual(len(result['seed']['loops']), len(seed['loops'])+1)
            self.assertEqual((root/'out/tote_loops.json').read_bytes(), (root/'out2/tote_loops.json').read_bytes())
            import sqlite3
            with closing(sqlite3.connect(root/'out/tote_loops.sqlite3')) as conn:
                self.assertEqual(conn.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
                self.assertEqual(conn.execute('PRAGMA foreign_key_check').fetchall(), [])
                self.assertEqual(conn.execute("SELECT plain_text FROM tote_steps WHERE loop_id='manual-fixture' AND step_index=3").fetchone()[0], 'Adjust the control.')
            with self.assertRaises(ValueError):
                m.integrate_batch(batch, seed, root/'sources', root/'out')


    def test_invalid_candidate_cases_fail_closed(self):
        import copy
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed, batch = fixture_batch(root)
            mutations = [
                lambda c: c['evidence'][0].update(quote='invented quote'),
                lambda c: c['evidence'][0].update(start=0),
                lambda c: c['loop'].update(epistemic_status='CANONICAL'),
                lambda c: c['loop'].update(max_iterations=0),
                lambda c: c['loop'].update(gestalts=['unknown']),
                lambda c: c['procedure']['operation'].update(evidence=[]),
                lambda c: c['procedure'].pop('fresh_retest'),
                lambda c: c['procedure']['operation'].update(evidence=[99]),
                lambda c: c['loop'].update(max_iterations=True),
                lambda c: c.update(unexpected=True),
            ]
            for mutation in mutations:
                bad = copy.deepcopy(batch)
                mutation(bad['candidates'][0])
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    m.validate_batch(bad, seed, root)
            pending = copy.deepcopy(batch)
            pending['candidates'][0]['review']['status'] = 'pending'
            m.validate_batch(pending, seed, root)
            with self.assertRaises(ValueError):
                m.integrate_batch(pending, seed, root, root/'not-published')
            self.assertFalse((root/'not-published').exists())
            duplicate = copy.deepcopy(batch['candidates'][0])
            duplicate['loop']['loop_id'] = 'other-id'
            duplicate['loop']['name'] = 'different-name'
            batch['candidates'].append(duplicate)
            with self.assertRaises(ValueError):
                m.validate_batch(batch, seed, root)

    def test_exact_terminology_requires_verbatim_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed, batch = fixture_batch(root)
            c = batch['candidates'][0]
            c['terminology'] = [dict(exact_term='Adjust the control', paraphrased_function='Change the fixture control', attribution='Synthetic fixture, not a historical NLP source', edition='Fixture v1', locator='line 1', evidence=[0])]
            m.validate_batch(batch, seed, root)
            c['terminology'][0]['exact_term'] = 'invented historical term'
            with self.assertRaises(ValueError):
                m.validate_batch(batch, seed, root)

    def test_prior_provenance_survives_new_batches(self):
        import copy
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed, batch = fixture_batch(root/'sources')
            first = m.integrate_batch(batch, seed, root/'sources', root/'one')
            next_batch = copy.deepcopy(batch)
            next_batch['batch_id'] = 'second'
            c = next_batch['candidates'][0]
            c['loop'].update(loop_id='manual-second', name='Second fixture', objective='A different objective')
            second = m.integrate_batch(next_batch, first['seed'], root/'sources', root/'two', prior_provenance=first['provenance'])
            self.assertEqual(len(second['provenance']['candidates']), 2)
            self.assertTrue((root/'two/sources/fixture/original.bin').exists())


class CLITests(unittest.TestCase):
    def test_cli_validates_and_integrates_real_fixture_files(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed, batch = fixture_batch(root/'sources')
            (root/'batch.json').write_bytes(m.encoded(batch))
            (root/'seed.json').write_bytes(m.encoded(seed))
            common = ['--batch', str(root/'batch.json'), '--seed', str(root/'seed.json'), '--snapshots', str(root/'sources')]
            for command in [['validate', *common], ['integrate-batch', *common, '--output', str(root/'output')], ['audit', '--output', str(root/'output')]]:
                result = subprocess.run([sys.executable, '-m', 'src.manual_agent', *command], cwd=m.ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(json.loads(result.stdout))
            self.assertTrue((root/'output/provenance.json').exists())


class NetworkTests(unittest.TestCase):
    def test_rejects_nonpublic_and_non_http_targets(self):
        for url in ['file:///etc/passwd', 'http://127.0.0.1/manual', 'https://[::1]/', 'https://user:pass@example.org/', 'http://169.254.169.254/latest', 'https://example.org:444/manual', 'http://224.0.0.1/manual', 'http://[ff02::1]/']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                m.public_target(url)

    def test_fetch_has_an_overall_deadline(self):
        import time
        with self.assertRaises(TimeoutError):
            with m.fetch_deadline(0.02):
                time.sleep(0.1)

    def test_manifest_url_is_an_exact_allowlist(self):
        manifest = {'sources': [{'source_id': 'a', 'url': 'https://example.org/manual'}]}
        self.assertEqual(m.select_source(manifest, 'a')['url'], 'https://example.org/manual')
        with self.assertRaises(ValueError):
            m.select_source(manifest, 'https://example.org/elsewhere')


if __name__ == '__main__':
    unittest.main()
