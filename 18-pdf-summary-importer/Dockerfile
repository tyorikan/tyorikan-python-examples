# 1. ベースイメージの指定
FROM python:3.13-slim

# 2. 環境変数の設定
# PORTはCloud Runによって提供される
ENV PYTHONUNBUFFERED=1 
ENV APP_HOME=/app

# 3. 作業ディレクトリの作成と設定
WORKDIR $APP_HOME

# 4. uvのインストール
RUN pip install uv

# 5. 依存関係ファイルのコピー
COPY pyproject.toml uv.lock ./

# 6. 依存関係のインストール
RUN uv sync

# 7. アプリケーションコードのコピー
COPY . .

# 8. コンテナ起動コマンド
EXPOSE 8080
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
