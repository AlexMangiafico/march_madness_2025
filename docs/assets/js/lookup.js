console.log("🔧 Script loaded, attempting fetch...");

let data;

fetch("/march_madness_2025/assets/data.json")
  .then(response => response.json())
  .then(json => {
    data = json;
    console.log("✅ Data loaded successfully", data);
  })
  .catch(error => {
    console.error("❌ Failed to load data", error);
  });

function lookupTeam() {
  const input = document.getElementById("teamInput").value.trim().toLowerCase();
  console.log("🔍 Looking up team:", input);

  const result = data.find(entry => entry.Team.toLowerCase() === input);

  if (result) {
    document.getElementById("result").innerText =
      `Win Probability: ${Math.round(result.WinProb * 100)}%`;
  } else {
    document.getElementById("result").innerText = "Team not found.";
  }
}
