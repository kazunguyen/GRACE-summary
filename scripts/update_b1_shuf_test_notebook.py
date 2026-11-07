import json

path = '08_Arm_B1_Shuf/notebooks/02_kaggle_qwen_q4_b1_shuf_test.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_cell_2_lines = [
    "import math\n",
    "ARM = 'B1-shuf'\n",
    "KAGGLE_INPUT_ROOT = Path('/kaggle/input')\n",
    "BUNDLE_WORK = Path('/kaggle/working/b1_shuf_test_bundles')\n",
    "OUT_ROOT = Path('/kaggle/working/b1_shuf_test_runtime_locked')\n",
    "BUNDLE_NAME = 'grace_b1_shuf_test_inputs.zip'\n",
    "BUNDLE_SHA256 = 'a6b2be70b85462d96d531884085eb62d581e5863cb8897a86b23f326f284508b'\n",
    "CHECKPOINT_NAME = 'grace_b1_shuf_test_runtime_locked_checkpoint.zip'\n",
    "CHECKPOINT_INPUT_PATH = None\n",
    "MODEL_FILENAME = 'Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf'\n",
    "MODEL_SHA256 = 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'\n",
    "MAX_RUNTIME_HOURS = 9\n",
    "CHECKPOINT_RESERVE_SECONDS = 300\n",
    "GPU_LAYERS = -1\n",
    "SETS = [\n",
    '    {"name": "seed_42/devign_test.zip", "sha256": "5333bb6a3615d19715f5d67a3e389e0c9cf20fb7c984a1fc22ec752d4f4d364a", "seed": 42, "dataset": "devign"},\n',
    '    {"name": "seed_42/reveal_test.zip", "sha256": "b17e8c454987de386916c1b236386232fada76310d4038e33e6370e036bafd8c", "seed": 42, "dataset": "reveal"},\n',
    '    {"name": "seed_43/devign_test.zip", "sha256": "1beb37a10d7c0fe302700675634044a64580fd2ff9b440230800e08632b4d236", "seed": 43, "dataset": "devign"},\n',
    '    {"name": "seed_43/reveal_test.zip", "sha256": "f102fcedbcc26de08be4eb5b56de533c2f05b1c949d2463188ec09592a6ea800", "seed": 43, "dataset": "reveal"},\n',
    '    {"name": "seed_44/devign_test.zip", "sha256": "77b427fe7a7bc7a71240c8b2282bb8980ea5afe0ec5fdbe4cbbdc7f8f035dab3", "seed": 44, "dataset": "devign"},\n',
    '    {"name": "seed_44/reveal_test.zip", "sha256": "6467d8ff18e38aa18849fabc3b90cdb6514104ed56892b92c6e3d9ce7a8b4868", "seed": 44, "dataset": "reveal"}\n',
    "]\n",
    'LOCKED_THRESHOLDS = {"42_devign": 0.98, "42_reveal": 0.66, "43_devign": 0.96, "43_reveal": 0.01, "44_devign": 0.67, "44_reveal": 0.04}\n',
    "\n",
    "FROZEN_MANIFEST_SHA256 = {\n",
    "    (42, 'devign'): '7bdf8cd7d1ee63a9a0cc28a4c87bda4b03f20de67f8c7f67b9691f348059df1e',\n",
    "    (42, 'reveal'): 'ab5ef7ec5e98aaafbd69d4ebe3d4a64e3ea91dd43233848c3e0b42f8f279d198',\n",
    "    (43, 'devign'): '4c1ac1f2bdec3d6730f2d6c3827bf9d31cba2baac871e2d2fc0e48a330f20633',\n",
    "    (43, 'reveal'): '30d8e018489f2c12192803c0e6ab03181402b3cd4a37e848a0167d211047ba51',\n",
    "    (44, 'devign'): '7a1de266b643b7239152e379dc84d335144d10c24e0b376a55782ba486cc532d',\n",
    "    (44, 'reveal'): '29306e03128fb6129e929971c63827c170e014603f2971824b1e57b3d751f728'\n",
    "}\n",
    "\n",
    "if (MODEL_FILENAME, MODEL_SHA256, GPU_LAYERS) != (\n",
    "    RUNTIME['model']['filename'], RUNTIME['model']['sha256'], RUNTIME['constructor']['n_gpu_layers']\n",
    "):\n",
    "    raise ValueError('Notebook model or GPU settings differ from runtime lock')\n",
]

nb['cells'][2]['source'] = new_cell_2_lines

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Updated B1-shuf test notebook Cell 2 successfully!')
