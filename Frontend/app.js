const suggestions = [];

const cards = document.getElementById("cards");
const helper = document.getElementById("helper");
const input = document.getElementById("query");
const button = document.getElementById("go");
const resultHead = document.querySelector(".results-head")

function renderCards(items) {
  cards.innerHTML = "";

  if (items.length > 0)
    resultHead.style.display = "block";
  else {
    resultHead.style.display = "none";
    return;
  }

  items.forEach((item, idx) => {
    const card = document.createElement("div");
    card.className = "card";
    card.style.animation = `fadeUp 0.4s ease ${idx * 0.08}s forwards`;
    card.innerHTML = `
      <div class="title">${item.title}</div>
      <div class="meta">${item.artist}</div>
      <div class="meta">${item.mood}</div>
    `;
    cards.appendChild(card);
  });
}

function handleRecommend() {
  const value = input.value.trim();
  if (!value) {
    helper.textContent = "Type a song to get recommendations.";
    return;
  }
  helper.textContent = `Showing matches for: "${value}"`;
  renderCards(suggestions);
}

button.addEventListener("click", handleRecommend);
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    handleRecommend();
  }
});

const style = document.createElement("style");
style.textContent = `
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .card { opacity: 0; }
`;

document.head.appendChild(style);
renderCards(suggestions);
