---
layout: page
title: "Creation/Prevention"
permalink: /creation_prevention/
---


[Feature Engineering Home]({{ site.baseurl }}/feature_engineering/) | [Useful Metrics]({{ site.baseurl }}/useful_metrics/) | [Creation/Prevention]({{ site.baseurl }}/creation_prevention/)

This is the central idea of my project. Many advanced basketball rating systems (like KenPom or BartTorvik) use Offensive Efficiency and Defensive Efficiency to predict team performance, but I believed that having ratings for only offense and defense was losing valuable information about how teams might match up against one another. Maybe the predictive power of one team rebounding well will be magnified against an opponent that rebounds poorly, or maybe the two effects will be mitigating because there can only be so many rebound opportunities per game. Maybe a team's strong shooting percentage numbers will be compounded by a team that allows high shooting percentages, or maybe the good shooting is more important in matchups against teams that turn the ball over and give up a higher number of shots. Most pressingly, how do all of these interactions change when a good team plays a bad team?

Classically, offensive and defensive efficiencies are measured as:

- **Offensive Rating (ORtg)**: Points scored per 100 possessions  
- **Defensive Rating (DRtg)**: Points allowed per 100 possessions  

When two teams play, each team's expected score can be estimated using:

- **Predicted Score (Team A)** = (Team A ORtg × Team B DRtg) / League Average
- **Predicted Score (Team B)** = (Team B ORtg × Team A DRtg) / League Average

Every team starts with the same rating, say the league average, and then one runs through the season to date, adjusting the offensive and defensive ratings of teams based on the difference between predicted scores and actual scores. After cycling through the season results several times the ratings will stabilize such that every ensuing pass through the results will not significantly impact the ratings.

In this project I attempt to use the same setup to predict the underlying stats of a future basketball game, not skipping right to the final score. If offensive efficiency is the ability to create points and defensive efficiency is the ability to prevent a generic opponent from creating points, I should be able to predict more specific outcomes in the same way, which would allow predictions based on what each team does well and poorly. We already think about some aspects of basketball this way: creating turnovers and not turning the ball over yourself (here framed as preventing the opponent from creating turnovers) are commonly referenced statistics. Some of my other metrics don't map as nicely to obvious goals that all teams share, like having ratings for the percentage of shots a team or its opponents takes from three point range.

The way these ratings are created is also the key to how they should be used. How many assists per made basket would Team A have in a potential matchup with Team B? I can multiply Team A's creation rating for assists per made basket by Team B's prevention rating and divide by the league average. Using all of my ratings like this turns the modeling problem into predicting a winner based on the underlying stats of a game, which is a much easier task.




