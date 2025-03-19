import pandas as pd

def load_game_data(filepath: str) -> pd.DataFrame:
    """Load raw season game kaggle_data."""
    return pd.read_csv(filepath)

def preprocess_games(df: pd.DataFrame) -> pd.DataFrame:
    """Basic preprocessing for game kaggle_data."""
    df = df.dropna()  # Handle missing values
    #took out game_id = index line here
    return df

def load_all_detailed_results() -> pd.DataFrame:
    m_detailed_results = load_game_data('kaggle_data/men/MRegularSeasonDetailedResults.csv')
    m_detailed_results['Side'] = 'Men'
    w_detailed_results = load_game_data('kaggle_data/women/WRegularSeasonDetailedResults.csv')
    w_detailed_results['Side'] = 'Women'

    detailed_results = pd.concat([m_detailed_results, w_detailed_results], ignore_index=True)

    return detailed_results