deadline = SESSION_DEADLINE_EPOCH
state = 'error'
try:
    progress = validate_records()
    needed = [key for key in bundles if progress[key] < len(expected[key])]
    if needed and time.time() < deadline - CHECKPOINT_RESERVE_SECONDS:
        command = [sys.executable, '-u', '/kaggle/working/kaggle_inference.py',
                   '--model', model_path, '--model-revision', revision,
                   '--arm', ARM, '--expected-model-sha256', MODEL_SHA256,
                   '--gpu-layers', str(GPU_LAYERS), '--deadline-epoch', str(deadline),
                   '--checkpoint-reserve-seconds', str(CHECKPOINT_RESERVE_SECONDS),
                   '--status', str(OUT_ROOT / 'tail_status.json')]
        for seed, ds in needed:
            command += ['--run', str(seed), ds, 'test', str(bundles[seed, ds]),
                        str(OUT_ROOT / f'seed_{seed}' / ds / 'test')]
        run_logged(command, 'test_remaining_three_seeds')
    progress = validate_records()
    if all(progress[key] == len(expected[key]) for key in expected):
        state = 'test_tail_complete'
    elif time.time() >= deadline - CHECKPOINT_RESERVE_SECONDS:
        state = 'timed_out'
    else:
        status_path = OUT_ROOT / 'tail_status.json'
        if not status_path.is_file() or not json.loads(status_path.read_bytes())['timed_out']:
            raise RuntimeError('Worker stopped without a timeout or completing the tail')
        state = 'timed_out'
finally:
    summary = dict(plan, state=state, new_records={f'{s}/{d}': n for (s,d),n in validate_records().items()})
    (OUT_ROOT / 'batch_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    import runpy
    runpy.run_path('/kaggle/working/kaggle_inference.py')['snapshot'](OUT_ROOT / 'tail_status.json')
    diagnostics_zip()
    print(state, CHECKPOINT_NAME, summary['new_records'])
