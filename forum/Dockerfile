FROM python:3-slim
WORKDIR /usr/src/app
COPY forum/requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY forum/forum.py .
CMD [ "python", "./forum.py" ]

