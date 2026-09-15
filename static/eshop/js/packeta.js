const packetaApiKey = "";

const packetaOptions = {
  country: "cz,sk",
  language: "sk",
  view: "modal",
  defaultCurrency: "EUR",
};

function showSelectedPickupPoint(point) {
  if (!point) {
    return;
  }

  document.getElementById("pickup-point-error").hidden = true;
  document.getElementById("packeta-selector-value").innerText = point.name;
  document.getElementById("pickup-point-id").value = point.id;
  document.getElementById("pickup-point-address").value = point.routingName;
}

document.querySelector(".packeta-selector-open").addEventListener("click", function () {
  Packeta.Widget.pick(packetaApiKey, showSelectedPickupPoint, packetaOptions);
});
