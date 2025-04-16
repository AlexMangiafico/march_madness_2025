console.log("🔧 lookup.js loaded");

async function lookupPrediction() {
  const gender = document.getElementById("gender").value;
  const loc = document.getElementById("location").value;
  const team = document.getElementById("teamInput").value.trim().toLowerCase();
  const opp = document.getElementById("oppInput").value.trim().toLowerCase();

  const file = `${gender}_${loc}.json`;
  const url = `/march_madness_2025/assets/${file}`;
  console.log(`📂 Fetching: ${url}`);

  try {
    const response = await fetch(url);
    const data = await response.json();
    console.log(`✅ Loaded ${data.length} records`);

    const match = data.find(entry =>
      entry.TeamName.toLowerCase() === team &&
      entry.OppTeamName.toLowerCase() === opp
    );

    const resultEl = document.getElementById("result");
    if (match) {
      resultEl.innerText = `Predicted Win Probability: ${Math.round(match.Pred * 100)}%`;
    } else {
      resultEl.innerText = "Match not found.";
    }
  } catch (error) {
    console.error("❌ Failed to fetch data", error);
    document.getElementById("result").innerText = "Error loading predictions.";
  }
}
