FROM python:3

# 開発用環境のためバージョン固定を行わない
# hadolint ignore=DL3013
RUN pip install --no-cache-dir ansible

CMD [ "echo", "hoge" ]