const express = require('express');
const path = require('path');
const axios = require('axios');
const bodyParser = require('body-parser');
const cors = require('cors');
const multer = require('multer');
const firebase = require('firebase-admin');
const serviceAccount = require('./serviceAccountKey.json');

const app = express();

app.set('view engine', 'ejs');
app.set('views', __dirname + '/views');

app.use(cors());
app.use(express.static(path.join(__dirname, 'static')));

// Middleware to parse JSON and URL-encoded body
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Set up multer storage and file filter
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

firebase.initializeApp({
    credential: firebase.credential.cert(serviceAccount),
    storageBucket: 'esdfirebase-2fe43.appspot.com' // Replace with your storage bucket name
});
const bucket = firebase.storage().bucket();

// Route handler for car
app.get('/cars', async (req, res) => {
    try {
        // Send a GET request to retrieve car data
        const response = await axios.get(`https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/`);

        // Extract car data from the response
        const carData = response.data;
        console.log('Retrieved car data:', carData);

        // Fetch image URLs for each car
        const carsWithImages = await Promise.all(carData.Cars.map(async (car) => {
            const folderPrefix = `cars/${car.VehicleIdentificationNum}/`;
            const [blobs] = await bucket.getFiles({ prefix: folderPrefix });

            const imageUrls = [];
            const futureTimestamp = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000); // 365 days in milliseconds

            for (const blob of blobs) {
                const fileExists = await blob.exists();
                if (fileExists[0]) {
                    const imageUrl = await blob.getSignedUrl({
                        action: 'read',
                        expires: futureTimestamp,
                    });
                    console.log(imageUrl);
                    imageUrls.push(imageUrl[0]);
                    break; // Only fetch the first image for each car
                } else {
                    console.log('File does not exist:', blob.name);
                }
            }

            return { ...car, imageUrls }; // Append imageUrls to the car object
        }));

        // Render the 'carlisting' view with the updated car data
        res.render('carlisting', { carData: carsWithImages });
    } catch (error) {
        console.error('Error:', error.message);
        res.status(500).send('Error fetching car data');
    }
});

// Route handler for car/:VehicleIdentificationNum
app.get('/car/:VehicleIdentificationNum', async (req, res) => {
    try {
        const { VehicleIdentificationNum } = req.params;
        const folderPrefix = `cars/${VehicleIdentificationNum}/`;
        const [blobs] = await bucket.getFiles({ prefix: folderPrefix });

        const imageUrls = [];
        const futureTimestamp = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000); // 365 days in milliseconds

        for (const blob of blobs) {
            const fileExists = await blob.exists();
            if (fileExists[0]) {
                const imageUrl = await blob.getSignedUrl({
                    action: 'read',
                    expires: futureTimestamp,
                });
                console.log(imageUrl);
                imageUrls.push(imageUrl[0]);
            } else {
                console.log('File does not exist:', blob.name);
            }
        }

        const response = await axios.get(`https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/${VehicleIdentificationNum}`);
        const carData = response.data;

        res.render('car', { carData, imageUrls });
    } catch (error) {
        console.error('Error:', error.message);
        res.status(500).send('Error fetching car data');
    }
});

app.get('/car/owner/:SellerID', async (req, res) => {
  try {
      // Extract the VehicleIdentificationNum from the request parameters
      const { SellerID } = req.params;

      // Send a GET request to retrieve car data
      const response = await axios.get(`https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/owner/${SellerID}`);

      // Extract car data from the response
      const carData = response.data;
      console.log('Retrieved car data:', carData);

      // Render the 'car' view with the retrieved car data
      res.render('rentmanagement', { carData });
  } catch (error) {
      console.error('Error:', error.message);
      res.render('rentmanagement', carData=0);
  }
});

// Endpoint to receive the sellerId
app.post('/seller', async (req, res) => {
    try {
        const { SellerID } = req.body;
        console.log('Received SellerID from sellerForm:', SellerID);
        
        // Send a response back to the client
        res.redirect(`http://127.0.0.1:5009/addcar?SellerID=${SellerID}`);
    } catch (error) {
        // Handle errors
        console.error('Error:', error.message);
        res.status(500).send('Error processing SellerID');
    }
});

// Route to serve the addcar.html file
app.get('/addcar', (req, res) => {
    res.render('addcar');
  });

app.post('/addcar', upload.array('Image'), async (req, res) => {
    try {
        // Extract data from the request body
        const { Brand, Model, VehicleIdentificationNum, Description, Price, Location, SellerID } = req.body;
        const Images = req.files; // Access the uploaded files using req.files

        // Array to store image URLs
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
        
        // Prepare the data to be sent in the POST request to createcar endpoint
        const carData = {
            Brand,
            Model,
            VehicleIdentificationNum,
            Description,
            Price,
            Location,
            SellerID
        };

        // Send a POST request to the specified endpoint
        const response = await axios.post('https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/', carData);

        // Handle the response from the API
        console.log('Car created successfully:', response.data);
        
        // Send a response back to the client
        res.status(200).send('Car created successfully');
    } catch (error) {
        // Handle errors
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

app.post('/updatecar', (req, res) => {
    res.render('updatecar'); // Assuming updatecar.ejs is in your views directory
});

// Route handler for POST request to /updatedetails
app.post('/updatedetails', upload.array('Image'), async (req, res) => {
    try {
        // Retrieve form data
        const VehicleIdentificationNum = req.body.VehicleIdentificationNum;
        const SellerID = req.body.SellerID;
        const Brand = req.body.Brand;
        const Model = req.body.Model;
        const Description = req.body.Description;
        const Price = req.body.Price;
        const Location = req.body.Location;
        const Images = req.files; // Access the uploaded files using req.files
        console.log("Data", req.body);
        console.log("Images", req.files);

        // Array to store image URLs
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

        // Prepare the data to be sent in the PUT request
        const details = {
            Model,
            Brand,
            VehicleIdentificationNum,
            Description,
            Price,
            Location,
            SellerID
        };

        // Send a PUT request to update car details
        const response = await axios.put('https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/', details);
        console.log('Response from PUT request:', response.data);

        res.redirect(`http://127.0.0.1:5009/car/${VehicleIdentificationNum}`);
    } catch (error) {
        console.error('Error:', error);
        res.status(500).send('Internal server error');
    }
});

app.post('/car/rent/:vin', (req, res) => {
    // Retrieve the VIN from the request params
    const vin = req.params.vin;
    console.log("VIN:",vin);
    // Forward the request to the OutSystems endpoint
    axios.put(`https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/Rent/${vin}`)
        .then(response => {
            // Forward the response from the OutSystems endpoint to the client
            res.status(response.status).send(response.data);
        })
        .catch(error => {
            // Handle errors
            console.error(error);
            res.status(500).send('Internal server error');
        });
});

app.post('/car/return/:vin', (req, res) => {
    // Retrieve the VIN from the request params
    const vin = req.params.vin;
    console.log("VIN:",vin);
    // Forward the request to the OutSystems endpoint
    axios.put(`https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/Return/${vin}`)
        .then(response => {
            // Forward the response from the OutSystems endpoint to the client
            res.status(response.status).send(response.data);
        })
        .catch(error => {
            // Handle errors
            console.error(error);
            res.status(500).send('Internal server error');
        });
});

// Handle POST request to /deletecar
app.post('/deletecar', async (req, res) => {
    try {
        // Extract the VehicleIdentificationNum from the request body
        const { VehicleIdentificationNum } = req.body;

        // Make a DELETE request to the external API
        const response = await axios.delete(`https://personal-dz59up8e.outsystemscloud.com/Rental/rest/v1/cars/${VehicleIdentificationNum}/`);

        // Handle the response from the API
        console.log('Response from API:', response.data);

        // Send a success response back to the client
        res.json({ success: true, message: 'Car deleted successfully' });
    } catch (error) {
        // Handle errors
        console.error('Error deleting car:', error.message);

        // Send an error response back to the client
        res.status(500).json({ success: false, message: 'Failed to delete car' });
    }
});

// Start the server
app.listen(5009, () => {
    console.log('Server is running on port 5009');
});