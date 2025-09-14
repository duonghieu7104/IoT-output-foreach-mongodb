// Kết nối tới database "iotdb"
db = db.getSiblingDB("iotdb");

db.createCollection("logs");

db.createCollection("alerts");

db.alerts.insertOne({
    init: "MongoDB IoT Alerts Collection Ready",
    createdAt: new Date()
});
