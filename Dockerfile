
FROM python:3-slim-buster

# Set the working directory
WORKDIR /usr/src/

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev

# Copy the requirements file into the container at /usr/src/app
COPY requirements.txt ./

# Install any dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy all source code files into the container
COPY . .

# Set the entry point to the main Python file (e.g., app.py)
CMD ["python", "./Vintagecar.py"]
