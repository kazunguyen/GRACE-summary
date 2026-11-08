# Review Packet: case_06_qemu_IRQ_testbit_21393_16959

- **Dataset:** Devign
- **Project:** qemu
- **Function Hint:** `IRQ_testbit`
- **Vulnerable Donor:** `devign:train:21393` (Commit `af7e9e74c6a62a5bcd911726a9e88d28b61490e0`)
- **Patched Candidate:** `devign:train:16959` (Commit `e69a17f65e9f12f33c48b04a789e49d40a8993f5`)
- **Payload SHA-256:** `d093215330d3ac0d31be24dea50f1b87790c8e18f0efc54909791876cf206017`

## Source Revisions
- Direct Parent Edge: **False**
- Vulnerable Parents: `['d56af005dc3d6354bd39411e8446b415bbcf86b8']`
- Patched Parents: `['47f73749c61765f7a898ac88f11995368740da10']`

## Changed Files
- Vulnerable commit changed: `['hw/openpic.c']`
- Patched commit changed: `['hw/openpic.c']`
- Shared files: `['hw/openpic.c']`

## Commit Messages
- **Vulnerable:** openpic: fix coding style issues

This patch fixes the following coding style violations:

  - structs have to be typedef and be CamelCase
  - if()s are always surrounded by curly braces

Signed-off-b
- **Patched:** openpic: use standard bitmap operations

Besides the private implementation being redundant, namespace collisions
prevented the use of other things in bitops.h.

Serialization does get a bit more awkw
