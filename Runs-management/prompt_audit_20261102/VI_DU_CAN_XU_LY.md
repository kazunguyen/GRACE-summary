# Ví dụ demo dưới 25% cần xử lý

Giữ nguyên contract 25% theo xác nhận người dùng. Chưa thay prompt hoặc chạy lại LLM.

| Arm | Phiên | Dataset/split | Target | Demo | Token gốc | Token còn | Tỷ lệ | Đã inference |
|---|---|---|---|---|---:|---:|---:|---|
| B2 | legacy | devign/validation | devign:validation:1836 | devign:train:26033 | 6062 | 1500 | 24.74% | True |
| B2-flip | legacy | devign/validation | devign:validation:1836 | devign:train:26033 | 6062 | 1500 | 24.74% | True |
| B2 | legacy | devign/test | devign:test:569 | devign:train:1095 | 39215 | 1500 | 3.83% | True |
| B2-flip | legacy | devign/test | devign:test:569 | devign:train:1095 | 39215 | 1500 | 3.83% | True |
| B2 | legacy | reveal/validation | reveal:validation:86 | reveal:train:14557 | 12753 | 1499 | 11.75% | True |
| B2-flip | legacy | reveal/validation | reveal:validation:86 | reveal:train:14557 | 12753 | 1499 | 11.75% | True |
