function formatPrice(value) {
  return value.toFixed(2).replace(".", ",");
}

const cart = getCart();
const productIds = Object.keys(cart);
const cartElement = document.getElementById("cart");
const clearCartButton = document.getElementById("clear-cart");
const checkoutSubmitButton = document.getElementById("checkout-submit");
const checkoutSection = document.getElementById("checkout-section");

if (productIds.length === 0) {
  cartElement.innerHTML = "<p>Váš košík je prázdny.</p>";
  checkoutSubmitButton.disabled = true;
} else {
  clearCartButton.hidden = false;
  checkoutSection.hidden = false;

  const deliveryFee = parseFloat(cartElement.dataset.deliveryFee);
  const productImageUrl = cartElement.dataset.productImage;
  const packetaLogoUrl = cartElement.dataset.packetaLogo;

  fetch("/cart/data/?ids=" + productIds.join(","))
    .then((response) => response.json())
    .then((products) => {
      let total = 0;

      products.forEach((product) => {
        const quantity = cart[product.id];
        const itemTotal = product.price * quantity;

        total += itemTotal;

        cartElement.innerHTML += `
            <div class="cart-line-items-wrapper">
              <img class="cart-product-image" src="${productImageUrl}" alt="Book">
              <div class="cart-line-items">
                <h2>${product.name} × ${quantity}</h2>
                <h2>${formatPrice(itemTotal)} €</h2>
              </div>
            </div>
        `;
      });

      total += deliveryFee;

      cartElement.innerHTML += `
        <div class="cart-line-items-wrapper">
          <img class="cart-product-image" src="${packetaLogoUrl}" alt="Packeta">
          <div class="cart-line-items">
            <h2>Doprava</h2>
            <h2>${formatPrice(deliveryFee)} €</h2>
          </div>
        </div>
        <hr>
        <h2 class="cart-total">Spolu ${formatPrice(total)} €</h2>
        <br>
      `;
    });
}

document.getElementById("checkout-form").addEventListener("submit", function (event) {
  if (productIds.length === 0) {
    event.preventDefault();
    return;
  }

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

clearCartButton.addEventListener("click", function () {
  saveCart({});
  updateCartAppearance();
  window.location.reload();
});
