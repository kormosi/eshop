document.getElementById("add-to-cart").addEventListener("click", function () {
  const productId = this.dataset.productId;
  const cart = getCart();

  cart[productId] = (cart[productId] || 0) + 1;

  saveCart(cart);
  updateCartAppearance();
});
