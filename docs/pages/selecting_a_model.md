---
layout: page
title: "Selecting a Model"
permalink: /selecting_a_model/
---



<!-- [Selecting a Model]({{ site.baseurl }}/selecting_a_model/) |  [Random Forest]({{ site.baseurl }}/random_forest/) |  [Neural Network]({{ site.baseurl }}/neural_network/) |  [Logistic Regression]({{ site.baseurl }}/logistic_regression/) |  [Backtesting]({{ site.baseurl }}/backtesting/) -->

With a set of features engineered to represent how teams create and prevent specific statistical outcomes, the next step was to choose a model capable of using these features to predict game results. I tested three different approaches: logistic regression, random forest, and a neural network. Each model used the predicted per-matchup statistics—such as estimated shooting percentages, expected turnover margins, and rebounding interactions—to generate win probabilities for each team.

While the random forest and neural network models provided flexible ways to capture complex nonlinear relationships, logistic regression proved to be the most effective option for this project. Its performance on backtesting—evaluated using log loss and predictive accuracy across past NCAA tournaments—was comparable to or better than the more complex models. Given its simplicity, speed, and interpretability, logistic regression was ultimately the best fit for a modeling pipeline that already incorporated significant domain knowledge through feature construction.

![Chart](backtesting_graphs.png)

Each model was tested by simulating previous tournaments using only the information available prior to each game. This allowed a direct comparison of how well each approach translated pregame features into accurate win probabilities. Logistic regression consistently performed well across multiple tournament years, suggesting it generalized effectively to new data.

In addition to strong performance metrics, logistic regression also provided clear insight into how individual features influenced predictions, which is useful for understanding the behavior of the model in edge cases and for communicating results. For these reasons, it was selected as the modeling approach for the remainder of the project.
