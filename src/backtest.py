from src.model import load_model_data
from src.data_loader import load_game_data, preprocess_games
from src.metrics import calculate_advanced_metrics
from src.ratings import calculate_team_ratings
from src.train import expand_on_wl_cols
from src.predict import append_predictions_to_matchups
from sklearn.metrics import accuracy_score

import pandas as pd

from typing import List

def get_predicted_years(model_type) -> List[int]:
    predictions = pd.read_csv(f"stored_csvs/m_{model_type}_model_predictions.csv")
    predicted_years = predictions['Season'].unique()
    return (predicted_years)

def find_test_tourney_games(model_type) -> pd.DataFrame:
    years = get_predicted_years(model_type)

    m_ncaa_compact = load_game_data("kaggle_data/men/tournament/MNCAATourneyCompactResults.csv")
    m_ncaa_compact['Tourney'] = 'NCAA'
    m_secondary_compact = load_game_data("kaggle_data/men/tournament/MSecondaryTourneyCompactResults.csv")
    m_secondary_compact.rename(columns = {'SecondaryTourney': 'Tourney'}, inplace=True)
    m_compact = pd.concat([m_secondary_compact, m_ncaa_compact], ignore_index=True)
    m_compact['Side'] = 'Men'
    m_compact = m_compact[m_compact['Season'].isin(years)].copy()
    m_compact = preprocess_games(m_compact)

    w_ncaa_compact = load_game_data("kaggle_data/women/tournament/WNCAATourneyCompactResults.csv")
    w_ncaa_compact['Tourney'] = 'NCAA'
    w_secondary_compact = load_game_data("kaggle_data/women/tournament/WSecondaryTourneyCompactResults.csv")
    w_secondary_compact.rename(columns = {'SecondaryTourney': 'Tourney'}, inplace=True)
    w_compact = pd.concat([w_secondary_compact, w_ncaa_compact], ignore_index=True)
    w_compact['Side'] = 'Women'
    w_compact = w_compact[w_compact['Season'].isin(years)].copy()
    w_compact = preprocess_games(w_compact)

    return m_compact, w_compact

def find_mse(predictions, true_col, prediction_col) -> int:
    only_predictions = predictions[[true_col, prediction_col]].copy()
    only_predictions['SquareError'] = abs(predictions[true_col] - predictions[prediction_col])**2
    return only_predictions['SquareError'].mean()

def mse_by_tourney(predictions, true_col, prediction_col):
    for side in ['Men', 'Women']:
        side_tourney_games = predictions[predictions['Side'] == side].copy()
        for eos_tourney in side_tourney_games['Tourney'].unique():
            tourney_games = side_tourney_games[side_tourney_games['Tourney'] == eos_tourney].copy()
            for year in tourney_games['Season'].unique():
                individual_tourney_games = tourney_games[tourney_games['Season'] == year].copy()
                #individual_tourney_games
                tourney_mse = find_mse(individual_tourney_games, 'Win', 'Pred')
                print(side, eos_tourney, year, len(individual_tourney_games), tourney_mse)

def backtest_predicted_years(model_types):
    if not model_types:
        print('Input at least one model type to backtest')
        pass
    for model_type in model_types:
        print('backtesting ' + model_type)
        m_test_tourney_games, w_test_tourney_games = find_test_tourney_games(model_type)
        all_test_tourney_games = pd.concat([m_test_tourney_games, w_test_tourney_games], ignore_index=True)
        all_test_tourney_games = expand_on_wl_cols(all_test_tourney_games)
        all_test_tourney_games = append_predictions_to_matchups(all_test_tourney_games, model_type)
        all_mse = find_mse(all_test_tourney_games, 'Win', 'Pred')
        #Prints by tournament
        #mse_by_tourney(all_test_tourney_games, 'Win', 'Pred')
        print('All Tournaments MSE: ', all_mse)

if __name__ == "__main__":
    backtest_predicted_years(['lr'])