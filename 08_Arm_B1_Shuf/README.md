# B1-shuf x 3 seed: preparation only

Mở `notebooks/01_prepare_b1_shuf_prompts.ipynb` bằng kernel local/WSL đang dùng cho GRACE-summary, chạy các cell theo thứ tự. Mặc định chỉ xuất **Devign/ReVeal validation, seed 42/43/44**. Không cần GPU. Notebook chưa được chạy và không có cell inference, Joern, CodeT5, commit/tag hoặc OSF.

## Cách chạy

1. Mở notebook trong repo. Nếu kernel đứng ngoài repo, đặt `PROJECT_ROOT_OVERRIDE` thành thư mục `GRACE-summary` (đường Windows hoặc WSL tương ứng).
2. Dùng môi trường có `numpy`, `pytest`, `transformers==4.57.1`, `sentencepiece`. Cell test dùng dữ liệu tổng hợp; không tải tokenizer/model. Không có cell tự cài dependencies.
3. Giữ `LOCAL_FILES_ONLY=True` nếu tokenizer đã có cache. Nếu chưa có, đổi thành False để tải **tokenizer** ở revision cố định `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
4. Kiểm tra `B1_ROOT`, `B2_ROOT`, `FROZEN_ROOT`, `RUNS`, `OUT_ROOT` rồi chạy cell `prepare(...)`. Kho donor lớn được quét/hash một lần mỗi dataset; có log tiến độ. Graph không được giữ toàn bộ trong RAM.
5. Kiểm tra báo cáo và để hai người đọc mẫu thủ công. Chưa chuyển sang inference chỉ vì đã có ZIP.

CLI tương đương, chạy từ folder arm (PowerShell; WSL dùng đường dẫn tương ứng):

```powershell
python prepare_shuf.py --split validation --local-files-only --out output/bundles_validation_v1
```

Muốn dựng cả test offline: chọn `--split all` hoặc thêm hai run test trong notebook, **dùng OUT_ROOT mới**. Dựng prompt test không gọi LLM và không chọn cấu hình theo kết quả test. Không có chế độ `--limit` để tránh gắn nhầm pilot thành full split.

## Quy tắc đã triển khai

- Tham chiếu là B1 `b1_b2_empty_demo_v1`: code, câu hỏi, scaffold demo trống và answer giữ nguyên từng ký tự; **chỉ thay khối graph**. Không có mã/nhãn demonstration. Nhãn target chỉ nằm ngoài renderer.
- B1 phải khớp hash và tái dựng đúng từ cache B2/specs cùng nguồn. Tập ID, nhãn và code phải khớp manifest split đóng băng. Sai khác làm dừng, không tái sinh tham chiếu.
- Donor lấy từ `01_Author_Baseline_Unified/output/research_freeze_20261101/<dataset>/donors.jsonl`, kiểm hash/count/UID train, giữ thứ tự file. Donor không có nodes không đủ điều kiện; graph chỉ có node và không có cạnh vẫn được phép.
- Ghép theo **số nút CPG đầy đủ trước khi cắt**. Quy tắc giống `DonorPool.shuffle_graph`: SHA-256 của ID qua `stable_seed`, cộng seed rồi XOR `0x5F3759DF`, dùng `numpy.default_rng`. Khoảng nới lần lượt 10%, 20%, 40%, 80%, 160%, 320%; biên nguyên làm tròn ra ngoài bằng floor/ceil, tối thiểu 1. Nếu vẫn không có donor thì dừng. Ghi số ứng viên, biên và mức nới từng target.
- Cùng ID/seed/input -> cùng donor/prompt; không ép ba seed khác donor. Seed inference riêng là 42, không biến seed lấy graph thành seed inference.
- Dùng formatter/cách cắt **prefix của B1**: lấy tối đa 40 nút và 80 cạnh đóng, bỏ cạnh cuối trước rồi bỏ nút cuối nếu vượt 1.500 token. Không cắt ngang văn bản graph. Kiểm tổng <=8.192 gồm chat wrapper và 64 token dự phòng.
- **Target thiếu CPG:** giữ nguyên prompt B1 cho cả ba seed, không lấy donor; ghi `target_graph_missing`, donor null. Báo riêng trong phân tích coverage; không coi mẫu này là can thiệp graph thành công. Đây là chính sách cần khóa trong đăng ký trước.

## Đầu ra

```text
output/<run>/
  seed_42/<dataset>/<split>/  # tương tự seed_43, seed_44
    prompts.jsonl
    pairing_audit.jsonl
    audit_summary.json
    bundle_manifest.json
    <dataset>_<split>_b1_shuf_seed_42_prompts.zip
  audit/<dataset>/<split>/
    audit_summary.json       # tách theo seed
    manual_sample.jsonl     # đúng 30 dòng hoặc toàn bộ nếu <30
  grace_b1_shuf_prompts.zip
```

Mẫu thủ công phân tầng theo seed, độ dài và cờ cắt graph; có ô ghi tên/nhận xét hai người đọc. Validation và test có mẫu riêng. Báo cáo lưu số prompt trùng B1 (không bắt buộc graph donor khác prompt khi graph có thể giống nhau), số graph thiếu, số ghép trong 10% và số phải nới. Manifest ghi hash nguồn, thư viện NumPy, tokenizer revision và trạng thái review/registration còn chờ. `inference_ready` luôn false: bộ này chưa có runtime B1-shuf.

Nếu thiếu graph >5%, manifest bật stop-rule; cần xử lý trước khi diễn giải. Nếu có `INCOMPLETE.txt`, lần xuất chưa hoàn tất. Không dùng bundle của lần chạy dở làm kết quả hoàn chỉnh. Script không ghi đè output không rỗng; chọn OUT_ROOT mới khi chạy lại. Đây là lựa chọn bảo toàn artifact, chưa có resume cho bước chuẩn bị.

## Phạm vi và đăng ký trước

40/80, scaffold demo trống và chính sách graph thiếu là các chi tiết cần công bố so với PDF. Đây là phép so **ghép cặp với B1 đã có**, không tự chứng nhận nghiên cứu đã preregister. Không thay backend B1 hoặc ghép score khác quantization để hoàn tất arm. Đọc `PREREG_B1_SHUF_DRAFT.md` trước bước đăng ký; không sửa protocol nghiên cứu chung từ notebook này.

## Kiểm thử

```powershell
python -m pytest test_prepare_shuf.py -q
```

Bộ test kiểm chọn donor tương thích code hiện có, số nút trước khi cắt, nới khoảng, parity với formatter B1, thay riêng graph, giữ mẫu thiếu CPG, sai hash, lấy đủ mẫu thủ công, xuất bundle với dữ liệu tổng hợp và từ chối ghi đè. Test không chứng minh kết quả inference hoặc thay thế hai người đọc prompt thật.
