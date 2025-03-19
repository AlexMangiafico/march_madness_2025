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
    df_to_expand['WLoc'] = df_to_expand['WLoc'].apply(lambda x: 1 if x == 'H' else (-1 if x == 'A' else 0))
    df_to_expand['LLoc'] = 0 - df_to_expand['WLoc']
    winner_rows = df_to_expand.copy()
    loser_rows = df_to_expand.copy()
    for col in df_to_expand.columns.tolist():
        if col[0] == 'W':
            stat = col[1:]
            winner_rows[stat] = winner_rows['W' + stat]
            winner_rows['Opp' + stat] = winner_rows['L' + stat]
            winner_rows['Win'] = 1
            loser_rows[stat] = loser_rows['L' + stat]
            loser_rows['Opp' + stat] = loser_rows['W' + stat]
            loser_rows['Win'] = 0

            winner_rows = winner_rows.drop(columns=['W' + stat, 'L' + stat])
            loser_rows = loser_rows.drop(columns=['W' + stat, 'L' + stat])

    games_expanded_detailed = pd.concat([winner_rows, loser_rows], ignore_index=True)
    return games_expanded_detailed

def get_training_games_stats():
    """Train the ML model using computed ratings."""
    detailed_results = load_all_detailed_results()
    detailed_results = preprocess_games(detailed_results)

    games_expanded_detailed = expand_on_wl_cols(detailed_results)
    games_expanded_detailed = calculate_advanced_metrics(games_expanded_detailed)
    return games_expanded_detailed


def train_lr(matchups, feature_cols: List[str], pred_col: str = 'Win'):
    X = matchups[feature_cols]
    y = matchups[pred_col]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_scaled = np.array(X_scaled)

    model = LogisticRegression(solver='lbfgs', max_iter=1000)
    model.fit(X_scaled, y)

    cv_log_loss = cross_val_score(model, X_scaled, y, cv=5, scoring='neg_log_loss')
    cv_log_loss = -cv_log_loss
    print(f"Cross-validated log loss scores: {cv_log_loss}")
    print(f"Mean log loss: {np.mean(cv_log_loss)}")
    print(f"Standard deviation: {np.std(cv_log_loss)}")
    return model, scaler

def train_rf(matchups, feature_cols: List[str], pred_col: str = 'Win', n_estimators: int = 100, max_depth: int = None):
    X = matchups[feature_cols]
    y = matchups[pred_col]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    model.fit(X_scaled, y)

    cv_log_loss = cross_val_score(model, X_scaled, y, cv=5, scoring='neg_log_loss')
    cv_log_loss = -cv_log_loss
    print(f"Cross-validated log loss scores: {cv_log_loss}")
    print(f"Mean log loss: {np.mean(cv_log_loss)}")
    print(f"Standard deviation: {np.std(cv_log_loss)}")

    return model, scaler


def train_nn(matchups, feature_cols: List[str], pred_col: str = 'Win'):
    X = matchups[feature_cols]
    y = matchups[pred_col]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    model = Sequential([
        Input(shape=(X_train.shape[1],)),
        Dense(18, activation='relu'),
        Dense(10, activation='relu'),
        Dense(1, activation='sigmoid')  # Single neuron for binary classification
    ])

    model.compile(optimizer=Adam(learning_rate=0.0001),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2, verbose=0)

    test_loss, test_accuracy = model.evaluate(X_test, y_test)
    print(f"Test Accuracy: {test_accuracy:.2f}")
    print(f"Test Loss: {test_loss:.2f}")

    return model, scaler



def add_rating_features_to_matchups(matchups_expanded: pd.DataFrame, all_rating_features):
    m_ratings = pd.read_csv('stored_csvs/MStatRatings.csv')
    w_ratings = pd.read_csv('stored_csvs/WStatRatings.csv')
    stat_ratings = pd.concat([m_ratings, w_ratings], ignore_index=True)
    matchups_features = matchups_expanded.merge(stat_ratings.copy(), on=['Season', 'TeamID'], how='inner')
    opp_stat_ratings = stat_ratings.rename(
        columns={col: "Opp" + col for col in stat_ratings.columns if "Season" not in col}).copy()
    matchups_features = matchups_features.merge(opp_stat_ratings, on=['Season', 'OppTeamID'], how='inner')

    #Create products
    for metric in all_rating_features:
        matchups_features[f"{metric}RatingProduct"] = (matchups_features[f"{metric}CreationRating"] * matchups_features[f"Opp{metric}PreventionRating"])
        matchups_features[f"Opp{metric}RatingProduct"] = (matchups_features[f"Opp{metric}CreationRating"] * matchups_features[f"{metric}PreventionRating"])

    return matchups_features


def train_models(matchups, which_models):
    feature_cols = [col for col in matchups.columns if ('Product' in col or col in ['Loc']) and 'Points' not in col]
    model_funcs = {'lr': train_lr, 'rf': train_rf, 'nn': train_nn}

    for model_type in which_models:
        train_func = model_funcs.get(model_type)
        if train_func:
            for side in ['Men', 'Women']:
                subset = matchups[matchups['Side'] == side]
                model, scaler = train_func(subset, feature_cols)
                save_model_data(model, feature_cols, scaler, f"models/{side[0].lower()}_{model_type}_model.pkl")
        else:
            print('No function found to train ' + str(train_func))


def create_train_matchups(begin_train_year: int):
    detailed_results = load_all_detailed_results()
    matchups = detailed_results[['Season', 'Side', 'WTeamID', 'LTeamID', 'WLoc']].copy()
    # These are the matchups we want to train our models on, want more kaggle_data but if we go back too far the game will be too different.
    # TODO figure out what year is best here, have to split by side if we want different train windows
    matchups = matchups[matchups['Season'] >= begin_train_year]
    return matchups




def main():
    training_games = get_training_games_stats()
    rating_metrics = ['Score', 'Possessions', 'FGPercent', 'FG3Percent', 'Att3Percent', 'FTPercent', 'ORPercent',
                      'AstPercent', 'PointsPerPoss', 'TOPerPoss', 'StlPerPoss', 'BlkPerPoss', 'PFPerPoss']

    #Saves ratings to csvs ~12 minutes
    #build_rating_features(training_games, rating_metrics)


    all_train_matchups = create_train_matchups(begin_train_year = 2020)
    all_train_matchups_expanded = expand_on_wl_cols(all_train_matchups)
    matchups_features = add_rating_features_to_matchups(all_train_matchups_expanded, rating_metrics)
    train_models(matchups_features, ['lr'])


if __name__ == "__main__":
    main()