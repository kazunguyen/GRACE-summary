"""Create an honest dated analysis record after inference started; never backdate preregistration."""
import json,shutil,zipfile
from datetime import datetime,timezone,timedelta
from pathlib import Path
import yaml
from validation_lock import RULES,RULES_SHA256,file_sha256,write_json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;BASE=ROOT/'01_Author_Baseline_Unified'
LOCK=HERE/'analysis_lock_20261101'
if LOCK.exists():raise SystemExit('Analysis record already exists; do not overwrite. Create a new version for amendments.')
LOCK.mkdir()
now=datetime.now(timezone.utc);stamp=now.isoformat();local=now.astimezone(timezone(timedelta(hours=7))).isoformat()
protocol=yaml.safe_load((BASE/'diagnostic_kit/configs/protocol.yaml').read_text(encoding='utf-8'))
inventory=[]
folders={'B0':ROOT/'02_Arm_B0_Source_Only/output/bundles','B1':ROOT/'03_Arm_B1_Graph_Only/output/bundles',
 'B2':BASE/'output/local_full/bundles_recovered_joern_final_20261031',
 'B2-flip':ROOT/'04_Arm_B2_Flip/output/bundles','B2-rep':ROOT/'05_Arm_B2_Rep/output/bundles'}
for arm,folder in folders.items():
    for dataset in ('devign','reveal'):
        for split in ('validation','test'):
            p=folder/dataset/split/'bundle_manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
            inventory.append({'arm':arm,'dataset':dataset,'split':split,'manifest_path':p.relative_to(ROOT).as_posix(),
                              'manifest_sha256':file_sha256(p),'prompt_set_sha256':m['prompts_sha256'],'count':m['count'],
                              'variant':m.get('prompt_variant','baseline_b2_figure6')})
analysis={'schema':'dated_analysis_record_v1','created_at_utc':stamp,'created_at_Asia_Bangkok':local,
          'registration_status':'local_analysis_record_after_inference_started','osf_publication_status':'not_published_no_connected_OSF_tool',
          'run_started_before_record':True,'external_test_progress':'unknown; user reports inference running',
          'not_a_retroactive_preregistration':True,'threshold_rules':RULES,'threshold_rules_sha256':RULES_SHA256,
          'model':protocol['backend'],'seeds':protocol['seeds'],'stats':protocol['stats'],
          'primary_contrasts':protocol['primary_contrasts'],'prompt_inventory':inventory,
          'donor_scope':'existing paired B2; known mismatch versus new Devign bank (5 validation,16 test prompts); no donor changes during current run',
          'test_use':'GPU scores may be generated already; threshold fitting reads validation records only. Test-first chronology remains disclosed.',
          'source_protocol_sha256':file_sha256(BASE/'diagnostic_kit/configs/protocol.yaml')}
write_json(LOCK/'protocol.analysis.json',analysis)
write_json(LOCK/'threshold_rules.json',{'rules':RULES,'rules_sha256':RULES_SHA256})
if (HERE/'thresholds.json').exists():shutil.copyfile(HERE/'thresholds.json',LOCK/'thresholds.initial.json')
shutil.copyfile(BASE/'diagnostic_kit/configs/protocol.yaml',LOCK/'protocol.template.snapshot.yaml')
text=f'''# Bản ghi giao thức và kế hoạch phân tích sau khi đã bắt đầu inference

Thời điểm thực tế: {local} (Asia/Bangkok), tương ứng {stamp} UTC.

Đây là bản ghi phân tích có thời điểm, **không phải đăng ký trước hồi tố**. Người dùng xác nhận inference đã chạy trước thời điểm này. Kết quả validation B2 đã được xem trong giai đoạn trước; hiện có thêm B0 validation. Tiến độ test trên các tài khoản Kaggle ngoài bản sao local không được xác nhận. Những run đã bắt đầu trước bản ghi giữ trạng thái thăm dò/đã tiếp xúc; không sửa timestamp, không gọi chúng đã được preregistered.

## Phạm vi và cấu hình

Tầng 1 gồm B0, B1, B2, B2-flip, B2-rep trên Devign/REVEAL; full official validation và test. Chạy Kaggle GPU, Qwen3-Coder-30B-A3B-Instruct Q4_K_M, model SHA-256 `{protocol['backend']['model_sha256']}`, tokenizer revision `{protocol['backend']['tokenizer_revision']}`, llama-cpp-python 0.3.16. Graph trần 40/80, ngân sách 1.500 token; code 3.000; demo 1.500; tổng 8.192 gồm chat template và dự trữ 64. B0/B1 giữ scaffold B2 trống theo yêu cầu; flip chỉ đảo nhãn, rep giữ nguyên prompt và gọi model mới. Danh sách hash prompt/variant của 20 tập nằm trong protocol.analysis.json.

Giữ bộ B2 ghép cặp hiện đang chạy; không thay donor/model/prompt trong phiên inference. Đã biết B2 Devign có 5 prompt validation và 16 prompt test dùng demo ngoài kho donor mới trong protocol template. Vì vậy không tuyên bố toàn bộ run hiện tại đã tuân thủ kho mới. Nếu tạo B2 mới từ kho mới, phải tạo phiên giao thức khác và dùng lại đúng B2 đó cho flip/rep. Chưa nghiệm thu thay thế metadata seed bằng backend seed ở các run lịch sử; notebook B2 mới truyền seed=42, logits/greedy không lấy mẫu.

## Quy tắc chọn ngưỡng đã cố định

Score từ logits gốc là sigmoid(logit_1-logit_0), không dựa vào việc nhãn có nằm trong top-5. Tự chọn tau trên đủ ID validation của đúng arm/dataset, chỉ dùng score valid hữu hạn, grid 0,01–0,99 bước 0,01, tối đa MCC. Hòa trong 1e-9: gần 0,5 nhất, sau đó ngưỡng nhỏ hơn. Nếu mọi MCC không xác định do predictor hằng: tau=0,5, MCC=null và đánh dấu degenerate. Báo coverage/invalid; không gán invalid về nhãn 0. Không khóa trên validation dở; phải khớp ID, label, prompt hash, model, seed và tokenizer/backend identity. Ngưỡng đã khóa không được ghi đè bằng kết quả đẹp hơn.

Việc chọn ngưỡng chỉ đọc file records của split validation; không mở test records hoặc metric test. Tính ngưỡng và lưu JSON là công việc CPU, độc lập với GPU inference. Nếu test đã được suy luận trước khi khóa ngưỡng, có thể chấm lại score bằng tau cố định mà không chạy lại GPU, nhưng phải công khai thứ tự thực tế. Thay đổi tiêu chí vì đã xem test phải được đánh dấu thăm dò.

## Phân tích đã có trong đề cương

Giữ contrasts, biên tác dụng, 5.000 bootstrap và Holm trong protocol template; không chọn lại model/arm hoặc seed từ test. Báo riêng metric raw greedy, score tại 0,5, score tại tau validation và AUROC/AUPRC. Rep là lượt gọi mới, checkpoint resume cùng run không phải một expert độc lập. Những bước prompt audit bằng người, donor và preregistration còn thiếu trong kiểm toán không tự được hoàn thành bởi file này.

## Công bố và phiên sau

Gói này được tạo local và có thể niêm phong bằng commit/tag riêng. Chưa đăng lên OSF: không có kết nối/tài khoản OSF trong phiên công cụ này. Không điền ngày local này thành ngày OSF. Nếu đăng sau, ghi thời điểm công bố thực tế và phân biệt phần nào được cố định trước/sau khi có kết quả. Các sửa đổi sau bản ghi phải thêm vào CHANGES_AFTER_ANALYSIS_LOCK.md, không sửa ngầm bản ghi này.
'''
(LOCK/'preregistration.md').write_text(text,encoding='utf-8')
(LOCK/'CHANGES_AFTER_ANALYSIS_LOCK.md').write_text('# Thay đổi sau bản ghi\n\nChưa có sửa đổi. Thêm thời điểm, lý do và mức tiếp xúc test cho từng thay đổi; không sửa bản ghi đã niêm phong.\n',encoding='utf-8')
files={p.name:file_sha256(p) for p in LOCK.iterdir() if p.is_file()}
write_json(LOCK/'SHA256SUMS.json',{'created_at_utc':stamp,'files':files})
archive=HERE/'analysis_record_for_OSF_20261101.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(LOCK.iterdir()):z.write(p,p.name)
print('Analysis record:',LOCK)
print('OSF-ready archive (not published):',archive)
