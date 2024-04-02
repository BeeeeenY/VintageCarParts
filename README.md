# VintageCarParts

## Table of Contents

- [Introduction](#introduction)
- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)

##### Introduction
The project consists of multiple microservices, each encapsulated within a Docker container. These microservices include:

Vintagecar: Description of the Vintagecar microservice.
Users: Description of the Users microservice.
Logintemplate: Description of the Logintemplate microservice.
Order: Description of the Order microservice.
Createpart: Description of the Createpart microservice.
Forum: Description of the Forum microservice.
Chat: Description of the Chat microservice.
Shipping: Description of the Shipping microservice.
Car: Description of the Car microservice.
Payment: Description of the Payment microservice.

##### Setup
###### Prerequisites
Before getting started, ensure you have the following installed:

Docker  
Docker Compose

###### Installation
Upload the required **databases** into your local environment.

To set up the required databases and tables, follow these steps:

Connect to your MySQL database server.

Create the following databases:

* Products
* Users
* Authentication
* Orders
* Payment
* Forum

Execute the SQL commands provided in the Database SQL Commands section below for each database.

Update the dbURL environment variable in the docker-compose.yml file according to your database setup:
- **For macOS:** mysql+mysqlconnector://root:root@host.docker.internal:8889/orders
- **For Windows:** mysql+mysqlconnector://root@host.docker.internal:3306/orders
Change the image names to your own Docker username in the docker-compose.yml file.

###### Usage
To build and run the microservices, use the following commands:

docker-compose build  
docker-compose up
