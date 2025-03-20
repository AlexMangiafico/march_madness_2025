from src.model import load_model_data
from src.data_loader import load_game_data, preprocess_games
from src.metrics import calculate_advanced_metrics
from src.ratings import calculate_team_ratings
from src.train import add_rating_features_to_matchups

from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import os
import glob
from itertools import combinations, permutations
from typing import List
import joblib


def save_kaggle_submission(year):
    """
    Generate and save Kaggle submission for the given year.
    This includes processing matchups, predicting outcomes, and comparing to a sample submission.
    """
    from src.simulate import get_seeds_slots

    # Generate possible matchups for men and women
    m_matchups, w_matchups = create_all_possible_matchups(range(year, year + 1))
    m_kaggle_matchups = m_matchups[m_matchups['Loc'] == 0]

    # Get seed and slot data for women teams
    w_seeds, w_slots = get_seeds_slots(year, 'Women')
    w_opp_seeds = w_seeds.copy().rename(columns={'TeamID': 'OppTeamID'})

    # Merge seed data into matchups
    w_matchups = w_matchups.merge(w_seeds, how='left', on=['Season', 'TeamID'])
    w_matchups.rename(columns={'Seed': 'TeamSeed'}, inplace=True)
    w_matchups = w_matchups.merge(w_opp_seeds, how='left', on=['Season', 'OppTeamID'])
    w_matchups.rename(columns={'Seed': 'OppTeamSeed'}, inplace=True)

    # Extract seed numbers and regions
    w_matchups['TeamSeedNumber'] = w_matchups['TeamSeed'].str.slice(1)
    w_matchups['OppTeamSeedNumber'] = w_matchups['OppTeamSeed'].str.slice(1)
    w_matchups['TeamRegion'] = w_matchups['TeamSeed'].str.slice(0, 1)
    w_matchups['OppTeamRegion'] = w_matchups['OppTeamSeed'].str.slice(0, 1)

    # Determine if matchups are within the same region
    w_matchups['SameRegion'] = np.where(
        (w_matchups['TeamRegion'] == w_matchups['OppTeamRegion']) & pd.notna(w_matchups['TeamRegion']) & pd.notna(
            w_matchups['OppTeamRegion']),
        True, False)

    # Assign tournament matchup locations based on region and seed
    w_matchups['TourneyMatchupLoc'] = np.where(
        w_matchups['SameRegion'],
        np.select(
            [
                (w_matchups['TeamSeedNumber'] == '01') & w_matchups['OppTeamSeedNumber'].isin(
                    ['16', '16a', '16b', '08', '09']),
                (w_matchups['TeamSeedNumber'] == '02') & w_matchups['OppTeamSeedNumber'].isin(['15', '07', '10']),
                (w_matchups['TeamSeedNumber'] == '03') & w_matchups['OppTeamSeedNumber'].isin(
                    ['14', '06', '11', '11a', '11b']),
                (w_matchups['TeamSeedNumber'] == '04') & w_matchups['OppTeamSeedNumber'].isin(['13', '05', '12']),
                (w_matchups['OppTeamSeedNumber'] == '01') & w_matchups['TeamSeedNumber'].isin(
                    ['16', '16a', '16b', '08', '09']),
                (w_matchups['OppTeamSeedNumber'] == '02') & w_matchups['TeamSeedNumber'].isin(['15', '07', '10']),
                (w_matchups['OppTeamSeedNumber'] == '03') & w_matchups['TeamSeedNumber'].isin(
                    ['14', '06', '11', '11a', '11b']),
                (w_matchups['OppTeamSeedNumber'] == '04') & w_matchups['TeamSeedNumber'].isin(['13', '05', '12'])
            ],
            [1, 1, 1, 1, -1, -1, -1, -1],
            default=0
        ),
        0
    )

    # Filter matchups where the location matches the tournament matchup location
    w_kaggle_matchups = w_matchups[w_matchups['Loc'] == w_matchups['TourneyMatchupLoc']]

    # Combine men’s and women’s Kaggle matchups and remove duplicates
    all_kaggle_matchups = pd.concat([m_kaggle_matchups, w_kaggle_matchups])
    all_kaggle_matchups = all_kaggle_matchups[all_kaggle_matchups['TeamID'] < all_kaggle_matchups['OppTeamID']]

    # Append predictions to matchups
    kaggle_predictions = append_predictions_to_matchups(all_kaggle_matchups, 'lr')

    # Remove unnecessary teams from the predictions
    unnecessary_ids = [3366, 3446, 3118, 3432, 3128, 3215, 3109, 3289, 3121, 3302, 3445, 3134, 3383, 3216, 3147, 3327]
    kaggle_predictions = kaggle_predictions[
        (~kaggle_predictions['TeamID'].isin(unnecessary_ids)) & (
            ~kaggle_predictions['OppTeamID'].isin(unnecessary_ids))]

    # Generate submission ID and save the Kaggle submission
    kaggle_predictions['ID'] = kaggle_predictions['Season'].astype(str) + '_' + kaggle_predictions['TeamID'].astype(
        str) + '_' + kaggle_predictions['OppTeamID'].astype(str)
    kaggle_submission = kaggle_predictions[['ID', 'Pred']]

    # Read the sample submission and compare rows
    sample_submissions = pd.read_csv('kaggle_data/SampleSubmissionStage2.csv')
    num_discrepancies = compare_rows(kaggle_submission, sample_submissions)

    if num_discrepancies == 0:
        kaggle_submission.to_csv("stored_csvs/submission.csv", index=False)
    else:
        print('Wrong matchup IDs')

    # Alternate submission where all of Duke's win probabilities are set to 1
    second_kaggle_predictions = kaggle_predictions.copy()
    second_kaggle_predictions['Pred'] = np.where(second_kaggle_predictions['TeamID'] == 1181, 1,
                                                 np.where(second_kaggle_predictions['OppTeamID'] == 1181, 0,
                                                          second_kaggle_predictions['Pred']))

    duke_kaggle_submission = second_kaggle_predictions[['ID', 'Pred']]
    num_discrepancies = compare_rows(duke_kaggle_submission, sample_submissions)
    if num_discrepancies == 0:
        duke_kaggle_submission.to_csv("stored_csvs/second_submission.csv", index=False)
    else:
        print('Wrong matchup IDs')


def compare_rows(my_submission, sample):
    """
    Compare submission IDs between two datasets to find discrepancies.
    Returns the number of differing IDs.
    """
    mine = set(my_submission['ID'])
    sample = set(sample['ID'])

    only_in_mine = mine - sample
    only_in_sample = sample - mine

    return len(only_in_mine) + len(only_in_sample)


def append_predictions_to_matchups(matchups: pd.DataFrame, model_type) -> pd.DataFrame:
    """
    Append model predictions to matchup data based on TeamID and OppTeamID.
    """
    m_predictions = pd.read_csv(f"stored_csvs/m_{model_type}_model_predictions.csv")
    w_predictions = pd.read_csv(f"stored_csvs/w_{model_type}_model_predictions.csv")
    all_predictions = pd.concat([m_predictions, w_predictions], ignore_index=True)
    matchups = matchups.merge(all_predictions, how='left', on=['TeamID', 'OppTeamID', 'Loc', 'Side', 'Season'])
    return matchups

def predict_future_games(matchups: pd.DataFrame, model_path: str):
    """
    Predict the outcomes of future games using a trained model.
    Returns the matchups with predicted probabilities.
    """
    model_data = load_model_data(model_path)
    model = model_data["model"]
    feature_cols = model_data["features"]
    scaler = model_data["scaler"]

    X_future = matchups[feature_cols]

    # Scale the features (using the same scaler used in training)
    if scaler is None:
        scaler = StandardScaler()

    X_future_scaled = scaler.transform(X_future)

    if 'nn' in model_path:
        predictions = model.predict(X_future_scaled)
    else:
        predictions = model.predict_proba(X_future_scaled)[:, 1]

    matchups['Pred'] = predictions
    return matchups


def side_year_possible_matchups(teams, year):
    """
    Generates all possible matchups for a given year, considering each team’s
    first and last D1 season, and the location of the matchup (-1, 0, 1).
    """

    # Get list of teams active in the given year
    team_list = teams[(teams['LastD1Season'] >= year) & (teams['FirstD1Season'] <= year)]['TeamID'].tolist()

    # Generate all possible team pairings
    unique_combos = list(permutations(team_list, 2))
    no_loc_matchups = pd.DataFrame(unique_combos, columns=['TeamID', 'OppTeamID'])
    no_loc_matchups['Season'] = year

    # Generate matchups for each location scenario (-1, 0, 1)
    matchups_by_loc = []
    for loc in [-1, 0, 1]:
        loc_matchups = no_loc_matchups.copy()
        loc_matchups['Loc'] = loc
        loc_matchups['OppLoc'] = -loc
        matchups_by_loc.append(loc_matchups)

    # Combine matchups from all location scenarios
    all_possible_matchups = pd.concat(matchups_by_loc, ignore_index=True)
    return all_possible_matchups


def create_all_possible_matchups(years: range):
    """
    Generates all possible matchups for men and women teams for each year in the given range,
    including assumed 'FirstD1Season' and 'LastD1Season' for the women's teams.
    """

    m_all_teams = pd.read_csv('kaggle_data/men/MTeams.csv')
    w_all_teams = pd.read_csv('kaggle_data/women/WTeams.csv')

    # These columns aren't provided, assumed data for women's teams
    w_all_teams['FirstD1Season'] = 2000
    w_all_teams['LastD1Season'] = 2025

    m_matchups_by_year = []
    w_matchups_by_year = []

    # Generate matchups for each year for both men and women teams
    for year in years:
        m_matchups_by_year.append(side_year_possible_matchups(m_all_teams, year))
        w_matchups_by_year.append(side_year_possible_matchups(w_all_teams, year))

    # Combine all matchups for men and women teams
    m_all_possible_matchups = pd.concat(m_matchups_by_year, ignore_index=True)
    w_all_possible_matchups = pd.concat(w_matchups_by_year, ignore_index=True)
    m_all_possible_matchups['Side'] = 'Men'
    w_all_possible_matchups['Side'] = 'Women'

    return m_all_possible_matchups, w_all_possible_matchups


def predict_all_possible_matchups(start_year, end_year, rating_metrics):
    """
    Generates predictions for all possible matchups for men and women teams between the specified years,
    using pre-trained models and various rating metrics.
    """

    years_to_predict = range(start_year, end_year + 1)

    # Create matchups for men and women teams
    m_matchups, w_matchups = create_all_possible_matchups(years_to_predict)

    # Add rating features to matchups
    m_matchups_features = add_rating_features_to_matchups(m_matchups, rating_metrics)
    w_matchups_features = add_rating_features_to_matchups(w_matchups, rating_metrics)

    matchup_features = {
        'm': m_matchups_features,
        'w': w_matchups_features
    }

    # Filter relevant columns for prediction
    predict_features = [col for col in m_matchups_features.columns if
                        ('Product' in col or col in ['Loc']) and 'Points' not in col]

    # Load pre-trained models
    model_files = glob.glob("models/[mw]_*.pkl")

    # Predict and save results for each model
    for model_file in model_files:
        model_name = os.path.splitext(os.path.basename(model_file))[0]  # Extract model name without extension
        prefix = model_name[0]  # Get 'm' or 'w' to determine which features to use

        if prefix in matchup_features:  # Ensure it's a valid model prefix
            predictions = predict_future_games(matchup_features[prefix], model_file)
            predictions = predictions[['TeamID', 'OppTeamID', 'Side', 'Season', 'Loc', 'Pred']]

            # Save predictions to CSV
            predictions.to_csv(f"stored_csvs/{model_name}_predictions.csv", index=False)


if __name__ == "__main__":
    rating_metrics = ['Score', 'Possessions', 'FGPercent', 'FG3Percent', 'Att3Percent', 'FTPercent', 'ORPercent',
                      'AstPercent', 'PointsPerPoss', 'TOPerPoss', 'StlPerPoss', 'BlkPerPoss', 'PFPerPoss']
    start_predict = 2021
    end_predict = 2025
    predict_all_possible_matchups(start_predict, end_predict, rating_metrics)
    save_kaggle_submission(2025)