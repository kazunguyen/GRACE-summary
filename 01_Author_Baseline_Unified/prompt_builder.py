"""
GRACE Prompt Builder Module
Assembles prompts strictly adhering to evaluation_contract_v2:
  - Context limit: 8192 UTF-8 bytes cap
  - Graph context: Whole CPG with max 40 nodes, max 80 edges
  - Truncation order: Demo code -> Graph context -> Target code (preserving prefix)
  - Output contract: Binary 0/1 on the exact last non-empty line
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from graph_extractor import format_graph_context


DEFAULT_TEMPLATE = """### TASK INSTRUCTION
You are an expert C/C++ software security researcher.
Determine whether the target function contains a software vulnerability.
Use the target code, graph context, and labeled reference examples as evidence.

### TARGET CODE
{target_code}

### GRAPH CONTEXT
{graph_context}

### REFERENCE EXAMPLES
{demonstrations}

### OUTPUT CONTRACT
Analyze the target function carefully. You may reason internally, but do not
write an explanation in the response. The last non-empty line of your response
must contain exactly one character: `1` if the target is Vulnerable, or `0` if
the target is Non-vulnerable. Do not output any other label or score.
"""


class PromptBuilder:
    def __init__(
        self,
        template_path: Optional[Path] = None,
        context_limit_bytes: int = 8192,
        graph_nodes_max: int = 40,
        graph_edges_max: int = 80,
        target_code_max_chars: int = 3000,
        standard_demo_max_chars: int = 1500,
    ):
        if template_path and template_path.is_file():
            self.template = template_path.read_text(encoding="utf-8")
        else:
            self.template = DEFAULT_TEMPLATE

        self.context_limit_bytes = context_limit_bytes
        self.graph_nodes_max = graph_nodes_max
        self.graph_edges_max = graph_edges_max
        self.target_code_max_chars = target_code_max_chars
        self.standard_demo_max_chars = standard_demo_max_chars

    def build_prompt(
        self,
        target_sample: Dict[str, Any],
        demonstration_sample: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Builds the prompt and iteratively reduces components if UTF-8 bytes exceed context_limit_bytes.
        Truncation order: Demo code -> Graph context -> Target code.
        """
        # 1. Target code initial slice
        target_code = target_sample.get("func", "")[: self.target_code_max_chars]

        # 2. Graph context initial slice
        nodes = target_sample.get("nodes", [])
        edges = target_sample.get("edges", [])
        graph_context, graph_meta = format_graph_context(
            nodes, edges, max_nodes=self.graph_nodes_max, max_edges=self.graph_edges_max
        )

        # 3. Demonstration initial slice
        demo_label_str = ""
        demo_code = ""
        if demonstration_sample is not None and demonstration_sample.get("func"):
            label_val = int(demonstration_sample.get("target", 0))
            demo_label_str = "Vulnerable (1)" if label_val == 1 else "Non-vulnerable (0)"
            demo_code = demonstration_sample["func"][: self.standard_demo_max_chars]

        def render(t_code: str, g_ctx: str, d_code: str) -> str:
            if d_code:
                demo_text = f"{demo_label_str} example:\n{d_code}"
            else:
                demo_text = "[No reference demonstration available]"

            return (
                self.template
                .replace("{target_code}", t_code)
                .replace("{graph_context}", g_ctx)
                .replace("{demonstrations}", demo_text)
            )

        prompt = render(target_code, graph_context, demo_code)
        encoded_bytes = len(prompt.encode("utf-8"))

        # Iterative truncation to fit within context_limit_bytes
        # Step A: Truncate demo code first
        while encoded_bytes > self.context_limit_bytes and demo_code:
            excess = encoded_bytes - self.context_limit_bytes
            reduction = min(len(demo_code), max(1, excess))
            demo_code = demo_code[: len(demo_code) - reduction]
            prompt = render(target_code, graph_context, demo_code)
            encoded_bytes = len(prompt.encode("utf-8"))

        # Step B: Truncate graph context if still exceeding
        while encoded_bytes > self.context_limit_bytes and graph_context:
            excess = encoded_bytes - self.context_limit_bytes
            reduction = min(len(graph_context), max(1, excess))
            graph_context = graph_context[: len(graph_context) - reduction]
            prompt = render(target_code, graph_context, demo_code)
            encoded_bytes = len(prompt.encode("utf-8"))

        # Step C: Truncate target code if still exceeding
        while encoded_bytes > self.context_limit_bytes and target_code:
            excess = encoded_bytes - self.context_limit_bytes
            reduction = min(len(target_code), max(1, excess))
            target_code = target_code[: len(target_code) - reduction]
            prompt = render(target_code, graph_context, demo_code)
            encoded_bytes = len(prompt.encode("utf-8"))

        if encoded_bytes > self.context_limit_bytes:
            raise ValueError(
                f"Prompt could not fit into {self.context_limit_bytes} bytes even after truncating all components! "
                f"Current bytes: {encoded_bytes}"
            )

        truncation_metadata = {
            "context_limit_bytes": self.context_limit_bytes,
            "prompt_utf8_bytes": encoded_bytes,
            "target_chars_used": len(target_code),
            "graph_chars_used": len(graph_context),
            "demo_chars_used": len(demo_code) if demo_code else 0,
            "graph_nodes_used": graph_meta["nodes_used"],
            "graph_edges_used": graph_meta["edges_used"],
        }

        return prompt, truncation_metadata
