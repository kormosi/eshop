const cart = getCart();
const productIds = Object.keys(cart);
const cartElement = document.getElementById("cart");

if (productIds.length === 0) {
  cartElement.innerHTML = "<p>Your cart is empty.</p>";
} else {
  fetch("/cart/data/?ids=" + productIds.join(","))
    .then((response) => response.json())
    .then((products) => {
      let total = 0;

      products.forEach((product) => {
        const quantity = cart[product.id];
        const itemTotal = product.price * quantity;

        total += itemTotal;

        cartElement.innerHTML += `
          <div>
            <h2>${product.name}</h2>
            <p>${product.price} ${product.currency} × ${quantity}</p>
            <p>${itemTotal.toFixed(2)} ${product.currency}</p>
          </div>
        `;
      });

      cartElement.innerHTML += `
        <hr>
        <h2>Total: ${total.toFixed(2)} EUR</h2>
      `;
    });
}

document.getElementById("checkout-form").addEventListener("submit", function (event) {
  const pickupPointId = document.getElementById("pickup-point-id").value;
  const error = document.getElementById("pickup-point-error");

  if (!pickupPointId) {
    event.preventDefault();
    error.hidden = false;
    return;
  }

  error.hidden = true;
  document.getElementById("cart-data").value = JSON.stringify(cart);
});
