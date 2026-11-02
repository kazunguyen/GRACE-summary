"""Sink Evidence Extraction Module (H2 Evidence for B1-H2 arm).
Trích xuất thông tin guarded/unguarded sink từ mã nguồn C/C++.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

SINK_CATEGORIES = {
    "memcpy": "buffer_write",
    "memmove": "buffer_write",
    "bcopy": "buffer_write",
    "memset": "buffer_write",
    "strcpy": "buffer_write",
    "strncpy": "buffer_write",
    "strcat": "buffer_write",
    "strncat": "buffer_write",
    "sprintf": "format_string",
    "snprintf": "format_string",
    "vsprintf": "format_string",
    "vsnprintf": "format_string",
    "printf": "format_string",
    "fprintf": "format_string",
    "gets": "buffer_write",
    "fgets": "buffer_write",
    "scanf": "format_string",
    "sscanf": "format_string",
    "malloc": "alloc",
    "calloc": "alloc",
    "realloc": "alloc",
    "free": "pointer_free",
}

WRAPPER_RULES = {
    "av_malloc": ("alloc", "FFmpeg allocation API"),
    "av_mallocz": ("alloc", "FFmpeg zeroed allocation API"),
    "av_free": ("pointer_free", "FFmpeg deallocation API"),
    "av_freep": ("pointer_free", "FFmpeg deallocation through pointer API"),
    "g_malloc": ("alloc", "GLib allocation API"),
    "g_malloc0": ("alloc", "GLib zeroed allocation API"),
    "g_free": ("pointer_free", "GLib deallocation API"),
}

_NONCODE = re.compile(r'//[^\r\n]*|/\*[\s\S]*?\*/|"(?:\\[\s\S]|[^"\\])*"|\'(?:\\[\s\S]|[^\'\\])*\'')
_TOKEN = re.compile(r'[A-Za-z_]\w*|->|::|&&|\|\||[^\s]')
_IDENT = re.compile(r'^[A-Za-z_]\w*$')
_CONTROL = {"if", "for", "while", "switch", "sizeof", "alignof", "return"}


def mask_noncode(code: str) -> str:
    return _NONCODE.sub(lambda m: "".join(c if c in "\r\n" else " " for c in m.group()), code)


def extract_sink_evidence(code: str) -> Dict[str, Any]:
    """Trích xuất danh sách các điểm gọi API nhạy cảm an ninh từ mã nguồn C/C++."""
    masked = mask_noncode(code)
    tokens = [(m.group(), m.start(), m.end()) for m in _TOKEN.finditer(masked)]
    pairs = {}
    stack = []
    for idx, (token, _, _) in enumerate(tokens):
        if token == "(":
            stack.append(idx)
        elif token == ")" and stack:
            pairs[stack.pop()] = idx

    recognized: List[Dict[str, Any]] = []
    for idx, (name, start, end) in enumerate(tokens[:-1]):
        if not _IDENT.fullmatch(name) or name in _CONTROL or tokens[idx + 1][0] != "(":
            continue
        closing = pairs.get(idx + 1)
        if closing is None:
            continue
        
        family = None
        if name in SINK_CATEGORIES:
            family = SINK_CATEGORIES[name]
        elif name in WRAPPER_RULES:
            family = WRAPPER_RULES[name][0]

        if family:
            line_no = code[:start].count("\n") + 1
            call_end = tokens[closing][2]
            expr = code[start:call_end].strip().replace("\n", " ")
            if len(expr) > 80:
                expr = expr[:77] + "..."
            recognized.append({
                "api_name": name,
                "family": family,
                "line": line_no,
                "expression": expr,
            })

    return {"recognized": recognized}


def build_evidence_text(code: str) -> str:
    """Trích xuất khối bằng chứng an ninh H2 dạng text từ mã nguồn."""
    try:
        res = extract_sink_evidence(code)
        recognized = res.get("recognized", [])
        if not recognized:
            return "No guarded sink evidence detected."
        lines = []
        for r in recognized[:5]:  # Ngân sách vừa đủ
            lines.append(f"Sink {r['api_name']} ({r.get('family', 'unspecified')}) at line {r.get('line', '?')}: {r.get('expression', '')}")
        return "\n".join(lines)
    except Exception:
        return "No guarded sink evidence detected."
