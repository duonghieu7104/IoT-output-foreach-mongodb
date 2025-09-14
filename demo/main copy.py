from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pymongo import MongoClient
import os
from datetime import datetime

# ========================
# ❌ Cấu hình MongoDB (tạo ở driver)
# ========================
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
client = MongoClient(MONGO_URI)   # ❌ Sai: kết nối mở ở driver
db = client["iotdb"]
collection = db["gas_sensor"]


def process_rdd_wrong(rdd):
    """
    Sai: thu thập dữ liệu về driver và ghi vào MongoDB từ driver
    """
    if rdd.isEmpty():
        print("⚠️ Received empty RDD batch")
        return

    try:
        # ❌ collect() kéo toàn bộ data từ worker về driver
        lines = rdd.collect()

        records = []
        for line in lines:
            parts = line.strip().split(",")
            if len(parts) < 4:
                print(f"⚠️ Skipping line, unexpected columns: {line}")
                continue

            sensor_id = parts[0]
            digital = int(parts[1])
            analog = float(parts[2])
            status = parts[3]

            record = {
                "sensor": sensor_id,
                "digital": digital,
                "analog": analog,
                "status": status,
                "timestamp": datetime.utcnow()
            }
            records.append(record)

        if records:
            collection.insert_many(records)   # ❌ Ghi vào MongoDB từ driver
            print(f"✅ Saved {len(records)} records (but from driver only)")
    except Exception as e:
        print(f"❌ Error processing RDD: {e}")


# ========================
# Main: Spark Streaming
# ========================
if __name__ == "__main__":
    sc = SparkContext("local[2]", "IoTStreamApp_Wrong")
    sc.setLogLevel("ERROR")
    ssc = StreamingContext(sc, 2)  # batch interval = 2s

    # Nhận dữ liệu từ socket
    lines = ssc.socketTextStream("localhost", 9998)

    # Xử lý theo kiểu sai
    lines.foreachRDD(process_rdd_wrong)

    print("📡 Spark Streaming started (WRONG version), listening on localhost:9998")
    ssc.start()
    ssc.awaitTermination()
