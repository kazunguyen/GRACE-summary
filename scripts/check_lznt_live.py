import os
from kaggle.api.kaggle_api_extended import KaggleApi

user = "lznt123"
token = "KGAT_107f196b3b616d0d60398c64eb11f2bd"
os.environ["KAGGLE_API_TOKEN"] = token
os.environ["KAGGLE_USERNAME"] = user
os.environ["KAGGLE_KEY"] = token

api = KaggleApi()
api.authenticate()

slug = "lznt123/grace-b3-validation"
st = api.kernels_status(slug)
print(f"[{slug}] Status: {st}")
