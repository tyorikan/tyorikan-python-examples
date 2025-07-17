FROM python:3.12-slim

# システムパッケージのインストール（PyAudioビルドに必要）
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    make \
    libasound2-dev \
    portaudio19-dev \
    python3-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルのコピー
COPY . .

# 非rootユーザーの作成（セキュリティ向上）
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# 環境変数の設定
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Cloud Run のポート設定
ENV PORT=8080
EXPOSE 8080

# Web アプリケーション起動
CMD ["python", "app.py"]