# IoT-output-foreach-mongodb

## 🚀 Giới thiệu  
Project này mô phỏng hệ thống IoT sử dụng **Apache Spark Streaming** để xử lý dữ liệu cảm biến theo thời gian thực.  
Nguồn dữ liệu được giả lập qua **socket server** (`socket_sensor.py`) đọc từ file log, gửi từng dòng vào Spark Streaming (`main.py`) để xử lý, phân tích và lưu vào **MongoDB**.  

---

## 🔹 Yêu cầu
- Git
- Docker & Docker Compose
- MongoDB Compass (tùy chọn để kiểm tra dữ liệu)  
  👉 [Tải MongoDB Compass](https://downloads.mongodb.com/compass/mongodb-compass-1.46.10-win32-x64.exe)

### Kết nối MongoDB Compass
- Host: `mongodb://localhost:27017`
- Database mặc định: `iotdb`


<img src="https://github.com/user-attachments/assets/d2af6b60-eb15-4de5-b0b9-42f8a4ad64c5" alt="Mongo Compass Connect" width="300" />

<img src="https://github.com/user-attachments/assets/51feea76-2bcc-4825-b82a-d3c4a056de9f" alt="Mongo Compass Collections" width="960" />



---

## 📥 Clone project
```bash
git clone https://github.com/duonghieu7104/IoT-output-foreach-mongodb.git
cd IoT-output-foreach-mongodb
```
<img width="1222" height="111" alt="image" src="https://github.com/user-attachments/assets/c7ffa86c-f826-454f-bbbe-2ca37957e293" />

## 🔹 Demo – Gas Sensor (Cảm biến khí Gas)  

### Mô tả  
- Giả lập 1 cảm biến khí gas.  
- Nếu nồng độ khí vượt ngưỡng an toàn → tạo cảnh báo.  
- Spark Streaming dùng `foreachRDD` để ghi dữ liệu và cảnh báo vào MongoDB.  

### Chạy thử  
Mở 1 terminal chạy socket server (giả lập log gas sensor)
```bash
docker exec -it spark-master-v3 spark-submit /app/demo/socket_sensor.py     
```
<img width="1039" height="116" alt="image" src="https://github.com/user-attachments/assets/b934c3b6-365a-439c-aa2c-7cecd1852c1c" />


Mở terminal khác chạy Spark Streaming xử lý log
```bash
docker exec -it spark-master-v3 spark-submit /app/demo/main.py     
```
<img width="986" height="265" alt="image" src="https://github.com/user-attachments/assets/a9eeb9fd-2ea8-448f-9bfc-6f64e082f980" />

Kiểm tra trong MongoDB

<img width="302" height="319" alt="image" src="https://github.com/user-attachments/assets/d1aebd9f-f3af-4288-b80a-0619513d84ae" />

2 collection `0_gas_sensor_logs` và `0_gas_sensor_arlerts`

<img width="290" height="175" alt="image" src="https://github.com/user-attachments/assets/42f0e316-216e-4d30-9c76-d9be76532d6f" />

<img width="1092" height="363" alt="image" src="https://github.com/user-attachments/assets/0443f4f0-2e6d-418a-8b05-fac08a4e4c64" />

<img width="1088" height="369" alt="image" src="https://github.com/user-attachments/assets/e6ddac2a-b8a4-4776-9cbc-4ab450750e4b" />


## 🔹 Bài tập – 100 cảm biến khí gas  
