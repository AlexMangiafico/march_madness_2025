---
layout: page
title: "Results"
permalink: /results/
---


## Predictions for the 2025 Tournament


Enter a team name to look up their win probability docs assets 524:

<h2>Prediction Lookup</h2>

<select id="gender">
  <option value="m">Men</option>
  <option value="w">Women</option>
</select>

<label for="location">Team 1 Location:</label>
<select id="location">
  <option value="home">Home</option>
  <option value="away">Away</option>
  <option value="neutral">Neutral</option>
</select>

<input type="text" id="teamInput" placeholder="Team Name">
<input type="text" id="oppInput" placeholder="Opponent Team Name">
<button onclick="lookupPrediction()">Look Up</button>

<p id="result"></p>

<script src="/march_madness_2025/assets/js/lookup.js"></script>

