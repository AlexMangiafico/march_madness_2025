import pandas as pd
from typing import List, Dict


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
    all_team_men_stat_ratings_df.to_csv("stored_csvs/MStatRatings.csv", index=False)

    all_team_women_stat_ratings_df = pd.concat(all_seasons_women_team_ratings, ignore_index=True)
    all_team_women_stat_ratings_df.to_csv("stored_csvs/WStatRatings.csv", index=False)
