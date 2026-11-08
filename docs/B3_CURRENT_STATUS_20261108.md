# B3 mới — trạng thái hiện tại và chỉ dẫn chạy

Chốt sau review REVEAL và tải checkpoint B1-shuf ngày08/11/2026. Đây là chỉ dẫn **hiện hành**; các audit/report v1–v5 và notebook lịch sử được giữ nguyên để truy vết, không đại diện cho trạng thái cuối.

## Kết luận ngắn

**Cả Devign và REVEAL đã sẵn sàng về dữ liệu, pool review, prompt và CPU delivery để chuyển sang nghiệm thu kỹ thuật GPU. Chưa được ghi native runtime PASS hay full validation hoàn tất.** Account huuhieu3333 ở lần kiểm gần nhất chỉ còn khoảng23,6 phút quota; không đủ request9h đã chuẩn bị. Phải kiểm lại quota trước launch.

## Đã làm xong

- Phục hồi source/actual fix/parent và mapping của một pair clean-train cho mỗi dataset; hai review thật trên final payload được validator chấp nhận. REVEAL không còn blocked vì pool rỗng.
- Devign Case08 FFmpeg: payload `0ced77fefccbcef797c3c01abfa0d139d5611e2d562e8f5ec01089ff05168ee1`.
- REVEAL curl `alloc_addbyter`, train16061→17887: payload `537b1732aa7cc6dbc3821044275e1364568c6a0893999262b9e5f1264a1c71a7`; actual fix/parent, đầy đủ patch và C lexical mapping được kiểm, hai phiếu22:50+07:00 approved.
- Full prompt census **Devign2.732 / REVEAL2.273**: ID/code đúng frozen validation, Figure6 đúng, target labels không vào prompt/selector, budgets đạt. REVEAL max chat5.280+64 reserve; demo697 tokens.
- Sửa schema inference ID/label join, input-root pin độc lập, ZIP/unpacked, restore/checkpoint identity/provenance, score consistency và native GPU log parser. Devign và REVEAL dùng cùng method/runtime contract.
- CPU verification101 tests ở lượt sửa v6;3 kiểm dataset-specific bổ sung cho REVEAL v7 đạt. Bằng chứng cũ chỉ tái sử dụng khi code/artifact hashes giữ nguyên; không gọi101 là tests đã chạy lại trong mọi lượt.
- Hai input datasets đã PRIVATE/ready trên cùng account huuhieu3333. Không đẩy sang account khác và chưa launch GPU.

## Dùng những artifact nào?

| Dataset | Input release / notebook | Validation | Kaggle private inputs |
|---|---|---:|---|
| Devign | [v6 manifest](../Runs-management/b3_verified_patch_v1/release_20261108_v6/release_manifest.json), [notebook](../Runs-management/b3_verified_patch_v1/release_20261108_v6/delivery/notebook.ipynb) | 2.732 | [grace-b3-v6-devign-inputs](https://www.kaggle.com/datasets/huuhieu3333/grace-b3-v6-devign-inputs) |
| REVEAL | [v7 REVEAL manifest](../Runs-management/b3_verified_patch_v1/release_20261108_v7_reveal/release_manifest.json), [notebook](../Runs-management/b3_verified_patch_v1/release_20261108_v7_reveal/delivery/notebook.ipynb) | 2.273 | [grace-b3-v7-reveal-inputs](https://www.kaggle.com/datasets/huuhieu3333/grace-b3-v7-reveal-inputs) |

Hai input versions là hai snapshot theo dataset, **cùng thuật toán** `b3-verified-patch-v1`, seed42. [Experiment index](../Runs-management/b3_verified_patch_v1/v7_reveal_acceptance_20261108/experiment_index.json) ràng buộc đúng hashes của cả hai. Mỗi pool hiện chỉ1 pair; phải công bố giới hạn này, không tuyên bố đã đánh giá adaptive retrieval với pool đa dạng.

Không chạy notebook delivery v5 đã bị audit phát hiện lỗi. Notebook chuẩn bị candidate từ baseline là công cụ discovery/human-review; không thay thế hai delivery inference đã nghiệm thu ở bảng trên.

## Gate còn lại trước full validation

1. Account/quota đủ cho session được chốt; kiểm lại mount model source/version và private input. Không âm thầm chuyển private data sang account khác.
2. Dùng **prepared SDK request**, giữ `machine_shape=NvidiaTeslaT4`, đọc lại notebook source và server shape. Devign base metadata template cần overlay model source/shape đã có trong prepared request; CLI cũ có thể bỏ shape.
3. Nghiệm thu runtime native thật: model/hash,7 package pins, backend source/build, tokenizer/HF–GGUF,2 T4/49 layers/context/scoring/provenance. CPU PASS chưa chứng minh runtime GPU.
4. G4 đạt → full validation mới2.732/2.273. Checkpoint khi hết thời gian/quota; không dừng theo metric. Chưa có score mới ở thời điểm chốt tài liệu.
5. Đủ validation → τ* **riêng từng dataset** theo grid/tie rule đã định, độc lập kiểm rồi khóa artifact mới. Không sửa frozen thresholds và không lấy scores/threshold lịch sử của B3 để bù.
6. Sau đó mới dựng/audit test input và chạy test; chưa mở nodiff/swap/flip GPU trong scope hiện tại.

## ZIP prompt bàn giao — chỉ local

`Runs-management/local_deliveries/B3_NEW_ALGORITHM_PROMPTS_DEVIGN_REVEAL_20261108.zip` chứa hai delivery/input ZIP nguyên bytes, notebook/runtime/manifests và prompt preview. [Receipt/hash](../Runs-management/b3_verified_patch_v1/B3_PROMPT_HANDOFF_MANIFEST_20261108.json). **ZIP tổng này không push Git.** Đây là gói bàn giao local; không upload cả hai input roots vào một notebook đang yêu cầu đúng một dataset.

## B1-shuf và kết quả lịch sử

B1-shuf checkpoint mới đã tải và kiểm: **6.416/15.018 (42,72%)**, thêm665; seed42 đủ cả hai tập, seed43 Devign1.410, các phần còn lại8.602. Dừng deadline, checkpoint hợp lệ; chưa resume thêm. [Chi tiết](../Runs-management/b1_shuf_download_20261108_231129/STATUS.md).

B1-full seed42 test đã hoàn tất. B3 validation lịch sử5.005 records là kết quả thuật toán/runtime cũ, lưu riêng; không được gộp vào scores của B3 mới. B2-rand status theo kết quả mới từ baseline, không được ghi lùi tiến độ khi đồng bộ docs.

## Bằng chứng chi tiết

[Dual-dataset readiness](../Runs-management/b3_verified_patch_v1/v7_reveal_acceptance_20261108/DUAL_DATASET_READINESS.md), [remediation](../Runs-management/b3_verified_patch_v1/v6_acceptance_verified_20261108/REMEDIATION_REPORT.md), [plan](B3_NEXT_RELEASE_PREPARATION_AND_ACCEPTANCE_20261108.md). Các báo cáo trước giữ trạng thái đúng tại thời điểm lập, không sửa lại để xóa lịch sử thiếu sót.
