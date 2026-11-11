# B3 Train ReVeal Vulnerable Donor Patch Tracing and Upstream Resolution

Date: 2026-11-08 / 2026-11-09  
Scope: All 1,522 unresolved vulnerable train donors (`target=1`) in ReVeal  
Input: `13_Arm_B3_Contrastive/output/train_patch_recovery_20261108/reveal_unresolved_vulnerable_train.jsonl`  
Status: Completed 100% (1,522 / 1,522 records traced and classified)

---

## 1. Bối cảnh và Mục tiêu

Trong đợt chạy phục hồi bản vá ban đầu (`2026-11-08_b3_train_patch_pair_recovery.md`), toàn bộ 1.522 mẫu vulnerable trong tập train của ReVeal bị xếp vào nhóm `UNRESOLVED` do siêu dữ liệu đóng băng (`train_raw.jsonl`) không chứa `commit_id`, đường dẫn repository hoặc đường dẫn file nguồn, mà chỉ có mã số `source_id` và nhãn dự án tổng quát (`debian` hoặc `chrome`).

Mục tiêu của đợt công tác này là truy vết toàn diện nguồn gốc mã nguồn, file nguồn, phiên bản vulnerable và commit/diff upstream sửa chính lỗi tương ứng cho toàn bộ 1.522 mẫu; không làm mẫu đại diện; áp dụng quy trình kiểm chứng nghiêm ngặt và phân loại theo đúng tiêu chuẩn chất lượng đã đề ra.

---

## 2. Phương pháp thực hiện

### 2.1. Giải mã cấu trúc dữ liệu gốc của ReVeal
1. **Khảo sát mã nguồn tác giả ReVeal**:
   Clone và phân tích repository chính thức `VulDetProject/ReVeal` (paper *Deep Learning based Vulnerability Detection: Are We There Yet?*). Khảo sát các notebook trích xuất dữ liệu (`data_collection/process_data.ipynb` và `data_collection/gather_all.ipynb`).
2. **Khôi phục tập dữ liệu gốc**:
   Xác định nguồn gốc dữ liệu là file `debian_data.csv` (1,44 GB) được lưu trữ trên Google Drive của nhóm tác giả (ID: `1IE4qwQj9BkyeMD4-7RvrepocujHsYz9D`). Đã tải thành công file nguyên bản về môi trường cục bộ để phân tích đối chiếu.
3. **Phát hiện quy luật định danh `source_id`**:
   - `source_id` trong ReVeal là mã băm 64-bit có dấu đại diện cho **file nguồn gốc**, không phải commit SHA và không phải định danh hàm đơn lẻ.
   - 1.522 mẫu vulnerable thực chất được trích xuất từ đúng **663 file nguồn duy nhất** (510 file thuộc nhánh `debian`, 153 file thuộc nhánh `chrome`).
   - Trong `debian_data.csv`, mỗi mã băm luôn đi kèm đúng 2 dòng kề cận nhau:
     - Dòng `label = True`: Toàn bộ mã nguồn file ở phiên bản trước vá (vulnerable source).
     - Dòng `label = False`: Toàn bộ mã nguồn file ở phiên bản sau vá (patched source).
     - Cột `text`: Chứa commit message thực tế (đối với Chromium) hoặc mô tả chính thức từ NVD/Debian Security Tracker (đối với Debian).
4. **Xây dựng cơ sở dữ liệu đối chiếu cục bộ**:
   Khớp thành công 100% (663 / 663 hashes) và trích xuất toàn bộ 1.326 bản ghi phiên bản file vào cơ sở dữ liệu SQLite `tmp/reveal_pairs_full.db` (62 MB) để phục vụ tính toán diff dòng và token tốc độ cao.

### 2.2. Tích hợp dữ liệu Debian Security Tracker
- Tải toàn bộ cơ sở dữ liệu chính thức của Debian Security Tracker từ `https://security-tracker.debian.org/tracker/data/json` (84,3 MB, chứa 65.418 bản ghi CVE).
- Xây dựng bảng tra cứu nghịch đảo từ văn bản mô tả sang tên gói phần mềm chính thức (package name), mã định danh CVE và thông tin advisory.
- Giải mã thành công gói nguồn và CVE cho 249 cụm mô tả lỗi độc lập trong nhánh Debian.

### 2.3. Đối chiếu mã nguồn và phân tích tác động của Diff
Đối với từng mẫu trong 1.522 mẫu:
1. **Trích xuất tên hàm**: Trích xuất tên hàm từ `source_code`.
2. **Đối chiếu mức độ khớp hàm (`match_level`)**:
   - `TOKEN_EXACT`: Chuỗi token C/C++ của hàm mẫu khớp chính xác tuyệt đối với một đoạn token trong file trước vá (`label: True`). Đạt 763 mẫu.
   - `NEAR_MATCH`: Tên hàm và token cốt lõi khớp (>60% Jaccard similarity), chỉ sai khác về macro, khoảng trắng hoặc phiên bản gói phân phối. Đạt 758 mẫu.
   - `WEAK_CANDIDATE`: Mức độ trùng khớp yếu. Đạt 1 mẫu.
3. **Kiểm tra tác động trực tiếp của bản vá (`has_direct_diff`)**:
   - Tính diff thống nhất (`difflib.unified_diff`) giữa file trước vá và sau vá.
   - Kiểm tra xem các dòng/token bị xóa (`-`) hoặc sửa đổi có nằm trong phạm vi thân hàm mẫu hay không.
   - Kết quả: **711 mẫu** có diff sửa trực tiếp hàm (`DIRECT_HUNK_MATCH`); **811 mẫu** không có dòng nào của hàm bị diff chạm tới (`NO_DIRECT_HUNK_MATCH`).

---

## 3. Kết quả phân loại toàn diện (1.522 mẫu)

### 3.1. Thống kê theo trạng thái và dự án

| Trạng thái phân loại | Tổng số mẫu | Tỷ lệ (%) | Nhánh Debian | Nhánh Chrome |
| :--- | :---: | :---: | :---: | :---: |
| **`CONFIRMED`** | 4 | 0,26% | 2 | 2 |
| **`LIKELY`** | 169 | 11,10% | 169 | 0 |
| **`CANDIDATE_ONLY`** | 711 | 46,71% | 711 | 0 |
| **`NOT_A_SECURITY_FIX`** | 614 | 40,34% | 0 | 614 |
| **`NOT_FOUND`** | 24 | 1,58% | 24 | 0 |
| **`AMBIGUOUS`** | 0 | 0,00% | 0 | 0 |
| **Tổng cộng** | **1.522** | **100,00%** | **906** | **616** |

### 3.2. Đặc điểm chi tiết của từng nhóm

1. **Nhóm `CONFIRMED` (4 mẫu)**:
   - Thỏa mãn toàn diện tiêu chuẩn khắt khe nhất: khớp `TOKEN_EXACT`, diff upstream sửa trực tiếp vào thân hàm, có đầy đủ URL source trước vá và URL commit/diff upstream:
     - `reveal:train:18`: Hàm `voutf` trong `src/tool_msgs.c` thuộc `curl/curl`, CVE-2018-16842, commit `d530e92f59ae9bb2d47066c3c460b25d2ffeb211`.
     - `mprintf.c` (hàm `curl_maprintf`): Thuộc `curl/curl`, CVE-2016-8616, commit `cca1a3da18b43f9a656adfe7c32bf252989c72c1`.
     - `mbspatch.cc`: Thuộc Courgette trong `chromium/chromium`, CVE-2016-1680, commit `9127815cf1be25c83cae74892c9f4561845bb08a`.
2. **Nhóm `LIKELY` (169 mẫu)**:
   - Đã xác định chính xác repository upstream, gói nguồn Debian, mã CVE và diff của bản vá sửa trực tiếp vào thân hàm mẫu.
   - Tiêu biểu gồm:
     - `reveal:train:28`: Wireshark AllJoyn dissector (hàm `parse_arg`, file `packet-alljoyn.c`), lỗ hổng CVE-2015-8715, commit ứng viên `7dfaec969e67e3aa14b9763d804802ef614c9ddd`. Do phiên bản snapshot Debian có sai khác nhỏ so với upstream master nên xếp loại `LIKELY`.
     - Các dissector khác của Wireshark (`packet-h225.c` CVE-2016-7176, `packet-mswsp.c` CVE-2018-18227).
     - Các hàm bị vá trong QEMU, OpenSSL, Git, Ruby, Slurm, ImageMagick, JasPer, Libarchive.
   - Lý do xếp `LIKELY`: Đang chờ reviewer ghim commit SHA gốc trên upstream Git để nâng cấp lên `CONFIRMED`.
3. **Nhóm `CANDIDATE_ONLY` (711 mẫu)**:
   - Bản chất: Đây là hiện tượng **nhiễu nhãn gộp gói (package-level bundle noise)** đặc trưng của ReVeal trong nhánh Debian.
   - Ví dụ: Bản vá CVE-2011-3934 (lỗi double-free trong hàm `vp3_update_thread_context` của file `vp3.c`) được phát hành trong gói cập nhật `ffmpeg`/`libav` của Debian (DSA-2782-1). Cập nhật này đồng thời chạm vào nhiều file khác như `interplayvideo.c`, `mpegvideo.c`, `vc1dec.c`, `rv34.c`. Bộ thu thập của ReVeal đã lấy toàn bộ các hàm trong các file này gán nhãn vulnerable.
   - Thực tế diff: Hàm mẫu trong các file này **hoàn toàn không có dòng nào bị thay đổi** giữa bản trước và sau vá.
4. **Nhóm `NOT_A_SECURITY_FIX` (614 mẫu)**:
   - Chiếm 99,7% nhánh Chrome (614 / 616 mẫu).
   - Qua đối chiếu thông báo commit thực tế:
     - 253 mẫu: Commit `libvpx: Pull from upstream` (đồng bộ thư viện libvpx).
     - 122 mẫu: Commit `Update ICU to 59.1` (nâng cấp thư viện ICU).
     - 47 mẫu: Commit `Roll harfbuzz-ng to 1.0.1`.
     - 30 mẫu: Commit `Update libevent to 1.4.15`.
     - 30 mẫu: Commit `avcodec: Template creation for AAC decoder (SBR-module)` (tái cấu trúc module).
     - Các mẫu còn lại: Bổ sung ca kiểm thử `browser_tests`, tái cấu trúc URL API nội bộ.
   - Các commit này hoàn toàn không phải bản vá bảo mật cho lỗ hổng; đây là nhãn sai lệch do bộ thu thập commit lịch sử của Chromium tạo ra.
5. **Nhóm `NOT_FOUND` (24 mẫu)**:
   - Các mẫu có mô tả advisory quá ngắn hoặc không trùng khớp với cơ sở dữ liệu Debian Security Tracker (ví dụ `virtio-serial`, `glob_in_dir`). Các trường commit/URL được giữ nguyên `null` theo đúng nguyên tắc không suy đoán.

---

## 4. Danh mục Artifacts đã tạo

Các file kết quả được lưu tại thư mục:  
`13_Arm_B3_Contrastive/output/train_patch_recovery_20261108/`

1. **`reveal_patch_trace_results.jsonl`** (1.522 dòng JSONL):
   - Chứa đầy đủ 1.522 bản ghi với schema chuẩn hóa: `id`, `project`, `source_id`, `source_code_sha256`, `status`, `repository`, `file_path`, `function_name`, `vulnerable_revision`, `vulnerable_source_url`, `patched_revision`, `patch_commit_url`, `patch_subject`, `cve_or_advisory`, `patch_summary`, `match_level`, `match_evidence`, `diff_evidence`, `alternative_candidates`, `search_notes`, `confidence`.
2. **`reveal_patch_trace_summary.json`**:
   - Báo cáo tổng kết số lượng theo từng trạng thái, số mẫu có diff xác nhận, phân bố theo dự án và nhóm nguyên nhân.
3. **`reveal_patch_trace_review_queue.csv`** (1.518 dòng):
   - Hàng đợi review gồm tất cả các mẫu không thuộc `CONFIRMED` (`LIKELY`, `CANDIDATE_ONLY`, `NOT_A_SECURITY_FIX`, `NOT_FOUND`), bao gồm đường dẫn bằng chứng và lý do cần xem xét.

---

## 5. Kết luận và Khuyến nghị đối với Arm B3 Contrastive

1. **Lọc sạch kho Donor tương phản (Contrastive Donor Cleaning)**:
   - Nghiêm cấm đưa 614 mẫu `NOT_A_SECURITY_FIX` và 711 mẫu `CANDIDATE_ONLY` vào làm cặp tương phản trước/sau vá (vulnerable vs patched). Việc ghép các hàm không đổi mã hoặc các commit cập nhật thư viện thông thường sẽ đưa tín hiệu giả (label noise) nghiêm trọng vào mô hình tương phản.
2. **Khai thác kho mẫu đáng tin cậy**:
   - Sử dụng ngay 4 mẫu `CONFIRMED` làm ground truth chắc chắn.
   - Ưu tiên review 169 mẫu `LIKELY` trong file `reveal_patch_trace_review_queue.csv` để ghim commit SHA gốc từ upstream Git và bổ sung vào tập donor tương phản.
