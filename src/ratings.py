import pandas as pd
from typing import List, Dict


def calculate_team_ratings(games_expanded, creation_ratings, prevention_ratings, metric, metric_average, iterations=10, k=0.01):
    # TODO can also probably produce error metrics here to generate distributions for each of these stats where we could do monte carlo to simulate a game enough to know the winner
    # TODO some way of tracking if we've iterated enough for things to stabilize, some kind of max adj, probably just save the whole frame as prev or something
    # Convert dictionaries to Pandas Series for vectorized operations
    creation_ratings = pd.Series(creation_ratings)
    prevention_ratings = pd.Series(prevention_ratings)

    max_adjust_percent = 1
    while max_adjust_percent > .001:
        teams = games_expanded['TeamID']
        opponents = games_expanded['OppTeamID']

        # Use .loc[] to index series instead of dictionaries
        expected_team_creation = creation_ratings.loc[teams].values * (prevention_ratings.loc[opponents].values / metric_average)
        expected_opponent_creation = creation_ratings.loc[opponents].values * (prevention_ratings.loc[teams].values / metric_average)

        actual_team_metric = games_expanded[metric]
        actual_opponent_metric = games_expanded['Opp' + metric]

        #Weights increase linearly from .5 to 1 over the course of the season?
        day_weights = k * (games_expanded['DayNum']/268+.5)
        #day_weights = k
        #print(day_weights)

        team_performance_adjustments = day_weights * (actual_team_metric - expected_team_creation)
        opponent_performance_adjustments = day_weights * (actual_opponent_metric - expected_opponent_creation)


        # Aggregate adjustments per team
        team_creation_adjustments = pd.DataFrame({'TeamID': teams, 'Adj': team_performance_adjustments}).groupby('TeamID')['Adj'].sum()
        team_prevention_adjustments = pd.DataFrame({'TeamID': teams, 'Adj': opponent_performance_adjustments}).groupby('TeamID')['Adj'].sum()
        opponent_creation_adjustments = pd.DataFrame({'TeamID': opponents, 'Adj': opponent_performance_adjustments}).groupby('TeamID')['Adj'].sum()
        opponent_prevention_adjustments = pd.DataFrame({'TeamID': opponents, 'Adj': team_performance_adjustments}).groupby('TeamID')['Adj'].sum()

        # Apply adjustments using .add() with fill_value=0
        creation_ratings = creation_ratings.add(team_creation_adjustments, fill_value=0)
        prevention_ratings = prevention_ratings.add(opponent_prevention_adjustments, fill_value=0)
        creation_ratings = creation_ratings.add(opponent_creation_adjustments, fill_value=0)
        prevention_ratings = prevention_ratings.add(team_prevention_adjustments, fill_value=0)

        max_adj = max(
            team_creation_adjustments.abs().max(),
            team_prevention_adjustments.abs().max(),
            opponent_creation_adjustments.abs().max(),
            opponent_prevention_adjustments.abs().max()
        )
        max_adjust_percent = max_adj/metric_average
        #print('max adj', max_adj/metric_average)



    # Convert back to DataFrame
    team_ratings = pd.DataFrame({
        'TeamID': creation_ratings.index,
        metric + 'CreationRating': creation_ratings.values,
        metric + 'PreventionRating': prevention_ratings.values
    })

    return team_ratings



def build_rating_features(games: pd.DataFrame, all_rating_metrics: List[str]):
    all_seasons_men_team_ratings = []
    all_seasons_women_team_ratings = []
    for side in ['Men', 'Women']:
        side_games = games[games['Side'] == side].copy()
        seasons = side_games['Season'].unique()
        for y in seasons:
            year_games = side_games[side_games['Season'] == y].copy()
            all_metrics = None
            for m in all_rating_metrics:

                #print('Side', side, 'Running Season', y, 'Metric', m)
                year_teams = year_games['TeamID'].unique()

                metric_average = year_games[m].mean()
                #print(metric_average)

                creation_ratings = {team: metric_average for team in year_teams}  # Starting offensive rating of 100 for all teams
                prevention_ratings = {team: metric_average for team in year_teams}  # Starting defensive rating of 100 for all teams

                #TODO can weight k here by how late in the season it is or something
                year_metric_team_ratings = calculate_team_ratings(year_games, creation_ratings, prevention_ratings, m, metric_average, iterations = 10, k=.01)
                year_metric_team_ratings[m + 'LeagueAverage'] = metric_average

                if all_metrics is None:
                    all_metrics = year_metric_team_ratings
                else:
                    all_metrics = all_metrics.merge(year_metric_team_ratings, on = 'TeamID')


            all_metrics['Season'] = y

            #print(year_team_ratings.head())
            if side == 'Men':
                all_seasons_men_team_ratings.append(all_metrics)
            else:
                all_seasons_women_team_ratings.append(all_metrics)


    #Higher prevention rating means the other team gets more of this metric against you
    all_team_men_stat_ratings_df = pd.concat(all_seasons_men_team_ratings, ignore_index=True)
    all_team_men_stat_ratings_df.to_csv("stored_csvs/MStatRatings.csv", index=False)

    all_team_women_stat_ratings_df = pd.concat(all_seasons_women_team_ratings, ignore_index=True)
    all_team_women_stat_ratings_df.to_csv("stored_csvs/WStatRatings.csv", index=False)