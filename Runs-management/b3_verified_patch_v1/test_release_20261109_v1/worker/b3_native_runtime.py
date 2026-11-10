import re

def native_log_check(text, contract):
    required = contract['gpu']['required_offloaded_layers']
    pairs = re.findall(r'offloaded\s+(\d+)\s*/\s*(\d+)\s+layers?\s+to\s+GPU', text, re.I)
    if not any(int(a) == int(b) == required for a,b in pairs):
        raise ValueError('Full GPU offload not verified')
    for field in ('n_ctx','n_batch','n_ubatch'):
        values = re.findall(r'\b'+field+r'\s*=\s*(\d+)\b', text)
        if not values or int(values[-1]) != contract['constructor'][field]:
            raise ValueError('Effective '+field+' differs from contract')
    devices = set(re.findall(r'using device CUDA(\d+)\s*\([^\n)]*\bT4\b[^\n)]*\)', text, re.I))
    devices.update(re.findall(r'Device\s+(\d+):\s+[^\n]*\bT4\b', text))
    if devices != set(map(str, range(contract['gpu']['device_count']))):
        raise ValueError('Two distinct T4 devices not verified')
