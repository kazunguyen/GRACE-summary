"""PI-authorized retry loop for this B3-swap kernel only; stops on RUNNING.

No guessed cancellation IDs, hardware changes, input changes or other kernels.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deploy_b3_swap_20261110 as deploy

def now():
    return datetime.now(timezone.utc).isoformat()

def main():
    stage = deploy.STAGE
    spec = json.loads((stage / 'deployment.json').read_bytes())
    if spec['ref'] != 'thanhduy9a4tv/grace-b3-swap-test-20261110-v1' or spec['arm'] != 'B3-swap':
        raise ValueError('Monitor restricted to the authorized B3-swap deployment')
    api, owner = deploy.auth(spec['config_folder'])
    assert owner == spec['owner']
    cycle = 0
    while True:
        cycle += 1
        event = {'at_utc': now(), 'pid': os.getpid(), 'cycle': cycle, 'ref': spec['ref']}
        try:
            response = api.kernels_status(spec['ref'])
            event['observed_status'] = response.status.name
            if event['observed_status'] == 'RUNNING':
                event.update(state='RUNNING', finished=True)
                deploy.save('monitor_status.json', event)
                deploy.main('verify-source')
                with (stage / 'monitor_events.jsonl').open('a', encoding='utf-8') as f:
                    f.write(json.dumps(event) + '\n')
                return
            if event['observed_status'] != 'QUEUED':
                event.update(state='STOPPED_NON_QUEUE_STATE', finished=True)
                deploy.save('monitor_status.json', event)
                with (stage / 'monitor_events.jsonl').open('a', encoding='utf-8') as f:
                    f.write(json.dumps(event) + '\n')
                return
            try:
                deploy.main('retry')
                event['retry_result'] = 'SUBMITTED_OR_ALREADY_RUNNING'
            except RuntimeError as exc:
                if 'Maximum batch GPU session count of 2 reached.' in str(exc):
                    event['retry_result'] = 'SERVER_BATCH_SESSION_LIMIT'
                else:
                    raise
            event.update(state='WAITING', finished=False)
        except Exception as exc:
            event.update(state='REQUEST_ERROR', error_type=type(exc).__name__, finished=False)
            # Credentials or request validation need intervention; never loop blindly.
            if type(exc).__name__ in ('HTTPError', 'ValueError', 'TypeError'):
                event['finished'] = True
        deploy.save('monitor_status.json', event)
        with (stage / 'monitor_events.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps(event) + '\n')
        if event.get('finished'):
            return
        time.sleep(60)

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    main()
