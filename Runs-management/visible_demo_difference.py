"""Conservative contrastive descriptions grounded in the displayed C/C++ excerpts."""
import re

FALLBACK = "No supported security-relevant difference was identified in the displayed excerpts."
LABEL_WORD = re.compile(r"\b(?:vulnerable|safe|unsafe)\b", re.I)
NON_CODE = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*[\s\S]*?\*/|//[^\n]*')
PATTERNS = (
    ("conditional check", re.compile(r"\bif\s*\((?:[^()\n;]|\([^()\n;]*\)){1,125}\)")),
    ("memory or resource call", re.compile(
        r"\b\w*(?:memcpy|memmove|memset|strcpy|strncpy|strcat|snprintf|sprintf|malloc|calloc|realloc|free|alloc|copy_to_user|copy_from_user)\w*"
        r"\s*\((?:[^()\n;]|\([^()\n;]*\)){0,100}\)", re.I,
    )),
    ("bracketed expression", re.compile(r"\b[A-Za-z_]\w*\s*\[[^\]\n;]{1,65}\]")),
)


def observations(excerpt):
    masked = NON_CODE.sub(lambda match: " " * len(match[0]), excerpt)
    body_start = masked.find("{")
    if body_start < 0:
        return []
    result = []
    for kind, pattern in PATTERNS:
        for match in pattern.finditer(masked, body_start + 1):
            if kind == "memory or resource call" and masked[match.end():].lstrip().startswith("{"):
                continue
            snippet = excerpt[match.start():match.end()].strip()
            if not LABEL_WORD.search(snippet) and "`" not in snippet:
                result.append((kind, snippet, re.sub(r"\s+", "", snippet)))
    return result


def describe(vulnerable_excerpt, safe_excerpt):
    """Describe a visible contrast without asserting reachability, safety or absence."""
    left, right = observations(vulnerable_excerpt), observations(safe_excerpt)
    left_keys = {item[2] for item in left}
    right_keys = {item[2] for item in right}
    for kind, _ in PATTERNS:
        first = next((item for item in left if item[0] == kind and item[2] not in right_keys), None)
        second = next((item for item in right if item[0] == kind and item[2] not in left_keys), None)
        if first is not None and second is not None:
            break
    else:
        return FALLBACK, {"status": "no_supported_difference"}
    text = (
        f"The Vulnerable example shows the {first[0]} `{first[1]}`. "
        f"The Non-vulnerable example shows the {second[0]} `{second[1]}`."
    )
    return text, {
        "status": "visible_code_contrast",
        "vulnerable_snippet": first[1], "non_vulnerable_snippet": second[1],
    }
