# Hướng dẫn chạy baseline

Cài phụ thuộc từ requirements.lock. Đảm bảo model/tokenizer Qwen và CodeT5 được tải theo revision trong evaluation_contract.yaml.

```powershell
python -m unittest -v test_baseline
python run_pipeline.py --dataset mock --split validation --mock --max-targets 10 --experiment-name mock-validation-v3
```

Mock dùng tokenizer giả, embedding giả và LLM giả; không dùng số liệu mock trong nghiên cứu. Lượt thật dùng hai notebook trong RUN_GUIDE_KAGGLE.md với model GGUF Q4_K_M; runner Transformers BF16 cũ đã chặn chạy thật để tránh nhầm baseline. Chạy thật yêu cầu tokenizer/model đúng revision và dữ liệu validation có nhãn, graph đã kiểm chứng. Chọn tên thí nghiệm mới khi prompt, model, dữ liệu hoặc contract thay đổi.

Xem DIAGNOSTIC_INTEGRATION.md để xuất specs/donor/manifest. Lượt test xác nhận cần khóa protocol và ngưỡng trên validation trước khi chạy.

## Logprob cho baseline B2

Notebook Kaggle lấy logits chưa ràng buộc của token đầu, kiểm tra `0` và `1` đều là một token, và ghi `records.jsonl`. Mỗi dòng chứa ID, nhãn, prompt hash, demo ID, token counts, model hash, token ID, `logprob_0`, `logprob_1`, `p0`, `p1`, `s`, `pred_argmax`, `top5` và trạng thái. `valid` chỉ nói score tính được; `response_valid` nói token model sinh có phải 0/1. Hai trạng thái này có thể khác nhau.

`s` được tính ổn định từ logits của hai token nhãn trong phân phối gốc, không giới hạn top-5. Mock không tạo logprob thật. Kiểm tra tokenizer Qwen, 20 mẫu validation, tỉ lệ score/response hợp lệ và thời gian trước khi chạy lớn. Không diễn giải logprob sau ràng buộc là logprob gốc.
