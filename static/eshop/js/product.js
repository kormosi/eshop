const addToCartButton = document.getElementById("add-to-cart");
const addToCartButtonOriginalText = addToCartButton.textContent.trim();
let addToCartResetTimeoutId;

addToCartButton.addEventListener("click", function () {
  const productId = this.dataset.productId;
  const cart = getCart();

  cart[productId] = (cart[productId] || 0) + 1;

  saveCart(cart);
  updateCartAppearance();

  clearTimeout(addToCartResetTimeoutId);
  addToCartButton.textContent = "Pridané do košíka ✓";
  addToCartButton.classList.add("added");

  addToCartResetTimeoutId = setTimeout(() => {
    addToCartButton.textContent = addToCartButtonOriginalText;
    addToCartButton.classList.remove("added");
  }, 2000);
});
