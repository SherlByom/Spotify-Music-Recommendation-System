const results = document.getElementById("results");
const cards = document.getElementById("cards");
const helper = document.getElementById("helper");
const input = document.getElementById("query");
const button = document.getElementById("go");

let dropdownElementClicked = false;
let selectedIndex = -1;

function renderCards(items) {
  cards.innerHTML = "";

  if (items.length > 0)
    results.style.display = "grid";
  else {
    results.style.display = "none";
    return;
  }

  items.forEach((item, index) => {
    const cardArea = document.createElement("a");
    cardArea.href = `${item.VIDEO_LINK}`;
    cardArea.target = "_blank";
    cardArea.rel = "noopener";
    cardArea.className = "card-area";

    const card = document.createElement("div");
    card.className = "card";
    card.style.animation = `fadeUp 0.4s ease ${index * 0.08}s forwards`;
    card.style.setProperty("--thumbnail", `url(${item.THUMBNAIL})`);
    card.innerHTML = `
      <div class="title">${item.TRACK_NAME}</div>
      <div class="meta">${item.ARTISTS.replaceAll(";", ", ")}</div>
      <div class="meta">${item.TRACK_GENRE}</div>
    `;

    cardArea.appendChild(card);
    cards.appendChild(cardArea);
  });
}

async function handleRecommend() {
  const url1 = `http://localhost:5000/suggestindex?`;
  const url2 = `http://localhost:5000/suggestname?`;
  const url = dropdownElementClicked ? url1 : url2;
  const value = input.value.trim();
  const k = 8;

  helper.style.color = "var(--muted)";
  helper.textContent = "Searching for suggestions, please wait...";

  if (!value) {
    helper.textContent = "Type a song to get recommendations.";
    return;
  }

  try {
    const suggestionUrl = dropdownElementClicked ? `${url}i=${selectedIndex}&k=${k}` : `${url}song=${value}&k=${k}`;
    const response = await fetch(suggestionUrl);
    
    if (!response.ok)
      throw new Error("Unable to find");

    const result = await response.json();

    if (result.error)
      throw new Error(result.error);

    const song = result.song;
    const suggestions = result.suggestions;

    helper.textContent = `Showing matches for: "${song.TRACK_NAME} - ${song.ARTISTS.replaceAll(";", ", ")}"`;
    renderCards(suggestions);
  }
  catch (error) {
    helper.style.color = "#ff4343";
    helper.textContent = `${error.message}`;
    return;
  }
}

async function getDropdown() {
  const url = `http://localhost:5000/dropdownquery?`;
  const query = input.value.trim();

  try {
    const suggestionUrl = `${url}q=${query}`;
    const response = await fetch(suggestionUrl);

    if (!response.ok)
      throw new Error("Unable to find");

    const result = await response.json();

    if (result.error)
      throw new Error(result.error);

    result.tuples.forEach((name, score, index) => {
      console.log(name);
      console.log(score);
      console.log(index);
    });
  }
  catch (error) {
    console.log("error");
  }
}

let debounceTimer;
button.addEventListener("click", handleRecommend);
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter")
    handleRecommend();
  else if (/^[a-z0-9]$/i.test(event.key)) {
    dropdownElementClicked = false;

    clearTimeout(debounceTimer);
    
    debounceTimer = setTimeout(() => {
      getDropdown();
    }, 300);
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
results.style.display = "none";