import pandas as pd
import numpy as np

def calculate_advanced_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw stats to advanced basketball metrics.
    Incoming DF will include cols for the team and the opponent
    Previously run on a df called games_expanded_detailed
    """

    df['Possessions'] = (df['FGA'] - df['OR'] + df['TO'] + 0.44 * df['FTA'])
    df['OppPossessions'] = (df['OppFGA'] - df['OppOR'] + df['OppTO'] + 0.44 * df['OppFTA'])

    for team in ["", 'Opp']:
        if team == 'Opp':
            other = ""
        else:
            other = 'Opp'
        df[team + 'FGPercent'] = np.where(df[team + 'FGA'] == 0, None, df[team + 'FGM'] / df[team + 'FGA'])
        df[team + 'FG3Percent'] = np.where(df[team + 'FGA3'] == 0, None, df[team + 'FGM3'] / df[team + 'FGA3'])
        df[team + 'FTPercent'] = np.where(df[team + 'FTA'] == 0, None, df[team + 'FTM'] / df[team + 'FTA'])
        df[team + 'ORPercent'] = np.where((df[team + 'OR'] == 0) & (df[other + 'DR'] == 0), None, df[team + 'OR'] / (df[team + 'OR'] + df[other + 'DR']))
        df[team + 'AstPercent'] = np.where(df[team + 'FGM'] == 0, None, df[team + 'Ast'] / df[team + 'FGM'])
        df[team + 'Att3Percent'] = np.where(df[team + 'FGA'] == 0, None, df[team + 'FGA3'] / df[team + 'FGA'])

        df[team + 'PointsPerPoss'] = np.where(df[team + 'Possessions'] == 0, None, df[team + 'Score'] / df[team + 'Possessions'])
        df[team + 'TOPerPoss'] = np.where(df[team + 'Possessions'] == 0, None, df[team + 'TO'] / df[team + 'Possessions'])
        df[team + 'StlPerPoss'] = np.where(df[other + 'Possessions'] == 0, None, df[team + 'Stl'] / df[other + 'Possessions'])
        df[team + 'BlkPerPoss'] = np.where(df[other + 'Possessions'] == 0, None, df[team + 'Blk'] / df[other + 'Possessions'])
        df[team + 'PFPerPoss'] = np.where(df[team + 'Possessions'] == 0, None, df[team + 'Stl'] / ( df[team + 'Possessions'] + df[other + 'Possessions']))

    return df