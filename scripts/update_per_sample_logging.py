from pathlib import Path

# 1. Update Runs-management/prepare_kaggle_test_4arms.py
p1 = Path("Runs-management/prepare_kaggle_test_4arms.py")
t1 = p1.read_text(encoding="utf-8")

old_rl = (
    '            if \'Inference \' in line or \'Completed\' in line:\\n",\n'
    '                    "                print(line.strip(), flush=True)\\n",'
)
new_rl = '            print(line, end=\'\', flush=True)\\n",'

old_sample = (
    '            if len(done_ids) % 100 == 0 or len(done_ids) == total_count:\\n",\n'
    '                    "                print(f\'Inference {arm} {ds} test: {len(done_ids)}/{total_count} (s={s_val:.4f}, raw={raw!r})\', flush=True)\\n",'
)
new_sample = '            print(f\'{arm}/{ds} {uid}: s={s_val:.4f}, raw={raw!r} ({len(done_ids)}/{total_count})\', flush=True)\\n",'

if old_rl in t1:
    t1 = t1.replace(old_rl, new_rl)
    print("Replaced run_logged stdout forwarding in prepare_kaggle_test_4arms.py")
else:
    print("Warning: old_rl not found")

if old_sample in t1:
    t1 = t1.replace(old_sample, new_sample)
    print("Replaced sample logging in prepare_kaggle_test_4arms.py")
else:
    print("Warning: old_sample not found")

p1.write_text(t1, encoding="utf-8")

# 2. Update scripts/create_b1_shuf_test_notebook.py
p2 = Path("scripts/create_b1_shuf_test_notebook.py")
t2 = p2.read_text(encoding="utf-8")

old_rl2 = (
    '            if \'Inference \' in line or \'Completed\' in line:\n'
    '                print(line.strip(), flush=True)'
)
new_rl2 = '            print(line, end=\'\', flush=True)'

old_sample2 = (
    '            if len(done_ids) % 100 == 0 or len(done_ids) == total_count:\n'
    '                print(f\'Inference {arm} s{seed} {ds} test: {len(done_ids)}/{total_count} (s={s_val:.4f}, raw={raw!r})\', flush=True)'
)
new_sample2 = '            print(f\'{arm}/s{seed}/{ds} {uid}: s={s_val:.4f}, raw={raw!r} ({len(done_ids)}/{total_count})\', flush=True)'

if old_rl2 in t2:
    t2 = t2.replace(old_rl2, new_rl2)
    print("Replaced run_logged in create_b1_shuf_test_notebook.py")
else:
    print("Warning: old_rl2 not found")

if old_sample2 in t2:
    t2 = t2.replace(old_sample2, new_sample2)
    print("Replaced sample logging in create_b1_shuf_test_notebook.py")
else:
    print("Warning: old_sample2 not found")

p2.write_text(t2, encoding="utf-8")
