# Phiếu Phản Ánh — K4 Level 3B, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng `> *Câu trả lời của bạn*` bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Đinh Hoàng Đức  Mã học viên: 2A202602795

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Khi deploy lên Railway mà quên đặt `AGENT_API_KEY`, app sẽ dừng ngay lúc khởi động. Nhờ vậy em biết thiếu cấu hình và không có API nào mở ra. Nếu để mặc định `changeme`, app vẫn chạy nhưng người khác có thể đoán key này, gọi `/ask` và dùng hết quota hoặc gây chi phí.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> `{"event":"ask_completed","level":"info","timestamp":"2026-09-29T09:51:13+00:00","user_id":"sv-test","cost_usd":0.001,"tokens":3}`. Em có thể lọc tất cả request của `sv-test` để xem người đó dùng bao nhiêu tiền. Em cũng có thể đếm tổng token hoặc tổng chi phí theo thời gian để làm dashboard/cảnh báo. `print("đã trả lời xong")` không có thời gian, user hay số liệu để máy phân tích.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | Chưa đo được: Docker Engine đang tắt |
| Multi-stage | Chưa đo được: Docker Engine đang tắt |

Giải thích: phần dung lượng chênh lệch đó là những gì?

> Lúc kiểm tra, Docker Desktop chưa chạy nên lệnh build không kết nối được Docker Engine và em chưa ghi được số MB thật. Bản một stage chứa cả base `python:3.11`, source, dependency và các file trong build context. Bản multi-stage chỉ lấy dependency đã cài cùng `app` và `utils` vào `python:3.12-slim`, nên bỏ được nhiều file build thừa. Em sẽ chạy lại hai lệnh khi bật Docker để điền số đo.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> Khi chỉ sửa `app/main.py`, layer `FROM`, `WORKDIR`, `COPY requirements.txt` và `RUN pip install` được lấy từ cache vì `requirements.txt` không đổi. Layer `COPY app ./app` và các layer sau nó chạy lại. Nếu đặt `COPY . .` trước `RUN pip install`, chỉ một ký tự đổi trong source cũng làm layer copy đổi, nên Docker phải cài lại toàn bộ thư viện: build chậm hơn.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> Một lỗ hổng có thể cho kẻ xấu chạy lệnh trong container. Nếu container chạy root và còn có cấu hình nguy hiểm như privileged, mount Docker socket hoặc có lỗi thoát container, họ có thể leo sang host với quyền cao. `USER appuser` làm tiến trình Python chỉ là user thường, nên khó đọc/ghi file hệ thống hoặc cài công cụ trong container hơn. Nó giảm hậu quả, nhưng vẫn cần tránh cấu hình privileged.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> Tối đa là 20 request trong 2 giây. Người dùng gửi 10 request ở giây 59 của một phút, rồi gửi thêm 10 request ở giây 00 của phút kế tiếp. Bộ đếm theo phút đồng hồ reset đúng lúc đổi phút nên cho qua cả hai đợt. Sliding window nhìn lại đủ 60 giây trước đó nên vẫn thấy 10 request cũ và chặn đợt thứ hai.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> Rate limit giới hạn số lần gọi trong 60 giây; cost guard giới hạn tiền ước tính của từng user trong cả tháng. Ví dụ user chỉ gọi một lần trong phút nhưng đã gần hết ngân sách tháng: rate limit cho qua, còn cost guard trả 402. Ngược lại, user mới nên chưa tốn gần gì nhưng gửi request thứ 11 trong 60 giây: cost guard còn cho, rate limit trả 429.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> Redis mất kết nối. Endpoint chung của cả 3 container kiểm tra Redis nên lần health check tiếp theo đều trả 503. Platform đánh dấu container không healthy và có thể lần lượt restart hoặc bỏ chúng khỏi traffic. Trong 30 giây Redis vẫn lỗi, các container tiếp tục không healthy nên request bị gián đoạn. Khi Redis sống lại, health check mới 200 và container mới nhận traffic. Tách `/health` giúp tránh restart vì lỗi dependency.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> Với Redis, `history_length` tăng chung dù request đi vào container nào: thường là 0, rồi 2, 4, ... vì mỗi lần `/ask` lưu hai message. Lịch sử còn bị giới hạn 20 message. Nếu dùng dict Python, mỗi container có một dict riêng. Load balancer đổi container thì số này không tăng đều, có thể quay lại 0 hoặc 2; user sẽ có cảm giác app quên lịch sử.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> Khi deploy Railway, em từng thấy `/ready` trả `503 Service Unavailable`. Em kiểm tra bằng curl và biết `/health` vẫn trả 200, nên app còn sống nhưng không sẵn sàng. Sau đó em kiểm tra biến môi trường trên Railway và phát hiện `REDIS_URL` chưa đúng/chưa nối được Redis. Em gắn lại URL Redis nội bộ trong dashboard, redeploy, rồi `/ready` trả `200 {"status":"ready"}`.
