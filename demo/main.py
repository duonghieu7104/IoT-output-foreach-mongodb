from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pymongo import MongoClient
import os
from datetime import datetime

# ========================
# Cấu hình MongoDB
# ========================
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = "iotdb"
COL_LOGS = "0_gas_sensor_logs"
COL_ALERTS = "0_gas_sensor_alerts"


def save_partition(iterable, collection_name, db_name=DB_NAME):
    """
    Lưu records trong mỗi partition vào MongoDB
    (đúng cách: kết nối được tạo bên trong worker).
    """
    client = MongoClient(MONGO_URI)
    db = client[db_name]
    collection = db[collection_name]

    buffer = list(iterable)
    if buffer:
        collection.insert_many(buffer)
        print(f"✅ Saved {len(buffer)} records to {db_name}.{collection_name}")
    else:
        print(f"⚠️ Empty partition, nothing to save for {collection_name}.")

    client.close()


def process_rdd(rdd):
    """
    Xử lý mỗi batch RDD từ DStream.
    """
    if rdd.isEmpty():
        print("⚠️ Received empty RDD batch")
        return

    def parse_line(line):
        try:
            parts = line.strip().split(",")
            if len(parts) < 3:
                return None, None

            sensor_id = parts[0]
            digital = int(parts[1])
            analog = float(parts[2])

            # record log bình thường
            log_record = {
                "sensor": sensor_id,
                "digital": digital,
                "analog": analog,
                "status": "N/A",
                "timestamp": datetime.utcnow()
            }

            # record alert nếu vượt ngưỡng
            alert_record = None
            if analog > 60:
                alert_record = {
                    "sensor": sensor_id,
                    "digital": digital,
                    "analog": analog,
                    "alert": "High gas concentration",
                    "timestamp": datetime.utcnow()
                }

            return log_record, alert_record
        except Exception as e:
            print(f"⚠️ Skipping line due to error: {line} | {e}")
            return None, None

    parsed = rdd.map(parse_line).filter(lambda x: x is not None)

    logs = parsed.map(lambda x: x[0]).filter(lambda x: x is not None)
    alerts = parsed.map(lambda x: x[1]).filter(lambda x: x is not None)

    logs.foreachPartition(lambda it: save_partition(it, COL_LOGS))
    alerts.foreachPartition(lambda it: save_partition(it, COL_ALERTS))


# ========================
# Main: Spark Streaming
# ========================
if __name__ == "__main__":
    sc = SparkContext("local[2]", "IoTStreamApp")
    sc.setLogLevel("ERROR")
    ssc = StreamingContext(sc, 2)

    # Nhận dữ liệu từ socket
    lines = ssc.socketTextStream("localhost", 9998)

    # Xử lý & lưu vào MongoDB
    lines.foreachRDD(process_rdd)

    print("📡 Spark Streaming started, listening on localhost:9998")
    ssc.start()
    ssc.awaitTermination()
