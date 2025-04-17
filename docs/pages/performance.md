---
layout: page
title: "Performance"
permalink: /performance/
---

## Comparing Predictions to Actual Results

Now that the 2025 NCAA Tournament has concluded, it's time to analyze how well my model performed. One of the chalkiest tournaments in recent memory presents problems evaluating performance, but the reality of the situation is that the small number of postseason games means there will be a lot of variance. ALl of the chalk was pretty good for my model, which consistently picked favorites with more certainty than betting markets and other models. This was good for a 178th place finish in the March Machine Learning Mania competition on Kaggle

https://www.kaggle.com/competitions/march-machine-learning-mania-2025/leaderboard




### Hits: Where the Model Got It Right

My biggest hits mostly came when I assigned 

### Misses: Where the Model Fell Short

My model 
My biggest miss on the men's side was Drake's first round upset of Missouri where I gave Missouri a 78% chance to win. Other models predicted Missouri around 67%.
On the women's side, I gave Oklahoma State 81% chance to beat South Dakota State in the first round, compared to a 67% average prediction from Kaggle experts.


[March Madness Machine Learning Mania](https://www.kaggle.com/competitions/march-machine-learning-mania-2025)


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
