# BÁO CÁO ĐỐI SOÁT ĐỘC LẬP STEP 6 VÀ BẢNG D
**Người thực hiện đối soát:** Nguyễn Quang Dũng<br>
**Đối tượng kiểm tra:** Branch `docs/phase1-consolidation-20261125` (commit `91a8191`), repository `GRACE-summary`<br>
**Thời điểm đối soát:** 25/11/2026<br>
**Nguyên tắc bảo toàn:** Không chỉnh sửa bất kỳ tệp tin nào, không checkout đè lên working tree hiện có, không commit, không merge, không cập nhật bản nháp paper. Toàn bộ quá trình kiểm tra và tái chạy được thực hiện trong môi trường cách ly (worktree tạm thời và virtualenv độc lập).

---

## 1. Provenance B2

### 1.1. Băm SHA-256 các tệp records của 4 split
Đã đối soát hàm băm SHA-256 của tệp `records.jsonl` tại thư mục B2 chuẩn (`STEP6_supervised_anchors/inputs/b2_canonical_frozen_donor_20261102`) với `assembly_report.json`, `rerun_summary.json` và nguồn nhập liệu ghi nhận trong `runs/final/*/B2/42/import_manifest.json`:

- **Devign validation:**
  - Đường dẫn: `STEP6_supervised_anchors/inputs/b2_canonical_frozen_donor_20261102/devign/validation/records.jsonl`
  - SHA-256 trên đĩa: `fd40fb2c228a0fe343bdd7b4c238635043276341c801793fbd425af766f7eb32`
  - `assembly_report.json`: `fd40fb2c228a0fe343bdd7b4c238635043276341c801793fbd425af766f7eb32`
  - `rerun_summary.json`: `fd40fb2c228a0fe343bdd7b4c238635043276341c801793fbd425af766f7eb32`
  - `runs/final/devign/validation/B2/42/import_manifest.json` (`sources_sha256`): `fd40fb2c228a0fe343bdd7b4c238635043276341c801793fbd425af766f7eb32`
  - **Kết luận:** Khớp hoàn toàn.

- **Devign test:**
  - Đường dẫn: `STEP6_supervised_anchors/inputs/b2_canonical_frozen_donor_20261102/devign/test/records.jsonl`
  - SHA-256 trên đĩa: `d0a61bfa6cc1700ddd5a6d668d4c42d808cce5fbc71b42b300fdd29060c71304`
  - `assembly_report.json`: `d0a61bfa6cc1700ddd5a6d668d4c42d808cce5fbc71b42b300fdd29060c71304`
  - `rerun_summary.json`: `d0a61bfa6cc1700ddd5a6d668d4c42d808cce5fbc71b42b300fdd29060c71304`
  - `runs/final/devign/test/B2/42/import_manifest.json` (`sources_sha256`): `d0a61bfa6cc1700ddd5a6d668d4c42d808cce5fbc71b42b300fdd29060c71304`
  - **Kết luận:** Khớp hoàn toàn.

- **ReVeal validation:**
  - Đường dẫn: `STEP6_supervised_anchors/inputs/b2_canonical_frozen_donor_20261102/reveal/validation/records.jsonl`
  - SHA-256 trên đĩa: `221a794e55d8f900ce3986e27cdf227a23a947aa4dd864b6ed597fe5363fa994`
  - `assembly_report.json`: `221a794e55d8f900ce3986e27cdf227a23a947aa4dd864b6ed597fe5363fa994`
  - `rerun_summary.json`: `221a794e55d8f900ce3986e27cdf227a23a947aa4dd864b6ed597fe5363fa994`
  - **Kết luận:** Khớp hoàn toàn.

- **ReVeal test:**
  - Đường dẫn: `STEP6_supervised_anchors/inputs/b2_canonical_frozen_donor_20261102/reveal/test/records.jsonl`
  - SHA-256 trên đĩa: `dcdaf0d0b52451b295e73cda7ba2e95653051035fcf3a9cd48e4b8d2ba39a415`
  - `assembly_report.json`: `dcdaf0d0b52451b295e73cda7ba2e95653051035fcf3a9cd48e4b8d2ba39a415`
  - `rerun_summary.json`: `dcdaf0d0b52451b295e73cda7ba2e95653051035fcf3a9cd48e4b8d2ba39a415`
  - **Kết luận:** Khớp hoàn toàn.

### 1.2. Devign validation: Đối soát 28 ID thay đổi
- Tổng số dòng: 2.732 dòng.
- So sánh giữa run3 gốc (`01_Author_Baseline_Unified/kaggle_qwen_q4_b2/downloaded_output_20261101_run3/grace_b2_four_split_8h/devign/validation/records.jsonl`) và tệp B2 chuẩn: Có chính xác **28 ID** thay đổi.
- Đối chiếu với danh sách rà soát donor-28 (`docs/hieu_review_28_devign_validation.csv`) và tệp tái chạy rerun-66 (`Runs-management/kaggle_outputs_20261105/b2_rand/grace_b2_rand_three_seed_11h/b2_donor_rerun_66/devign/validation/records.jsonl`): Tập 28 ID thay đổi trùng khớp 100% với tập 28 `target_id` trong danh sách kiểm tra của Hiếu và 28 bản ghi của rerun-66.
- 2.704 dòng còn lại giữ nguyên từng byte so với run3.

### 1.3. Devign test: Đối soát 38 ID thay đổi
- Tổng số dòng: 2.732 dòng.
- So sánh giữa run3 gốc và tệp B2 chuẩn: Có chính xác **38 ID** thay đổi.
- Đối chiếu với tệp rerun-66 test (`Runs-management/kaggle_outputs_20261105/b2_rand/grace_b2_rand_three_seed_11h/b2_donor_rerun_66/devign/test/records.jsonl`): Tập 38 ID thay đổi trùng khớp 100% với 38 bản ghi trong rerun-66.
- 2.694 dòng còn lại giữ nguyên từng byte so with run3.

### 1.4. Kiểm tra chi tiết các trường của các ID thay đổi
Đã duyệt qua toàn bộ 28 bản ghi thay đổi của Devign validation và 38 bản ghi thay đổi của Devign test:
- **Nhãn (`label`):** 0 trường hợp thay đổi nhãn (100% khớp ground-truth $y$).
- **Mã băm prompt (`prompt_sha256`):** Thay đổi ở toàn bộ 28/28 bản ghi validation và 38/38 bản ghi test do thay đổi ngữ cảnh donor prompt.
- **Điểm số (`s`):** Thay đổi ở toàn bộ 28/28 bản ghi validation và 38/38 bản ghi test. Điểm số và trạng thái `valid` trong B2 chuẩn khớp hoàn toàn (28/28 và 38/38) với kết quả suy luận từ rerun-66.
- Không có bất kỳ thay đổi ngoài dự kiến nào trên các trường metadata khác (`arm="B2"`, `seed=42`, `dataset="devign"`).

### 1.5. Xác nhận ReVeal không đổi
- **ReVeal validation:** Tổng số 2.273 dòng; số dòng khác biệt so với run3 là **0**.
- **ReVeal test:** Tổng số 2.274 dòng; số dòng khác biệt so với run3 là **0**.
- Độ phủ ID và số dòng giữ nguyên vẹn 100%.

**Đánh giá Mục 1:** **PASS**

---

## 2. Rerun Control và Kết quả Step 6

### 2.1. Tái tạo lock gốc từ Control Run và giải thích sai lệch mã băm do CRLF/LF
- Thư mục đối chứng: `STEP6_supervised_anchors/runs/complementarity_step6/step6_lock_64fb2c99d904_rerun_control_b2_20261125/`
- Thư mục lock gốc: `STEP6_supervised_anchors/runs/complementarity_step6/step6_lock_64fb2c99d904_44f00d19/`
- **Đối chiếu kết quả JSON:**
  - Devign: Khớp 985/985 trường lá (differing leaves = 0). Tệp `complementarity_step6.json` của control run có SHA-256 byte thô là `3bcabe54ed92df7dea583e17da5c5483bdc77b28ff49450e41a8d9cfb16661a1`, trùng khớp tuyệt đối 100% từng byte với tệp lock gốc.
  - ReVeal: Khớp 985/985 trường lá (differing leaves = 0). Tệp `complementarity_step6.json` của control run có SHA-256 byte thô là `55612876d34951e68c39016b9c8a0d0a5a85334c4785c8dc8e88ed85fef44ac0`, trùng khớp tuyệt đối 100% từng byte với tệp lock gốc.
- **Giải thích sai lệch mã băm do CRLF/LF:**
  - Trên hệ điều hành Windows, thiết lập mặc định của Git chuyển đổi các ký tự kết thúc dòng LF thành CRLF khi checkout đối với các tệp văn bản CSV (`joined_validation.csv`, `joined_test.csv`).
  - Cụ thể: `devign/joined_validation.csv` trên Windows có 2.733 ký tự CRLF, mã băm thô là `1c157107f3ea...`. Khi chuẩn hóa bỏ `\r` (về LF nguyên bản), mã băm trở về `9ad933305e63...`.
  - Trong `analysis_manifest.json`, tác giả gốc khóa mã băm theo bản checkout Windows mang CRLF (`1c157107f3ea...` và `fbc408df39b0...`).
  - Script `STEP6_supervised_anchors/src/rerun_step6_canonical_b2.py` đã chủ động xử lý bằng cách kiểm tra cả băm thô và băm sau khi chuẩn hóa `b"\r\n" -> b"\n"`. Đây thuần túy là hiện tượng định dạng xuống dòng giữa Windows và Linux, nội dung dữ liệu bên trong không bị biến đổi.

### 2.2. Kiểm tra tính toàn vẹn của Canonical Rerun
Đã thẩm tra quá trình thực thi của Canonical Rerun (`step6_lock_64fb2c99d904_rerun_canonical_b2_20261125`):
- **Nguồn B2:** Dùng đúng thư mục `STEP6_supervised_anchors/inputs/b2_canonical_frozen_donor_20261102`.
- **Joined CSV:** Đọc trực tiếp từ joined CSV của lock gốc `44f00d19`, bảo toàn các cột $y$, $p_{\text{gate}}$, $\text{group}$, $s_{\text{sup\_lr}}$ và `code_sha256`. Chỉ thay thế giá trị $s_{\text{llm}}$ và $\text{valid}$ cho các dòng tương ứng của B2 chuẩn.
- **Đặc trưng $X_{\text{pre}}$:** Tải từ `STEP6_supervised_anchors/runs/h3b_locked/step6_lock_64fb2c99d904/`. Cả 4 tệp `xpre_validation.npz` và `xpre_test.npz` trên đĩa đều khớp chính xác mã băm SHA-256 trong manifest:
  - `devign/validation`: `44898c6090a9705d3e84d9ec9aefa0b0ce335766335886199976695ae6c37fa1`
  - `devign/test`: `7122bbb11dc4819418447ea7bb280628533c1ca828ce6761c3d19a34b024b5b7`
  - `reveal/validation`: `fd88b1426aa6d2cd2cfcfbc6eb195f1b489194bf34bdbb2a486676601b0b60a8`
  - `reveal/test`: `f5113d4e81d3b02cd9017a24214f19ab15af71df0bbd1a8802d9e47ec9c290f1`
- **Ngưỡng và cụm:** Dùng đúng ngưỡng đã khóa (`devign`: $\tau_{\text{gate}}=0{,}4$, $\tau_{\text{sup}}=0{,}37$; `reveal`: $\tau_{\text{gate}}=0{,}17$, $\tau_{\text{sup}}=0{,}15$) và giữ nguyên định danh cụm lấy mẫu.
- **Script phân tích:** `step6_complementarity.py` không bị can thiệp (SHA-256: `882a5c8bc364ee90d73255afc6e4e62decd834d3d6d43f38cc42894864975fdc`).

### 2.3. Số trường khác biệt và đối chiếu các trường chính trong JSON
- **Devign:** Khác biệt **293 / 985** trường lá so với lock gốc.
- **ReVeal:** Khác biệt **0 / 985** trường lá so với lock gốc.
- **Đối chiếu các trường trọng yếu trong JSON (`complementarity_step6.json`):**
  - Số ca LLM sửa đúng lỗi H3-B (`llm_correct_repairs`): Lock cũ = 397; Canonical mới = **400**.
  - Tổng số ca sửa / gây hại so với H3-B: Lock cũ = 397 / 718; Canonical mới = **400 / 716**.
  - Tham chiếu chuyên gia ngẫu nhiên H3-B:
    - Trung bình: Lock cũ = 433,85; Canonical mới = **433,05**.
    - Phân vị 97,5%: Lock cũ = 465,05; Canonical mới = **464,0**.
  - Trần Oracle (`test_oracle_ceiling.oracle_accuracy`): Lock cũ = 77,1596% (77,16%); Canonical mới = **77,2694% (77,27%)**.
  - Định tuyến lợi ích so với ngẫu nhiên tại ngân sách 10% ($\Delta\text{BA}$): Lock cũ = +0,0204 [0,0138; 0,0270]; Canonical mới = **+0,0195 [0,0129; 0,0262]**.

**Đánh giá Mục 2:** **PASS**

---

## 3. Bảng D (Table D) và Tiêu chí H5.2

### 3.1. Phương pháp tính toán độc lập
- Dùng ngưỡng $\tau_{\text{shared}}$ chọn từ dự đoán OOF của $P_{\text{pre}}$ trên tập xác thực áp dụng đồng thời cho $P_{\text{pre}}$ và $P_{\text{post}}$ trên tập kiểm thử.
- Thuật toán tái lặp: Paired cluster bootstrap với $B = 5.000$ lượt, seed `20261117`.
- Cụm tái mẫu: Commit đối với Devign (2.068 cụm kiểm thử) và hash mã nguồn đối với ReVeal (646 cụm kiểm thử).
- Môi trường tái chạy: Ubuntu 24.04 (WSL2), Python 3.12.3, `numpy 1.26.4`, `scipy 1.17.1`, `scikit-learn 1.5.2`.

### 3.2. Số liệu tái chạy đối chiếu chính xác
Kết quả tái chạy trực tiếp từ mã nguồn và dữ liệu kiểm thử khớp chính xác tuyệt đối đến 10 chữ số thập phân:

- **Bộ dữ liệu Devign:**
  - $\tau_{\text{shared}} = 0{,}53$
  - $\text{MCC}_{\text{pre}} = 0{,}2865809754$
  - $\text{MCC}_{\text{post}} = 0{,}2849657285$
  - $\Delta\text{MCC} = -0{,}0016152469$
  - KTC 95%: $[-0{,}0107054784;\; 0{,}0074804350]$
  - Cận trên KTC 95%: $0{,}0074804350 < 0{,}02$ (margin H5.2)

- **Bộ dữ liệu ReVeal:**
  - $\tau_{\text{shared}} = 0{,}20$
  - $\text{MCC}_{\text{pre}} = 0{,}3768604303$
  - $\text{MCC}_{\text{post}} = 0{,}3690352464$
  - $\Delta\text{MCC} = -0{,}0078251839$
  - KTC 95%: $[-0{,}0168575401;\; -0{,}0009828440]$
  - Cận trên KTC 95%: $-0{,}0009828440 < 0{,}02$ (margin H5.2)

### 3.3. Kiểm tra tiêu chí H5.2
- **Tiêu chuẩn kiểm định H5.2:** Cận trên khoảng tin cậy 95% của $\Delta\text{MCC}$ ($P_{\text{post}} - P_{\text{pre}}$) phải nhỏ hơn biên tương đương thực chất $0{,}02$ để bác bỏ giả thuyết bổ sung thông tin vượt trội của B2.
- **Devign:** Cận trên $0{,}0074804350 < 0{,}02$ $\rightarrow$ **ĐẠT (PASS)**.
- **ReVeal:** Cận trên $-0{,}0009828440 < 0{,}02$ $\rightarrow$ **ĐẠT (PASS)**.

**Đánh giá Mục 3:** **PASS**

---

## 4. H5.3: Đối soát Số ca Sửa chữa của LLM và Phân vị Chuyên gia Ngẫu nhiên

### 4.1. Tự tính toán số ca sửa chữa và 20 lượt rút ngẫu nhiên (seed 42)
Đã tái hiện thuật toán rút 20 chuyên gia ngẫu nhiên có cùng tỷ lệ dự đoán dương với LLM (`rate`):

- **Devign (H3B_GATE):**
  - Số ca LLM sửa đúng lỗi của H3-B: **400** ca.
  - 20 giá trị sửa chữa từ chuyên gia ngẫu nhiên:<br>
    `[439, 428, 440, 430, 406, 422, 460, 426, 430, 464, 423, 419, 424, 422, 416, 464, 431, 446, 427, 444]`
  - Dãy 20 giá trị sau sắp xếp tăng dần:<br>
    `[406, 416, 419, 422, 422, 423, 424, 426, 427, 428, 430, 430, 431, 439, 440, 444, 446, 460, 464, 464]`
  - Vị trí chỉ số: Phần tử thứ 19 (index 18) = 464; Phần tử thứ 20 (index 19) = 464.
  - **Phương pháp nội suy phân vị:** Do hai giá trị cao nhất bằng nhau ($464 = 464$), mọi phương pháp nội suy phân vị trong NumPy (`linear`, `lower`, `higher`, `midpoint`, `nearest`) đều cho kết quả:
    - **P95 = 464,0**
    - **P97.5 = 464,0**
  - **Kiểm định:** $400 \le 464{,}0$. Tiêu chí H5.3 đạt ở cả phân vị 95 (văn bản đăng ký) và phân vị 97,5 (mã nguồn khóa).

- **ReVeal (H3B_GATE):**
  - Số ca LLM sửa đúng lỗi của H3-B: **164** ca.
  - 20 giá trị sửa chữa từ chuyên gia ngẫu nhiên:<br>
    `[148, 159, 179, 160, 156, 167, 173, 160, 161, 158, 154, 161, 161, 172, 161, 156, 154, 168, 155, 164]`
  - Dãy 20 giá trị sau sắp xếp tăng dần:<br>
    `[148, 154, 154, 155, 156, 156, 158, 159, 160, 160, 161, 161, 161, 161, 164, 167, 168, 172, 173, 179]`
  - Vị trí chỉ số: Phần tử thứ 19 (index 18) = 173; Phần tử thứ 20 (index 19) = 179.
  - **Phương pháp nội suy phân vị (mặc định NumPy `linear`):**
    - Với $q = 0{,}95$: vị trí $19 \times 0{,}95 = 18{,}05 \rightarrow 173 + 0{,}05 \times (179 - 173) = \mathbf{173{,}3}$.
    - Với $q = 0{,}975$: vị trí $19 \times 0{,}975 = 18{,}525 \rightarrow 173 + 0{,}525 \times (179 - 173) = \mathbf{176{,}15}$.
    - (Dưới các phương pháp khác: `lower` = 173; `higher` = 179; `midpoint` = 176,0; `nearest` = 173).
  - **Kiểm định:** $164 \le 173{,}3$ và $164 \le 176{,}15$. Tiêu chí H5.3 đạt ở cả phân vị 95 và 97,5 dưới mọi phương pháp nội suy.

### 4.2. Kết luận tiêu chí H5.3 độc lập
Tiêu chí H5.3 kiểm tra năng lực bổ trợ sửa lỗi của LLM so với chuyên gia ngẫu nhiên (chỉ ra rằng LLM không sửa được nhiều lỗi hơn một cách có ý nghĩa thống kê so với phân vị kỳ vọng của chuyên gia ngẫu nhiên). Tiêu chí này **ĐẠT (PASS)** độc lập trên cả hai bộ dữ liệu ở cả hai mốc phân vị P95 và P97.5.

**Đánh giá Mục 4:** **PASS**

---

## 5. Đồng bộ Paper và Tình trạng Tồn đọng

### 5.1. So sánh với `[Official]-Paper/evidence/h52_shared_threshold.json`
- Tệp `[Official]-Paper/evidence/h52_shared_threshold.json` hiện **chưa được cập nhật** theo kết quả B2 chuẩn:
  - Trường `inputs_sha256` vẫn đang trỏ tới các tệp của lock cũ `step6_lock_64fb2c99d904_44f00d19` (ví dụ `devign/complementarity_step6.json` băm `3bcabe54...`).
  - Số liệu Devign trong tệp evidence này vẫn là số cũ: $\text{mcc}_{\text{post}} = 0{,}2858130263$, $\Delta\text{MCC} = -0{,}0007679491$ $[-0{,}0095187513;\; 0{,}0079549956]$.

### 5.2. Các vị trí mang số liệu cũ trong bản nháp Paper
Kiểm tra trực tiếp hai bản nháp `[Official]-Paper/paper_draft_v1.md` và `[Official]-Paper/paper_draft_v1_vi.md`:
1. **Bảng D (Table D, dòng 174):**
   - Đang ghi: `Devign | 0.53 | 0.2866 | 0.2858 | −0.0008 [−0.0095, 0.0080]`
   - Số chuẩn cần cập nhật: `Devign | 0.53 | 0.2866 | 0.2850 | −0.0016 [−0.0107, 0.0075]`
2. **Đoạn văn phân tích §4.5 (dòng 179):**
   - Đang ghi: B2 sửa 397 lỗi và gây thêm 718 lỗi trên Devign; phân vị 97,5% là 465,05; độ chính xác Oracle là 77,16%.
   - Số chuẩn cần cập nhật: B2 sửa **400** lỗi và gây thêm **716** lỗi trên Devign; phân vị 97,5% là **464,0**; độ chính xác Oracle là **77,27%**.
3. **Đoạn văn định tuyến §4.5 (dòng 181):**
   - Đang ghi: Tại ngân sách 10%, định tuyến theo lợi ích thay đổi balanced accuracy $+0{,}0204$ $[0{,}0138;\; 0{,}0270]$.
   - Số chuẩn cần cập nhật: $+0{,}0195$ $[0{,}0129;\; 0{,}0262]$.

### 5.3. Xác nhận tình trạng không sửa đổi
Như worklog ngày 25/11/2026 đã nêu rõ: nhóm tác giả cố ý chưa cập nhật bản nháp bài báo và tệp evidence vì bản nháp đang đợi thầy phê duyệt phương án chốt. Tôi hoàn toàn tuân thủ nguyên tắc không tự ý sửa đổi các tệp này trong phiên đối soát.

**Đánh giá Mục 5:** **PASS** (Xác minh đúng thực trạng tồn đọng, đúng các vị trí cần cập nhật sau khi thầy duyệt).

---

## 6. Tổng kết Đánh giá PASS/FAIL

| STT | Hạng mục kiểm tra | Trạng thái | Ghi chú bằng chứng chính |
|:---|:---|:---:|:---|
| **1** | **Provenance B2** | **PASS** | Băm SHA-256 4 split khớp tuyệt đối manifest và rerun summary. Devign validation đổi đúng 28 ID khớp donor-28 review list; Devign test đổi đúng 38 ID khớp rerun-66; nhãn không đổi, ReVeal giữ nguyên 100%. |
| **2** | **Rerun Control và Step 6** | **PASS** | Control rerun tái tạo 985/985 trường của lock `44f00d19` ở cả hai dataset. Sai lệch hash thô giải thích thỏa đáng do chuẩn xuống dòng CRLF/LF trên Windows. Canonical rerun dùng đúng B2 chuẩn, đúng joined CSV, đúng $X_{\text{pre}}$, đúng nhóm và ngưỡng. |
| **3** | **Bảng D & Tiêu chí H5.2** | **PASS** | Tái chạy bootstrap 5.000 lượt (seed 20261117). Devign: $\tau=0{,}53$, $\Delta\text{MCC}=-0{,}0016152469$ $[-0{,}0107054784;\; 0{,}0074804350]$; ReVeal: $\tau=0{,}2$, $\Delta\text{MCC}=-0{,}0078251839$ $[-0{,}0168575401;\; -0{,}0009828440]$. Cận trên đều nhỏ hơn 0,02. |
| **4** | **Tiêu chí H5.3** | **PASS** | LLM repairs: Devign = 400 $\le$ P95 (464,0) / P97.5 (464,0); ReVeal = 164 $\le$ P95 (173,3) / P97.5 (176,15). Mọi phương pháp nội suy phân vị đều cho cùng kết luận. |
| **5** | **Đồng bộ Paper** | **PASS** | Đã xác minh chính xác các số liệu còn mang giá trị cũ từ run3 tại Bảng D, §4.5 và `h52_shared_threshold.json`. Tôn trọng chỉ đạo giữ nguyên chờ thầy duyệt. |

---

## 7. Đánh giá Mức độ Sai lệch và Ảnh hưởng Kết luận Khoa học

- **Mức độ sai lệch số học:** Việc cập nhật B2 chuẩn sau đợt chạy lại donor-66 chỉ tác động đến tập dữ liệu Devign ở chữ số thập phân thứ 3 (ví dụ $\Delta\text{MCC}$ dịch chuyển từ $-0{,}0008$ thành $-0{,}0016$, độ chính xác Oracle dịch chuyển từ $77{,}16\%$ thành $77{,}27\%$). Tập dữ liệu ReVeal không có bất kỳ thay đổi nào.
- **Ảnh hưởng đến các kết luận nghiên cứu:**
  - Tiêu chí **H5.2** (Complementarity qua Shared Threshold): Cận trên khoảng tin cậy của Devign ($0{,}0075$) và ReVeal ($-0{,}0010$) đều nằm sâu dưới ngưỡng biên $0{,}02$. Kết luận B2 không tạo ra giá trị gia tăng sau truy vấn được giữ nguyên vẹn.
  - Tiêu chí **H5.3** (Sửa lỗi so với Random Expert): Số ca sửa lỗi của LLM vẫn nằm dưới phân vị kỳ vọng của chuyên gia ngẫu nhiên ở cả P95 và P97.5 trên cả hai tập dữ liệu. Kết luận kiểm định giữ nguyên vẹn.
  - Không có bất kỳ kết luận hay phán quyết khoa học nào bị đảo chiều.

---

## 8. Môi trường Thực thi và Runtime Đã Dùng

- **Hệ thống đối soát:** Windows 11 host kết hợp Linux WSL2 (Ubuntu 24.04).
- **Môi trường Python tái chạy:**
  - Đường dẫn venv: `/tmp/step6_audit_venv/bin/python` (trên WSL2)
  - Python version: `3.12.3`
  - Thư viện cốt lõi: `numpy==1.26.4`, `scipy==1.17.1`, `scikit-learn==1.5.2` (khớp hoàn toàn với cấu hình ghi nhận tại `rerun_summary.json`).
- **Tình trạng Working Tree:** Toàn bộ repository `GRACE-summary` không có bất kỳ file nào bị sửa đổi hay mất mát; git worktree tạm đã được dọn sạch hoàn toàn. Working tree trở về nguyên trạng ban đầu.
