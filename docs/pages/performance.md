---
layout: page
title: "Performance"
permalink: /performance/
---

## Comparing Predictions to Actual Results

Now that the **2025 NCAA Tournament** has concluded, it's time to analyze how well our **logistic regression model** performed. We’ll compare:
- **Pre-Tournament Win Probabilities vs. Actual Outcomes**
- **Bracket Performance Metrics**
- **Key Hits & Misses** in Our Predictions

---

## Model Accuracy and Metrics

We evaluate our model’s performance using the following key metrics:

| Metric                | Score  |
|-----------------------|--------|
| Overall Accuracy     | **XX%** |
| Log Loss            | **X.XX** |
| Brier Score        | **X.XX** |
| Bracket Performance | **Top X% of ESPN entries** |

- **Accuracy**: The percentage of correctly predicted game winners.
- **Log Loss**: Measures how well our probability estimates matched actual outcomes (lower is better).
- **Brier Score**: Evaluates the calibration of our probability predictions.
- **Bracket Performance**: Where our bracket ranked among public contests.

---

## Key Insights from Tournament Performance

### Hits: Where the Model Got It Right ✅

1. **Cinderella Predictions**
   - Our model flagged **[Team X] (Seed #X)** as a strong upset candidate, giving them a **Y%** chance to win their first-round game—significantly higher than public consensus. They advanced to the **Sweet 16**.
   - Another lower-seeded team, **[Team Y]**, was identified as undervalued in offensive efficiency. They pulled off multiple wins before falling in the **Elite Eight**.

2. **Overrated High Seeds**
   - The model **downgraded [Team Z]**, a #2 seed, due to weak defensive efficiency metrics. They were eliminated in the **Round of 32**, aligning with our lower-than-expected win probability.
   - **Another high seed**, [Team A], was predicted to struggle against a **high-tempo, three-point shooting opponent**—which proved accurate.

3. **Final Four Projections**
   - The model correctly identified **X out of 4** Final Four teams.
   - Our **most probable champion** reached the title game, demonstrating strong predictive power.

---

### Misses: Where the Model Fell Short ❌

1. **Underrating a Surprise Team**
   - **[Team B]**, a lower seed, made a deep run despite low predicted odds. The model **undervalued** their defensive adjustments and late-season performance surge.
   - This suggests a need to incorporate **momentum factors or late-season performance trends**.

2. **Unexpected Early Exits**
   - The model **overestimated** the chances of **[Team C]**, a top-ranked team, advancing to the Final Four. A key injury and poor shooting performance led to an **early exit**.
   - This highlights the difficulty of accounting for **in-game variability and injuries** in pre-tournament models.

---

## Bracket Performance Visualization

Below is a **comparison of our predicted bracket vs. the actual tournament results**:

![Bracket Performance](images/bracket_performance.png)

- **Green**: Correctly predicted winners.
- **Red**: Incorrect predictions.
- **Blue**: Unexpected upsets.

Additionally, here’s a **scatter plot of predicted win probabilities vs. actual outcomes**:

![Prediction Accuracy](images/prediction_accuracy.png)

This visualization helps identify systematic **biases in the model**—for example, whether it consistently **overestimated or underestimated** certain seed ranges.

---

## Lessons & Model Improvements for Next Year

### 1. Incorporating Late-Season Trends 📈
- Teams that improved significantly in the final month were **undervalued** by our model.
- Solution: Introduce **weighted recent performance metrics** to adjust for hot streaks.

### 2. Accounting for Play Style & Matchup Dependencies 🎯
- Some teams performed **better/worse than expected** based on matchup-specific factors.
- Solution: Add **synergy metrics** that assess strengths/weaknesses against specific opponents.

### 3. Adjusting for Injuries & Depth 🚑
- The model didn’t account for **key injuries** or **bench depth**, which affected certain results.
- Solution: Explore integrating **real-time injury reports** and **bench contribution metrics**.

---

## Final Thoughts

While no model can **perfectly predict** March Madness, our **data-driven approach** outperformed most traditional bracket strategies. By refining our methodology and incorporating lessons from this year's tournament, we aim to build an even **stronger predictive model for 2026**.

Stay tuned for **updated methodologies and expanded data sources for next year’s predictions!** 🚀
