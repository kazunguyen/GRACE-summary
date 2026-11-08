import os
import sys
import json
import builtins
import requests

orig_open = builtins.open
def utf8_open(*args, **kwargs):
    if len(args) > 1 and 'b' in args[1]:
        return orig_open(*args, **kwargs)
    if 'mode' in kwargs and 'b' in kwargs['mode']:
        return orig_open(*args, **kwargs)
    if 'encoding' not in kwargs:
        kwargs['encoding'] = 'utf-8'
    return orig_open(*args, **kwargs)
builtins.open = utf8_open

from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk.kernels.types.kernels_api_service import ApiListKernelSessionOutputRequest

ACCOUNTS = {
    'thanhduy9a4tv': {'key': 'KGAT_47e27c5341b3301eea2f4e8f3d4743d6'},
    'tomandjerry223': {'key': None}
}

RUNS = [
    ('B1-full', 'tomandjerry223', 'grace-b1-full-validation'),
    ('B2-nolabel', 'tomandjerry223', 'grace-b2-nolabel-validation'),
    ('B2-labelonly', 'thanhduy9a4tv', 'grace-b2-labelonly-validation'),
    ('B2-rep', 'thanhduy9a4tv', 'grace-b2-rep-validation'),
]

out_dir = 'Runs-management/downloaded_executed_notebooks'
os.makedirs(out_dir, exist_ok=True)

for arm, user, slug in RUNS:
    os.environ['KAGGLE_USERNAME'] = user
    if ACCOUNTS[user]['key']:
        os.environ['KAGGLE_KEY'] = ACCOUNTS[user]['key']
        os.environ['KAGGLE_API_TOKEN'] = ACCOUNTS[user]['key']
    else:
        for k in ['KAGGLE_KEY', 'KAGGLE_API_TOKEN']:
            if k in os.environ:
                del os.environ[k]

    api = KaggleApi()
    api.authenticate()
    with api.build_kaggle_client() as kaggle:
        req = ApiListKernelSessionOutputRequest()
        req.user_name = user
        req.kernel_slug = slug
        resp = kaggle.kernels.kernels_api_client.list_kernel_session_output(req)
        if not resp.files:
            print(f"Failed to get files for {arm}")
            continue
        sample_url = resp.files[0].url
        base_url = sample_url.split('/' + resp.files[0].file_name)[0] + '/'
        
        # Download __notebook__.ipynb
        nb_url = base_url + '__notebook__.ipynb'
        r = requests.get(nb_url)
        arm_slug = arm.lower().replace('-', '_')
        if r.status_code == 200:
            nb_path = os.path.join(out_dir, f'02_kaggle_qwen_q4_{arm_slug}_validation_executed.ipynb')
            with open(nb_path, 'wb') as f:
                f.write(r.content)
            nb = json.loads(r.content)
            outs = sum(len(c.get('outputs', [])) for c in nb.get('cells', []))
            print(f"{arm}: EXECUTED NOTEBOOK SUCCESS! ({len(r.content)} bytes, {outs} outputs) -> {nb_path}")
        else:
            print(f"{arm}: Failed __notebook__.ipynb (status {r.status_code})")

        # Also download __results__.html if available
        html_url = base_url + '__results__.html'
        r_html = requests.get(html_url)
        if r_html.status_code == 200:
            html_path = os.path.join(out_dir, f'02_kaggle_qwen_q4_{arm_slug}_validation_report.html')
            with open(html_path, 'wb') as f:
                f.write(r_html.content)
            print(f"{arm}: HTML REPORT SUCCESS! ({len(r_html.content)} bytes) -> {html_path}")
