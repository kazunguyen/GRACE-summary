# Audit lần 5 — candidate nguồn thật đầu tiên, 08/11/2026

**Kết luận: có thể chuyển sang chuẩn bị/chuyển hồ sơ cho hai reviewer độc lập của case Devign 08. Đã kiểm chứng nguồn upstream và mapping chỉ khác dòng trống. Tuy nhiên chưa nên ký duyệt payload hiện tại hoặc nạp pool: cần chốt cách biểu diễn mapping nguồn và sửa rationale trước khi khóa packet cuối. Chưa đạt G2, chưa được chạy GPU.**

## Phạm vi và bằng chứng thực hiện

- Kiểm hồ sơ mới `g1_source_investigation_20261108`, builder và các thay đổi ingest/gate sau audit 4.
- Chạy **một lần** bộ B3 bị ảnh hưởng: **43 passed, 0 failed, 0 skipped**, 50,78 giây. Không chạy lại ba bộ không liên quan hoặc builder tạo dossier vào thư mục hiện có.
- Tải lại độc lập đúng **ba tài nguyên công khai**: API commit FFmpeg, file parent và file fix. Cả ba khớp **nguyên bytes** với archive được nộp. Trình đọc web không lấy được trang commit; đối chiếu thành công bằng HTTPS CLI với TLS verification, lưu responses riêng trong audit.
- Áp dụng cả hai hunk của actual upstream patch lên toàn bộ parent file, kiểm từng dòng context/removed: kết quả bằng toàn bộ fix file. Kiểm Git blob SHA-1 của fix file khớp metadata commit.
- Đối chiếu hai donor với clean train, nhãn 1/0, schema candidate, canonical payload hash của candidate/packet/form/report và hàm trích từ source file.
- Đối chiếu hash lịch sử: v1 **103**, v2 **118**, v3 **118** file đều nguyên vẹn. Không sửa source, bank, release hoặc phiếu review thật.

## Kết quả có thể xác nhận

| Hạng mục | Kết quả |
|---|---|
| Repository/path | `FFmpeg/FFmpeg`, `libavcodec/escape124.c`, xác nhận từ upstream readback |
| Actual fix | `3d7817048cb387de87600f2152075f78b37b60a6` |
| Parent | `4b529edff8934c258af95e5acc51f84deea66262`, có trong parent list của actual fix |
| Nội dung fix | Đổi tham số `can_safely_read` từ `int` sang `uint64_t`, đồng thời đổi biểu thức tại caller `size * 34` thành `size * 34L` |
| Source/archive/diff | File bytes, report file hashes, API patch và full-file patch application đều khớp |
| Donor mapping | `devign:train:8614` nhãn 1, `devign:train:26054` nhãn 0; cả hai thuộc frozen clean train |
| Hàm nguồn | Trước/sau đều ở dòng 51–53 của file upstream; khớp sidecar `upstream_before_raw/upstream_after_raw` |
| Định dạng donor | Không khớp exact bytes với upstream; chỉ cần bỏ **dòng hoàn toàn rỗng** trong donor là khớp nguyên văn hàm upstream. Không cần thay token, khoảng trắng trong dòng hoặc code |
| Payload/packet/form | Canonical payload hash khớp `f9591b61817ea3f976fbb897263dae2604fae1f62f81be2f8248efb46ad4ee41`; candidate `reviews=[]` |
| Pool/review | Chưa có hai phiếu thật hoặc pool mới ACTIVE trong hồ sơ được nộp |

Nguồn gốc bản vá integer overflow dẫn tới excessive memory allocation được hỗ trợ bởi [commit FFmpeg](https://github.com/FFmpeg/FFmpeg/commit/3d7817048cb387de87600f2152075f78b37b60a6). Audit chưa xác minh nội dung Ticket 1629 hoặc xây dựng/chạy bản FFmpeg cũ để chứng minh tác động khai thác.

## Các sửa đổi phần mềm sau audit 4

- CLI Step 6 gọi ingest với `raise_on_error=True`; lỗi form/parse được ghi vào ledger và có exception. Test R01 qua. Hàm cấp thấp vẫn mặc định không raise; caller khác phải xử lý giá trị thất bại, không gọi rồi bỏ qua.
- Pair mới và pair giữ lại dùng `resolve_review_consensus`; có xử lý normalized reviewer, thời gian UTC, cùng timestamp mâu thuẫn và giới hạn reviewer. Các test R02/R03 qua.
- Pool đề xuất merge pair giữ lại và pair mới, xuất membership diff; test thêm B giữ A qua.
- Step 8 bắt buộc các file trong nhóm module/script/authority/freeze/tokenizer; có binding report Step 7 bằng release target và inputs seal. Các test thiếu nhóm/thiếu file và report mismatch qua.
- R08 hiện kiểm trạng thái manifest v3 có sẵn; **không phải** một phép thử đầy đủ tự gây file corruption hay thay verdict inputs. Vì thế không dùng riêng tên R01–R08 hoặc số 43 tests để khẳng định mọi nhánh đều được kiểm chứng. Không yêu cầu mở thêm bộ test diện rộng cho bước review nguồn này.

Các thay đổi đủ để tiếp tục bước review hồ sơ nguồn. Chúng chưa cấu thành release inference mới: hash ba script Step 6/7/8 hiện khác manifest v3, đúng với việc giữ v3 nguyên vẹn và phát triển tiếp ở working tree. Trước G3 phải phát hành version mới có inputs/report đồng bộ, bao gồm builder dossier cùng evidence artifacts thực sự sử dụng.

## Những việc phải hoàn thiện trước khi ký hai review cuối và nạp pool

### 1. Chốt mapping dòng trống và giữ nguồn nguyên văn trong hồ sơ được review

Builder hiện ghi `source.before/after` bằng **donor code**, còn hàm upstream thật ở `upstream_*_raw` ngoài candidate payload. Schema pass vì source fields đã được đặt bằng donor; không chứng minh hai giá trị đó là raw upstream bytes.

Audit đã kiểm độc lập và xác nhận case này **chỉ khác dòng rỗng**. Đây là bằng chứng mapping tốt, không phải bằng chứng exact-byte match. Tuy nhiên chưa thấy quyết định governance riêng chốt phép mapping này như yêu cầu audit trước.

**Cần làm:** ghi decision mapping cụ thể, trước inference, phân biệt source raw với donor dùng trong demo; lưu raw file/extraction hashes, donor hashes, phép biến đổi “bỏ dòng hoàn toàn rỗng” và kết quả đối chiếu. Không dùng `.split()` như bằng chứng lexical/semantic equivalence chung cho C/C++; nó không phải tokenizer ngôn ngữ và có thể làm mất khác biệt quan trọng trong trường hợp khác. Không sửa frozen donor bank.

Ràng buộc phần bằng chứng mapping vào **payload được review** hoặc một evidence-manifest hash trong payload, để không thể thay sidecar/raw evidence sau khi ký mà review vẫn còn hiệu lực. Mọi thay đổi payload phải tính canonical hash mới và phát lại packet/form. Đây là việc cần làm **trước review cuối**, không tự nới quy tắc validator hiện tại.

### 2. Sửa rationale cho đúng phạm vi chứng cứ và demo

Rationale hiện khẳng định “signed 32-bit integer overflow”, “invalid bitstream reads” và “memory corruption”. Source caller khai báo `unsigned size`; thay đổi vừa liên quan phép nhân, vừa chuyển kiểu đối số. Chỉ từ hồ sơ hiện tại chưa đủ quy kết toàn bộ thành signed 32-bit overflow hoặc khẳng định memory corruption. Commit message hỗ trợ trực tiếp integer overflow dẫn tới excessive memory allocation.

**Cần làm:** mô tả chắc chắn theo chứng cứ: bản vá sửa xử lý độ rộng số nguyên trong kiểm tra số bit, thay kiểu tham số và mở rộng biểu thức nhân ở caller, nhằm tránh excessive memory allocation theo commit. Nếu muốn kết luận tác động mạnh hơn, cần nguồn/bằng chứng bổ sung; không bắt buộc viết PoC hay build FFmpeg để chỉ trình bày phạm vi đã được chứng minh.

Phải ghi rõ **demo pair chỉ thể hiện thay kiểu tham số**, còn `size * 34L` nằm ở hàm `unpack_codebook` ngoài hai donor đang hiển thị. Hai reviewer cần xem cả actual diff/source context; không mô tả demo như đã chứa toàn bộ security fix. Mức phù hợp làm contrastive demonstration phải do hai reviewer thực sự đánh giá.

### 3. Đóng hồ sơ G1 trước khi gọi là verified hoàn toàn

Builder có các status/count và explanations hardcode theo case, không có assertion buộc normalized match phải true trước khi ghi `G1_VERIFIED_CANDIDATE_DOCUMENTED`. Audit này đã kiểm lại và mapping thực tế đúng; nhưng report do builder tự sinh không thay kết quả đối chiếu đó.

**Cần làm:** lần phát hành dossier tiếp theo có evidence manifest tính hash cho API response/raw files/extractions/diff/candidate/packet và builder; lưu URL/revision, thời gian, fetch/cache cho mỗi nguồn. Thêm điều kiện mapping/patch/hash thực vào verdict, không chỉ gán status theo case ID. Dùng folder/version mới để giữ dossier hiện tại làm lịch sử.

Chỉ cần kiểm targeted việc mapping và payload/evidence binding sau sửa; không cần chạy lại liên tục cả audit hoặc tái tải các source bytes không thay đổi. Sau khi code ổn định và phát hành release chính thức, thực hiện các bộ kiểm tra bắt buộc theo quy trình repo.

## Quyết định chuyển bước

| Cổng/công việc | Quyết định lần này |
|---|---|
| Điều tra source Devign | Có tiến bộ thực: một upstream fix/parent và mapping case 08 đã được audit xác nhận |
| G1 tuyệt đối theo report hiện tại | Chưa ký nhận vô điều kiện: còn decision mapping, rationale và binding evidence |
| Chuẩn bị/trao đổi review sơ bộ | **Được tiếp tục ngay**, gửi cả raw sources, actual diff và phần khác định dạng; không chỉ gửi template |
| Hai review cuối trên payload khóa | Sau khi hoàn thiện ba mục trên; hai người duyệt độc lập, không sinh approve giả |
| G2 ACTIVE pool | Chưa; chỉ sau hai review hợp lệ và pool release được kiểm |
| REVEAL | Vẫn UNRESOLVED. Kiểm kê raw export không phải đã khôi phục mapping nguồn; không suy “không thể tìm được” từ thiếu metadata nội bộ |
| G3/G4/full validation GPU | Chưa; cần pool đạt, full prompt census và runtime acceptance theo kế hoạch |

**Bước tiếp theo cụ thể:** hoàn thiện quyết định mapping + rationale/evidence binding cho chính case 08, rồi phát packet cuối cho hai reviewer. Không cần tìm thêm hàng loạt candidate hay chạy thêm GPU để giải quyết ba việc này. Sau review thật mới nghiệm thu G2; nếu chỉ Devign sẵn sàng, triển khai riêng cần ghi phạm vi bằng văn bản, REVEAL vẫn BLOCKED.

## Bằng chứng kiểm lại

- [Đối chiếu local dossier, patch và bank](dossier_checks.json).
- [Đối chiếu upstream HTTPS](upstream_readback.json); responses tại `upstream_readback/`.
- [43 tests độc lập](pytest.log), [runner result](pytest_result.json).
- [Inventory trước kiểm tra](source_inventory.json), [kết luận/bảo toàn cuối](readiness.json).

Audit chỉ tạo file trong thư mục audit mới; không ký review thay người thật, không nạp pool và không sửa threshold/runtime/Kaggle.
