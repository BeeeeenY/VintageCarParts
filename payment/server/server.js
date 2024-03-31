require("dotenv").config()

const swaggerUi = require("swagger-ui-express");
const YAML = require("yamljs");
const express = require("express");
const app = express();
const cors = require("cors");
app.use(express.json());
app.use(express.urlencoded({ extended: true })); // Parse URL-encoded bodies
app.use(
  cors({
    origin: ["http://localhost:8888", "http://127.0.0.1:5002","http://127.0.0.1:5005"],
  })
);

const stripe = require("stripe")(process.env.STRIPE_PRIVATE_KEY)
// Load your API definition file
const swaggerDocument = YAML.load("./swagger.yaml");
app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocument));

// const storeItems = new Map([
//   [1, { priceInCents: 100000, name: "Aston Martin DB7 I6 engine parts" }],
//   [2, { priceInCents: 20000, name: "Get an A for ESD" }],
//   [3, { priceInCents: 20000, name: "Get an A for ESM" }],
// ])
const storeItems = new Map([])

/**
 * @swagger
 * tags:
 *   name: Store
 *   description: Endpoints for managing store items and cart
 */

/**
 * @swagger
 * /items:
 *   get:
 *     summary: Get all items in the store
 *     description: Retrieve all items available in the store
 *     responses:
 *       200:
 *         description: A list of store items
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 type: object
 *                 properties:
 *                   id:
 *                     type: integer
 *                     description: The ID of the item
 *                   name:
 *                     type: string
 *                     description: The name of the item
 *                   priceInCents:
 *                     type: integer
 *                     description: The price of the item in cents
 */

// this endpoint to serve the items' data
app.get("/items", (req, res) => {
  const itemsArray = Array.from(storeItems, ([id, details]) => ({
    id,
    ...details,
  }));
  res.json(itemsArray);
});
/**
 * @swagger
 * /add-to-cart:
 *   post:
 *     summary: Add an item to the cart
 *     description: Add an item to the shopping cart with specified details
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               PartID:
 *                 type: integer
 *                 description: ID of the part being ordered
 *               Price:
 *                 type: number
 *                 description: Price of the part being ordered
 *               quantity:
 *                 type: integer
 *                 description: Quantity of the part being ordered
 *               BuyerID:
 *                 type: integer
 *                 description: ID of the user placing the order
 *               SellerID:
 *                 type: integer
 *                 description: ID of the seller
 *               ProductName:
 *                 type: string
 *                 description: Optional name of the product
 *     responses:
 *       302:
 *         description: Redirect to the cart page after adding the item to the cart
 *       500:
 *         description: Internal server error
 */

// To add in user
app.post("/add-to-cart", (req, res) => {
  console.log("Received data:", req.body);
  const {  PartID, Price, quantity, BuyerID, SellerID, ProductName } = req.body;
  
  // Assuming PartID is unique, directly add it to the storeItems
  storeItems.set(parseInt(PartID), {
    priceInCents: Math.round(parseFloat(Price)*100),
    quantity: parseInt(quantity),
    BuyerID: parseInt(BuyerID),
    SellerID: parseInt(SellerID),
    name: ProductName,
  });
  console.log(storeItems)
  // Redirect to cart.html after adding the item to the cart
  res.redirect('http://127.0.0.1:5002/cart');
  
});

/**
 * @swagger
 * /clear-cart:
 *   post:
 *     summary: Clear the cart
 *     description: Clear all items from the shopping cart
 *     responses:
 *       200:
 *         description: Cart cleared successfully
 *       500:
 *         description: Internal server error
 */


app.post("/clear-cart", (req, res) => {
  storeItems.clear(); // This clears the entire map, effectively emptying the cart
  console.log("Cart has been emptied");
  res.status(200).send("Cart cleared successfully");
});

/**
 * @swagger
 * /create-checkout-session:
 *   post:
 *     summary: Create a checkout session
 *     description: Create a new checkout session for processing payments
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               items:
 *                 type: array
 *                 items:
 *                   type: object
 *                   properties:
 *                     id:
 *                       type: integer
 *                       description: ID of the item
 *                     quantity:
 *                       type: integer
 *                       description: Quantity of the item
 *     responses:
 *       200:
 *         description: URL for the checkout session
 *       500:
 *         description: Internal server error
 */

app.post("/create-checkout-session", async (req, res) => {
  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ["card"],
      mode: "payment",
      line_items: req.body.items.map(item => {
        const storeItem = storeItems.get(item.id)
        return {
          price_data: {
            currency: "usd",
            product_data: {
              name: storeItem.name,
            },
            unit_amount: storeItem.priceInCents,
          },
          quantity: item.quantity,
        }
      }),
      success_url: `http://127.0.0.1:5005/create_order_new`,
      cancel_url: `http://127.0.0.1:5002`,
    })
    res.json({ url: session.url })
  } catch (e) {
    res.status(500).json({ error: e.message })
  }
})


// app.listen(3000)


// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});