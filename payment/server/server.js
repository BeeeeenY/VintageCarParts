require("dotenv").config()

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

// const storeItems = new Map([
//   [1, { priceInCents: 100000, name: "Aston Martin DB7 I6 engine parts" }],
//   [2, { priceInCents: 20000, name: "Get an A for ESD" }],
//   [3, { priceInCents: 20000, name: "Get an A for ESM" }],
// ])
const storeItems = new Map([])

// this endpoint to serve the items' data
app.get("/items", (req, res) => {
  const itemsArray = Array.from(storeItems, ([id, details]) => ({
    id,
    ...details,
  }));
  res.json(itemsArray);
});

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

app.post("/clear-cart", (req, res) => {
  storeItems.clear(); // This clears the entire map, effectively emptying the cart
  console.log("Cart has been emptied");
  res.status(200).send("Cart cleared successfully");
});

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

app.listen(3000)
