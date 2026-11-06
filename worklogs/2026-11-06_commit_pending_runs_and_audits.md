# Commit và push cập nhật local - 06/11/2026

Theo yêu cầu người dùng, chuẩn bị commit toàn bộ thay đổi không bị Git ignore trên nhánh fix/kaggle-repeat-main, rồi push cùng 5 commit local có sẵn lên origin. Bao gồm cập nhật I-10/I-11, notebook đã thực thi, sổ RUNS/current_status, hồ sơ B1-H2 exploratory, các audit B3 lịch sử và worklog. Folder 09_Arm_B3_Contrastive đã xóa không được khôi phục.

## Dữ liệu lớn

Bốn specs gốc dưới grace_15arms_prompts_and_clean_specs/specs/ có kích thước 110–213 MB, vượt 100 MiB/file. Giữ nguyên file local, thêm ignore chính xác và manifest local_specs_manifest.json ghi size/SHA-256/source ZIP. Không tuyên bố chúng đã có bản sao mới trên remote. Không force-add các output/checkpoint ZIP bị ignore từ trước. Các records JSONL không bị ignore trong Runs-management/kaggle_outputs_20261105 được đưa vào commit.

## Kiểm tra trước commit

- Ba bộ test bắt buộc của AGENTS.md (preregistration_integrity, probes, stats_and_complementarity) cùng current_status và frozen_resume: 46 test pass lần đầu; một test notebook thiếu dependency, sau khi bổ sung nbformat vào thư mục test riêng, cập nhật test để chấp nhận notebook thực thi có provenance và helper khớp đúng runtime Kaggle đã nhập; test đó pass. Tổng 47 test riêng biệt đạt. Không xóa output notebook để hợp test.
- Compile tĩnh 29 file Python/notebook mới hoặc sửa: không lỗi.
- Quét 307 file ứng viên theo các mẫu credential thông dụng: không phát hiện. Không ghi giá trị credential vào log.
- git diff --check đạt khi cho phép CRLF hợp lệ (core.whitespace có cr-at-eol); không đổi line ending artifact có hash.
- Audit độc lập ở lượt trước đã đối chiếu 17.800 record I-10/I-11 qua 89 kiểm tra, không sai lệch.

## Giới hạn

Không chạy inference, fit ngưỡng, đổi thiết kế B3/H2 hoặc sửa artifact OSF trong lượt commit. Các giới hạn provenance/nội dung và trạng thái exploratory ghi trong README/worklog tương ứng vẫn được giữ. Dependency test bổ sung nằm ở C:/MY-FILES/LAB-THAY-THO/tmp/commit_test_deps_20261106/, không cài vào global hoặc đưa vào repo.
