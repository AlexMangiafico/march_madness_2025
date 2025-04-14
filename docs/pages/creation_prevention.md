---
layout: page
title: "Creation/Prevention"
permalink: /creation_prevention/
---


[Feature Engineering Home]({{ site.baseurl }}/feature_engineering/) | [Useful Metrics]({{ site.baseurl }}/useful_metrics/) | [Creation/Prevention]({{ site.baseurl }}/creation_prevention/) | [Matchup Features]({{ site.baseurl }}/matchup_features/)

```python
import pandas as pd
from typing import List, Dict
```


```python
def calculate_team_ratings(games_expanded, creation_ratings, prevention_ratings, metric, metric_average, iterations=10,
                           k=0.01):
    """
    Adjusts and calculates team ratings based on game performance metrics, iterating until adjustments stabilize.

    The function calculates team performance adjustments by comparing actual game metrics against expected metrics,
    then iteratively updates team ratings (both creation and prevention ratings) until the adjustments are sufficiently small.
    The rate of adjustment is weighted based on the day number of the season.
    """

    # Convert dictionaries to Pandas Series for vectorized operations
    creation_ratings = pd.Series(creation_ratings)
    prevention_ratings = pd.Series(prevention_ratings)

    max_adjust_percent = 1
    while max_adjust_percent > .001:
        teams = games_expanded['TeamID']
        opponents = games_expanded['OppTeamID']

        # Compute expected team and opponent metrics based on ratings
        expected_team_creation = creation_ratings.loc[teams].values * (
                    prevention_ratings.loc[opponents].values / metric_average)
        expected_opponent_creation = creation_ratings.loc[opponents].values * (
                    prevention_ratings.loc[teams].values / metric_average)

        actual_team_metric = games_expanded[metric]
        actual_opponent_metric = games_expanded['Opp' + metric]

        # Weight adjustments by the day number
        day_weights = k * (games_expanded['DayNum'] / 268 + .5)

        # Calculate performance adjustments for teams and opponents
        team_performance_adjustments = day_weights * (actual_team_metric - expected_team_creation)
        opponent_performance_adjustments = day_weights * (actual_opponent_metric - expected_opponent_creation)

        # Aggregate adjustments per team
        team_creation_adjustments = \
        pd.DataFrame({'TeamID': teams, 'Adj': team_performance_adjustments}).groupby('TeamID')['Adj'].sum()
        team_prevention_adjustments = \
        pd.DataFrame({'TeamID': teams, 'Adj': opponent_performance_adjustments}).groupby('TeamID')['Adj'].sum()
        opponent_creation_adjustments = \
        pd.DataFrame({'TeamID': opponents, 'Adj': opponent_performance_adjustments}).groupby('TeamID')['Adj'].sum()
        opponent_prevention_adjustments = \
        pd.DataFrame({'TeamID': opponents, 'Adj': team_performance_adjustments}).groupby('TeamID')['Adj'].sum()

        # Apply adjustments
        creation_ratings = creation_ratings.add(team_creation_adjustments, fill_value=0)
        prevention_ratings = prevention_ratings.add(opponent_prevention_adjustments, fill_value=0)
        creation_ratings = creation_ratings.add(opponent_creation_adjustments, fill_value=0)
        prevention_ratings = prevention_ratings.add(team_prevention_adjustments, fill_value=0)

        # Calculate the maximum adjustment and check if it is small enough to stop iterating
        max_adj = max(
            team_creation_adjustments.abs().max(),
            team_prevention_adjustments.abs().max(),
            opponent_creation_adjustments.abs().max(),
            opponent_prevention_adjustments.abs().max()
        )
        max_adjust_percent = max_adj / metric_average

    # Convert the final ratings back to a DataFrame
    team_ratings = pd.DataFrame({
        'TeamID': creation_ratings.index,
        metric + 'CreationRating': creation_ratings.values,
        metric + 'PreventionRating': prevention_ratings.values
    })

    return team_ratings
```


```python
def build_rating_features(games: pd.DataFrame, all_rating_metrics: List[str]):
    """
    Builds team rating features for each season and metric, iterating over both men and women teams.

    The function calculates team ratings for each season based on the provided rating metrics. For each metric, it
    computes the creation and prevention ratings for each team using `calculate_team_ratings`, then merges the results
    across different seasons and teams. These ratings are saved to CSV files for both men and women teams.
    """

    all_seasons_men_team_ratings = []
    all_seasons_women_team_ratings = []
    for side in ['Men', 'Women']:
        side_games = games[games['Side'] == side].copy()
        seasons = side_games['Season'].unique()
        for y in seasons:
            year_games = side_games[side_games['Season'] == y].copy()
            all_metrics = None
            for m in all_rating_metrics:
                year_teams = year_games['TeamID'].unique()

                metric_average = year_games[m].mean()

                creation_ratings = {team: metric_average for team in
                                    year_teams}  # Starting offensive rating of 100 for all teams
                prevention_ratings = {team: metric_average for team in
                                      year_teams}  # Starting defensive rating of 100 for all teams

                year_metric_team_ratings = calculate_team_ratings(year_games, creation_ratings, prevention_ratings, m,
                                                                  metric_average, iterations=10, k=.01)
                year_metric_team_ratings[m + 'LeagueAverage'] = metric_average

                if all_metrics is None:
                    all_metrics = year_metric_team_ratings
                else:
                    all_metrics = all_metrics.merge(year_metric_team_ratings, on='TeamID')

            all_metrics['Season'] = y

            if side == 'Men':
                all_seasons_men_team_ratings.append(all_metrics)
            else:
                all_seasons_women_team_ratings.append(all_metrics)

    # Save the final ratings to CSV files
    all_team_men_stat_ratings_df = pd.concat(all_seasons_men_team_ratings, ignore_index=True)
    all_team_women_stat_ratings_df = pd.concat(all_seasons_women_team_ratings, ignore_index=True)

    return all_team_men_stat_ratings_df, all_team_women_stat_ratings_df

```


```python
games_expanded_detailed = pd.read_csv('useful_metrics_end.csv')

rating_metrics = ['Score', 'Possessions', 'FGPercent', 'FG3Percent', 'Att3Percent', 'FTPercent', 'ORPercent',
                      'AstPercent', 'PointsPerPoss', 'TOPerPoss', 'StlPerPoss', 'BlkPerPoss', 'PFPerPoss']

m_ratings, w_ratings = build_rating_features(games_expanded_detailed, rating_metrics)

```


```python
print(m_ratings)
```

          TeamID  ScoreCreationRating  ScorePreventionRating  ScoreLeagueAverage  \
    0       1102            56.744189              55.333151           69.775997   
    1       1103            77.074126              77.602896           69.775997   
    2       1104            75.469963              62.195261           69.775997   
    3       1105            67.018756              81.717981           69.775997   
    4       1106            58.765530              65.894485           69.775997   
    ...      ...                  ...                    ...                 ...   
    7976    1476            64.590828              76.186996           72.779560   
    7977    1477            64.295711              76.376560           72.779560   
    7978    1478            70.855866              88.048718           72.779560   
    7979    1479            64.479751              78.055171           72.779560   
    7980    1480            65.534550              79.628931           72.779560   
    
          PossessionsCreationRating  PossessionsPreventionRating  \
    0                     54.583529                    54.175379   
    1                     69.983576                    69.969042   
    2                     66.797516                    66.740225   
    3                     74.502880                    73.507844   
    4                     65.713362                    65.098640   
    ...                         ...                          ...   
    7976                  65.360607                    65.661251   
    7977                  68.852464                    68.426272   
    7978                  70.633880                    70.681162   
    7979                  65.706588                    66.313612   
    7980                  68.860435                    68.895262   
    
          PossessionsLeagueAverage  FGPercentCreationRating  \
    0                    68.364606                 0.486247   
    1                    68.364606                 0.479433   
    2                    68.364606                 0.447284   
    3                    68.364606                 0.383960   
    4                    68.364606                 0.409195   
    ...                        ...                      ...   
    7976                 68.866208                 0.418853   
    7977                 68.866208                 0.413980   
    7978                 68.866208                 0.443869   
    7979                 68.866208                 0.412814   
    7980                 68.866208                 0.418822   
    
          FGPercentPreventionRating  FGPercentLeagueAverage  ...  \
    0                      0.449625                0.440157  ...   
    1                      0.485226                0.440157  ...   
    2                      0.400868                0.440157  ...   
    3                      0.489388                0.440157  ...   
    4                      0.432545                0.440157  ...   
    ...                         ...                     ...  ...   
    7976                   0.476268                0.443881  ...   
    7977                   0.483552                0.443881  ...   
    7978                   0.498108                0.443881  ...   
    7979                   0.500161                0.443881  ...   
    7980                   0.491535                0.443881  ...   
    
          StlPerPossCreationRating  StlPerPossPreventionRating  \
    0                     0.112997                    0.099914   
    1                     0.099152                    0.100469   
    2                     0.102707                    0.077734   
    3                     0.114869                    0.117383   
    4                     0.122836                    0.129141   
    ...                        ...                         ...   
    7976                  0.082549                    0.106565   
    7977                  0.123601                    0.118205   
    7978                  0.088511                    0.113859   
    7979                  0.092371                    0.089724   
    7980                  0.098263                    0.096671   
    
          StlPerPossLeagueAverage  BlkPerPossCreationRating  \
    0                    0.102906                  0.034301   
    1                    0.102906                  0.035870   
    2                    0.102906                  0.067973   
    3                    0.102906                  0.027841   
    4                    0.102906                  0.046638   
    ...                       ...                       ...   
    7976                 0.096651                  0.036721   
    7977                 0.096651                  0.050833   
    7978                 0.096651                  0.026530   
    7979                 0.096651                  0.025546   
    7980                 0.096651                  0.039342   
    
          BlkPerPossPreventionRating  BlkPerPossLeagueAverage  \
    0                       0.028565                 0.047626   
    1                       0.042770                 0.047626   
    2                       0.039024                 0.047626   
    3                       0.063213                 0.047626   
    4                       0.049501                 0.047626   
    ...                          ...                      ...   
    7976                    0.064226                 0.048359   
    7977                    0.056088                 0.048359   
    7978                    0.048850                 0.048359   
    7979                    0.048492                 0.048359   
    7980                    0.045996                 0.048359   
    
          PFPerPossCreationRating  PFPerPossPreventionRating  \
    0                    0.056321                   0.050032   
    1                    0.049594                   0.050243   
    2                    0.051240                   0.038974   
    3                    0.057110                   0.059141   
    4                    0.060975                   0.064844   
    ...                       ...                        ...   
    7976                 0.041374                   0.053159   
    7977                 0.061681                   0.059473   
    7978                 0.044351                   0.056840   
    7979                 0.046503                   0.044639   
    7980                 0.049198                   0.048462   
    
          PFPerPossLeagueAverage  Season  
    0                   0.051457    2003  
    1                   0.051457    2003  
    2                   0.051457    2003  
    3                   0.051457    2003  
    4                   0.051457    2003  
    ...                      ...     ...  
    7976                0.048320    2025  
    7977                0.048320    2025  
    7978                0.048320    2025  
    7979                0.048320    2025  
    7980                0.048320    2025  
    
    [7981 rows x 41 columns]



```python

```
