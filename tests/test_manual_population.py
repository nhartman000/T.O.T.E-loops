"""Regression and real-data acceptance for reviewed manual specifications."""
import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from src import build_db, manual_agent as m
from tests.test_manual_agent import fixture_batch


class IdentityTests(unittest.TestCase):
    def test_dotted_loop_identity_is_not_a_filesystem_identifier(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed, batch = fixture_batch(root / 'sources')
            batch['candidates'][0]['loop']['loop_id'] = 'manual.fixture.v1'
            result = m.integrate_batch(batch, seed, root/'sources', root/'out')
            self.assertEqual(result['seed']['loops'][-1]['loop_id'], 'manual.fixture.v1')
            with self.assertRaises(ValueError):
                m.identifier('manual.fixture.v1')
            for invalid in ('../escape', 'foo/bar', '..', 'foo..bar'):
                bad = copy.deepcopy(batch)
                bad['candidates'][0]['loop']['loop_id'] = invalid
                with self.assertRaises(ValueError):
                    m.validate_batch(bad, seed, root/'sources')


class CanonicalRebuildTests(unittest.TestCase):
    def test_sibling_provenance_preserves_admitted_procedures(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed, batch = fixture_batch(root/'sources')
            m.integrate_batch(batch, seed, root/'sources', root/'out')
            folder = root/'out'
            before = json.loads((folder/'tote_loops.json').read_text())
            with patch.multiple(build_db, SEED=folder/'seed_loops.json', DATABASE=folder/'tote_loops.sqlite3', EXPORT=folder/'tote_loops.json'):
                build_db.build()
            after = json.loads((folder/'tote_loops.json').read_text())
            self.assertEqual(before, after)
            from src.manual_admission import audit_output
            self.assertTrue(audit_output(folder)['audited'])


class ProvenanceRequiredTests(unittest.TestCase):
    def test_enriched_seed_requires_prior_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed, batch = fixture_batch(root/'sources')
            first = m.integrate_batch(batch, seed, root/'sources', root/'first')
            next_batch = copy.deepcopy(batch)
            next_batch['batch_id'] = 'second'
            next_batch['candidates'][0]['loop'].update(loop_id='manual-second', name='Second', objective='Different')
            with self.assertRaisesRegex(ValueError, 'provenance'):
                m.integrate_batch(next_batch, first['seed'], root/'sources', root/'second')
            self.assertFalse((root/'second').exists())

    def test_canonical_build_requires_sibling_before_touching_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed, batch = fixture_batch(root/'sources')
            m.integrate_batch(batch, seed, root/'sources', root/'out')
            folder = root/'out'
            (folder/'provenance.json').unlink()
            before = (folder/'tote_loops.sqlite3').read_bytes()
            with patch.multiple(build_db, SEED=folder/'seed_loops.json', DATABASE=folder/'tote_loops.sqlite3', EXPORT=folder/'tote_loops.json'):
                with self.assertRaisesRegex(ValueError, 'provenance'):
                    build_db.build()
            self.assertEqual(before, (folder/'tote_loops.sqlite3').read_bytes())

    def test_explicit_nonexistent_prior_path_is_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed, batch = fixture_batch(root/'sources')
            (root/'batch.json').write_bytes(m.encoded(batch))
            (root/'seed.json').write_bytes(m.encoded(seed))
            import io
            from contextlib import redirect_stderr
            error = io.StringIO()
            with redirect_stderr(error):
                self.assertEqual(m.main(['integrate-batch', '--batch', str(root/'batch.json'), '--seed', str(root/'seed.json'), '--snapshots', str(root/'sources'), '--output', str(root/'out'), '--prior-provenance', str(root/'missing.json')]), 2)
            self.assertIn('--prior-provenance', error.getvalue())
            self.assertFalse((root/'out').exists())


class SourceIdentityTests(unittest.TestCase):
    def test_same_bytes_do_not_allow_historical_source_metadata_replacement(self):
        for key in ('url', 'publisher', 'license'):
            with self.subTest(field=key), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                seed, batch = fixture_batch(root/'sources')
                first = m.integrate_batch(batch, seed, root/'sources', root/'first')
                path = root/'sources/fixture/snapshot.json'
                snapshot = json.loads(path.read_text())
                snapshot['source'][key] += '-changed'
                path.write_bytes(m.encoded(snapshot))
                with self.assertRaisesRegex(ValueError, '[Ss]ource'):
                    m.integrate_batch(batch, first['seed'], root/'sources', root/'second', prior_provenance=first['provenance'])
                self.assertFalse((root/'second').exists())


class InventoryTests(unittest.TestCase):
    def test_audit_and_canonical_build_reject_corrupt_provenance_inventories(self):
        from src.manual_admission import audit_output
        def mutate(value, kind, batch):
            if kind == 'duplicate candidate':
                value['candidates'].append(copy.deepcopy(value['candidates'][0]))
            elif kind == 'missing candidate':
                value['candidates'] = []
            elif kind == 'extra fingerprint':
                value['fingerprints']['fake'] = '0'*64
            elif kind == 'missing fingerprint':
                value['fingerprints'] = {}
            elif kind == 'fake batch hash':
                value['batches'][batch['batch_id']] = '0'*64
            elif kind == 'extra batch':
                value['batches']['fake'] = '0'*64
            elif kind == 'missing source':
                value['sources'] = {}
            elif kind == 'extra source':
                value['sources']['fake'] = copy.deepcopy(value['sources']['fixture'])
            elif kind == 'source declaration mismatch':
                value['sources']['fixture']['source']['publisher'] = 'Invented publisher'
            elif kind == 'rehashed procedure mutation':
                value['candidates'][0]['procedure']['operation']['text'] = 'Invented procedure'
                envelope = copy.deepcopy(batch)
                envelope['candidates'] = copy.deepcopy(value['candidates'])
                value['batch_envelopes'] = {batch['batch_id']: envelope}
                value['batches'][batch['batch_id']] = m.digest(m.encoded(envelope))
            elif kind == 'missing envelopes':
                value.pop('batch_envelopes', None)
            elif kind == 'conflicting envelope membership':
                envelope = copy.deepcopy(batch)
                envelope['candidates'][0]['review']['notes'] = 'Changed historical approval'
                value['batch_envelopes'] = {batch['batch_id']: envelope}
                value['batches'][batch['batch_id']] = m.digest(m.encoded(envelope))
        kinds = ('duplicate candidate', 'missing candidate', 'extra fingerprint', 'missing fingerprint', 'fake batch hash', 'extra batch', 'missing source', 'extra source', 'source declaration mismatch', 'rehashed procedure mutation', 'missing envelopes', 'conflicting envelope membership')
        for kind in kinds:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                seed, batch = fixture_batch(root/'sources')
                result = m.integrate_batch(batch, seed, root/'sources', root/'out')
                provenance = copy.deepcopy(result['provenance'])
                mutate(provenance, kind, batch)
                folder = root/'out'
                (folder/'provenance.json').write_bytes(m.encoded(provenance))
                with self.assertRaises(ValueError):
                    audit_output(folder)
                before = (folder/'tote_loops.sqlite3').read_bytes()
                with patch.multiple(build_db, SEED=folder/'seed_loops.json', DATABASE=folder/'tote_loops.sqlite3', EXPORT=folder/'tote_loops.json'):
                    with self.assertRaises(ValueError):
                        build_db.build()
                self.assertEqual(before, (folder/'tote_loops.sqlite3').read_bytes())
                with self.assertRaises(ValueError):
                    m.integrate_batch(batch, result['seed'], root/'sources', root/'next', prior_provenance=provenance)

    def test_isolated_builder_rejects_incomplete_procedure_inventory(self):
        from src.manual_admission import build_isolated
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed, batch = fixture_batch(root/'sources')
            first = m.integrate_batch(batch, seed, root/'sources', root/'first')
            stage = root/'stage'
            stage.mkdir()
            with self.assertRaisesRegex(ValueError, '[Ii]nventory'):
                build_isolated(first['seed'], [], stage)
            self.assertFalse((stage/'tote_loops.sqlite3').exists())

    def test_orphan_prior_candidate_cannot_disappear_from_seed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed, batch = fixture_batch(root/'sources')
            first = m.integrate_batch(batch, seed, root/'sources', root/'first')
            altered = copy.deepcopy(first['seed'])
            altered['loops'] = [l for l in altered['loops'] if l['loop_id'] != 'manual-fixture']
            altered.pop('manual_admission', None)
            with self.assertRaises(ValueError):
                m.integrate_batch(batch, altered, root/'sources', root/'second', prior_provenance=first['provenance'])


class PopulationAcceptanceTests(unittest.TestCase):
    def test_reviewed_population_and_original_seed_preservation(self):
        import hashlib
        seed = json.loads((m.ROOT/'data/seed_loops.json').read_text())
        self.assertEqual(len(seed['loops']), 22)
        original = copy.deepcopy(seed)
        original.pop('manual_admission', None)
        original['loops'] = [loop for loop in seed['loops'] if loop['loop_id'].startswith(('ai.', 'code.'))]
        self.assertEqual(hashlib.sha256(json.dumps(original, sort_keys=True).encode()).hexdigest(),
                         '2cb8dfd6c510c5a7f7a451fa4cc841d7b3edcfd46310e0d6b601a4940efa662d')
        provenance = json.loads((m.ROOT/'data/provenance.json').read_text())
        self.assertEqual(len(provenance['candidates']), 12)
        for c in provenance['candidates']:
            self.assertEqual(c['loop']['epistemic_status'], 'DERIVED')
            self.assertIn('DERIVED SPECIFICATION', c['review']['notes'])
            self.assertEqual(c['review']['status'], 'approved')
        self.assertEqual(len(provenance['sources']), 11)
        for source in provenance['sources'].values():
            self.assertEqual(source['source']['representation'], 'reviewed_evidence_excerpt')
            self.assertTrue(source['source']['original_retrieval']['response_sha256'])
            self.assertTrue(source['source']['profession'])

    def test_canonical_main_rebuild_audit_and_idempotent_replay(self):
        from src.manual_admission import audit_output
        import shutil
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            shutil.copytree(m.ROOT/'data', root/'data')
            folder = root/'data'
            before = json.loads((folder/'tote_loops.json').read_text())
            with patch.multiple(build_db, SEED=folder/'seed_loops.json', DATABASE=folder/'tote_loops.sqlite3', EXPORT=folder/'tote_loops.json'):
                build_db.build()
            self.assertEqual(before, json.loads((folder/'tote_loops.json').read_text()))
            self.assertTrue(audit_output(folder)['audited'])
            seed = json.loads((folder/'seed_loops.json').read_text())
            provenance = json.loads((folder/'provenance.json').read_text())
            batch = json.loads((m.ROOT/'data/manual-batch-v1.json').read_text())
            m.integrate_batch(batch, seed, folder/'sources', root/'replay', prior_provenance=provenance)
            self.assertEqual((root/'replay/tote_loops.json').read_bytes(), (m.ROOT/'data/tote_loops.json').read_bytes())


if __name__ == '__main__':
    unittest.main()
