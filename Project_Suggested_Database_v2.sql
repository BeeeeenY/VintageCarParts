	CREATE DATABASE IF NOT EXISTS `Products` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
	USE `Products`;

	-- Create Parts table
	CREATE TABLE Parts (
		PartID INT AUTO_INCREMENT PRIMARY KEY,
		Name VARCHAR(255) NOT NULL,
		AuthenticationNum VARCHAR(255) NULL,
		Category VARCHAR(255) NOT NULL,
		Description TEXT,
		Price DECIMAL(10, 2),
		QuantityAvailable INT,
		Location VARCHAR(255),
		Brand VARCHAR(255) NULL,
		Model VARCHAR(255) NULL,
        PostDate DATETIME,
		status VARCHAR(255) NULL
	);
    
      CREATE TABLE Comments (
		CommentID INT AUTO_INCREMENT PRIMARY KEY,
		UserID INT,
		Content TEXT,
		CommentDate DATETIME
	);
    
    
	CREATE DATABASE IF NOT EXISTS `Users` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
	USE `Users`;

	-- Create Users table
	CREATE TABLE Users (
		UserID INT AUTO_INCREMENT PRIMARY KEY,
		Name VARCHAR(255) NOT NULL,
		Phone VARCHAR(20),
		Age INT,
		Country VARCHAR(255)
	);

	CREATE DATABASE IF NOT EXISTS `Authentication` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
	USE `Authentication`;

	CREATE TABLE UserAuth (
		AuthID INT AUTO_INCREMENT PRIMARY KEY,
		UserID INT,
		Email VARCHAR(255) NOT NULL UNIQUE,
		PasswordHash VARCHAR(255) NOT NULL
	);

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
		FOREIGN KEY (UserID) REFERENCES `Users`.`Users`(UserID)
	);

	CREATE DATABASE IF NOT EXISTS `Orders` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

	USE `Orders`;

	-- Create Orders and OrderDetails tables
	CREATE TABLE Cart (
		CartID INT AUTO_INCREMENT PRIMARY KEY,
		UserID INT,
		OrderDate DATETIME,
		Status VARCHAR(255),
		FOREIGN KEY (UserID) REFERENCES `Users`.`Users`(UserID)
	);

	CREATE TABLE OrderDetails (
		OrderDetailID INT AUTO_INCREMENT PRIMARY KEY,
		CartID INT,
		PartID INT,
		Quantity INT,
		Purchaseddate date,
		Price DECIMAL(10, 2),
		FOREIGN KEY (CartID) REFERENCES Cart(CartID),
		FOREIGN KEY (PartID) REFERENCES `Products`.`Parts`(PartID)
	);

	CREATE DATABASE IF NOT EXISTS `Payment` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
	USE `Payment`;

	CREATE TABLE PaymentMethods (
		PaymentMethodID INT AUTO_INCREMENT PRIMARY KEY,
		UserID INT,
		Type ENUM('credit card', 'PayPal', 'bank transfer'),
		Provider VARCHAR(50),
		AccountDetails TEXT,
		ExpiryDate DATE,
		BillingAddressID INT,
		FOREIGN KEY (UserID) REFERENCES `Users`.`Users`(UserID),
		FOREIGN KEY (BillingAddressID) REFERENCES `Authentication`.`Addresses`(AddressID)
	);

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
		FOREIGN KEY (UserID) REFERENCES `Users`.`Users`(UserID),
		FOREIGN KEY (PaymentMethodID) REFERENCES PaymentMethods(PaymentMethodID),
		FOREIGN KEY (OrderID) REFERENCES `Orders`.`Cart`(CartID)
	);

	CREATE DATABASE IF NOT EXISTS `Forum` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
	USE `Forum`;

	-- Create Posts table
	CREATE TABLE Posts (
		PostID INT AUTO_INCREMENT PRIMARY KEY,
		UserID INT,
		Title VARCHAR(255) NOT NULL,
		Content TEXT NOT NULL,
		PostDate DATETIME,
		LastUpdated DATETIME,
		FOREIGN KEY (UserID) REFERENCES `Users`.`Users`(UserID)
	);

	-- Create Comments table
	CREATE TABLE Comments (
		CommentID INT AUTO_INCREMENT PRIMARY KEY,
		UserID INT,
		Content TEXT NOT NULL,
		CommentDate DATETIME,
		FOREIGN KEY (UserID) REFERENCES `Users`.`Users`(UserID)
	);

	--  THE FOLLOWING COMMANDS ARE TO INSERT TO ROWS INTO THE RELEVANT DATABASE AND DATA TABLE

	USE `Products`;

	-- Insert into Parts
	INSERT INTO Parts (Name, AuthenticationNum, Category, Description, Price, QuantityAvailable, Location, Brand, Model, PostDate, status) VALUES 
	('Part A', '12345', 'Electronics', 'Description of part A', 99.99, 10, 'Korea', 'BMW', 'X5', NOW(), 'Available'),
	('Part B', '67890', 'Automotive', 'Description of part B', 199.99, 5, 'USA', 'Mini Cooper', 'Countryman',NOW(), 'Available'),
	('Part C', '11223', 'Hardware', 'Description of part C', 9.99, 20, 'Europe', 'Ferrari', '812 GTS',NOW(), 'Available');
    
	INSERT INTO Comments (CommentID, UserID, Content, CommentDate) VALUES 
	(3, 1, 'I am interested in Part A', NOW()),
	(2, 1, 'I have Part B available for trade', NOW()),
	(1, 1, 'How much discount on bulk purchase for Part C?', NOW());
    
	USE `Users`;

	-- Insert into Users
	INSERT INTO Users (Name, Phone, Age, Country) VALUES 
	('John Doe', '123-456-7890', 30, 'US'),
	('Jane Smith', '098-765-4321', 25, 'UK'),
	('Bob Brown', '456-789-1230', 40, 'CA');

	USE `Authentication`;

	-- Assuming UserIDs from Users table: 1, 2, 3
	-- Insert into UserAuth
	INSERT INTO UserAuth (UserID, Email, PasswordHash) VALUES 
	(1, 'john.doe@example.com', 'hashedpassword1'),
	(2, 'jane.smith@example.com', 'hashedpassword2'),
	(3, 'bob.brown@example.com', 'hashedpassword3');

	-- Insert into Addresses
	INSERT INTO Addresses (UserID, FirstName, LastName, Company, StreetAddress1, StreetAddress2, City, StateProvince, PostalCode, Country, Phone, AddressType) VALUES 
	(1, 'John', 'Doe', 'Company A', '123 Main St', 'Suite 100', 'CityA', 'StateA', '12345', 'US', '123-456-7890', 'shipping'),
	(2, 'Jane', 'Smith', 'Company B', '456 Second St', NULL, 'CityB', 'StateB', '67890', 'UK', '098-765-4321', 'billing'),
	(3, 'Bob', 'Brown', '', '789 Third St', NULL, 'CityC', 'StateC', '111213', 'CA', '456-789-1230', 'shipping');

	USE `Orders`;

	-- Assuming UserIDs from Users table: 1, 2, 3
	-- Insert into Cart
	INSERT INTO Cart (UserID, OrderDate, Status) VALUES 
	(1, NOW(), 'Pending'),
	(2, NOW(), 'Packing'),
	(3, NOW(), 'Shipped');

	-- Assuming CartIDs: 1, 2, 3 and PartIDs from Parts table: 1, 2, 3
	-- Insert into OrderDetails
	INSERT INTO OrderDetails (CartID, PartID, Quantity, Purchaseddate, Price) VALUES 
	(1, 1, 2, CURDATE(), 99.99),
	(2, 2, 1, CURDATE(), 199.99),
	(3, 3, 3, CURDATE(), 9.99);

	USE `Payment`;

	-- Assuming UserIDs from Users table: 1, 2, 3
	-- Insert into PaymentMethods
	INSERT INTO PaymentMethods (UserID, Type, Provider, AccountDetails, ExpiryDate, BillingAddressID) VALUES 
	(1, 'credit card', 'Bank A', 'Account Details A', '2025-12-31', 1),
	(2, 'PayPal', 'PayPal Service', 'Account Details B', '2024-11-30', 2),
	(3, 'bank transfer', 'Bank B', 'Account Details C', '2023-10-31', 3);

	-- Assuming OrderIDs from Cart table: 1, 2, 3 and PaymentMethodIDs: 1, 2, 3
	-- Insert into PaymentTransactions
	INSERT INTO PaymentTransactions (OrderID, UserID, PaymentMethodID, Amount, Currency, Status, TransactionDate) VALUES 
	(1, 1, 1, 199.98, 'USD', 'Completed', NOW()),
	(2, 2, 2, 199.99, 'GBP', 'Pending', NOW()),
	(3, 3, 3, 29.97, 'CAD', 'Failed', NOW());

	USE `Forum`;

	-- Assuming UserIDs from Users table: 1, 2, 3
	-- Insert into Posts
	INSERT INTO Posts (UserID, Title, Content, PostDate, LastUpdated) VALUES 
	(1, 'How to repair Part A', 'Content on repairing Part A', NOW(), NOW()),
	(2, 'Seeking advice on Part B', 'Need advice on using Part B effectively', NOW(), NOW()),
	(3, 'Bulk deals on Part C?', 'Looking for bulk deals on Part C. Any suggestions?', NOW(), NOW());

	-- Assuming PostIDs from Posts table: 1, 2, 3
	-- Insert into Comments
	INSERT INTO Comments (CommentID, UserID, Content, CommentDate) VALUES 
	(1, 2, 'Try checking the manual', NOW()),
	(2, 3, 'Part B is very durable, no worries', NOW()),
	(3, 1, 'Bulk deals are usually available end of year', NOW());

