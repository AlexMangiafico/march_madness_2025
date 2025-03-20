from src.data_loader import load_all_detailed_results, preprocess_games
from src.metrics import calculate_advanced_metrics
from src.ratings import build_rating_features
from src.model import save_model_data
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler


import pandas as pd
import numpy as np
from typing import List, Dict
import joblib
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam


def expand_on_wl_cols(df_to_expand: pd.DataFrame) -> pd.DataFrame:
    """
    Expands the dataframe to separate winner and loser rows, adding 'Win' and 'Opp' stats.
    """

    # Convert WLoc to numerical values: 1 for home win, -1 for away win, 0 for neutral
    df_to_expand['WLoc'] = df_to_expand['WLoc'].apply(lambda x: 1 if x == 'H' else (-1 if x == 'A' else 0))
    df_to_expand['LLoc'] = -df_to_expand['WLoc']  # LLoc is the inverse of WLoc

    winner_rows = df_to_expand.copy()
    loser_rows = df_to_expand.copy()

    # Loop through columns to process stats for winner and loser
    for col in df_to_expand.columns:
        if col.startswith('W'):  # Process only columns starting with 'W'
            stat = col[1:]  # Get stat name (e.g., 'Pts' from 'WPts')

            # Populate stats for winner and opponent
            winner_rows[stat] = winner_rows['W' + stat]
            winner_rows['Opp' + stat] = winner_rows['L' + stat]
            winner_rows['Win'] = 1  # Mark winner

            loser_rows[stat] = loser_rows['L' + stat]
            loser_rows['Opp' + stat] = loser_rows['W' + stat]
            loser_rows['Win'] = 0  # Mark loser

            # Drop the original columns for winner and loser
            winner_rows = winner_rows.drop(columns=['W' + stat, 'L' + stat])
            loser_rows = loser_rows.drop(columns=['W' + stat, 'L' + stat])

    # Concatenate winner and loser rows into a single dataframe
    return pd.concat([winner_rows, loser_rows], ignore_index=True)

def get_training_games_stats():
    """Train the ML model using computed ratings."""
    detailed_results = load_all_detailed_results()
    detailed_results = preprocess_games(detailed_results)

    games_expanded_detailed = expand_on_wl_cols(detailed_results)
    games_expanded_detailed = calculate_advanced_metrics(games_expanded_detailed)
    return games_expanded_detailed


def train_lr(matchups, feature_cols: List[str], pred_col: str = 'Win'):
    """
    Trains a logistic regression model on matchups data and evaluates its performance.
    Performs cross-validation to calculate log loss scores.
    """

    # Prepare features (X) and target (y)
    X = matchups[feature_cols]
    y = matchups[pred_col]

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Initialize and train the logistic regression model
    model = LogisticRegression(solver='lbfgs', max_iter=1000)
    model.fit(X_scaled, y)

    # Perform cross-validation to calculate log loss scores
    cv_log_loss = cross_val_score(model, X_scaled, y, cv=5, scoring='neg_log_loss')
    cv_log_loss = -cv_log_loss  # Negate the values as they are negative in the cross_val_score output

    # Print log loss statistics
    print(f"Cross-validated lr log loss scores: {cv_log_loss}")
    print(f"Mean log loss: {np.mean(cv_log_loss)}")
    print(f"Standard deviation: {np.std(cv_log_loss)}")

    return model, scaler


def train_rf(matchups, feature_cols: List[str], pred_col: str = 'Win', n_estimators: int = 100, max_depth: int = None):
    """
    Trains a random forest classifier on matchups data and evaluates its performance.
    Performs cross-validation to calculate log loss scores.
    """

    # Prepare features (X) and target (y)
    X = matchups[feature_cols]
    y = matchups[pred_col]

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Initialize and train the random forest model
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    model.fit(X_scaled, y)

    # Perform cross-validation to calculate log loss scores
    cv_log_loss = cross_val_score(model, X_scaled, y, cv=5, scoring='neg_log_loss')
    cv_log_loss = -cv_log_loss  # Negate the values as they are negative in the cross_val_score output

    # Print log loss statistics
    print(f"Cross-validated rf log loss scores: {cv_log_loss}")
    print(f"Mean log loss: {np.mean(cv_log_loss)}")
    print(f"Standard deviation: {np.std(cv_log_loss)}")

    return model, scaler

def train_nn(matchups, feature_cols: List[str], pred_col: str = 'Win'):
    """
    Trains a neural network model to predict win/loss outcomes using matchups data.
    Evaluates the model's accuracy and loss on the test set.
    """
    # Prepare features (X) and target (y)
    X = matchups[feature_cols]
    y = matchups[pred_col]

    # Standardize the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Define the neural network model
    model = Sequential([
        Input(shape=(X_train.shape[1],)),
        Dense(18, activation='relu'),
        Dense(10, activation='relu'),
        Dense(1, activation='sigmoid')  # Single neuron for binary classification
    ])

    # Compile the model with Adam optimizer and binary crossentropy loss
    model.compile(optimizer=Adam(learning_rate=0.0001),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    # Train the model
    history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2, verbose=0)

    # Evaluate the model on the test data
    test_loss, test_accuracy = model.evaluate(X_test, y_test)
    print(f"Test Accuracy: {test_accuracy:.2f}")
    print(f"Test Loss: {test_loss:.2f}")

    return model, scaler


def add_rating_features_to_matchups(matchups_expanded: pd.DataFrame, all_rating_features):
    """
    Adds rating features (team and opponent ratings) to the matchups dataframe.
    Creates interaction features based on team and opponent ratings for specified metrics.
    """

    # Load team ratings data
    m_ratings = pd.read_csv('stored_csvs/MStatRatings.csv')
    w_ratings = pd.read_csv('stored_csvs/WStatRatings.csv')

    # Combine men's and women's ratings
    stat_ratings = pd.concat([m_ratings, w_ratings], ignore_index=True)

    # Merge team ratings with matchups data
    matchups_features = matchups_expanded.merge(stat_ratings, on=['Season', 'TeamID'], how='inner')

    # Prepare opponent's ratings by renaming columns
    opp_stat_ratings = stat_ratings.rename(
        columns={col: "Opp" + col for col in stat_ratings.columns if "Season" not in col}).copy()

    # Merge opponent ratings with matchups data
    matchups_features = matchups_features.merge(opp_stat_ratings, on=['Season', 'OppTeamID'], how='inner')

    # Create interaction features by multiplying ratings
    for metric in all_rating_features:
        matchups_features[f"{metric}RatingProduct"] = (matchups_features[f"{metric}CreationRating"] *
                                                       matchups_features[f"Opp{metric}PreventionRating"])
        matchups_features[f"Opp{metric}RatingProduct"] = (matchups_features[f"Opp{metric}CreationRating"] *
                                                          matchups_features[f"{metric}PreventionRating"])

    return matchups_features


def train_models(matchups, which_models):
    """
    Trains specified models (Logistic Regression, Random Forest, Neural Network) on the matchups data.
    Saves the trained models and their corresponding scalers for both men's and women's data.
    """

    # Define feature columns and model training functions
    feature_cols = [col for col in matchups.columns if ('Product' in col or col in ['Loc']) and 'Points' not in col]
    model_funcs = {'lr': train_lr, 'rf': train_rf, 'nn': train_nn}

    # Iterate over the specified models
    for model_type in which_models:
        train_func = model_funcs.get(model_type)

        if train_func:  # Check if the function exists
            for side in ['Men', 'Women']:  # Train models for both men's and women's matchups
                subset = matchups[matchups['Side'] == side]
                model, scaler = train_func(subset, feature_cols)

                # Save the model and scaler
                save_model_data(model, feature_cols, scaler, f"models/{side[0].lower()}_{model_type}_model.pkl")
        else:
            print(f'No function found to train {model_type}')


def create_train_matchups(begin_train_year: int):
    """
    Prepares and filters the matchup data for model training starting from a specified season.
    """

    # Load the detailed results
    detailed_results = load_all_detailed_results()

    # Extract relevant columns for matchups
    matchups = detailed_results[['Season', 'Side', 'WTeamID', 'LTeamID', 'WLoc']].copy()

    # Filter matchups based on the specified training start year
    matchups = matchups[matchups['Season'] >= begin_train_year]

    return matchups


def main():
    """
    Main function to execute the full pipeline for training models with game statistics and rating features.
    """

    # Get the training game statistics
    training_games = get_training_games_stats()

    # Define the rating metrics to calculate
    rating_metrics = [
        'Score', 'Possessions', 'FGPercent', 'FG3Percent', 'Att3Percent', 'FTPercent', 'ORPercent',
        'AstPercent', 'PointsPerPoss', 'TOPerPoss', 'StlPerPoss', 'BlkPerPoss', 'PFPerPoss'
    ]

    # Save team ratings to CSV files
    build_rating_features(training_games, rating_metrics)

    # Prepare matchups for training starting from the 2020 season
    all_train_matchups = create_train_matchups(begin_train_year=2020)
    all_train_matchups_expanded = expand_on_wl_cols(all_train_matchups)

    # Add rating features to the matchups
    matchups_features = add_rating_features_to_matchups(all_train_matchups_expanded, rating_metrics)

    # Train models using the prepared features (e.g., Logistic Regression)
    train_models(matchups_features, ['lr'])


if __name__ == "__main__":
    main()