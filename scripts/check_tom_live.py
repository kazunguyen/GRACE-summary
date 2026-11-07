import os
from kaggle.api.kaggle_api_extended import KaggleApi

user = "tomandjerry223"
token = "c78b44e56259c2bb09962d5d1806ddf1"
os.environ.pop("KAGGLE_API_TOKEN", None)
os.environ["KAGGLE_USERNAME"] = user
os.environ["KAGGLE_KEY"] = token

api = KaggleApi()
api.authenticate()

for slug in ["tomandjerry223/grace-b2-labelonly-test", "tomandjerry223/grace-b2-nolabel-test"]:
    st = api.kernels_status(slug)
    print(f"[{slug}] Status: {st}")
