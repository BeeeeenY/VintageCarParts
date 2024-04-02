document.addEventListener('DOMContentLoaded', () => {
  const cart = [];
  
  function fetchAndDisplayItems() {
      fetch("http://localhost:3000/items")
          .then(response => response.json())
          .then(items => {
              const productsElement = document.getElementById("products");
              items.forEach(item => {
                  const itemElement = document.createElement("div");
                  itemElement.className = "product";
                  itemElement.innerHTML = `
                      <span>${item.name} - $${(item.priceInCents / 100).toFixed(2)}</span>
                      <button data-id="${item.id}">Add to Cart</button>
                  `;
                  productsElement.appendChild(itemElement);
              });
              attachAddToCartEventListeners();
          })
          .catch(error => console.error("Error fetching items:", error));
  }

  function attachAddToCartEventListeners() {
      document.querySelectorAll('#products .product button').forEach(button => {
          button.addEventListener('click', (event) => {
              const productId = button.getAttribute('data-id');
              addToCart(productId);
          });
      });
  }

  function addToCart(productId) {
      const existingProduct = cart.find(item => item.id === productId);
      if (existingProduct) {
          existingProduct.quantity += 1;
      } else {
          cart.push({ id: productId, quantity: 1 });
      }
      renderCart();
  }

  function renderCart() {
      const cartElement = document.getElementById("cart");
      cartElement.innerHTML = '<h3>Shopping Cart</h3>';
      cart.forEach(item => {
          const itemElement = document.createElement('div');
          itemElement.textContent = `Item ID: ${item.id}, Quantity: ${item.quantity}`;
          cartElement.appendChild(itemElement);
      });
  }

  const checkout = () => {
    fetch("http://localhost:3000/create-checkout-session", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            items: cart.map(item => ({ id: parseInt(item.id), quantity: item.quantity })),
        }),
    })
    .then(res => {
        if (res.ok) return res.json();
        return res.json().then(json => Promise.reject(json));
    })
    .then(({ url }) => {
        window.location = url;
    })
    .catch(e => {
        console.error(e.error);
    });
};

document.getElementById('checkout').addEventListener('click', (event) => {
    event.preventDefault();
    if (cart.length > 0) {
        checkout();
    } else {
        alert("Your cart is empty.");
    }
});

  fetchAndDisplayItems();
  renderCart();
});

document.getElementById('proceed-to-checkout').addEventListener('click', (event) => {
    event.preventDefault();
    redirectToCheckout();
});
