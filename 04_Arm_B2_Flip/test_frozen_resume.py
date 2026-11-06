"""CPU checks using the real I-06 checkpoint; fake scores stay in temporary folders."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

import kaggle_flip_frozen_runtime as rt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUNDLES = HERE / 'output/bundles_frozen_donor_20261101'
CHECKPOINT = HERE / 'output/kaggle_20261102_quangdung1111_run1/grace_b2_flip_checkpoint.zip'
KEYS = [('devign', 'validation'), ('reveal', 'validation'), ('devign', 'test'), ('reveal', 'test')]
TMP_BASE = HERE / 'offline_test_artifacts'
assert TMP_BASE.resolve().is_relative_to(HERE.resolve())
TMP_BASE.mkdir(exist_ok=True)


def settings():
    with zipfile.ZipFile(CHECKPOINT) as z:
        identity = json.loads(z.read('devign/validation/run_manifest.json'))
    for k in ('dataset', 'split', 'bundle_sha256', 'prompt_set_sha256'):
        identity.pop(k, None)
    snapshot = json.loads((BUNDLES/'prepare_summary.json').read_text(encoding='utf-8'))['donor_snapshot_sha256']
    return identity, snapshot


def session(root, checkpoint=CHECKPOINT, identity=None):
    ident, snapshot = settings()
    runs = [(d, s, BUNDLES/d/s/f'{d}_{s}_b2_flip_kaggle.zip', Path(root)/d/s) for d, s in KEYS]
    return rt.prepare_session(runs, root, checkpoint, identity or ident, snapshot)


def fake_row(item, context):
    row = {k: item[k] for k in ('id', 'dataset', 'split', 'label', 'prompt_sha256', 'demo_ids', 'tokens', 'graph_missing')}
    return dict(row, arm='B2-flip', seed=42, model_sha256=context['identity']['model_sha256'],
                raw='1', s=.6, valid=True, response_valid=True)


class DeliberateStop(Exception):
    pass


class FrozenResumeTests(unittest.TestCase):
    def test_generated_prompts_match_independent_donor_audit(self):
        path = ROOT/'Runs-management/b2_flip_I06_20261102/all_prompt_comparison.jsonl'
        expected = {r['id']: r for r in rt.read_rows(path)}
        ident, snapshot = settings()
        seen = 0
        for d, s in KEYS:
            m, rr = rt.load_bundle(BUNDLES/d/s/f'{d}_{s}_b2_flip_kaggle.zip', snapshot)
            for row in rr:
                e = expected[row['id']]
                self.assertEqual(row['prompt_sha256'], e['new_prompt_sha256'])
                self.assertEqual(row['previous_prompt_sha256'], e['old_prompt_sha256'])
                self.assertEqual(row['demo_ids'], [e['new_demo_id']])
                seen += 1
        self.assertEqual(seen, 10011)

    def test_migration_repair_priority_and_native_resume(self):
        source_sha = rt.sha256(CHECKPOINT)
        with tempfile.TemporaryDirectory(prefix='flip_offline_test_', dir=TMP_BASE) as tmp:
            first = Path(tmp)/'first'
            ctx = session(first)
            self.assertEqual(sum(len(c['done']) for c in ctx['contexts'].values()), 5202)
            requests = ctx['plan']['repair_requests']
            self.assertEqual(len(requests), 33)
            self.assertEqual(sum(r['split'] == 'validation' for r in requests), 28)
            self.assertEqual(sum(r['split'] == 'test' for r in requests), 5)
            self.assertEqual(rt.sha256(first/'history/original_checkpoint.zip'), source_sha)
            self.assertEqual(len(rt.read_rows(first/'history/stale_records.jsonl')), 33)
            calls = []
            tick = [0]

            def first_infer(item, context):
                calls.append(item['id'])
                if len(calls) == 10:
                    tick[0] = 2
                return fake_row(item, context)

            with contextlib.redirect_stdout(io.StringIO()):
                status = rt.process_session(ctx, first_infer, 1, clock=lambda: tick[0])
            self.assertTrue(status['timed_out'])
            self.assertEqual(status['repair_remaining'], 23)
            self.assertEqual(status['completed_records_total'], 5212)
            self.assertEqual(calls, [r['id'] for r in requests[:10]])
            # Re-entering a working folder must keep the ten repaired scores.
            again = session(first)
            self.assertEqual(sum(len(c['done']) for c in again['contexts'].values()), 5212)
            native = Path(tmp)/'native.zip'
            with zipfile.ZipFile(native, 'w', zipfile.ZIP_DEFLATED) as z:
                for p in first.rglob('*'):
                    if p.is_file():
                        z.write(p, p.relative_to(first).as_posix())
            second = Path(tmp)/'second'
            resumed = session(second, native)
            self.assertEqual(resumed['plan']['repair_requests'], requests)
            self.assertEqual(rt.sha256(second/'history/original_checkpoint.zip'), source_sha)
            more = []

            def second_infer(item, context):
                if len(more) == 23:
                    raise DeliberateStop('Stop at the first pending request after the repair queue')
                more.append(item['id'])
                if item['split'] == 'test':
                    locked = rt.read_json(second/'thresholds.json')['entries']['B2-flip/devign']
                    self.assertEqual(locked['n_expected'], 2732)
                    self.assertEqual(locked['validation_prompt_set_sha256'], resumed['contexts']['devign','validation']['manifest']['prompts_sha256'])
                return fake_row(item, context)

            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(DeliberateStop):
                rt.process_session(resumed, second_infer, 1, clock=lambda: 0)
            self.assertEqual(calls+more, [r['id'] for r in requests if r['split']=='validation'] + [r['id'] for r in requests if r['split']=='test'])
            self.assertEqual(sum(len(c['done']) for c in resumed['contexts'].values()), 5235)
            # A subsequent process starts with a previously missing request, without repairing twice.
            third = session(second, native)
            pending = []

            def one_pending(item, context):
                if pending:
                    raise DeliberateStop()
                pending.append(item['id'])
                self.assertNotIn(item['id'], {r['id'] for r in requests})
                return fake_row(item, context)

            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(DeliberateStop):
                rt.process_session(third, one_pending, 1, clock=lambda: 0)
            self.assertEqual(len(pending), 1)
            self.assertEqual(sum(len(c['done']) for c in third['contexts'].values()), 5236)
            # Finish the temporary fixture without GPU calls, exercising complete-run finalization.
            for c in third['contexts'].values():
                for item in c['rows']:
                    if item['id'] not in c['done']:
                        c['done'][item['id']] = fake_row(item, c)
                rt.write_rows_atomic(c['out']/'records.jsonl', list(c['done'].values()))
            def must_not_infer(*_):
                raise AssertionError('Completed prompt requested again')
            with contextlib.redirect_stdout(io.StringIO()):
                complete = rt.process_session(third, must_not_infer, 1, clock=lambda: 0)
            self.assertEqual(complete['state'], 'complete')
            self.assertEqual(complete['completed_records_total'], 10011)
            self.assertEqual(complete['inferred_this_session'], 0)
            self.assertEqual(rt.read_json(second/'devign/test/evaluation.json')['n_total'], 2732)
        self.assertEqual(rt.sha256(CHECKPOINT), source_sha)

    def test_unknown_old_hash_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix='flip_offline_test_', dir=TMP_BASE) as tmp:
            bad = Path(tmp)/'bad.zip'
            with zipfile.ZipFile(CHECKPOINT) as src, zipfile.ZipFile(bad,'w',zipfile.ZIP_DEFLATED) as dest:
                for name in src.namelist():
                    data=src.read(name)
                    if name=='devign/validation/records.jsonl':
                        rr=[json.loads(line) for line in data.splitlines() if line.strip()]
                        rr[0]['prompt_sha256']='f'*64
                        data=('\n'.join(json.dumps(r) for r in rr)+'\n').encode()
                    dest.writestr(name,data)
            with self.assertRaisesRegex(ValueError,'Unknown checkpoint prompt hash'):
                session(Path(tmp)/'out',bad)

    def test_changed_model_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix='flip_offline_test_', dir=TMP_BASE) as tmp:
            identity,_=settings()
            identity['model_sha256']='e'*64
            with self.assertRaisesRegex(ValueError,'Model bytes/backend version'):
                session(Path(tmp)/'out', identity=identity)

    def test_notebook_sources_compile_and_match_helpers(self):
        import nbformat
        for path in (HERE/'notebooks').glob('*.ipynb'):
            nb = nbformat.read(path, as_version=4)
            nbformat.validate(nb)
            executed = any(cell.get('outputs') for cell in nb.cells if cell.cell_type == 'code')
            if executed:
                # Imported execution notebooks retain outputs as run evidence.
                execution = nb.metadata.get('papermill', {})
                self.assertIsNone(execution.get('exception'))
                self.assertTrue(execution.get('end_time'))
                helper_root = ROOT/'Runs-management/kaggle_outputs_20261105/b2_flip'
            for cell in nb.cells:
                if cell.cell_type != 'code':
                    continue
                if executed:
                    self.assertIsNotNone(cell.execution_count)
                    self.assertFalse(any(output.output_type == 'error' for output in cell.outputs))
                else:
                    self.assertFalse(cell.outputs)
                code = cell.source
                if code.startswith('%%writefile'):
                    header, code = code.split('\n', 1)
                    helper = Path(header.split()[-1]).name
                    expected = (helper_root/helper) if executed else (
                        (ROOT/'Runs-management/validation_lock.py') if helper=='validation_lock.py' else HERE/helper)
                    self.assertEqual(code, expected.read_text(encoding='utf-8'))
                compile(code, str(path), 'exec')

    def test_input_discovery_ignores_legacy_bundle_and_username(self):
        with tempfile.TemporaryDirectory(prefix='flip_offline_test_', dir=TMP_BASE) as tmp:
            folder = Path(tmp)
            inputs = folder/'input'
            for account in ('arbitrary-account-new', 'different-account-legacy', 'checkpoint-owner'):
                (inputs/account).mkdir(parents=True)
            shutil.copyfile(BUNDLES/'grace_b2_flip_frozen_donor_inputs.zip', inputs/'arbitrary-account-new/grace_b2_flip_frozen_donor_inputs.zip')
            shutil.copyfile(HERE/'output/bundles/grace_b2_flip_inputs.zip', inputs/'different-account-legacy/grace_b2_flip_inputs.zip')
            shutil.copyfile(CHECKPOINT, inputs/'checkpoint-owner/grace_b2_flip_checkpoint.zip')
            nb = json.loads((HERE/'notebooks/02_kaggle_qwen_q4_b2_flip.ipynb').read_text(encoding='utf-8'))
            ns = {'Path': Path, 'json': json, 'zipfile': zipfile, 'hashlib': __import__('hashlib'),
                  'note': lambda *_: None, 'diagnostics_zip': lambda: None}
            config = ''.join(nb['cells'][3]['source']).replace("Path('/kaggle/input')", f'Path({str(inputs)!r})')
            exec(config, ns)
            ns['BUNDLE_WORK'] = folder/'bundle_work'
            exec(''.join(nb['cells'][4]['source']), ns)
            self.assertEqual(set(ns['BUNDLE_PATHS']), set(KEYS))
            _, snapshot = settings()
            for path in ns['BUNDLE_PATHS'].values():
                manifest, _ = rt.load_bundle(path, snapshot)
                self.assertEqual(manifest['prompt_variant'], rt.VARIANT)


if __name__ == '__main__':
    unittest.main(verbosity=2)
