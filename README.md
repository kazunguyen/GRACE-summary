# GRACE Summary: Kho Nghiên Cứu & Tối Ưu Hóa GRACE

Kho lưu trữ chuẩn hóa toàn bộ mã nguồn mô hình gốc (Author Baseline) và các nhánh cải tiến phương pháp GRACE (Graph-based In-Context Learning for Vulnerability Detection).

---

## Cấu Trúc Kho Lưu Trữ

- **`01_Author_Baseline_Unified/`**: Bản triển khai chuẩn hóa duy nhất của mô hình gốc tác giả GRACE, tuân thủ `evaluation_contract_v2_context8192bytes_20261029`.
  - Giải quyết dứt điểm các điểm bất đồng giữa các phiên bản baseline lịch sử.
  - Tích hợp bộ kiểm thử tự động, chạy lại được ngay lập tức ở chế độ Mock và Full API.
  - Xem tài liệu chi tiết tại [01_Author_Baseline_Unified/README.md](file:///d:/JUNIOR/LabThayTho/GRACE-summary/01_Author_Baseline_Unified/README.md).

- **Các thư mục tiếp theo (Dự kiến mở rộng)**:
  - `02_Enhancement_C1_HybridRetrieval/`
  - `03_Enhancement_C2_StratifiedDemos/`
  - ...
  - `08_Enhancement_Full/`

---

## Nhánh Git (Branches)

- **`main`**: Nhánh chính của dự án.
- **`baseline-unified`**: Nhánh triển khai bản baseline thống nhất gốc của tác giả. Mọi cải tiến mới sẽ được phân nhánh và đối chiếu dựa trên baseline này.
