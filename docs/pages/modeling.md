---
layout: page
title: "Modeling"
permalink: /modeling/
---

# Modeling Overview

## Creating Advanced Metrics

The first step in our analytical journey involves generating **advanced basketball metrics** that go beyond simple box scores like points, rebounds, or assists. These new metrics provide deeper insights into team and player performance, helping us evaluate how effectively a team is performing in key areas.

### Developing Advanced Offensive and Defensive Rankings

In addition to basic stats, we also developed advanced **offensive** and **defensive rankings** based on several key performance indicators (KPIs) that go beyond points scored or allowed. These rankings incorporate metrics such as:

- **Effective Field Goal Percentage (eFG%)**: A measure that accounts for the added value of three-pointers.
- **Turnover Rate**: A team's ability to limit turnovers or capitalize on forced turnovers.
- **Assist-to-Turnover Ratio**: A metric that evaluates a team's ball movement and decision-making under pressure.
- **Defensive Rebound Percentage**: A measure of how well a team finishes defensive possessions by grabbing rebounds.

By weighting these metrics based on their impact in a given game or season, we created rankings that provide a more holistic view of a team's performance on both sides of the ball.

## Modeling Game Outcomes

With these advanced metrics in hand, we began modeling game outcomes based on the combination of offensive and defensive rankings we generated. The goal was to predict the outcome of March Madness games by evaluating team matchups through the lens of these metrics rather than relying solely on traditional stats like points scored or allowed.

### Logistic Regression (LogReg)

The first modeling approach we tried was **Logistic Regression (LogReg)**. This model is a classic choice for binary classification problems, making it a natural fit for predicting the outcome of games (win or loss). By using the team rankings and various advanced metrics as input features, we trained the model to predict the probability of a team winning given their offensive and defensive capabilities.

### Random Forests

Next, we experimented with **Random Forests**, a powerful ensemble method that can handle a mix of categorical and numerical features. Random Forests are well-suited for capturing non-linear relationships in the data, making them ideal for this kind of problem. The model was trained using the same set of features, and it was able to detect complex patterns and interactions between the metrics that might not be obvious from a simple logistic regression.

Random Forests also provided important **feature importance** metrics, helping us identify which advanced stats were most influential in predicting game outcomes. For example, it was found that offensive rebounding allowed and assist-to-turnover ratio were some of the key factors in predicting upsets.

### Neural Networks

Finally, we tested **Neural Networks** as a more sophisticated, non-linear model for predicting game outcomes. Neural networks are particularly useful when dealing with large, complex datasets with many features, like the ones we had with multiple advanced metrics. We trained a neural network to predict game outcomes based on the input features of each team, adjusting the model architecture and hyperparameters to maximize performance.

Neural networks allowed us to capture intricate patterns in the data, but the results were more difficult to interpret than with Random Forests. Despite this, the model performed well, especially when paired with feature engineering and hyperparameter tuning.

## Model Evaluation

We evaluated all three models—Logistic Regression, Random Forests, and Neural Networks—using **cross-validation** and metrics like **accuracy**, **precision**, **recall**, and **F1-score**. The Random Forests model outperformed the others, but the Neural Network showed promise when hyperparameters were fine-tuned.

## Conclusion

Through the process of creating advanced metrics and applying machine learning techniques, we were able to develop models that predict March Madness game outcomes with greater precision than traditional statistical approaches. By focusing on advanced team rankings and key performance indicators, we gained valuable insights into how different aspects of the game—beyond just points scored—affect the outcome of a matchup. The combination of advanced metrics and machine learning models enables a deeper understanding of team dynamics and provides a competitive edge when predicting game outcomes.

---
Stay tuned for more updates on our model's performance and improvements as we dive deeper into the data and refine our methods!
