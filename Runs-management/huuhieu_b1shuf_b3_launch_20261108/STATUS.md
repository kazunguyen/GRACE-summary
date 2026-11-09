# HU — B1-shuf continuation và B3 mới

Hai notebook được push theo yêu cầu chạy trên **cùng account huuhieu3333**, không dùng quota còn lại làm điều kiện chặn phía client. Không có chuyển dữ liệu sang account khác.

| Job | Notebook thực tế trên server | Phạm vi / điểm bắt đầu |
|---|---|---|
| B1-shuf | [grace-b1-shuf-resume6416](https://www.kaggle.com/code/huuhieu3333/grace-b1-shuf-resume6416) | Resume6416/15018, còn8602; seed42 giữ nguyên, tiếp seed43 Devign rồi các phần còn lại |
| B3 mới | [grace-b3-new-devign-and-reveal-validation](https://www.kaggle.com/code/huuhieu3333/grace-b3-new-devign-and-reveal-validation) | B3 validation seed42; Devign2732 → REVEAL2273 theo thứ tự cố định, không test/fit threshold/arm khác |

Launch được API nhận lúc08/11 **23:52:24** và **23:53:19 GMT+7**, version1. Kaggle tạo slug từ title khác slug request ban đầu; receipt ghi cả ref thực và ref yêu cầu, các lượt readback/status dùng đúng ref thực. Không tạo phiên trùng để sửa tên.

## Đã kiểm trước/sau push

- **17 preflight tests PASS**: actual B1 restore ZIP/unpacked đủ6416 và giữ mọi member bytes; B1 worker hash nguyên; actual B3 dual-input selection ZIP/unpacked đúng dataset; checkpoint lưu prefix record hoàn chỉnh không sửa live output; child lỗi hoặc census thiếu không mở dataset sau; source/config/shape/input guards. Shared delivery/scoring/restore regression dùng code đã nghiệm thu. Test mock chỉ kiểm điều phối, không được tính thành GPU evidence.
- Checkpoint B1 mới: SHA `f69ddb1bf1f06a96ad04391d032d6f3be95b7fab35bd926ef851cb2028715b19`, cùng manifest `1f008abc6f0d9928fca6c5684d9b49f508182a733acb12f0d8bbb03d11d3a70c`; private dataset mới `huuhieu3333/grace-b1-shuf-checkpoint-6416-20261108`. Old B1 session được xác nhận đã dừng trước launch.
- SDK request của **mỗi notebook**: PRIVATE, internet enabled, `machine_shape=NvidiaTeslaT4`, timeout32400s. Không chia một cặp T4 giữa hai process model trong cùng notebook; Kaggle cấp mỗi notebook một T4x2 runtime độc lập. B3 chỉ có một child model active tại một thời điểm.
- Source readback của cả hai notebook **khớp toàn bộ cells**, server xác nhận private/GPU enabled/đúng T4 shape và đúng dataset/model kernel sources. B3 dùng cả hai input releases Devign v6, REVEAL v7, giữ nguyên pins/worker/helper/contract của chúng.
- B1 giữ launch contract6-package85d877… và worker5d700… của checkpoint, không đổi run identity để resume. Thêm pin SciPy1.16.3, khớp `pip_freeze` của **cả hai** session cha; không chứng nhận hồi tố SciPy bằng contract7-package cho record cũ. B3 giữ contract7-package4c9c3bcf….

## Native runtime gates bắt buộc trước score

Mỗi child yêu cầu model SHA/tokenizer revision, backend sdist SHA và installed versions đúng; constructor8192 context/batch256/ubatch256, layer split, tensor_split=None, GPU layers=-1, inference seed sentinel4294967295; không sampling. Native log phải xác nhận2 T4 và49/49 offload, effective context/batch. HF/GGUF token IDs phải khớp; reset KV và lấy logits trực tiếp. Mismatch gây abort, không fallback CPU/model/backend khác.

Layer allocation theo free VRAM lúc load, không hứa cố định25/24 layer. Những con số thực cần native log và provenance; không suy từ machine shape hoặc RUNNING.

## Checkpoint / dừng

- Cả hai có deadline9h tính từ đầu notebook, giữ300s dự phòng; không dừng theo metric.
- B1 giữ export checkpoint khoảng60s của worker đã khóa, bỏ qua đúng records cũ đã xác minh.
- B3 snapshot khoảng60s cho dataset active. Copy chỉ giữ prefix JSONL hoàn chỉnh; kiểm identity/provenance/score, ghi ZIP tạm rồi atomic replace. Không sửa file live hoặc score cũ. Nếu snapshot đang đụng file ghi, giữ checkpoint tốt trước đó và retry. Child lỗi hoặc chưa đủ census thì dừng chuỗi, REVEAL không tự chạy thay cho phần Devign thiếu.

## Quan sát thực tế hiện có

API status hiện báo **RUNNING cho cả hai**, failure_message rỗng. Endpoint output/live-log đang trả0 files và0 ký tự log cho phiên đang chạy. Vì vậy **chưa chốt native runtime PASS, chưa công bố số record mới**. Native guards vẫn tự cưỡng chế trước inference; cần thu provenance/output khi endpoint cung cấp để nghiệm thu bằng chứng thực.

Hồ sơ: `cpu_preflight.json`, `cpu_preflight.log`; mỗi job có `delivery.json`, `launch.json`, `source_readback.json`, `status.json`, `live_observation.json`. Run API state và worker progress là hai khái niệm khác nhau. User đã bỏ quota veto phía client; các giới hạn/rejection thực của Kaggle vẫn do server quyết định.
