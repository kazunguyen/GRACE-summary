"""Verify the <=100 MiB prompt input delivery, without ML dependencies."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
INVENTORY=ROOT/'Runs-management/prompt_input_inventory_20261102.json'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--git-ref',help='Also check exact blobs in a local/fetched Git ref')
    args=parser.parse_args();manifest=json.loads(INVENTORY.read_text(encoding='utf-8'))
    git_blobs={}
    if args.git_ref:
        result=subprocess.run(['git','-C',str(ROOT),'ls-tree','-r','-z','--full-tree',args.git_ref],check=True,stdout=subprocess.PIPE)
        for record in result.stdout.split(b'\0'):
            if record:
                meta,path=record.split(b'\t',1)
                git_blobs[path.decode('utf-8')]=meta.decode().split()[2]
    checked=0;errors=[];skipped=[]
    for entry in manifest['files']:
        rel=entry['path'];path=ROOT/rel
        if not path.resolve().is_relative_to(ROOT):raise ValueError('Path outside repo')
        if entry['action']=='skip_over_100_mib':
            skipped.append({'path':rel,'bytes':entry['bytes'],'present_local':path.exists()});continue
        if not path.is_file():errors.append({'path':rel,'error':'missing eligible input'});continue
        size=path.stat().st_size
        if size!=entry['bytes'] or size>manifest['file_limit_bytes']:
            errors.append({'path':rel,'error':'size mismatch/over limit'});continue
        digest=hashlib.sha256();blob=hashlib.sha1(b'blob '+str(size).encode()+b'\0')
        with path.open('rb') as stream:
            for chunk in iter(lambda:stream.read(4*1024*1024),b''):
                digest.update(chunk);blob.update(chunk)
        if digest.hexdigest()!=entry['sha256']:
            errors.append({'path':rel,'error':'SHA256 mismatch'});continue
        if args.git_ref and git_blobs.get(rel)!=blob.hexdigest():
            errors.append({'path':rel,'error':'missing/different bytes in Git ref'});continue
        checked+=1
    report={'status':'pass' if not errors else 'fail','verified_eligible_files':checked,
        'expected_eligible_files':manifest['eligible_file_count'],'git_ref':args.git_ref,
        'skipped_over_100_mib':skipped,'errors':errors,
        'scope':'eligible input files only; full CPG/donor graphs still require separate transfer'}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors or checked!=manifest['eligible_file_count']:raise SystemExit(1)
if __name__=='__main__':main()
