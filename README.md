# VintageCarParts

## Table of Contents

- [Introduction](#introduction)
- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)

##### Introduction
The project consists of multiple microservices, each encapsulated within a Docker container. These microservices include:

- **Vintagecar**: This microservice handles functionalities related to vintage cars. It may include features such as listing vintage cars for sale, providing details about vintage car models, and managing vintage car inventory.
- **Users**: The Users microservice manages user-related operations within the system. It handles user authentication and registration
- **Logintemplate**: The Logintemplate microservice provides authentication and login functionalities for users accessing the system. It manages user login sessions, verifies user credentials, and ensures secure access to the system.
- **Order**: The Order microservice facilitates order management functionalities. It allows users to place orders for products or services, view order history, track order statuses, and manage orders throughout the order lifecycle.
- **Createpart**: The Createpart microservice enables users to create and manage parts listings within the system. It provides functionalities for adding new parts, updating existing parts, and managing part inventory.
- **Forum**: The Forum microservice serves as a platform for users to engage in discussions, share information, and ask questions related to the system's domain. It manages forum posts and comment.
- **Chat**:  The Chat microservice facilitates real-time communication between users within the system. It provides chat functionalities -  one-on-one
- **Car**: The Car microservice deals with functionalities related to rental of modern cars. It may include features such as listing modern car models, providing details about car specifications, and managing modern car inventory.
- **Payment**: The Payment microservice manages payment processing functionalities within the system. It handles payment methods, transactions, payment gateway integrations, and ensures secure and reliable payment processing.

##### Setup
###### Prerequisites
Before getting started, ensure you have the following installed:

- Docker  
- Docker Compose

###### Installation
Upload the required **databases** into your local environment.

To set up the required databases and tables, follow these steps:

1. Connect to your MySQL database server.
2. Create the following databases:
   - Products: This database stores information related to products and parts. It may include details such as product names, descriptions, prices, quantities available, and other relevant attributes.
   - Users:  The Users database manages user information within the system. It typically includes details such as user names, contact information, age, country, and any other relevant user profile data.
   - Authentication:  The Authentication database handles user authentication and authorization. It stores user credentials, such as email addresses and hashed passwords, to ensure secure access to the system.
   - Orders: The Orders database tracks orders placed by users. It includes details such as order IDs, products ordered, quantities, prices, shipping information, and order statuses.
   - Payment: The Payment database manages payment-related information.
   - Forum: The Forum database stores posts, comments, and other discussion-related data, allowing users to engage in conversations, ask questions, and share knowledge within the system.

Execute the SQL commands provided in the Database SQL Commands section below for each database.

Update the dbURL environment variable in the `docker-compose.yml` file according to your database setup:
- **For macOS:** `mysql+mysqlconnector://root:root@host.docker.internal:8889/orders`
- **For Windows:** `mysql+mysqlconnector://root@host.docker.internal:3306/orders`

Change the image names to your own Docker username in the `docker-compose.yml` file.

###### Usage
To build and run the microservices, use the following commands:

```bash
docker-compose build
docker-compose up
