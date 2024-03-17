FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY templates /usr/src/app/templates
COPY static /usr/src/app/static
COPY ./serviceAccountKey.json ./
COPY logintemplate.py ./
EXPOSE 5001
CMD ["python", "logintemplate.py"]