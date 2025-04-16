---
layout: page
title: "Results"
permalink: /results/
---


## Predictions for the 2025 Tournament


Enter a team name to look up their win probability 458:

<input type="text" id="teamInput" placeholder="e.g. Iowa" />
<button onclick="lookupTeam()">Lookup</button>

<p id="result"></p>

<script>
let data = [];

// Load the data from the JSON file in the assets folder
fetch("/assets/data.json")
  .then(response => response.json())
  .then(json => {
    data = json;
    console.log("Data loaded:", data);
  })
  .catch(error => {
    console.error("Error loading data:", error);
    document.getElementById("result").innerText = "Failed to load team data.";
  });

function lookupTeam() {
  const input = document.getElementById("teamInput").value.trim().toLowerCase();
  const result = data.find(entry => entry.Team.toLowerCase() === input);

  if (result) {
    document.getElementById("result").innerText = `Win Probability: ${Math.round(result.WinProb * 100)}%`;
  } else {
    document.getElementById("result").innerText = "Team not found.";
  }
}
</script>
