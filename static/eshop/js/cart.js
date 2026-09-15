const CART_STORAGE_KEY = "cart";
const CART_MIN_QUANTITY = 1;
const CART_MAX_QUANTITY = 99;

function getCart() {
  return JSON.parse(localStorage.getItem(CART_STORAGE_KEY) || "{}");
}

function saveCart(cart) {
  localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
}

function updateCartAppearance() {
  const cart = getCart();

  // Clamp the product count inside the allowed range
  Object.keys(cart).forEach((id) => {
    cart[id] = Math.max(CART_MIN_QUANTITY, Math.min(CART_MAX_QUANTITY, cart[id]));
  });
  saveCart(cart);

  const count = Object.values(cart).reduce((sum, quantity) => sum + quantity, 0);
  const cartCount = document.getElementById("cart-count");
  cartCount.textContent = count;
  cartCount.hidden = count === 0;
}

updateCartAppearance();
