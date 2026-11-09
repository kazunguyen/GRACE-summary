# Đối chiếu trực tiếp với ZIP runtime lock ngày07/11

Nguồn: `Runs-management/grace_hieu_5arms_runtime_locked_20261107.zip`, SHA-256 `76a49a770897b7d0832ee87aa7d7e308ebbca57fdd7aaaf02f0f07f2400f156c`.

**Kết luận: các cấu hình model/backend/GPU/runtime/scoring của hai notebook mới vẫn tuân thủ contract trong ZIP. Chưa thể chứng nhận môi trường thực tế đã đạt cho phiên đang chạy khi chưa thu được native logs.** Không gọi hai notebook mới là bản sao nguyên byte của notebook ZIP: chúng khác scope/điều phối/resume và có sửa parser được nêu dưới đây.

## 1. Contract của ZIP

Cả5 notebook trong ZIP nhúng **cùng một contract**, raw SHA `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`. ZIP gồm B1-full/B1-shuf/B2-labelonly/B2-nolabel/B2-rep; không có notebook B3. B3 mới kế thừa các quy tắc runtime đó bằng contract mở rộng.

| Hạng mục | Quy tắc giữ nguyên |
|---|---|
| Model | Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M; SHA `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335` |
| Backend | llama-cpp-python0.3.16, sdist SHA `34ed0f9bd9431af045bb63d9324ae620ad0536653740e9bb163a2e1fcb973be6`; không thay backend |
| Tokenizer | Qwen tokenizer revision `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`, chat template và HF/GGUF token equality giữ nguyên |
| GPU | T4x2, `LLAMA_SPLIT_MODE_LAYER`, `n_gpu_layers=-1`, `main_gpu=0`, `tensor_split=None`; yêu cầu49/49 layers offload |
| Context/batch | n_ctx8192, n_batch256, n_ubatch256; flash_attn=false, logits_all=true |
| Decoding/scoring | Không sampling; reset trước mỗi prompt; unconstrained first-token logits, float64 normalization; binary score như ZIP; raw không binary vẫn giữ numeric score hợp lệ |
| Seed | Constructor4294967295 là sentinel như ZIP; prompt seed riêng42/43/44 của B1-shuf,42 của B3. Không đánh đồng prompt seed với RNG sampling |
| Build | CUDA enabled, compute architecture75, Python family3.13; record compiler/CUDA/driver/CMake/build flags và compiled-library hashes |

Các phiên không bị yêu cầu image/compiler/driver hoặc wheel giống từng byte: **chính ZIP cho phép Kaggle platform build**, miễn source/package/constructor đúng và lưu provenance. Không tự nâng tiêu chuẩn này thành bit-identical build, cũng không bỏ các trường ghi nhận bắt buộc.

## 2. B1-shuf hiện chạy

- Contract nhúng **giống nguyên bytes** contract ZIP85d877…; model/version/constructor không đổi so với checkpoint6.416.
- Helper không giống nguyên bytes: diff duy nhất là parser GPU được sửa từ chỉ nhận `Device n: … T4` sang nhận cả `using device CUDAn (Tesla T4)`. Ưu tiên IDs thực dùng khi load, bắt buộc đúng tập `{0,1}`; vẫn giữ49/49 offload/context/batch gates. Đây là bug fix đọc native log, không đổi cách chia model hoặc tắt assertion. [Diff](b1_helper_vs_zip.diff).
- Sáu package của ZIP đều pin nguyên: numpy2.1.3, huggingface-hub0.36.2, tokenizers0.22.2, transformers4.57.1, llama-cpp-python0.3.16, scikit-learn1.5.2.
- Bổ sung pin/assert SciPy1.16.3, đúng version đã quan sát ở cả hai session checkpoint cha. Không sửa identity contract cũ hoặc gán chứng nhận7-package hồi tố cho records cũ.

## 3. B3 mới hiện chạy

Đối chiếu object JSON cho **từng nhóm** `constructor`, `model`, `tokenizer`, `backend_source`, `gpu`, `build`, `scoring`, `decoding`: **tất cả bằng nhau** với ZIP.

Khác biệt package duy nhất: B3 thêm `scipy==1.16.3`; sáu version cũ giữ nguyên. Vì vậy raw contract hash B3 là4c9c3bcf… theo release đã duyệt, không thể gọi raw hash giống85d877… của ZIP.

Coordinator chạy Devign rồi REVEAL bằng cùng worker/helper, mỗi dataset giữ input root riêng. Một child model active tại một thời điểm trong notebook B3; điều phối/checkpoint không thay numeric inference settings.

## 4. Cách chia GPU cần hiểu đúng

`tensor_split=None` và layer split nghĩa là backend phân bổ layer theo free VRAM lúc load trên hai T4. **ZIP ghi rõ fixed_ratio_guaranteed=false**, nên không có cam kết luôn25/24 layer hoặc50/50 chính xác. Điều bắt buộc là đúng profile, không silent CPU layer fallback, full49/49 và đầy đủ log/device/VRAM provenance.

Hai notebook nhận hai runtime T4x2 riêng của Kaggle trên cùng account. Không có việc chia một cặp T4 thành một GPU cho B1 và một GPU cho B3.

## 5. Mức bằng chứng hiện tại

- Đã kiểm source nhúng, input/runtime pins,17 CPU tests và server source readback: exact cell match, PRIVATE/GPU enabled, shape NvidiaTeslaT4, đúng dataset/model sources.
- Native gates tự abort trước score khi model/package/tokenizer/offload/context không đúng; không fallback CPU/backend/model khác.
- Endpoint live-output chưa cung cấp file/log. **Chưa kết luận actual native runtime PASS** hoặc actual layer distribution từ chỉ API RUNNING. Cần thu native/provenance mới để nghiệm thu thực tế.

[So sánh máy đọc được](comparison_to_runtime_zip.json), [trạng thái launch](STATUS.md).
