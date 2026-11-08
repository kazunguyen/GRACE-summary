# Review Evidence Packet: case_03_qemu_vnc_client_error_11725_3267

- **Dataset:** Devign
- **Project:** qemu
- **Function Hint:** `vnc_client_error`
- **Vulnerable Donor:** `devign:train:11725` (Commit `198a0039c5fca224a77e9761e2350dd9cc102ad0`)
- **Patched Candidate:** `devign:train:3267` (Commit `5fb6c7a8b26eab1a22207d24b4784bd2b39ab54b`)
- **Payload SHA-256:** `3933d59c76f09db058e7e2475471acd6ea87d2baad3be8d839978f944d704b94`

## Source Revisions
- Direct Parent Edge in Git: **False**
- Vulnerable Parents: `['11a1feb6552e3a4709e454faea5e3be5ca8d9e6a']`
- Patched Parents: `['19a490bfca85165de1acd2d5c3964fb44615746d']`

## Changed Files
- Vulnerable Commit Modified: `['vnc.c']`
- Patched Commit Modified: `['Makefile', 'vnc.c', 'vnc.h']`
- Shared Files: `['vnc.c']`

## Commit Messages
- **Vulnerable:** vnc: rework VncState release workflow.

Split socket closing and releasing of VncState into two steps.  First
close the socket and set the variable to -1 to indicate shutdown in
progress.  Do the actu
- **Patched:** Move TLS auth into separate file ("Daniel P. Berrange")

This patch refactors the existing TLS code to make the main VNC code
more managable. The code moves to two new files

 - vnc-tls.c: generic hel

## Review Instructions for Human Reviewers
Please fill out a separate review form verifying:
1. `same_function_verified`: Are the two functions genuinely the same function in upstream source?
2. `security_fix_verified`: Does the change represent an authentic security vulnerability fix?
3. `source_revisions_verified`: Do the commit revisions connect via git parentage and actual patch diff?
4. `explanation_supported`: Is the difference rationale supported by reviewed code changes?
Include `payload_sha256` matching above to certify authenticity.
