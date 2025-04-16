---
layout: page
title: "Results"
permalink: /results/
---


## Predictions for the 2025 Tournament


Enter a team name to look up their win probability docs assets 519:

<input type="text" id="teamInput" placeholder="Enter team name">
<button id="lookupButton">Lookup</button>
<p id="result">Waiting for input...</p>

{% raw %}
<script>
let data = [];

// Log when the page is loaded
console.log("🔧 Script loaded, attempting fetch...");

// Fetch data
fetch("/march_madness_2025/assets/data.json")
  .then(response => {
    if (!response.ok) throw new Error("Network response was not ok");
    return response.json();
  })
  .then(json => {
    data = json;
    console.log("✅ Data loaded successfully", data.slice(0, 3)); // log a sample
  })
  .catch(error => {
    console.error("❌ Error loading JSON:", error);
    document.getElementById("result").innerText = "Failed to load data.";
  });

// Lookup function
function lookupTeam() {
  const inputElement = document.getElementById("teamInput");
  const outputElement = document.getElementById("result");

  if (!data || data.length === 0) {
    outputElement.innerText = "Data not loaded yet. Try again in a moment.";
    return;
  }

  const input = inputElement.value.trim().toLowerCase();
  console.log("🔍 Looking up team:", input);

  const result = data.find(entry => entry.Team.toLowerCase() === input);

  if (result) {
    outputElement.innerText = `Win Probability: ${Math.round(result.WinProb * 100)}%`;
    console.log("✅ Match found:", result);
  } else {
    outputElement.innerText = "Team not found.";
    console.log("❌ No match found.");
  }
}

// Add event listener safely
document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("lookupButton");
  if (button) {
    button.addEventListener("click", lookupTeam);
    console.log("🚀 Lookup button connected.");
  } else {
    console.error("❌ Lookup button not found!");
  }
});
</script>
{% endraw %}
