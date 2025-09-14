from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pymongo import MongoClient
from datetime import datetime
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = "iotdb"
COL_LOGS = "100_gas_sensor_logs"
COL_ALERTS = "100_gas_sensor_alerts"
COL_AVG = "100_gas_sensor_avg"

def save_partition(iterable, collection_name, db_name=DB_NAME):
    client = MongoClient(MONGO_URI)
    db = client[db_name]
    collection = db[collection_name]
    buffer = list(iterable)
    if buffer:
        for doc in buffer:
            collection.replace_one({"_id": doc["_id"]}, doc, upsert=True)
        print(f"✅ Upserted {len(buffer)} → {collection_name}")
    client.close()

def process_rdd(rdd):
    if rdd.isEmpty():
        print("⚠️ Empty RDD batch")
        return

    def parse_line(line):
        try:
            parts = line.strip().split(",")
            ts_str = parts[0]
            sensor_id = parts[1].split("=")[1]
            gas_level = float(parts[2].split("=")[1])
            status = parts[3].split("=")[1]

            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")

            log_record = {
                "_id": f"{sensor_id}_{int(ts.timestamp())}",
                "sensor": sensor_id,
                "gas_level": gas_level,
                "status": status,
                "timestamp": ts
            }

            alert_record = None
            if gas_level > 7:
                alert_record = {
                    "_id": f"{sensor_id}_{int(ts.timestamp())}_ALERT",
                    "sensor": sensor_id,
                    "gas_level": gas_level,
                    "alert": "High gas concentration",
                    "timestamp": ts
                }

            return log_record, alert_record
        except:
            return None, None

    parsed = rdd.map(parse_line).filter(lambda x: x is not None)
    logs = parsed.map(lambda x: x[0]).filter(lambda x: x is not None)
    alerts = parsed.map(lambda x: x[1]).filter(lambda x: x is not None)

    logs.foreachPartition(lambda it: save_partition(it, COL_LOGS))
    alerts.foreachPartition(lambda it: save_partition(it, COL_ALERTS))

# Main Spark Streaming
if __name__ == "__main__":
    sc = SparkContext("local[2]", "IoTStreamApp")
    ssc = StreamingContext(sc, 2)
    ssc.checkpoint("./checkpoint_100_sensors")

    lines = ssc.socketTextStream("localhost", 9999)

    # Logs + alerts
    lines.foreachRDD(process_rdd)

    # Windowed average 60s sliding 30s
    def parse_for_avg(line):
        try:
            parts = line.strip().split(",")
            sensor_id = parts[1].split("=")[1]
            gas_level = float(parts[2].split("=")[1])
            return (sensor_id, (gas_level, 1))
        except:
            return None

    pairs = lines.map(parse_for_avg).filter(lambda x: x is not None)
    windowed = pairs.reduceByKeyAndWindow(
        lambda a,b: (a[0]+b[0], a[1]+b[1]),
        lambda a,b: (a[0]-b[0], a[1]-b[1]),
        60, 30
    )
    avg = windowed.mapValues(lambda v: round(v[0]/v[1],2) if v[1]>0 else 0)
    avg_records = avg.map(lambda kv: {
        "_id": f"{kv[0]}_{int(datetime.utcnow().timestamp())}_AVG",
        "sensor": kv[0],
        "avg_gas_level": kv[1],
        "timestamp": datetime.utcnow(),
        "window": "60s"
    })
    avg_records.foreachRDD(lambda rdd: rdd.foreachPartition(lambda it: save_partition(it, COL_AVG)))

    print("📡 Spark Streaming started for 100 sensors on localhost:9998")
    ssc.start()
    ssc.awaitTermination()
