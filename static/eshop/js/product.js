const addToCartButton = document.getElementById("add-to-cart");
const addToCartButtonOriginalText = addToCartButton.textContent.trim();
const cartIcon = document.querySelector(".cart-icon");
let addToCartResetTimeoutId;

function shakeCartIcon() {
  cartIcon.classList.remove("shake");
  void cartIcon.offsetWidth; // restart the animation even on repeated clicks
  cartIcon.classList.add("shake");
}

addToCartButton.addEventListener("click", function () {
  const productId = this.dataset.productId;
  const cart = getCart();

  cart[productId] = (cart[productId] || 0) + 1;

  saveCart(cart);
  updateCartAppearance();

  clearTimeout(addToCartResetTimeoutId);
  addToCartButton.textContent = "Pridané do košíka ✓";
  addToCartButton.classList.add("added");
  
  shakeCartIcon();

  addToCartResetTimeoutId = setTimeout(() => {
    addToCartButton.textContent = addToCartButtonOriginalText;
    addToCartButton.classList.remove("added");
  }, 1750);
});
