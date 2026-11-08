"""Read-only fetch of three public source endpoints into audit evidence only."""
from pathlib import Path
import hashlib,json,ssl,urllib.request
from datetime import datetime,timezone
import certifi
OUT=Path(__file__).resolve().parent
BASE=OUT.parent/'g1_source_investigation_20261108/case_08_ffmpeg_can_safely_read_8614_26054'
fix='3d7817048cb387de87600f2152075f78b37b60a6';parent='4b529edff8934c258af95e5acc51f84deea66262'
sources=[('commit.json',f'https://api.github.com/repos/FFmpeg/FFmpeg/commits/{fix}','github_commit_3d7817048c.json'),
    ('parent.c',f'https://raw.githubusercontent.com/FFmpeg/FFmpeg/{parent}/libavcodec/escape124.c','parent_file_4b529edff8.c'),
    ('fix.c',f'https://raw.githubusercontent.com/FFmpeg/FFmpeg/{fix}/libavcodec/escape124.c','fix_file_3d7817048c.c')]
results=[];dest=OUT/'upstream_readback';dest.mkdir(exist_ok=True)
for name,url,archived in sources:
    row={'url':url,'checked_at_utc':datetime.now(timezone.utc).isoformat()}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'GRACE-independent-source-audit'})
        with urllib.request.urlopen(req,context=ssl.create_default_context(cafile=certifi.where()),timeout=25) as res:raw=res.read()
        (dest/name).write_bytes(raw);row['sha256']=hashlib.sha256(raw).hexdigest()
        row['exact_archive_bytes_match']=raw==(BASE/archived).read_bytes()
        if name=='commit.json':
            live=json.loads(raw);old=json.loads((BASE/archived).read_bytes())
            row['source_identity_fields_match']=all(live[k]==old[k] for k in ('sha','parents','files','commit'))
    except Exception as exc:row['error']=str(exc)
    results.append(row)
(OUT/'upstream_readback.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
print(json.dumps(results,indent=2))
