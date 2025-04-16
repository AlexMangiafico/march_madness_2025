---
layout: page
title: "Creation/Prevention"
permalink: /creation_prevention/
---


[Feature Engineering Home]({{ site.baseurl }}/feature_engineering/) | [Useful Metrics]({{ site.baseurl }}/useful_metrics/) | [Creation/Prevention]({{ site.baseurl }}/creation_prevention/) | [Matchup Features]({{ site.baseurl }}/matchup_features/)

This is the central idea of my project. Many advanced basketball rating systems (like KenPom or BartTorvik) use Offensive Efficiency and Defensive Efficiency to predict team performance, but I believed that having ratings for only offense and defense was losing valuable information about how teams might match up against one another. Maybe the predictive power of one team rebounding well will be magnified against an opponent that rebounds poorly, or maybe the two effects will be mitigating because there can only be so many rebound opportunities per game. Maybe a team's strong shooting percentage numbers will be compounded by a team that allows high shooting percentages, or maybe the good shooting is more important in matchups against teams that turn the ball over and give up a higher number of shots. Most pressingly, how do all of these interactions change when a good team plays a bad team?

Classically, offensive and defensive efficiencies are measured as:

- **Offensive Rating (ORtg)**: Points scored per 100 possessions  
- **Defensive Rating (DRtg)**: Points allowed per 100 possessions  

When two teams play, each team's expected score can be estimated using:

- **Predicted Score (Team A)** = (Team A ORtg × Team B DRtg) / League Average
- **Predicted Score (Team B)** = (Team B ORtg × Team A DRtg) / League Average

In this project I attempt to use the same setup to predict the underlying stats of a future basketball game. If offensive efficiency is the ability to create points and defensive efficiency is the ability to prevent a generic opponent from creating points, I should be able to predict more specific outcomes in the same way. We already think about some aspects of basketball this way: creating turnovers and not turning the ball over yourself (here framed as preventing the opponent from creating turnovers) are commonly referenced statistics. Some of my other metrics don't map as nicely to existing language, like creation of 
