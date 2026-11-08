# Review Packet: case_03_qemu_vnc_client_error_11725_3267

- **Dataset:** Devign
- **Project:** qemu
- **Function Hint:** `vnc_client_error`
- **Vulnerable Donor:** `devign:train:11725` (Commit `198a0039c5fca224a77e9761e2350dd9cc102ad0`)
- **Patched Candidate:** `devign:train:3267` (Commit `5fb6c7a8b26eab1a22207d24b4784bd2b39ab54b`)
- **Payload SHA-256:** `7b62a4a5653f2f7228acfeb10916c98a5b04ffa3a0e6cd83cad149a8b00a7ce8`

## Source Revisions
- Direct Parent Edge: **False**
- Vulnerable Parents: `['11a1feb6552e3a4709e454faea5e3be5ca8d9e6a']`
- Patched Parents: `['19a490bfca85165de1acd2d5c3964fb44615746d']`

## Changed Files
- Vulnerable commit changed: `['vnc.c']`
- Patched commit changed: `['vnc.c', 'Makefile', 'vnc.h']`
- Shared files: `['vnc.c']`

## Commit Messages
- **Vulnerable:** vnc: rework VncState release workflow.

Split socket closing and releasing of VncState into two steps.  First
close the socket and set the variable to -1 to indicate shutdown in
progress.  Do the actu
- **Patched:** Move TLS auth into separate file ("Daniel P. Berrange")

This patch refactors the existing TLS code to make the main VNC code
more managable. The code moves to two new files

 - vnc-tls.c: generic hel
