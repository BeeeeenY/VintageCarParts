CREATE DATABASE IF NOT EXISTS `VintageCar` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `VintageCar`;

DROP TABLE IF EXISTS Comments;
DROP TABLE IF EXISTS Posts;
DROP TABLE IF EXISTS Profiles;
DROP TABLE IF EXISTS OrderDetails;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Parts;

CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Phone VARCHAR(20),
    Age INT
);

CREATE TABLE Parts (
    PartID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Category VARCHAR(255) NOT NULL,
    Description TEXT,
    Price DECIMAL(10, 2),
    QuantityAvailable INT,
    Location VARCHAR(255)
);

CREATE TABLE Orders (
    OrderID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    OrderDate DATETIME,
    Status VARCHAR(255),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE OrderDetails (
    OrderDetailID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT,
    PartID INT,
    Quantity INT,
    Price DECIMAL(10, 2),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (PartID) REFERENCES Parts(PartID)
);

CREATE TABLE Profiles (
    ProfileID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL UNIQUE,
    Bio TEXT,
    Interests TEXT,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE Posts (
    PostID INT AUTO_INCREMENT PRIMARY KEY,
    ProfileID INT,
    Content TEXT,
    PostDate DATETIME,
    FOREIGN KEY (ProfileID) REFERENCES Profiles(ProfileID)
);

CREATE TABLE Comments (
    CommentID INT AUTO_INCREMENT PRIMARY KEY,
    PostID INT,
    ProfileID INT,
    Content TEXT,
    CommentDate DATETIME,
    FOREIGN KEY (PostID) REFERENCES Posts(PostID),
    FOREIGN KEY (ProfileID) REFERENCES Profiles(ProfileID)
);

-- Inserting sample data into Users
INSERT INTO Users (Name, Phone, Age) VALUES
('John Doe', '555-1234', 30),
('Jane Smith', '555-5678', 28),
('Alex Johnson', '555-9012', 35);

-- Inserting sample data into Parts
INSERT INTO Parts (Name, Category, Description, Price, QuantityAvailable, Location) VALUES
('Steering Wheel', 'Interior', 'Vintage steering wheel from 1950s Chevrolet', 150.00, 5, 'USA'),
('Tail Light', 'Exterior', 'Rear tail light for 1960s Ford Mustang', 80.00, 3, 'UK'),
('Engine Block', 'Engine', 'V8 engine block for 1970 Dodge Challenger', 1200.00, 1, 'Germany');

-- Inserting sample data into Orders
INSERT INTO Orders (UserID, OrderDate, Status) VALUES
((SELECT UserID FROM Users WHERE Name = 'John Doe'), '2024-02-05', 'Processing'),
((SELECT UserID FROM Users WHERE Name = 'Jane Smith'), '2024-02-06', 'Shipped');

-- Inserting sample data into OrderDetails
INSERT INTO OrderDetails (OrderID, PartID, Quantity, Price) VALUES
((SELECT OrderID FROM Orders LIMIT 1), (SELECT PartID FROM Parts WHERE Name = 'Steering Wheel'), 1, 150.00),
((SELECT OrderID FROM Orders LIMIT 1), (SELECT PartID FROM Parts WHERE Name = 'Engine Block'), 1, 1200.00),
((SELECT OrderID FROM Orders ORDER BY OrderID DESC LIMIT 1), (SELECT PartID FROM Parts WHERE Name = 'Tail Light'), 2, 160.00);

-- Inserting sample data into Profiles, Posts, and Comments requires UserID, ProfileID, and PostID

INSERT INTO Profiles (UserID, Bio, Interests) VALUES
((SELECT UserID FROM Users WHERE Name = 'John Doe'), 'Vintage car enthusiast', 'Restoration, Collecting'),
((SELECT UserID FROM Users WHERE Name = 'Jane Smith'), 'Classic car restorer', 'DIY, Engine tuning');

-- Drop existing tables if they exist to avoid conflicts
DROP TABLE IF EXISTS PaymentTransactions, PaymentMethods, Addresses, UserAuth;

-- Create UserAuth table for storing authentication details
CREATE TABLE UserAuth (
    AuthID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    email VARCHAR(255) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE
    -- Salt VARCHAR(255) NOT NULL,
    -- LastLogin DATETIME,
    -- FailedLoginAttempts INT DEFAULT 0,
    -- PasswordResetToken VARCHAR(255),
    -- TokenExpiryDate DATETIME,
    -- FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- Create Addresses table
CREATE TABLE Addresses (
    AddressID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    FirstName VARCHAR(255),
    LastName VARCHAR(255),
    Company VARCHAR(255),
    StreetAddress1 VARCHAR(255),
    StreetAddress2 VARCHAR(255),
    City VARCHAR(255),
    StateProvince VARCHAR(255),
    PostalCode VARCHAR(20),
    Country VARCHAR(2),
    Phone VARCHAR(20),
    AddressType ENUM('billing', 'shipping'),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- Create PaymentMethods table
CREATE TABLE PaymentMethods (
    PaymentMethodID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    Type ENUM('credit card', 'PayPal', 'bank transfer'),
    Provider VARCHAR(50),
    AccountDetails TEXT,
    ExpiryDate DATE,
    BillingAddressID INT,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (BillingAddressID) REFERENCES Addresses(AddressID)
);

-- Create PaymentTransactions table
CREATE TABLE PaymentTransactions (
    TransactionID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT,
    UserID INT,
    PaymentMethodID INT,
    Amount DECIMAL(10, 2),
    Currency VARCHAR(3),
    Status VARCHAR(50),
    TransactionDate DATETIME,
    PaymentGatewayResponse TEXT,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (PaymentMethodID) REFERENCES PaymentMethods(PaymentMethodID)
    -- Note: Add `FOREIGN KEY (OrderID) REFERENCES Orders(OrderID)` if the Orders table exists
);

-- Sample insert into UserAuth (Passwords should be hashed in a real scenario)
INSERT INTO UserAuth (UserID, Email, username, PasswordHash) VALUES
(1, 'alice@example.com','alice', 'hashed_password');

-- Sample insert into Addresses
INSERT INTO Addresses (UserID, FirstName, LastName, StreetAddress1, City, StateProvince, PostalCode, Country, Phone, AddressType) VALUES
(1, 'Alice', 'Wonderland', '123 Vintage Lane', 'Retroville', 'Nostalgia', '12345', 'US', '555-0101', 'shipping');

-- Sample insert into PaymentMethods (AccountDetails should be encrypted in a real scenario)
INSERT INTO PaymentMethods (UserID, Type, Provider, AccountDetails, ExpiryDate, BillingAddressID) VALUES
(1, 'credit card', 'Visa', '123456789', '2025-12-31', 1);

INSERT INTO PaymentTransactions (OrderID, UserID, PaymentMethodID, Amount, Currency, Status, TransactionDate, PaymentGatewayResponse) VALUES
(1, 1, 1, 750.00, 'USD', 'Completed', NOW(), 'Transaction successful'),
(2, 1, 1, 1200.00, 'USD', 'Pending', NOW(), 'Awaiting confirmation');