---
layout: page
title: "Results"
permalink: /results/
---


## Predictions for the 2025 Tournament


Enter a team name to look up their win probability docs assets 515:

<input type="text" id="teamInput" placeholder="Enter team name">
<button onclick="lookupTeam()">Lookup</button>
<p id="result"></p>

<script>
let data = [];

// Load the JSON file from the correct path
fetch("/march_madness_2025/assets/data.json")
  .then(response => response.json())
  .then(json => {
    data = json;
    console.log("✅ Data loaded", data);
  })
  .catch(error => {
    console.error("❌ Error loading JSON:", error);
  });

// Lookup function
function lookupTeam() {
  const input = document.getElementById("teamInput").value.trim().toLowerCase();

  if (!data || data.length === 0) {
    document.getElementById("result").innerText = "Data not loaded yet. Please wait a moment.";
    return;
  }

  const result = data.find(entry => entry.Team.toLowerCase() === input);

  if (result) {
    document.getElementById("result").innerText = `Win Probability: ${Math.round(result.WinProb * 100)}%`;
  } else {
    document.getElementById("result").innerText = "Team not found.";
  }
}
</script>
