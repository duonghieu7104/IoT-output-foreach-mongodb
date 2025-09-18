# IoT-output-foreach-mongodb

## 🚀 Giới thiệu  

Project này mô phỏng hệ thống IoT sử dụng **Apache Spark Streaming** để xử lý dữ liệu cảm biến theo thời gian thực.  
Nguồn dữ liệu được giả lập qua **socket server** (`socket_sensor.py`) đọc từ file log, gửi từng dòng vào Spark Streaming (`main.py`) để xử lý, phân tích và lưu vào **MongoDB**.  


# 📑 Mục lục

- [📋 Cấu trúc Project](#-cấu-trúc-project)
- [🔹 Yêu cầu](#-yêu-cầu)
- [📥 Clone project](#-clone-project)
- [🔹 Demo – Gas Sensor](#-demo--gas-sensor-cảm-biến-khí-gas)
  - [Mô tả](#mô-tả)
  - [Chạy thử](#chạy-thử)
- [🔹 Bài tập IoT Gas Sensor Streaming với Spark và MongoDB](#-bài-tập-iot-gas-sensor-streaming-với-spark-và-mongodb)
  - [📋 Mô tả tổng quan](#-mô-tả-tổng-quan)
  - [📡 Dữ liệu đầu vào](#-dữ-liệu-đầu-vào)
  - [🎯 Yêu cầu chức năng](#-yêu-cầu-chức-năng)
  - [Cấu trúc dữ liệu output trong MongoDB](#cấu-trúc-dữ-liệu-output-trong-mongodb)
  - [Kết quả mong đợi](#kết-quả-mong-đợi)
  - [Truy vấn avg sau 1 phút](#truy-vấn-avg-sau-1-phút)



## 📋 Cấu trúc Project

```
IoT-output-foreach-mongodb/
├── demo/
│   ├── socket_sensor.py    # Socket server giả lập dữ liệu
│   └── main.py            # Spark Streaming application
├── ex/
│   ├── socket_sensor.py    # Socket server giả lập dữ liệu
│   └── main.py            # Bài tập cần hoàn thiện
├── logs/                  # Chứa các file logs.txt 
│   ├── 0_gas_sensor_log.txt
│   └── 100_gas_sensor_log.txt
├── docker-compose.yml      # Docker configuration
├── mongo-init.js
├── spark.Dockerfile
└── README.md              # Documentation
```


---

## 🔹 Yêu cầu

* **Git** (clone project)
* **Docker & Docker Compose** (chạy Spark + MongoDB qua `docker-compose.yml`)
* **MongoDB Shell (`mongosh`)** hoặc **MongoDB Compass** (tùy chọn) để kiểm tra dữ liệu:
  > MongoDB Compass: [Tải MongoDB Compass](https://downloads.mongodb.com/compass/mongodb-compass-1.46.10-win32-x64.exe)

---


## 📥 Clone project

```bash
git clone https://github.com/duonghieu7104/IoT-output-foreach-mongodb.git
cd IoT-output-foreach-mongodb
docker-compose up -d
```

![Clone Project](https://github.com/user-attachments/assets/c7ffa86c-f826-454f-bbbe-2ca37957e293)

---

## 🔹 Demo – Gas Sensor (Cảm biến khí Gas)  

### Mô tả  

- Giả lập 1 cảm biến khí gas  
- Nếu nồng độ khí vượt ngưỡng an toàn → tạo cảnh báo  
- Spark Streaming dùng `foreachRDD` để ghi dữ liệu và cảnh báo vào MongoDB  

### Chạy thử  

**Bước 1:** Mở 1 terminal chạy socket server (giả lập log gas sensor)

```bash
docker exec -it spark-master-v3 spark-submit /app/demo/socket_sensor.py     
```

![Socket Server](https://github.com/user-attachments/assets/c5dfa058-1409-4230-8296-a6195a6cc993)

**Bước 2:** Mở terminal khác chạy Spark Streaming xử lý log

```bash
docker exec -it spark-master-v3 spark-submit /app/demo/main.py     
```

![Spark Streaming](https://github.com/user-attachments/assets/5dfa3c88-339c-4e6c-8765-5be3dc4380d3)

**Bước 3:** Kiểm tra trong MongoDB

**Kết nối MongoDB Compass**

- **Host:** `mongodb://localhost:27017`
- **Database mặc định:** `iotdb`

![MongoDB Check](https://github.com/user-attachments/assets/d1aebd9f-f3af-4288-b80a-0619513d84ae)

Sẽ có 2 collection: `0_gas_sensor_logs` và `0_gas_sensor_alerts`

![Collections Overview](https://github.com/user-attachments/assets/42f0e316-216e-4d30-9c76-d9be76532d6f)

**Collection `0_gas_sensor_logs`:**
![Gas Sensor Logs](https://github.com/user-attachments/assets/0443f4f0-2e6d-418a-8b05-fac08a4e4c64)

**Collection `0_gas_sensor_alerts`:**
![Gas Sensor Alerts](https://github.com/user-attachments/assets/e6ddac2a-b8a4-4776-9cbc-4ab450750e4b)

---

# 🔹 Bài tập IoT Gas Sensor Streaming với Spark và MongoDB (hoàn thành code trong `ex`)

## 📋 Mô tả tổng quan
Xây dựng hệ thống giám sát real-time cho 100 cảm biến khí gas sử dụng Apache Spark Streaming và MongoDB. Hệ thống cần có khả năng:
- Thu thập dữ liệu streaming từ các cảm biến
- Phát hiện và cảnh báo tự động khi nồng độ khí vượt ngưỡng
- Lưu trữ dữ liệu và tính toán thống kê theo thời gian thực

## 📡 Dữ liệu đầu vào
File `socket_sensor.py` sẽ gửi dữ liệu qua **port 9998** với format:
```
2025-09-13 13:45:05, sensor=1, gas_level=7.75, status=ALERT
2025-09-13 13:45:05, sensor=2, gas_level=4.36, status=NORMAL
2025-09-13 13:45:05, sensor=3, gas_level=6.33, status=NORMAL
... (100 cảm biến)
```

### Format dữ liệu chi tiết:
- **Timestamp**: `YYYY-MM-DD HH:MM:SS`
- **Sensor ID**: `sensor=<ID>` (1-100)
- **Gas Level**: `gas_level=<float>` (nồng độ khí)
- **Status**: `status=<NORMAL|ALERT>`

## 🎯 Yêu cầu chức năng

### 1. Thu thập và lưu trữ dữ liệu logs
- Sử dụng Spark Streaming để nhận data từ socket (localhost:9998)
- Parse dữ liệu từ format text thành cấu trúc JSON
- Ghi tất cả logs vào MongoDB collection: `100_gas_sensor_logs`
- Sử dụng `foreachRDD` để xử lý batch data

### 2. Phát hiện và cảnh báo ngưỡng an toàn
- **Ngưỡng cảnh báo**: `gas_level > 7.0`
- Tự động tạo bản ghi cảnh báo khi phát hiện vượt ngưỡng
- Lưu cảnh báo vào collection riêng: `100_gas_sensor_alerts`
- Thông tin cảnh báo bao gồm: sensor_id, gas_level, message, timestamp

### 3. Tính toán giá trị trung bình theo cửa sổ thời gian
- **Window**: 60 giây (window duration)
- **Slide interval**: 30 giây (sliding interval)
- Tính average gas_level cho mỗi sensor theo window
- Lưu kết quả vào collection: `100_gas_sensor_avg`

### 4. Lưu trữ MongoDB
- **Database**: `iotdb`
- **Collections**:
  - `100_gas_sensor_logs`: Raw sensor data
  - `100_gas_sensor_alerts`: Alert records  
  - `100_gas_sensor_avg`: Windowed averages
- Sử dụng `replace_one` với `upsert=True` để tránh duplicate


### Data Processing Pipeline:
1. **Stream Input** → Parse text lines
2. **Data Validation** → Filter invalid records  
3. **Alert Detection** → Check gas_level threshold
4. **Parallel Write** → Logs + Alerts to MongoDB
5. **Window Calculation** → Average computation
6. **Result Storage** → Save averages to MongoDB

## Cấu trúc dữ liệu output trong MongoDB

### Log Record:
```json
{
  "_id": "1_1757771105",
  "sensor": "1",
  "gas_level": 7.75,
  "status": "ALERT",
  "timestamp": {
    "$date": "2025-09-13T13:45:05.000Z"
  }
}
```

### Alert Record:
```json
{
  "_id": "1_1757771105_ALERT",
  "sensor": "1",
  "gas_level": 7.75,
  "alert": "High gas concentration",
  "timestamp": {
    "$date": "2025-09-13T13:45:05.000Z"
  }
}
```

### Average Record:
```json
{
  "_id": "5_1757848160_AVG",
  "sensor": "5",
  "avg_gas_level": 4.81,
  "timestamp": {
    "$date": "2025-09-14T11:09:20.684Z"
  },
  "window": "60s"
}
```
```bash
docker exec -it spark-master-v3 spark-submit /app/ex/socket_sensor.py
docker exec -it spark-master-v3 spark-submit /app/ex/main.py
```

### Kết quả mong đợi

**Dữ liệu từ 100 cảm biến:**
![100 Sensors Data](https://github.com/user-attachments/assets/2206eb9e-a9f5-4122-829b-ee6c9d34968e)

**Sau 1 phút sẽ tính trung bình và lưu vào `100_gas_sensors_avg`:**
![Average Data](https://github.com/user-attachments/assets/a34b1131-886b-49dd-aef1-89e9d936ec4f)

---

### Truy vấn avg sau 1 phút
#### Dùng MongoDB Shell


```bash
docker exec -it mongo-v3 mongosh
```
<img width="1052" height="255" alt="image" src="https://github.com/user-attachments/assets/e8a2aa01-c6a8-4fe3-81e2-3d4ee613ccee" />


```bash
use iotdb
db["100_gas_sensor_avg"].find({}).sort({ avg_gas_level: -1 }).limit(5)
```
<img width="751" height="487" alt="image" src="https://github.com/user-attachments/assets/d473e9f4-8c9c-4e43-82be-b51875b74289" />

#### Dùng MongoDB Compass

<img width="1099" height="253" alt="image" src="https://github.com/user-attachments/assets/e18f742c-a314-4951-a3e6-127f96a89391" />

Kết quả

<img width="1607" height="636" alt="image" src="https://github.com/user-attachments/assets/5132c78c-d45d-4ae2-b19b-015c949348b7" />



