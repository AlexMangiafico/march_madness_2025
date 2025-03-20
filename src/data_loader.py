import pandas as pd


def load_game_data(filepath: str) -> pd.DataFrame:
    """Load raw game data from a CSV file."""
    return pd.read_csv(filepath)


def preprocess_games(df: pd.DataFrame) -> pd.DataFrame:
    """Perform basic preprocessing on game data."""
    # Remove rows with missing values
    return df.dropna()


def load_all_detailed_results() -> pd.DataFrame:
    """Load and merge detailed regular-season results for men's and women's games."""
    # Load men's detailed results and label as 'Men'
    m_detailed_results = load_game_data('kaggle_data/men/MRegularSeasonDetailedResults.csv')
    m_detailed_results['Side'] = 'Men'

    # Load women's detailed results and label as 'Women'
    w_detailed_results = load_game_data('kaggle_data/women/WRegularSeasonDetailedResults.csv')
    w_detailed_results['Side'] = 'Women'

    # Combine both datasets
    return pd.concat([m_detailed_results, w_detailed_results], ignore_index=True)