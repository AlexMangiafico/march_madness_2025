from src.model import load_model_data
from src.data_loader import load_game_data, preprocess_games
from src.metrics import calculate_advanced_metrics
from src.ratings import calculate_team_ratings
from src.train import expand_on_wl_cols
from src.predict import append_predictions_to_matchups
from sklearn.metrics import accuracy_score

import pandas as pd
from typing import List


def get_predicted_years(model_type: str) -> List[int]:
    """
    Reads stored model predictions and extracts unique years that have predictions.
    """
    predictions = pd.read_csv(f"stored_csvs/m_{model_type}_model_predictions.csv")
    return predictions['Season'].unique()


def find_test_tourney_games(model_type: str) -> pd.DataFrame:
    """
    Loads and preprocesses tournament game results for seasons where predictions exist.
    Returns separate DataFrames for men's and women's tournaments.
    """
    years = get_predicted_years(model_type)

    # Load and preprocess men's tournament data
    m_ncaa_compact = load_game_data("kaggle_data/men/tournament/MNCAATourneyCompactResults.csv")
    m_ncaa_compact['Tourney'] = 'NCAA'
    m_secondary_compact = load_game_data("kaggle_data/men/tournament/MSecondaryTourneyCompactResults.csv")
    m_secondary_compact.rename(columns={'SecondaryTourney': 'Tourney'}, inplace=True)
    m_compact = pd.concat([m_secondary_compact, m_ncaa_compact], ignore_index=True)
    m_compact['Side'] = 'Men'
    m_compact = m_compact[m_compact['Season'].isin(years)].copy()
    m_compact = preprocess_games(m_compact)

    # Load and preprocess women's tournament data
    w_ncaa_compact = load_game_data("kaggle_data/women/tournament/WNCAATourneyCompactResults.csv")
    w_ncaa_compact['Tourney'] = 'NCAA'
    w_secondary_compact = load_game_data("kaggle_data/women/tournament/WSecondaryTourneyCompactResults.csv")
    w_secondary_compact.rename(columns={'SecondaryTourney': 'Tourney'}, inplace=True)
    w_compact = pd.concat([w_secondary_compact, w_ncaa_compact], ignore_index=True)
    w_compact['Side'] = 'Women'
    w_compact = w_compact[w_compact['Season'].isin(years)].copy()
    w_compact = preprocess_games(w_compact)

    return m_compact, w_compact


def find_mse(predictions: pd.DataFrame, true_col: str, prediction_col: str) -> float:
    """
    Computes the Mean Squared Error (MSE) between actual and predicted values.
    """
    predictions['SquareError'] = (predictions[true_col] - predictions[prediction_col]) ** 2
    return predictions['SquareError'].mean()


def mse_by_tourney(predictions: pd.DataFrame, true_col: str, prediction_col: str) -> None:
    """
    Computes and prints the MSE for each tournament and season.
    """
    for side in ['Men', 'Women']:
        side_tourney_games = predictions[predictions['Side'] == side].copy()
        for eos_tourney in side_tourney_games['Tourney'].unique():
            tourney_games = side_tourney_games[side_tourney_games['Tourney'] == eos_tourney].copy()
            for year in tourney_games['Season'].unique():
                individual_tourney_games = tourney_games[tourney_games['Season'] == year].copy()
                tourney_mse = find_mse(individual_tourney_games, true_col, prediction_col)
                #print(f"{side} {eos_tourney} {year}: {len(individual_tourney_games)} games, MSE = {tourney_mse}")


def backtest_predicted_years(model_types: List[str]) -> None:
    """
    Backtests models by evaluating their predictions against actual tournament results.
    Computes overall and tournament-specific MSE.
    """
    if not model_types:
        print('Input at least one model type to backtest')
        return

    for model_type in model_types:
        print(f'Backtesting {model_type} model')

        # Load test tournament games
        m_test_tourney_games, w_test_tourney_games = find_test_tourney_games(model_type)
        all_test_tourney_games = pd.concat([m_test_tourney_games, w_test_tourney_games], ignore_index=True)

        # Expand win-loss columns and append model predictions
        all_test_tourney_games = expand_on_wl_cols(all_test_tourney_games)
        all_test_tourney_games = append_predictions_to_matchups(all_test_tourney_games, model_type)

        # Compute overall MSE
        all_mse = find_mse(all_test_tourney_games, 'Win', 'Pred')
        print(f'All Tournaments MSE: {all_mse}')

        # Compute MSE by tournament
        mse_by_tourney(all_test_tourney_games, 'Win', 'Pred')


if __name__ == "__main__":
    backtest_predicted_years(['lr'])
