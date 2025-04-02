---
layout: page
title: "Useful Metrics"
permalink: /useful_metrics/
---


[Feature Engineering Home]({{ site.baseurl }}/feature_engineering/) | [Useful Metrics]({{ site.baseurl }}/useful_metrics/) | [Creation/Prevention]({{ site.baseurl }}/creation_prevention/) | [Matchup Features]({{ site.baseurl }}/matchup_features/)

When building a predictive model for basketball outcomes, raw stats like field goals made and turnovers don't always tell the full story. To get a clearer picture of a team's performance, I transform these raw numbers into more meaningful metrics that account for pace, efficiency, and contextual factors.

Below, I break down the key new statistics generated in our feature engineering process and explain why they are useful.

Shooting Percentages

Shooting efficiency is a critical factor in evaluating a team's offensive performance. Instead of just using raw field goals made (FGM) and attempted (FGA), I compute shooting percentages:

# Field goal percentage
teamFGPercent = np.where(df[team + 'FGA'] == 0, None, df[team + 'FGM'] / df[team + 'FGA'])

# Three-point percentage
teamFG3Percent = np.where(df[team + 'FGA3'] == 0, None, df[team + 'FGM3'] / df[team + 'FGA3'])

# Free throw percentage
teamFTPercent = np.where(df[team + 'FTA'] == 0, None, df[team + 'FTM'] / df[team + 'FTA'])

Why This Matters

Field Goal Percentage (FG%) tells us how efficiently a team scores overall.

Three-Point Percentage (3P%) isolates long-range shooting ability.

Free Throw Percentage (FT%) matters in close games where free throws can decide the outcome.

Rebounding and Assist Rates

Rebounds and assists contribute significantly to a team's offensive and defensive success, but their raw totals can be misleading. To adjust for context, I calculate percentages instead of just using raw counts.

# Offensive Rebound Percentage
teamORPercent = np.where((df[team + 'OR'] == 0) & (df[other + 'DR'] == 0), None, df[team + 'OR'] / (df[team + 'OR'] + df[other + 'DR']))

# Assist Percentage
teamAstPercent = np.where(df[team + 'FGM'] == 0, None, df[team + 'Ast'] / df[team + 'FGM'])

Why This Matters

Offensive Rebound Percentage (OR%) accounts for missed shots leading to more rebounding opportunities. A team grabbing 10 offensive rebounds might seem impressive, but it matters whether they had 20 or 40 chances.

Assist Percentage (Ast%) measures ball movement and offensive efficiency by tracking how many field goals were assisted rather than made in isolation.

Three-Point Attempt Rate

Some teams rely heavily on three-pointers, while others focus on inside scoring. This metric quantifies a team's tendency to attempt threes.

# Three-Point Attempt Rate
teamAtt3Percent = np.where(df[team + 'FGA'] == 0, None, df[team + 'FGA3'] / df[team + 'FGA'])

Why This Matters

A higher 3P Attempt Rate means a team relies more on perimeter shooting, which can influence variance in game outcomes.

Understanding this helps predict performance against teams that defend the three-point line well.

Per-Possession Stats

Raw totals for points, turnovers, steals, and blocks don’t account for differences in pace (some teams play faster and generate more possessions). To correct this, I normalize these stats per possession.

# Points per possession
teamPointsPerPoss = np.where(df[team + 'Possessions'] == 0, None, df[team + 'Score'] / df[team + 'Possessions'])

# Turnovers per possession
teamTOPerPoss = np.where(df[team + 'Possessions'] == 0, None, df[team + 'TO'] / df[team + 'Possessions'])

# Steals per opponent possession
teamStlPerPoss = np.where(df[other + 'Possessions'] == 0, None, df[team + 'Stl'] / df[other + 'Possessions'])

# Blocks per opponent possession
teamBlkPerPoss = np.where(df[other + 'Possessions'] == 0, None, df[team + 'Blk'] / df[other + 'Possessions'])

# Personal fouls per total possessions in game
teamPFPerPoss = np.where(df[team + 'Possessions'] == 0, None, df[team + 'Stl'] / (df[team + 'Possessions'] + df[other + 'Possessions']))

Why This Matters

Points Per Possession (PPP) measures true scoring efficiency, factoring in pace.

Turnovers Per Possession (TO%) highlights a team's ball security.

Steals & Blocks Per Possession adjust for the fact that teams with more possessions naturally accumulate more steals and blocks.

Personal Fouls Per Possession helps track defensive discipline and potential foul trouble.

Summary

These engineered features help remove biases from raw stats and make comparisons between teams fairer. Instead of relying on absolute numbers, I use rates and percentages to provide a more accurate picture of team strengths and weaknesses.

By incorporating these advanced metrics, our model can make better predictions and offer deeper insights into team performance.
