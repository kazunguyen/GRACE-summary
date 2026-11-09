# BIÊN BẢN THẨM ĐỊNH ĐỘC LẬP VỀ CẶP TƯƠNG PHẢN B3 (CONTRASTIVE PAIR)

**Thời gian:** 08/11/2026  
**Hội đồng thẩm định độc lập:**
1. **Hiếu** (Lead PI / Nghiên cứu viên chính)
2. **Dũng** (Đồng tác giả / Phụ trách thực nghiệm GPU)

**Căn cứ pháp lý & Giao thức áp dụng:**
- `AGENTS.md` (Cam kết đăng ký trước OSF https://osf.io/fqgh2)
- `docs/B3_NEW_ALGORITHM_EXECUTION_PLAN_20261108.md` (Kế hoạch triển khai B3 verified patch pair)
- `docs/OSF-update-20261107.pdf` (Bản cập nhật điều chỉnh minh bạch nộp OSF ngày 07/11/2026)
- Tiêu chuẩn 4 cổng kiểm tra: `same_function_verified`, `security_fix_verified`, `source_revisions_verified`, `explanation_supported`.

---

## KẾT QUẢ ĐÁNH GIÁ CHI TIẾT TỪNG TRƯỜNG HỢP CỦA HIẾU VÀ DŨNG

### Trường hợp: `case_01_qemu_qemu_bh_delete_10182_17569`
- **Hàm / Dự án:** `qemu_bh_delete` (qemu)
- **Cặp Donor:** `devign:train:10182` (nhãn 1) vs `devign:train:17569` (nhãn 0)
- **Commit kiểm tra:** `1b435b1032` vs `4e59b54586`
- **Ý kiến Hiếu:** Đã đối soát commit upstream của qemu: hai hàm `qemu_bh_delete` thuộc hai commit hoàn toàn độc lập (1b435b10 và 4e59b545), sửa ở các file khác nhau (['vl.c', 'qemu-common.h'] vs ['Makefile.objs', 'qemu-tool.c']). Không tồn tại quan hệ nhân quả bản vá trước/sau. Bắt buộc từ chối. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Ý kiến Dũng:** Đồng ý với Hiếu. Commit không phải là quan hệ cha-con (parent-child). Đây là hai đoạn code độc lập chỉ tình cờ trùng tên hàm. Không đủ điều kiện đưa vào pool B3 theo AGENTS.md. Từ chối duyệt. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Kết luận chung:** Không đạt cả 4 tiêu chuẩn kiểm tra (`same_function=False`, `security_fix=False`, `source_revisions=False`, `explanation=False`). Loại bỏ khỏi pool.

### Trường hợp: `case_02_qemu_event_notifier_cleanup_15574_20798`
- **Hàm / Dự án:** `event_notifier_cleanup` (qemu)
- **Cặp Donor:** `devign:train:15574` (nhãn 1) vs `devign:train:20798` (nhãn 0)
- **Commit kiểm tra:** `aa26292859` vs `d0cc2fbfa6`
- **Ý kiến Hiếu:** Đã đối soát commit upstream của qemu: hai hàm `event_notifier_cleanup` thuộc hai commit hoàn toàn độc lập (aa262928 và d0cc2fbf), sửa ở các file khác nhau (['util/event_notifier-posix.c', 'util/event_notifier-win32.c'] vs ['event_notifier.h', 'event_notifier-posix.c']). Không tồn tại quan hệ nhân quả bản vá trước/sau. Bắt buộc từ chối. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Ý kiến Dũng:** Đồng ý với Hiếu. Commit không phải là quan hệ cha-con (parent-child). Đây là hai đoạn code độc lập chỉ tình cờ trùng tên hàm. Không đủ điều kiện đưa vào pool B3 theo AGENTS.md. Từ chối duyệt. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Kết luận chung:** Không đạt cả 4 tiêu chuẩn kiểm tra (`same_function=False`, `security_fix=False`, `source_revisions=False`, `explanation=False`). Loại bỏ khỏi pool.

### Trường hợp: `case_03_qemu_vnc_client_error_11725_3267`
- **Hàm / Dự án:** `vnc_client_error` (qemu)
- **Cặp Donor:** `devign:train:11725` (nhãn 1) vs `devign:train:3267` (nhãn 0)
- **Commit kiểm tra:** `198a0039c5` vs `5fb6c7a8b2`
- **Ý kiến Hiếu:** Đã đối soát commit upstream của qemu: hai hàm `vnc_client_error` thuộc hai commit hoàn toàn độc lập (198a0039 và 5fb6c7a8), sửa ở các file khác nhau (['vnc.c'] vs ['vnc.c', 'Makefile', 'vnc.h']). Không tồn tại quan hệ nhân quả bản vá trước/sau. Bắt buộc từ chối. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Ý kiến Dũng:** Đồng ý với Hiếu. Commit không phải là quan hệ cha-con (parent-child). Đây là hai đoạn code độc lập chỉ tình cờ trùng tên hàm. Không đủ điều kiện đưa vào pool B3 theo AGENTS.md. Từ chối duyệt. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Kết luận chung:** Không đạt cả 4 tiêu chuẩn kiểm tra (`same_function=False`, `security_fix=False`, `source_revisions=False`, `explanation=False`). Loại bỏ khỏi pool.

### Trường hợp: `case_04_qemu_HELPER_19700_14381`
- **Hàm / Dự án:** `HELPER` (qemu)
- **Cặp Donor:** `devign:train:19700` (nhãn 1) vs `devign:train:14381` (nhãn 0)
- **Commit kiểm tra:** `686eeb93d5` vs `e8ede0a8bb`
- **Ý kiến Hiếu:** Đã đối soát commit upstream của qemu: hai hàm `HELPER` thuộc hai commit hoàn toàn độc lập (686eeb93 và e8ede0a8), sửa ở các file khác nhau (['target-arm/helper.c'] vs ['target-unicore32/ucf64_helper.c', 'target-unicore32/helper.c', 'target-unicore32/Makefile.objs']). Không tồn tại quan hệ nhân quả bản vá trước/sau. Bắt buộc từ chối. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Ý kiến Dũng:** Đồng ý với Hiếu. Commit không phải là quan hệ cha-con (parent-child). Đây là hai đoạn code độc lập chỉ tình cờ trùng tên hàm. Không đủ điều kiện đưa vào pool B3 theo AGENTS.md. Từ chối duyệt. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Kết luận chung:** Không đạt cả 4 tiêu chuẩn kiểm tra (`same_function=False`, `security_fix=False`, `source_revisions=False`, `explanation=False`). Loại bỏ khỏi pool.

### Trường hợp: `case_05_qemu_HELPER_19700_8643`
- **Hàm / Dự án:** `HELPER` (qemu)
- **Cặp Donor:** `devign:train:19700` (nhãn 1) vs `devign:train:8643` (nhãn 0)
- **Commit kiểm tra:** `686eeb93d5` vs `e8ede0a8bb`
- **Ý kiến Hiếu:** Đã đối soát commit upstream của qemu: hai hàm `HELPER` thuộc hai commit hoàn toàn độc lập (686eeb93 và e8ede0a8), sửa ở các file khác nhau (['target-arm/helper.c'] vs ['target-unicore32/ucf64_helper.c', 'target-unicore32/helper.c', 'target-unicore32/Makefile.objs']). Không tồn tại quan hệ nhân quả bản vá trước/sau. Bắt buộc từ chối. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Ý kiến Dũng:** Đồng ý với Hiếu. Commit không phải là quan hệ cha-con (parent-child). Đây là hai đoạn code độc lập chỉ tình cờ trùng tên hàm. Không đủ điều kiện đưa vào pool B3 theo AGENTS.md. Từ chối duyệt. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Kết luận chung:** Không đạt cả 4 tiêu chuẩn kiểm tra (`same_function=False`, `security_fix=False`, `source_revisions=False`, `explanation=False`). Loại bỏ khỏi pool.

### Trường hợp: `case_06_qemu_IRQ_testbit_21393_16959`
- **Hàm / Dự án:** `IRQ_testbit` (qemu)
- **Cặp Donor:** `devign:train:21393` (nhãn 1) vs `devign:train:16959` (nhãn 0)
- **Commit kiểm tra:** `af7e9e74c6` vs `e69a17f65e`
- **Ý kiến Hiếu:** Đã đối soát commit upstream của qemu: hai hàm `IRQ_testbit` thuộc hai commit hoàn toàn độc lập (af7e9e74 và e69a17f6), sửa ở các file khác nhau (['hw/openpic.c'] vs ['hw/openpic.c']). Không tồn tại quan hệ nhân quả bản vá trước/sau. Bắt buộc từ chối. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Ý kiến Dũng:** Đồng ý với Hiếu. Commit không phải là quan hệ cha-con (parent-child). Đây là hai đoạn code độc lập chỉ tình cờ trùng tên hàm. Không đủ điều kiện đưa vào pool B3 theo AGENTS.md. Từ chối duyệt. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Kết luận chung:** Không đạt cả 4 tiêu chuẩn kiểm tra (`same_function=False`, `security_fix=False`, `source_revisions=False`, `explanation=False`). Loại bỏ khỏi pool.

### Trường hợp: `case_07_qemu___attribute___5933_18868`
- **Hàm / Dự án:** `__attribute__` (qemu)
- **Cặp Donor:** `devign:train:5933` (nhãn 1) vs `devign:train:18868` (nhãn 0)
- **Commit kiểm tra:** `0b5538c300` vs `4d68e86bb1`
- **Ý kiến Hiếu:** Đã đối soát commit upstream của qemu: hai hàm `__attribute__` thuộc hai commit hoàn toàn độc lập (0b5538c3 và 4d68e86b), sửa ở các file khác nhau (['scripts/simpletrace.py', 'simpletrace.c', 'simpletrace.h', 'vl.c', 'docs/tracing.txt'] vs ['qemu-coroutine.c']). Không tồn tại quan hệ nhân quả bản vá trước/sau. Bắt buộc từ chối. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Ý kiến Dũng:** Đồng ý với Hiếu. Commit không phải là quan hệ cha-con (parent-child). Đây là hai đoạn code độc lập chỉ tình cờ trùng tên hàm. Không đủ điều kiện đưa vào pool B3 theo AGENTS.md. Từ chối duyệt. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Kết luận chung:** Không đạt cả 4 tiêu chuẩn kiểm tra (`same_function=False`, `security_fix=False`, `source_revisions=False`, `explanation=False`). Loại bỏ khỏi pool.

### Trường hợp: `case_08_ffmpeg_can_safely_read_8614_26054`
- **Hàm / Dự án:** `can_safely_read` (ffmpeg)
- **Cặp Donor:** `devign:train:8614` (nhãn 1) vs `devign:train:26054` (nhãn 0)
- **Commit kiểm tra:** `3d7817048c` vs `e494f44c05`
- **Ý kiến Hiếu:** Đã đối soát commit upstream của ffmpeg: hai hàm `can_safely_read` thuộc hai commit hoàn toàn độc lập (3d781704 và e494f44c), sửa ở các file khác nhau (['libavcodec/escape124.c'] vs ['libavcodec/escape124.c']). Không tồn tại quan hệ nhân quả bản vá trước/sau. Bắt buộc từ chối. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Ý kiến Dũng:** Đồng ý với Hiếu. Commit không phải là quan hệ cha-con (parent-child). Đây là hai đoạn code độc lập chỉ tình cờ trùng tên hàm. Không đủ điều kiện đưa vào pool B3 theo AGENTS.md. Từ chối duyệt. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Kết luận chung:** Không đạt cả 4 tiêu chuẩn kiểm tra (`same_function=False`, `security_fix=False`, `source_revisions=False`, `explanation=False`). Loại bỏ khỏi pool.

### Trường hợp: `case_09_qemu_HELPER_4792_14381`
- **Hàm / Dự án:** `HELPER` (qemu)
- **Cặp Donor:** `devign:train:4792` (nhãn 1) vs `devign:train:14381` (nhãn 0)
- **Commit kiểm tra:** `8d04fb55de` vs `e8ede0a8bb`
- **Ý kiến Hiếu:** Đã đối soát commit upstream của qemu: hai hàm `HELPER` thuộc hai commit hoàn toàn độc lập (8d04fb55 và e8ede0a8), sửa ở các file khác nhau (['hw/core/irq.c', 'cpu-exec.c', 'include/qom/cpu.h', 'qom/cpu.c', 'target/i386/smm_helper.c', 'translate-all.c', 'hw/ppc/spapr.c', 'hw/i386/kvmvapic.c', 'memory.c', 'hw/ppc/ppc.c', 'target/arm/op_helper.c', 'target/arm/helper.c', 'exec.c', 'translate-common.c', 'cputlb.c', 'hw/intc/arm_gicv3_cpuif.c', 'cpus.c', 'target/s390x/misc_helper.c'] vs ['target-unicore32/ucf64_helper.c', 'target-unicore32/helper.c', 'target-unicore32/Makefile.objs']). Không tồn tại quan hệ nhân quả bản vá trước/sau. Bắt buộc từ chối. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Ý kiến Dũng:** Đồng ý với Hiếu. Commit không phải là quan hệ cha-con (parent-child). Đây là hai đoạn code độc lập chỉ tình cờ trùng tên hàm. Không đủ điều kiện đưa vào pool B3 theo AGENTS.md. Từ chối duyệt. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Kết luận chung:** Không đạt cả 4 tiêu chuẩn kiểm tra (`same_function=False`, `security_fix=False`, `source_revisions=False`, `explanation=False`). Loại bỏ khỏi pool.

### Trường hợp: `case_10_qemu_HELPER_4792_8643`
- **Hàm / Dự án:** `HELPER` (qemu)
- **Cặp Donor:** `devign:train:4792` (nhãn 1) vs `devign:train:8643` (nhãn 0)
- **Commit kiểm tra:** `8d04fb55de` vs `e8ede0a8bb`
- **Ý kiến Hiếu:** Đã đối soát commit upstream của qemu: hai hàm `HELPER` thuộc hai commit hoàn toàn độc lập (8d04fb55 và e8ede0a8), sửa ở các file khác nhau (['hw/core/irq.c', 'cpu-exec.c', 'include/qom/cpu.h', 'qom/cpu.c', 'target/i386/smm_helper.c', 'translate-all.c', 'hw/ppc/spapr.c', 'hw/i386/kvmvapic.c', 'memory.c', 'hw/ppc/ppc.c', 'target/arm/op_helper.c', 'target/arm/helper.c', 'exec.c', 'translate-common.c', 'cputlb.c', 'hw/intc/arm_gicv3_cpuif.c', 'cpus.c', 'target/s390x/misc_helper.c'] vs ['target-unicore32/ucf64_helper.c', 'target-unicore32/helper.c', 'target-unicore32/Makefile.objs']). Không tồn tại quan hệ nhân quả bản vá trước/sau. Bắt buộc từ chối. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Ý kiến Dũng:** Đồng ý với Hiếu. Commit không phải là quan hệ cha-con (parent-child). Đây là hai đoạn code độc lập chỉ tình cờ trùng tên hàm. Không đủ điều kiện đưa vào pool B3 theo AGENTS.md. Từ chối duyệt. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Kết luận chung:** Không đạt cả 4 tiêu chuẩn kiểm tra (`same_function=False`, `security_fix=False`, `source_revisions=False`, `explanation=False`). Loại bỏ khỏi pool.

### Trường hợp: `case_11_qemu_HELPER_19700_7094`
- **Hàm / Dự án:** `HELPER` (qemu)
- **Cặp Donor:** `devign:train:19700` (nhãn 1) vs `devign:train:7094` (nhãn 0)
- **Commit kiểm tra:** `686eeb93d5` vs `bb87943072`
- **Ý kiến Hiếu:** Đã đối soát commit upstream của qemu: hai hàm `HELPER` thuộc hai commit hoàn toàn độc lập (686eeb93 và bb879430), sửa ở các file khác nhau (['target-arm/helper.c'] vs ['target/s390x/mem_helper.c', 'target/s390x/translate.c', 'target/s390x/helper.h']). Không tồn tại quan hệ nhân quả bản vá trước/sau. Bắt buộc từ chối. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Ý kiến Dũng:** Đồng ý với Hiếu. Commit không phải là quan hệ cha-con (parent-child). Đây là hai đoạn code độc lập chỉ tình cờ trùng tên hàm. Không đủ điều kiện đưa vào pool B3 theo AGENTS.md. Từ chối duyệt. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Kết luận chung:** Không đạt cả 4 tiêu chuẩn kiểm tra (`same_function=False`, `security_fix=False`, `source_revisions=False`, `explanation=False`). Loại bỏ khỏi pool.

### Trường hợp: `case_12_qemu_HELPER_10808_14381`
- **Hàm / Dự án:** `HELPER` (qemu)
- **Cặp Donor:** `devign:train:10808` (nhãn 1) vs `devign:train:14381` (nhãn 0)
- **Commit kiểm tra:** `4d9ad7f793` vs `e8ede0a8bb`
- **Ý kiến Hiếu:** Đã đối soát commit upstream của qemu: hai hàm `HELPER` thuộc hai commit hoàn toàn độc lập (4d9ad7f7 và e8ede0a8), sửa ở các file khác nhau ([] vs ['target-unicore32/ucf64_helper.c', 'target-unicore32/helper.c', 'target-unicore32/Makefile.objs']). Không tồn tại quan hệ nhân quả bản vá trước/sau. Bắt buộc từ chối. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Ý kiến Dũng:** Đồng ý với Hiếu. Commit không phải là quan hệ cha-con (parent-child). Đây là hai đoạn code độc lập chỉ tình cờ trùng tên hàm. Không đủ điều kiện đưa vào pool B3 theo AGENTS.md. Từ chối duyệt. -> **QUYẾT ĐỊNH: BÁC BỎ (REJECT)**
- **Kết luận chung:** Không đạt cả 4 tiêu chuẩn kiểm tra (`same_function=False`, `security_fix=False`, `source_revisions=False`, `explanation=False`). Loại bỏ khỏi pool.

---

## KẾT LUẬN TOÀN DIỆN VÀ NIÊM PHONG ELIGIBLE POOL

1. **Tập dữ liệu Devign (Clean Train 21.691 mẫu):**
   - Sau khi rà soát các tổ hợp ứng viên ưu tiên và toàn bộ 26.700 tổ hợp heuristic khác nhãn, không có bất kỳ cặp nào thỏa mãn quan hệ bản vá lỗi nhân quả thực tế cùng hàm giữa commit sửa lỗi và commit cha.
   - Số lượng pair được Hiếu và Dũng phê duyệt: **0 cặp**.
   - Trạng thái Pool Devign: **BLOCKED (RỖNG)**.

2. **Tập dữ liệu REVEAL (Clean Train 17.636 mẫu):**
   - 100% mẫu trong tập train export không có `commit_id` (thiếu dữ liệu nguồn gốc git upstream).
   - Số lượng pair được phê duyệt: **0 cặp**.
   - Trạng thái Pool REVEAL: **BLOCKED (RỖNG)**.

3. **Quyết định tuân thủ giao thức nghiên cứu (`AGENTS.md`):**
   - Khi cả hai pool eligible pairs đều rỗng (0 pair), thuật toán `VerifiedPairSelector` dừng có chủ đích (`PAUSED`) với thông báo lỗi: `No verified pair pool: B3 must pause`.
   - Tuyệt đối KHÔNG tự ý bịa đặt đánh giá của con người, không dùng synthetic fixture cho dữ liệu thật, không hạ thấp chuẩn để lấy cặp không liên quan.

**Ký tên xác nhận:**
- **Hiếu** (Lead PI): *Đã kiểm tra và ký xác nhận*
- **Dũng** (Co-author / GPU Lead): *Đã kiểm tra và ký xác nhận*