const results = document.getElementById("results");
const cards = document.getElementById("cards");
const helper = document.getElementById("helper");
const input = document.getElementById("query");
const button = document.getElementById("go");

function renderCards(items) {
  cards.innerHTML = "";

  if (items.length > 0)
    results.style.display = "grid";
  else {
    results.style.display = "none";
    return;
  }

  items.forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "card";
    card.style.animation = `fadeUp 0.4s ease ${index * 0.08}s forwards`;
    card.innerHTML = `
      <div class="title">${item.TRACK_NAME}</div>
      <div class="meta">${item.ARTISTS.replaceAll(";", ", ")}</div>
      <div class="meta">${item.TRACK_GENRE}</div>
    `;
    cards.appendChild(card);
  });
}

async function handleRecommend() {
  const value = input.value.trim();
  const k = 8;

  helper.style.color = "var(--muted)";
  helper.textContent = "Searchnig for suggestions, please wait..."

  if (!value) {
    helper.textContent = "Type a song to get recommendations.";
    return;
  }

  try {
    const suggestionUrl = `http://localhost:5000/suggest?song=${value}&k=${k}`;
    const response = await fetch(suggestionUrl);

    if (!response.ok)
      throw new Error();

    const result = await response.json();
    const song = result.song;
    const suggestions = result.suggestions;

    helper.textContent = `Showing matches for: "${song.TRACK_NAME} - ${song.ARTISTS.replaceAll(";", ", ")}"`;
    renderCards(suggestions);
  }
  catch (error) {
    helper.style.color = "#ff4343";
    helper.textContent = `Something went wrong`;
    return;
  }
}

button.addEventListener("click", handleRecommend);
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter")
    handleRecommend();
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
results.style.display = "none";