"""Task-owned local watcher: stop automatically when all 10 validation locks exist."""
import os,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
from auto_lock_validation import scan_once

HERE=Path(__file__).resolve().parent
class Tee:
    def __init__(self,console,path):self.console=console;self.file=path.open('a',encoding='utf-8',buffering=1)
    def write(self,text):self.console.write(text);self.file.write(text)
    def flush(self):self.console.flush();self.file.flush()
sys.stdout=Tee(sys.stdout,HERE/'threshold_watch.log')
sys.stderr=Tee(sys.stderr,HERE/'threshold_watch.stderr.log')
(HERE/'threshold_watch.pid').write_text(str(os.getpid()),encoding='ascii')
while not (HERE/'threshold_watch.stop').exists():
    print(datetime.now(timezone.utc).isoformat(),'scan local validation artifacts',flush=True)
    try:
        statuses=scan_once()
        if all(r['complete'] for r in statuses):
            print('All validation thresholds locked; watcher finished.',flush=True);break
    except Exception:
        # A checkpoint may be copying/writing. Never fit through an identity error;
        # leave existing immutable locks intact and retry after the next interval.
        traceback.print_exc()
    time.sleep(60)
print('Watcher stopped.',flush=True)
