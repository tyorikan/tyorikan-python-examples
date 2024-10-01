FROM python:3.12-slim

WORKDIR /usr/src/app

# Oracle Instant Clientのダウンロードとインストール
RUN apt-get update && \
    apt-get install -y wget libaio1 unzip && \
    wget https://download.oracle.com/otn_software/linux/instantclient/2111000/instantclient-basic-linux.x64-21.11.0.0.0dbru.zip && \
    mkdir -p /opt/oracle && \
    unzip instantclient-basic-linux.x64-21.11.0.0.0dbru.zip -d /opt/oracle && \
    rm instantclient-basic-linux.x64-21.11.0.0.0dbru.zip && \
    cd /opt/oracle/instantclient_21_11 && \
    ln -sf libclntsh.so.21.1 libclntsh.so

# 環境変数の設定
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_11

# アプリケーションのインストールと設定
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]