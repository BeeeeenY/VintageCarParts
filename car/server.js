const express = require('express');
const path = require('path');
const axios = require('axios');
const bodyParser = require('body-parser');
const cors = require('cors');
const multer = require('multer');
const firebase = require('firebase-admin');
const swaggerUi = require("swagger-ui-express");
const serviceAccount = require('./serviceAccountKey.json');
const YAML = require("yamljs");

const app = express();

app.use(function(req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});

const swaggerDocument = YAML.load("./swagger.yaml");
app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocument));

// EJS Template
app.set('view engine', 'ejs');
app.set('views', __dirname + '/views');

// CORS
app.use(cors());

// Static Images
app.use(express.static(path.join(__dirname, 'static')));

// Parse JSON and URL-encoded body
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Set up multer storage and file filter
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Firebase Storage 
firebase.initializeApp({
    credential: firebase.credential.cert(serviceAccount),
    storageBucket: 'esdfirebase-2fe43.appspot.com'
});
const bucket = firebase.storage().bucket();

// Car Rental Listing
app.get('/cars', async (req, res) => {
    try {
        const response = await axios.get(`https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/`);
        const carData = response.data;
        console.log('Retrieved car data:', carData);

        // Fetch image URLs for each car
        const carsWithImages = await Promise.all(carData.Cars.map(async (car) => {
            const folderPrefix = `cars/${car.VehicleIdentificationNum}/`;
            const [blobs] = await bucket.getFiles({ prefix: folderPrefix });

            const imageUrls = [];
            const futureTimestamp = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000);

            for (const blob of blobs) {
                const fileExists = await blob.exists();
                if (fileExists[0]) {
                    const imageUrl = await blob.getSignedUrl({
                        action: 'read',
                        expires: futureTimestamp,
                    });
                    console.log("Images", imageUrl);
                    imageUrls.push(imageUrl[0]);
                    break; // Only fetch the first image for each car
                } else {
                    console.log('File does not exist:', blob.name);
                }
            }

            return { ...car, imageUrls };
        }));

        res.render('carlisting', { carData: carsWithImages });

    } catch (error) {
        console.error('Error:', error.message);
        res.status(500).send('Error fetching car data');
    }
});

// Car Details
app.get('/car/:VehicleIdentificationNum', async (req, res) => {
    try {
        const { VehicleIdentificationNum } = req.params;
        const folderPrefix = `cars/${VehicleIdentificationNum}/`;
        const [blobs] = await bucket.getFiles({ prefix: folderPrefix });

        const imageUrls = [];
        const futureTimestamp = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000);

        for (const blob of blobs) {
            const fileExists = await blob.exists();
            if (fileExists[0]) {
                const imageUrl = await blob.getSignedUrl({
                    action: 'read',
                    expires: futureTimestamp,
                });
                console.log("Images", imageUrl);
                imageUrls.push(imageUrl[0]);
            } else {
                console.log('File does not exist:', blob.name);
            }
        }

        const response = await axios.get(`https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/${VehicleIdentificationNum}`);
        const carData = response.data;
        // Uncomment to send swagger JSON response
        // res.json({ carData, imageUrls });
        res.render('car', { carData, imageUrls });

    } catch (error) {
        console.error('Error:', error.message);
        res.status(500).send('Error fetching car data');
    }
});

// Car Rental Management
app.get('/car/owner/:SellerID', async (req, res) => {
    try {
        const { SellerID } = req.params;

        const response = await axios.get(`https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/owner/${SellerID}`);
        const carData = response.data;
        console.log('Retrieved car data:', carData);

      // uncomment to send JSON response for swagger
        // res.json({ carData });
        res.render('rentmanagement', { carData });
        

    } catch (error) {
        console.error('Error:', error.message);
        // res.status(500).json({ error: 'Error fetching car data' });
        res.render('rentmanagement', carData=0);

    }
});

// Receive SellerID
app.post('/seller', async (req, res) => {
    try {
        const { SellerID } = req.body;
        console.log('Received SellerID from sellerForm:', SellerID);

        const responseData = {
                message: 'Received SellerID successfully',
                SellerID: SellerID
            };
    
        res.redirect(`http://127.0.0.1:5009/addcar?SellerID=${SellerID}`);

    } catch (error) {
        console.error('Error:', error.message);
        res.status(500).send('Error processing SellerID');
    }
});

// Render addcar form
app.get('/addcar', (req, res) => {
    res.render('addcar');
  });

// Add Car
app.post('/addcar', upload.array('Image'), async (req, res) => {
    try {
        const { Brand, Model, VehicleIdentificationNum, Description, Price, Location, SellerID } = req.body;
        const Images = req.files;
        console.log("Images:", Images);

        const imageUrls = [];

        if (Images && Images.length > 0) {
            for (const image of Images) {
                const imageName = `${image.originalname}`;
                const folderPath = `cars/${VehicleIdentificationNum}/`;
                const filePath = folderPath + imageName;

                // Check if the file already exists in storage
                const fileExists = await bucket.file(filePath).exists();

                // If the file doesn't exist, proceed with uploading it
                if (!fileExists[0]) {
                    const file = bucket.file(filePath);
                    const stream = file.createWriteStream({
                        metadata: {
                            contentType: image.mimetype
                        }
                    });

                    // Upload image
                    await new Promise((resolve, reject) => {
                        stream.on('error', (err) => {
                            console.error('Error uploading image:', err);
                            reject(err);
                        });
                        stream.on('finish', async () => {
                            console.log('Image uploaded successfully');
                            // Get the public URL of the uploaded image
                            const imageUrl = `https://storage.googleapis.com/${bucket.name}/${filePath}`;
                            imageUrls.push(imageUrl);
                            resolve();
                        });
                        stream.end(image.buffer);
                    });
                } else {
                    console.log('Image already exists:', imageName);
                }
            }
        }
        
        const carData = {
            Brand,
            Model,
            VehicleIdentificationNum,
            Description,
            Price,
            Location,
            SellerID
        };

        const response = await axios.post('https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/', carData);
        console.log('Car created successfully:', response.data);
        
        res.redirect(`http://127.0.0.1:5009/car/${VehicleIdentificationNum}`);

    } catch (error) {
        console.error('Error:', error.message);
        if (error.response) {
            console.error('Error creating car:', error.response.data);
            res.status(500).send('Error creating car');
        } else {
            console.error('Error creating car:', error.message);
            res.status(500).send('Error creating car');
        }
    }
});

// Render updatecar form
app.post('/updatecar', (req, res) => {
    res.render('updatecar'); // Assuming updatecar.ejs is in your views directory
});

// Update car details
app.post('/updatedetails', upload.array('Image'), async (req, res) => {
    try {
        const VehicleIdentificationNum = req.body.VehicleIdentificationNum;
        const SellerID = req.body.SellerID;
        const Brand = req.body.Brand;
        const Model = req.body.Model;
        const Description = req.body.Description;
        const Price = req.body.Price;
        const Location = req.body.Location;
        const Images = req.files;
        console.log("Data:", req.body);
        console.log("Images:", req.files);

        const imageUrls = [];

        // Check if images were uploaded
        if (Images && Images.length > 0) {
            // Process each uploaded image
            for (const image of Images) {
                const imageName = `${image.originalname}`;
                const folderPath = `cars/${VehicleIdentificationNum}/`;
                const filePath = folderPath + imageName;

                // Check if the file already exists in storage
                const fileExists = await bucket.file(filePath).exists();

                // If the file doesn't exist, proceed with uploading it
                if (!fileExists[0]) {
                    const file = bucket.file(filePath);
                    const stream = file.createWriteStream({
                        metadata: {
                            contentType: image.mimetype
                        }
                    });

                    // Upload image
                    await new Promise((resolve, reject) => {
                        stream.on('error', (err) => {
                            console.error('Error uploading image:', err);
                            reject(err);
                        });
                        stream.on('finish', async () => {
                            console.log('Image uploaded successfully');
                            // Get the public URL of the uploaded image
                            const imageUrl = `https://storage.googleapis.com/${bucket.name}/${filePath}`;
                            imageUrls.push(imageUrl);
                            resolve();
                        });
                        stream.end(image.buffer);
                    });
                } else {
                    console.log('Image already exists:', imageName);
                }
            }
        }

        const details = {
            Model,
            Brand,
            VehicleIdentificationNum,
            Description,
            Price,
            Location,
            SellerID
        };

        const response = await axios.put('https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/', details);
        console.log('Response from PUT request:', response.data);

        res.redirect(`http://127.0.0.1:5009/car/${VehicleIdentificationNum}`);

    } catch (error) {
        console.error('Error:', error);
        res.status(500).send('Internal server error');
    }
});

// Update availability to 'False'
app.post('/car/rent/:vin', (req, res) => {
    const vin = req.params.vin;
    console.log("VIN:",vin);
    axios.put(`https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/Rent/${vin}`)
        .then(response => {
            res.status(response.status).send(response.data);
        })
        .catch(error => {
            console.error(error);
            res.status(500).send('Internal server error');
        });
});

// Update availability to 'True'
app.post('/car/return/:vin', (req, res) => {
    const vin = req.params.vin;
    console.log("VIN:",vin);
    axios.put(`https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/Return/${vin}`)
        .then(response => {
            res.status(response.status).send(response.data);
        })
        .catch(error => {
            console.error(error);
            res.status(500).send('Internal server error');
        });
});

// Delete car
app.post('/deletecar', async (req, res) => {
    try {
        const { VehicleIdentificationNum } = req.body;

        const response = await axios.delete(`https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/${VehicleIdentificationNum}/`);
        console.log('Response from API:', response.data);

        res.json({ success: true, message: 'Car deleted successfully' });

    } catch (error) {
        console.error('Error deleting car:', error.message);
        res.status(500).json({ success: false, message: 'Failed to delete car' });
    }
});

app.listen(5009, () => {
    console.log('Server is running on port 5009');
});
