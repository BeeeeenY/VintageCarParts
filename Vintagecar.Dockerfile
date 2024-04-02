FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
COPY templates /usr/src/app/templates
COPY static /usr/src/app/static
RUN pip install --no-cache-dir -r requirements.txt
COPY ./serviceAccountKey.json ./
COPY ./Vintagecar.py .
CMD ["python", "Vintagecar.py"]