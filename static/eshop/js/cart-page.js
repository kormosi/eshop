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

      function addLine(imageUrl, alt, label, price) {
        const wrapper = document.createElement("div");
        wrapper.className = "cart-line-items-wrapper";
        const img = document.createElement("img");
        img.className = "cart-product-image";
        img.src = imageUrl;
        img.alt = alt;
        const lines = document.createElement("div");
        lines.className = "cart-line-items";
        for (const text of [label, formatPrice(price) + " €"]) {
          const h2 = document.createElement("h2");
          h2.textContent = text;
          lines.append(h2);
        }
        wrapper.append(img, lines);
        cartElement.append(wrapper);
      }

      products.forEach((product) => {
        const quantity = Number(cart[product.id]) || 0;
        const itemTotal = product.price * quantity;
        total += itemTotal;
        addLine(productImageUrl, "Book", `${product.name} × ${quantity}`, itemTotal);
      });

      total += deliveryFee;
      addLine(packetaLogoUrl, "Packeta", "Doprava", deliveryFee);

      cartElement.append(document.createElement("hr"));
      const totalEl = document.createElement("h2");
      totalEl.className = "cart-total";
      totalEl.textContent = `Spolu ${formatPrice(total)} €`;
      cartElement.append(totalEl, document.createElement("br"));
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
