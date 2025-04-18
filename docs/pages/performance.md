---
layout: page
title: "Performance"
permalink: /performance/
---

## Comparing Predictions to Actual Results

Now that the 2025 NCAA Tournament has concluded, it's time to analyze how well my model performed. One of the chalkiest tournaments in recent memory presents problems evaluating performance, but the reality of the situation is that the small number of postseason games means there will be a lot of variance. ALl of the chalk was pretty good for my model, which consistently picked favorites with more certainty than betting markets and other models. This was good for a 178th place finish in the March Machine Learning Mania competition on Kaggle ([Leaderboard](https://www.kaggle.com/competitions/march-machine-learning-mania-2025/leaderboard)).


### Notable Hits and Misses:

My biggest hits mostly came when I assigned high probabilities to favorites that other submissions considered more marginal. I routinely picked Connecticut very confidently on the Women's side but they were favored in every game so the reward for each of those games was not huge. The biggest results that helped to separate me from the field were Colorado State's first round over Memphis on the men's side (I gave Colorado State 61% whereas other submissions mostly thought of the game as a pure tossup) and Connecticut's final four victory over UCLA for the women (I gave 75% and the field was around 64%).

My model suffered where there were upsets, most notably Drake's first round upset of Missouri for the men (I gave Missouri 78%) and the South Dakota State women's upset of Oklahoma State (I gave SDSU 81%). The field predicted both these games as 33% chance of an upset, which is a big difference when evaluating using log loss or Brier score.


## Final Thoughts

I have built varied march madness models in the past and I was pleased by the performance of this iteration. I think one drawback to my approach was that I could not train my model on eaerly rounds of data to predict later rounds. Simpler elo setups are able to simulate the first round of the tournament and then adjust team rankings based on those simulated results before simulating the next round. While it may sound counterintuitive to change rankings based on randomized outcomes, it turns out to be correct because if a weak team makes it deep in the tournament then they are more likely to be better than the world thought they were coming in. With my setup, though, I would have had to remake all rankings for every team every round in every simulation before using the logistic model to make new predictions, and that was computationally unrealistic. I did not run into too many issues due to the lack of early upsets, but I do wonder if I'd have been slightly less confident in later round predictions had I been able to include earlier results. In any case, I look forward to making some changes for next year and once again sweating every game of both tournaments.
