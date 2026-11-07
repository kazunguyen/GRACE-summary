import json
import sys
import os
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('01_Author_Baseline_Unified/diagnostic_kit/src'))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from grace_diag.amended_b3 import (
    digest, patch_text, changed_lines, difference_from_source,
    make_pair_candidate, validate_pair, VerifiedPairSelector
)
from tests.test_amended_b3 import fixture_pair
from grace_diag.token_budget import TokenCounter

pair_data, bank = fixture_pair('test-patch-1', 'process_packet')
print('Pair created:', pair_data['pair_id'])
print('Key difference:', pair_data['key_difference'])

with open('data/specs/devign_validation_15arms.jsonl', 'r', encoding='utf-8') as f:
    raw_target = json.loads(f.readline())

target = {
    'id': raw_target['id'],
    'query_code': raw_target['query_code'],
    'nodes': raw_target['nodes'],
    'edges': raw_target['edges']
}

counter = TokenCounter(None)
counter.approx = False
selector = VerifiedPairSelector([pair_data], bank, 'devign')
sel_p, demos, meta = selector.select(target['query_code'])
print('Selected:', meta)

# Render
family = selector.render_family(target, counter)
print('Arms generated:', list(family.keys()))
print('=== B3 PROMPT ===')
print('Keys in family B3:', family['B3'].keys())
print('=== DEMONSTRATION SECTION ===')
idx = family['B3']['prompt'].find('Here is a demonstration')
if idx != -1:
    print(family['B3']['prompt'][idx:])
else:
    print(family['B3']['prompt'][-1500:])
