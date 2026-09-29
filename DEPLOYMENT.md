# Thông Tin Deploy — Checkpoint 5

> Điền file này sau khi deploy xong. `pytest tests/test_cp5.py` đọc file này
> để tìm địa chỉ service của bạn và gọi thử.
>
> **Chỉ ghi TÊN biến môi trường, tuyệt đối không dán giá trị API key vào đây.**
> Repo này công khai — dán khóa vào là mất khóa.

## Thông Tin Học Viên

| Mục | Nội dung |
|-----|----------|
| Họ và tên | Đinh Hoàng Đức |
| Mã học viên | 2A202602795 |
| Repo | https://github.com/ducdh205/K4-L3B-DAY12-DinhHoangDuc-2A202602795-CloudServicesAndDeployment.git |

## Service

| Mục | Nội dung |
|-----|----------|
| Public URL | https://k4-l3b-day12-dinhhoangduc-2a202602795-cloudservi-production.up.railway.app |
| Platform | Railway / Render / Cloud Run — Railway |
| Ngày deploy | 29/09/2026 |

## Biến Môi Trường Đã Set Trên Cloud

Ghi tên biến và **nguồn giá trị**, không ghi giá trị:

| Biến | Đã set | Ghi chú |
|------|--------|---------|
| `PORT` | ✅ | platform tự gán |
| `AGENT_API_KEY` | ✅ | đặt trong dashboard, không nằm trong repo |
| `REDIS_URL` | ✅ | redis://default:pgHmtmoujUfcUdNyLbBSfSYiOyzUKpig@redis.railway.internal:6379 |
| `RATE_LIMIT_PER_MINUTE` | ✅ | 10 |
| `MONTHLY_BUDGET_USD` | ✅ | 10.0 |
| `LOG_LEVEL` | ✅ | INFO |

## Lệnh Kiểm Tra

```bash
# 1. Liveness — mong đợi 200 {"status":"ok"}
curl -i https://k4-l3b-day12-dinhhoangduc-2a202602795-cloudservi-production.up.railway.app/health

# 2. Readiness — mong đợi 200 {"status":"ready"} (đã nối được Redis)
curl -i https://k4-l3b-day12-dinhhoangduc-2a202602795-cloudservi-production.up.railway.app/ready

# 3. Không có API key — mong đợi 401
curl -i -X POST https://k4-l3b-day12-dinhhoangduc-2a202602795-cloudservi-production.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'

# 4. Có API key — mong đợi 200 kèm câu trả lời
curl -i -X POST https://k4-l3b-day12-dinhhoangduc-2a202602795-cloudservi-production.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AGENT_API_KEY" \
  -H "X-User-Id: sv-test" \
  -d '{"question":"Deploy là gì?"}'

# 5. Rate limit — gọi 15 lần, những lần cuối phải trả 429
for i in $(seq 1 15); do
  curl -s -o /dev/null -w "%{http_code} " -X POST https://k4-l3b-day12-dinhhoangduc-2a202602795-cloudservi-production.up.railway.app/ask \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $AGENT_API_KEY" \
    -H "X-User-Id: sv-test" \
    -d '{"question":"test"}'
done; echo
```

## Kết Quả Chạy Thật

Dán output của các lệnh trên vào đây:
```bash
# 1. Liveness — mong đợi 200 {"status":"ok"}
curl -i https://k4-l3b-day12-dinhhoangduc-2a202602795-cloudservi-production.up.railway.app/health

HTTP/2 200 
content-type: application/json
date: Tue, 29 Sep 2026 08:27:24 GMT
server: railway-hikari
x-railway-request-id: Nr26VPD3T5eFkhfUAXC71g
content-length: 15
x-hikari-trace: sin1.tr00
x-railway-edge: sin1

{"status":"ok"}%     

# 2. Readiness — mong đợi 200 {"status":"ready"} (đã nối được Redis)
curl -i https://k4-l3b-day12-dinhhoangduc-2a202602795-cloudservi-production.up.railway.app/ready

HTTP/2 200 
content-type: application/json
date: Tue, 29 Sep 2026 09:50:14 GMT
server: railway-hikari
x-railway-request-id: 2sCRUrsgQpCfXZprAQeqjw
content-length: 18
x-hikari-trace: sin1.tr00
x-railway-edge: sin1

{"status":"ready"}%   


# 3. Không có API key — mong đợi 401
curl -i -X POST https://k4-l3b-day12-dinhhoangduc-2a202602795-cloudservi-production.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'

HTTP/2 401 
content-type: application/json
date: Tue, 29 Sep 2026 09:50:35 GMT
server: railway-hikari
x-railway-request-id: VyJKc4HJS9O6vamnmrpb1w
content-length: 39
x-hikari-trace: sin1.hs0s
x-railway-edge: sin1

{"detail":"Invalid or missing API key"}%      

# 4. Có API key — mong đợi 200 kèm câu trả lời
curl -i -X POST https://k4-l3b-day12-dinhhoangduc-2a202602795-cloudservi-production.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AGENT_API_KEY" \
  -H "X-User-Id: sv-test" \
  -d '{"question":"Deploy là gì?"}'

  HTTP/2 200 
content-type: application/json
date: Tue, 29 Sep 2026 09:51:13 GMT
server: railway-hikari
x-railway-request-id: pNmGzieOR8eOOcncipRofQ
content-length: 108
x-hikari-trace: sin1.tr00
x-railway-edge: sin1

{"answer":"Mock answer: Deploy là gì?","user_id":"sv-test","history_length":0,"cost_usd":0.001,"tokens":3}%      

# 5. Rate limit — gọi 15 lần, những lần cuối phải trả 429
for i in $(seq 1 15); do
  curl -s -o /dev/null -w "%{http_code} " -X POST https://k4-l3b-day12-dinhhoangduc-2a202602795-cloudservi-production.up.railway.app/ask \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $AGENT_API_KEY" \
    -H "X-User-Id: sv-test" \
    -d '{"question":"test"}'
done; echo

200 200 200 200 200 200 200 200 200 200 429 429 429 429 429 

```
## Ảnh Chụp Màn Hình

Đặt ảnh trong thư mục `screenshots/`:

- `screenshots/dashboard.png` — trang quản lý service trên platform

- `screenshots/health.png` — kết quả gọi `/health` từ trình duyệt hoặc curl

