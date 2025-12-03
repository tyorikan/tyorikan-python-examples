## --no-build デプロイ
python-platform 指定しないと FastAPI 内で利用する pydantic_core でエラーになる  

`No module named 'pydantic_core._pydantic_core'`

```shell
$ uv pip install \
--target ./vendor \
--python-platform x86_64-unknown-linux-gnu \
--python-version 3.13 \
-r requirements.txt

$ time gcloud beta run deploy simple-fast-api \
--source . \
--region=asia-northeast1 \
--no-build \
--base-image=python313 \
--command=python \
--args=main.py \
--set-env-vars PYTHONPATH=./vendor

Deploying container to Cloud Run service [simple-fast-api] in project [your-gcp-project] region [asia-northeast1]
✓ Deploying... Done.
  ✓ Uploading sources...
  ✓ Creating Revision...
  ✓ Routing traffic...
Done.
Service [simple-fast-api] revision [simple-fast-api-00001-xxx] has been deployed and is serving 100 percent of traffic.
Service URL: https://simple-fast-api-123456789012.asia-northeast1.run.app
gcloud beta run deploy simple-fast-api --source . --region=asia-northeast1     12.51s user 0.97s system 34% cpu 39.483 total
```