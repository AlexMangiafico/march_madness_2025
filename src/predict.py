from src.model import load_model_data
from src.data_loader import load_game_data, preprocess_games
from src.metrics import calculate_advanced_metrics
from src.ratings import calculate_team_ratings
from src.train import add_rating_features_to_matchups

from sklearn.preprocessing import StandardScaler
import pandas as pd
import os
import glob
from itertools import combinations, permutations
from typing import List
import joblib

def append_predictions_to_matchups(matchups: pd.DataFrame, model_type) -> pd.DataFrame:
    '''matchups must have TeamID and OppTeamID cols among others'''
    m_predictions = pd.read_csv(f"stored_csvs/m_{model_type}_model_predictions.csv")
    w_predictions = pd.read_csv(f"stored_csvs/w_{model_type}_model_predictions.csv")
    all_predictions = pd.concat([m_predictions, w_predictions], ignore_index=True)
    matchups = matchups.merge(all_predictions, how = 'left', on = ['TeamID', 'OppTeamID', 'Loc', 'Side', 'Season'])
    return matchups

def predict_future_games(matchups: pd.DataFrame, model_path: str):
    """Predict outcomes of future games using trained model."""

    model_data = load_model_data(model_path)
    model = model_data["model"]
    feature_cols = model_data["features"]
    scaler = model_data["scaler"]

    X_future = matchups[feature_cols]
    # Scale the features (using the same scaler used in training)
    if scaler is None:
        # If no scaler is passed, use default
        scaler = StandardScaler()

    X_future_scaled = scaler.transform(X_future)

    if 'nn' in model_path:
        predictions = model.predict(X_future_scaled)  # Probability of the positive class (Win)
    else:
        predictions = model.predict_proba(X_future_scaled)[:, 1]  # Probability of the positive class (Win)
    matchups['Pred'] = predictions
    return matchups




def side_year_possible_matchups(teams, year):
    team_list = teams[(teams['LastD1Season'] >= year) & (teams['FirstD1Season'] <= year)]['TeamID'].tolist()
    #seems a little redundant but allows merges later which is much easier
    unique_combos = list(permutations(team_list, 2))
    no_loc_matchups = pd.DataFrame(unique_combos, columns=['TeamID', 'OppTeamID'])
    no_loc_matchups['Season'] = year
    matchups_by_loc = []
    for loc in [-1,0,1]:
        loc_matchups = no_loc_matchups.copy()
        loc_matchups['Loc'] = loc
        loc_matchups['OppLoc'] = 0 - loc
        matchups_by_loc.append(loc_matchups)

    all_possible_matchups = pd.concat(matchups_by_loc, ignore_index=True)
    return all_possible_matchups

def create_all_possible_matchups(years: range):
    m_all_teams = pd.read_csv('kaggle_data/men/MTeams.csv')
    w_all_teams = pd.read_csv('kaggle_data/women/WTeams.csv')

    # These columns aren't provided, I guess we're supposed to assume the schools have been the same?????
    w_all_teams['FirstD1Season'] = 2000
    w_all_teams['LastD1Season'] = 2025

    m_matchups_by_year = []
    w_matchups_by_year = []

    for year in years:
        m_matchups_by_year.append(side_year_possible_matchups(m_all_teams, year))
        w_matchups_by_year.append(side_year_possible_matchups(w_all_teams, year))

    m_all_possible_matchups = pd.concat(m_matchups_by_year, ignore_index=True)
    w_all_possible_matchups = pd.concat(w_matchups_by_year, ignore_index=True)
    m_all_possible_matchups['Side'] = 'Men'
    w_all_possible_matchups['Side'] = 'Women'

    return m_all_possible_matchups, w_all_possible_matchups

def predict_all_possible_matchups(start_year, end_year, rating_metrics):
    years_to_predict = range(start_year, end_year + 1)

    m_matchups, w_matchups = create_all_possible_matchups(years_to_predict)
    m_matchups_features = add_rating_features_to_matchups(m_matchups, rating_metrics)
    w_matchups_features = add_rating_features_to_matchups(w_matchups, rating_metrics)

    matchup_features = {
        'm': m_matchups_features,
        'w': w_matchups_features
    }



    predict_features = [col for col in m_matchups_features.columns if ('Product' in col or col in ['Loc']) and 'Points' not in col]

    model_files = glob.glob("models/[mw]_*.pkl")

    for model_file in model_files:
        model_name = os.path.splitext(os.path.basename(model_file))[0]  # Extract model name without extension
        prefix = model_name[0]  # Get 'm' or 'w' to determine which features to use

        if prefix in matchup_features:  # Ensure it's a valid model prefix
            predictions = predict_future_games(matchup_features[prefix], model_file)
            predictions = predictions[['TeamID', 'OppTeamID', 'Side', 'Season', 'Loc', 'Pred']]

            # Save to CSV with a name based on the model
            predictions.to_csv(f"stored_csvs/{model_name}_predictions.csv", index=False)



if __name__ == "__main__":
    rating_metrics = ['Score', 'Possessions', 'FGPercent', 'FG3Percent', 'Att3Percent', 'FTPercent', 'ORPercent',
                      'AstPercent', 'PointsPerPoss', 'TOPerPoss', 'StlPerPoss', 'BlkPerPoss', 'PFPerPoss']
    start_predict = 2021
    end_predict = 2025
    predict_all_possible_matchups(start_predict, end_predict, rating_metrics)