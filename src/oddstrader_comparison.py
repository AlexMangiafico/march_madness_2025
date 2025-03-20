import re
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_website(url: str):
    """
    Scrapes the given website URL to extract betting odds and bookmaker information.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--disable-gpu")  # Necessary for headless mode on Windows
    options.add_argument("--no-sandbox")

    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    offering_dict = {}
    try:
        # Wait for game rows to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tr[data-cy='participant-row']"))
        )
        game_rows = driver.find_elements(By.CSS_SELECTOR, "tr[data-cy='participant-row']")

        if not game_rows:
            print("No game rows found!")

        for game in game_rows:
            row_text = game.text.splitlines()

            # Remove unwanted lines from extracted text
            if row_text[0][-2:] in ["AM", "PM"] or row_text[0].startswith("#") or row_text[0].startswith("FINAL"):
                row_text.pop(0)

            try:
                team_name = row_text[0]
                moneyline = int(row_text[3])
                book = row_text[4]
                offering_dict[team_name] = (moneyline, book)
            except Exception as e:
                print(f"Error processing row: {e}")

    except Exception as e:
        print(f"Initial error occurred: {e}")

    driver.quit()
    return offering_dict


def offering_dict_to_df(offerings: dict) -> pd.DataFrame:
    """
    Converts the extracted betting offerings into a DataFrame with matchups.
    """
    team_list = list(offerings.items())
    matchups = []

    for i in range(0, len(team_list) - 1, 2):
        (away_team, (away_odds, away_book)) = team_list[i]
        (home_team, (home_odds, home_book)) = team_list[i + 1]
        matchups.append([away_team, away_odds, away_book, home_team, home_odds, home_book])

    return pd.DataFrame(matchups,
                        columns=["AwayTeam", "AwayOddsOffered", "AwayBook", "HomeTeam", "HomeOddsOffered", "HomeBook"])


def convert_oddstrader_team_names(matchups: pd.DataFrame):
    name_replacements = {
        'Coastal Carolina': 'Coastal Car',
        'Western': 'W',
        'Eastern': 'E',
        'State': 'St',
        '(': '',
        ')': '',
        '.': '',
        'Bryant University': 'Bryant',
        'UTSA': 'UT San Antonio',
        'Kent St': 'Kent',
        'Green Bay': 'WI Green Bay',
        'Albany': 'SUNY Albany',
        'Virginia Commonwealth': 'VCU',
        'Massachusetts-Lowell': 'MA Lowell',
        'Saint Louis': 'St Louis',
        'Georgia Southern': 'Ga Southern',
        'Saint': 'St',
        'George Washington': 'G Washington',
        'North Carolina St': 'NC State',
        'Fairleigh Dickinson': 'F Dickinson',
        'LIU': 'LIU Brooklyn',
        'USC Upstate': 'SC Upstate',
        'Loyola Chicago': 'Loyola-Chicago',
        'Ole Miss': 'Mississippi',
        'Gardner-Webb': 'Gardner Webb',
        'Florida Atlantic': 'FL Atlantic',
        'Tennessee-Martin': 'TN Martin',
        'Boston University': 'Boston Univ',
        'American University': 'American Univ',
        'Mount St Mary\'s': 'Mt St Mary\'s',
        'Maryland-E Shore': 'MD E Shore',
        'South Carolina St': 'S Carolina St',
        'W Kentucky': 'WKU',
        'Milwaukee': 'WI Milwaukee',
        'Arkansas-Pine Bluff': 'Ark Pine Bluff',
        'Arkansas-Little Rock': 'Ark Little Rock',
        'Florida Atlantic': 'FL Atlantic',
        'Queens University of Charlotte': 'Queens NC',
        'North Carolina Central': 'NC Central',
        'Florida International': 'Florida Intl',
        'Abilene Christian': 'Abilene Chr',
        'Southern University': 'Southern Univ',
        'Cal St Bakersfield': 'CS Bakersfield',
        'Illinois-Chicago': 'IL Chicago',
        'Grambling St': 'Grambling',
        'Cal St Fullerton': 'CS Fullerton',
        'Cal St Northridge': 'CS Northridge',
        'California Baptist': 'Cal Baptist',
        'Mississippi Valley St': 'MS Valley St',
        'Southern Illinois': 'S Illinois',
        'Central Michigan': 'C Michigan',
        'North Dakota St': 'N Dakota St',
        'Loyola Marymount': 'Loy Marymount',
        'SIU-Edwardsville': 'SIUE',
        'South Dakota St': 'S Dakota St',
        'Southeast Missouri St': 'SE Missouri St',
        'Northern Illinois': 'N Illinois',
        'North Carolina A&T': 'NC A&T',
        'Charleston Southern': 'Charleston So',
        'Nebraska-Omaha': 'NE Omaha',
        'Southeastern Louisiana': 'SE Louisiana',
        'Texas A&M-CC': 'TAM C. Christi',
        'Houston Christian': 'Houston Chr',
        'NC-Wilmington': 'UNC Wilmington',
        'Northwestern St': 'Northwestern LA',
        'Central Connecticut St': 'Central Conn',
        'Prairie View A&M': 'Prairie View',
        'Northern Colorado': 'N Colorado',
        'St Mary\'s': 'St Mary\'s CA',
        # Add more replacements as needed
    }

    for name in ['AwayTeam', 'HomeTeam']:
        for old_name, new_name in name_replacements.items():
            matchups[name] = matchups[name].str.replace(old_name, new_name, regex=False)

    return matchups

def build_comparison_df(matchups, teams, my_predictions):
    """
    Creates a DataFrame to compare my predictions to the oddstrader lines
    """
    matchups['AwayProbOffered'] = np.where(matchups['AwayOddsOffered'] < 0, matchups['AwayOddsOffered'] / (
            matchups['AwayOddsOffered'] - 100), 100 / (matchups['AwayOddsOffered'] + 100))
    matchups['HomeProbOffered'] = np.where(matchups['HomeOddsOffered'] < 0, matchups['HomeOddsOffered'] / (
            matchups['HomeOddsOffered'] - 100), 100 / (matchups['HomeOddsOffered'] + 100))
    matchups['MatchupString'] = matchups['AwayTeam'] + " at " + matchups['HomeTeam']

    team_name_to_id = teams.set_index('TeamName')['TeamID'].to_dict()

    matchups['TeamID'] = matchups['AwayTeam'].map(team_name_to_id)
    matchups['OppTeamID'] = matchups['HomeTeam'].map(team_name_to_id)


    oddstrader_filtered_predictions = my_predictions[(my_predictions['Season'] == 2025) & (my_predictions['Side'] == 'Men') & (my_predictions['Loc'] == 0)]
    matchups = pd.merge(matchups, oddstrader_filtered_predictions, on = ['TeamID', 'OppTeamID'])

    matchups.rename(columns={'Pred': 'MyAwayWinProb'}, inplace=True)

    matchups['MyHomeWinProb'] = 1 - matchups['MyAwayWinProb']
    matchups['AwayEdge'] = matchups['MyAwayWinProb'] - matchups['AwayProbOffered']
    matchups['HomeEdge'] = matchups['MyHomeWinProb'] - matchups['HomeProbOffered']
    matchups['MaxEdge'] = np.where(matchups['HomeEdge'] > matchups['AwayEdge'], matchups['HomeEdge'],
                                   matchups['AwayEdge'])
    matchups.sort_values(by=['MaxEdge'], ascending=False, inplace=True)
    return matchups

def main():
    teams = pd.read_csv("kaggle_data/men/MTeams.csv")
    my_predictions = pd.read_csv("stored_csvs/m_lr_model_predictions.csv")
    offering_dict = scrape_website("https://www.oddstrader.com/ncaa-college-basketball/?eid&g=game&m=money")

    matchups = offering_dict_to_df(offering_dict)
    kaggle_named = convert_oddstrader_team_names(matchups)
    final_display = build_comparison_df(kaggle_named, teams, my_predictions)
    print(final_display.head(10))

if __name__ == "__main__":
    main()