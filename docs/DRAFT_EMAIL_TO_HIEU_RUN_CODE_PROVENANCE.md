# Thư nháp hỏi Hiếu về code/readback của các run GRACE

Chưa gửi.

Tiêu đề: Nhờ xác nhận notebook/worker đã chạy cho các arm được giao Hiếu

Hiếu ơi,

Mình đang hoàn thiện hồ sơ tái lập GRACE. Mình đã rà run manifest, notebook/session đã lưu và toàn bộ branch hiện có trên origin. Hiện đã khớp exact worker SHA cho B1-full test, B1-shuf test và B2-rand test. Các run của B0, B1, B1-H2, B2, B2-flip và B2-rand validation được worklog ghi là Dũng thực hiện; người dùng đã xác nhận Dũng là mình và xác nhận các Kaggle account liên quan thuộc mình. Vì vậy mình không hỏi Hiếu về các nhóm đó.

Các nhóm được giao Hiếu dưới đây còn thiếu bằng chứng exact về byte notebook/worker tạo records. Nhờ Hiếu gửi kernel slug + version, notebook đã chạy hoặc source readback, và runner_sha256/cell-source hash nếu còn. Nếu không còn source hash, vui lòng ghi rõ session nào do Hiếu trực tiếp chạy và có thể khôi phục từ đâu.

| Run cần xác nhận | Nhóm records | Bằng chứng hiện có nhưng chưa đủ |
|---|---|---|
| B1-full validation | Devign + ReVeal, seed 42 (2 nhóm) | Có native/session logs; thiếu worker SHA khớp records. |
| B1-shuf validation | Devign + ReVeal, seeds 42–44 (6 nhóm) | Seed42/43 chưa thấy session tương ứng; seed44 Devign có 2,113/2,732 records ngoài cửa sổ session, ReVeal nằm trong cửa sổ nhưng chưa có worker SHA. Xin mapping từng seed/dataset và source hash. |
| B2-labelonly | Devign + ReVeal, validation + test, seed 42 (4 nhóm) | Có session logs và executed validation notebook; thiếu runner SHA. |
| B2-nolabel | Devign + ReVeal, validation + test, seed 42 (4 nhóm) | Có session logs và executed validation notebook; thiếu runner SHA. |
| B2-rep | Devign + ReVeal, validation + test, seed 42 (4 nhóm) | Test evidence ghi Kaggle account huuhieu3333; không có worker SHA. Xin xác nhận session có phải do Hiếu chạy và gửi readback/hash nếu còn. |

Tổng cộng 20 nhóm được hỏi. Các nhóm code-binding còn thiếu khác thuộc những run của Dũng/the user theo worklog và xác nhận trực tiếp; sẽ truy nguồn riêng, không gán cho Hiếu.

Để tránh nhầm, mỗi câu trả lời nên ghi theo dataset / split / arm / seed, kèm records file hoặc thời gian chạy. Nếu code nằm trong notebook, một bản export đã chạy cùng cell-source readback/hash sẽ giúp nối notebook với output. Nếu có nhiều kernel ghép output, xin ghi rõ nhóm records nào lấy từ session nào.

Cảm ơn Hiếu.
