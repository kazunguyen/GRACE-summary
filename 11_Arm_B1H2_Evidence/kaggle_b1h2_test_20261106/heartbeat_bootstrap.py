print('[PING] B1-H2 notebook: Python execution started', flush=True)

import sys
import threading
import time

# Stop and unregister a previous heartbeat when Run All is repeated in one kernel.
_previous_heartbeat = globals().get('_b1h2_heartbeat_cleanup')
if _previous_heartbeat is not None:
    _previous_heartbeat('restarted')

HEARTBEAT_INTERVAL_SECONDS = 30
_heartbeat_session_start = time.time()
_heartbeat_stop_event = threading.Event()
_heartbeat_state = {'stage': 'bootstrap'}
_heartbeat_stream = sys.stdout


def heartbeat_stage(stage):
    _heartbeat_state['stage'] = str(stage)
    print('[STAGE] ' + str(stage), flush=True)


def _heartbeat_loop(stop=_heartbeat_stop_event, state=_heartbeat_state,
                    stream=_heartbeat_stream, started=_heartbeat_session_start,
                    interval=HEARTBEAT_INTERVAL_SECONDS):
    # This thread does no file, network, GPU or subprocess I/O.
    while not stop.wait(interval):
        elapsed = time.time() - started
        stamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        stream.write(f'[PING] {stamp} kernel_alive elapsed={elapsed:.0f}s stage={state["stage"]}\n')
        stream.flush()


_heartbeat_thread = threading.Thread(target=_heartbeat_loop, name='b1h2-heartbeat', daemon=True)
_heartbeat_thread.start()
_heartbeat_shell = get_ipython()


def _b1h2_heartbeat_cleanup(reason='finished'):
    _heartbeat_stop_event.set()
    if _heartbeat_thread is not threading.current_thread():
        _heartbeat_thread.join(timeout=1)
    try:
        _heartbeat_shell.events.unregister('post_run_cell', _heartbeat_after_cell)
    except (ValueError, KeyError):
        pass
    print('[PING STOP] ' + str(reason), flush=True)


def _heartbeat_after_cell(result):
    error = getattr(result, 'error_before_exec', None) or getattr(result, 'error_in_exec', None)
    if error is not None:
        _b1h2_heartbeat_cleanup(f'cell failed: {type(error).__name__}: {error}')


_heartbeat_shell.events.register('post_run_cell', _heartbeat_after_cell)
heartbeat_stage('starting notebook setup')
