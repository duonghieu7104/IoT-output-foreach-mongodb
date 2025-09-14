FROM bitnami/spark:3.5.0

USER root
# Cài thêm các thư viện Python cần thiết
RUN pip install --no-cache-dir pymongo findspark
USER 1001
