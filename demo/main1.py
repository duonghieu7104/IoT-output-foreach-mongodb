from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pymongo import MongoClient
import os, atexit
from datetime import datetime

# ========================
# Cấu hình MongoDB
# ========================
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = "iotdb"
COL_LOGS = "0_gas_sensor_logs"
COL_ALERTS = "0_gas_sensor_alerts"

# ========================
# ANSI Colors
# ========================
BLUE = "\033[36m"   
GREEN = "\033[32m"  
PINK = "\033[95m"   
YELLOW = "\033[33m"  
RED = "\033[31m"
RESET = "\033[0m"

# ========================
# Global Mongo Client (per worker)
# ========================
_mongo_client = None

def get_mongo_client():
    """
    Singleton MongoClient trên mỗi worker node.
    Pymongo tự quản lý connection pool bên trong.
    """
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGO_URI, maxPoolSize=50)
        print(f"{BLUE}MongoClient initialized with pool (max 50){RESET}")
        # Đảm bảo cleanup khi worker shutdown
        atexit.register(lambda: _mongo_client.close())
    return _mongo_client


def save_partition(iterable, collection_name, db_name=DB_NAME):
    """
    Lưu records trong mỗi partition vào MongoDB,
    tái sử dụng connection pool thay vì mở/đóng liên tục.
    """
    client = get_mongo_client()
    db = client[db_name]
    collection = db[collection_name]

    buffer = list(iterable)
    if buffer:
        collection.insert_many(buffer)
        if collection_name == COL_LOGS:
            print(f"{GREEN}Saved {len(buffer)} records to {db_name}.{collection_name}{RESET}")
        elif collection_name == COL_ALERTS:
            print(f"{PINK}Saved {len(buffer)} records to {db_name}.{collection_name}{RESET}")
    else:
        print(f"{YELLOW}Empty partition, nothing to save for {collection_name}.{RESET}")


def process_rdd(rdd):
    if rdd.isEmpty():
        print(f"{YELLOW}Received empty RDD batch{RESET}")
        return

    def parse_line(line):
        try:
            parts = line.strip().split(",")
            if len(parts) < 3:
                return None, None

            sensor_id = parts[0]
            digital = int(parts[1])
            analog = float(parts[2])

            log_record = {
                "sensor": sensor_id,
                "digital": digital,
                "analog": analog,
                "status": "N/A",
                "timestamp": datetime.utcnow()
            }

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
            print(f"{YELLOW}Skipping line due to error: {line} | {e}{RESET}")
            return None, None

    parsed = rdd.map(parse_line).filter(lambda x: x is not None)

    logs = parsed.map(lambda x: x[0]).filter(lambda x: x is not None)
    alerts = parsed.map(lambda x: x[1]).filter(lambda x: x is not None)

    logs.foreachPartition(lambda it: save_partition(it, COL_LOGS))
    alerts.foreachPartition(lambda it: save_partition(it, COL_ALERTS))


if __name__ == "__main__":
    sc = SparkContext("local[2]", "IoTStreamApp")
    sc.setLogLevel("ERROR")
    ssc = StreamingContext(sc, 2)

    lines = ssc.socketTextStream("localhost", 9998)
    lines.foreachRDD(process_rdd)

    print(f"{BLUE}Spark Streaming started, listening on localhost:9998{RESET}")
    ssc.start()
    ssc.awaitTermination()
