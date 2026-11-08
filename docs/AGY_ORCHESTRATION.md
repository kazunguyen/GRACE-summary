# AGY worker orchestration

User preference (2026-11-08): use AGY CLI for all delegated workers. The main
assistant coordinates, talks to the user and reviews evidence. Do not spawn GPT
subagents or silently fall back to another backend. Earlier permission mentioning
sol/luna does not override the later instruction to avoid GPT multiagent work.

Use `scripts/agy_team.py` for isolated task directories, explicit prompts, CLI
conversation IDs, logs and output hashes. Installed CLI is currently
`C:/Users/ADMIN/AppData/Local/agy/bin/agy.exe`; resolve it dynamically if moved.
The selected worker model is `gemini-3.8-flash-medium`, discovered from the actual
CLI. Do not use `--dangerously-skip-permissions`. Individual workers run in
their own workspace under the batch directory with scoped input copies and
separate outputs. They must never edit originals, launch GPU jobs, change locks,
use credentials, send messages to people, or fabricate human review decisions.

Outputs are untrusted until reviewed. A SUCCESS response or zero exit code is
not acceptance: verify source hashes, row IDs/counts, citations, scripts and
claims independently. Preserve failed/partial runs and distinguish submitted,
running, completed, reviewed and rejected work. Stop on authentication/quota
errors and report the blocker rather than replacing AGY with GPT workers.

Current working delegation pattern is data-minimized code generation:
`scripts/prepare_agy_safe_codegen_20261108.py` prepares three schema-only tasks;
`scripts/agy_team.py TASK --batch Runs-management/agy_b3_safe_codegen_20261108`
calls AGY in plan mode with an explicit no-tools prompt. Workers return file
contents in JSON, which the controller stores only under the task's outputs.
Review generated code before local execution against train banks. Never feed the
resulting donor indexes, snippets or private data back into workers without
specific authorization. An initial full-bank Devign delegation was rejected by
automatic review; it must not be retried indirectly. The generic schema-only
code-generation alternative avoids that payload.

AGY may return `SUCCESS` with an empty response and `denied_actions` when a
headless tool needs permission. Treat that as blocked, never as completion.
This account does not support `--mode auto`; use plan/code-response mode.

For B3 discovery use clean train banks only. Candidate discovery, source
authentication, human review, prompt freeze and inference are separate stages.
No candidate becomes an eligible verified patch pair merely because a worker
labels it so. Genuine dual human review and the existing admission checks remain
required. Existing Kaggle inference is outside worker scope.
