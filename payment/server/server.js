require("dotenv").config()

const express = require("express");
const app = express();
const cors = require("cors");
app.use(express.json());
app.use(express.urlencoded({ extended: true })); // Parse URL-encoded bodies
app.use(
  cors({
    origin: "http://localhost:8888",
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
  const {  PartID, Price, quantity, BuyerID, SellerID } = req.body;
  
  // Assuming PartID is unique, directly add it to the storeItems
  storeItems.set(parseInt(PartID), {
    priceInCents: parseInt(Price),
    quantity: parseInt(quantity),
    BuyerID: parseInt(BuyerID),
    SellerID: parseInt(SellerID)
  });
  console.log(storeItems)
  res.sendStatus(200);
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
      success_url: `${process.env.CLIENT_URL}/success.html`,
      cancel_url: `${process.env.CLIENT_URL}/cancel.html`,
    })
    res.json({ url: session.url })
  } catch (e) {
    res.status(500).json({ error: e.message })
  }
})

app.listen(3000)
