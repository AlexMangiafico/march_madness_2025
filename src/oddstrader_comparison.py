import re
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from typing import List

def scrape_website(url: str):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Optional, removes the browser window
    options.add_argument("--disable-gpu")  # Required for headless mode on Windows
    options.add_argument("--no-sandbox")

    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Open the OddsTrader website
    driver.get(url)

    # Wait for the page to load fully by waiting for a specific element
    offering_dict = {}
    try:

        # Wait for the game rows to be available (Adjust the selector as needed)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr[data-cy='participant-row']")))
        # Find all the rows that contain matchups and betting lines
        game_rows = driver.find_elements(By.CSS_SELECTOR, "tr[data-cy='participant-row']")
        # Check if we found the rows
        if not game_rows:
            print("No game rows found!")

        # Loop through each row to extract the matchups and lines
        for game in game_rows:
            # Print the entire row's text for diagnostics
            row_text = game.text
            lines = row_text.splitlines()
            # if lines[0] not in teams['TeamName'].copy():
            # lines.pop(0)

            if (lines[0][-2:] in ["AM", "PM"]):
                lines.pop(0)
            if lines[0][:1] == "#":
                lines.pop(0)
            if lines[0][:5] == "FINAL":
                lines.pop(0)

            try:
                team_name = lines[0]
                moneyline = int(lines[3])
                book = lines[4]
                offering_dict[team_name] = (moneyline, book)
            except Exception as e:
                print(f"An error occurred: {e}")


    except Exception as e:
        print(f"An initial error occurred: {e}")

    # Close the browser
    driver.quit()
    print(offering_dict)
    return offering_dict

def offering_dict_to_df(offerings: dict):
    team_list = list(offerings.items())

    # Create pairs of consecutive teams
    matchups = []
    for i in range(0, len(team_list) - 1, 2):  # Step by 2
        (away_team, (away_odds, away_book)) = team_list[i]
        (home_team, (home_odds, home_book)) = team_list[i + 1]
        matchups.append([away_team, away_odds, away_book, home_team, home_odds, home_book])

    df = pd.DataFrame(matchups, columns=["AwayTeam", "AwayOddsOffered", "AwayBook", "HomeTeam", "HomeOddsOffered", "HomeBook"])
    return df

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

def pull_home_prediction(year: int, all_teams: pd.DataFrame, predictions, away_team: str, home_team: str, neutral_court = False):

    if home_team not in all_teams['TeamName'].values:
        print('no team found for ' + home_team)
        return None
    if away_team not in all_teams['TeamName'].values:
        print('no team found for ' + away_team)
        return None

    home_id = all_teams[all_teams['TeamName'] == home_team]['TeamID'].values[0]
    away_id = all_teams[all_teams['TeamName'] == away_team]['TeamID'].values[0]
    #print(home_team, away_team, home_id, away_id)

    if not neutral_court:
        if home_id < away_id:
            home_win_prob = predictions[(predictions['Season'] == year) & (predictions['TeamID'] == home_id) & (predictions['OppTeamID'] == away_id) & (predictions['Loc'] == 1)]['Pred'].values[0]
        else:
            home_win_prob = 1 - predictions[(predictions['Season'] == year) & (predictions['TeamID'] == away_id) & (predictions['OppTeamID'] == home_id) & (predictions['Loc'] == -1)]['Pred'].values[0]
    else:
        if home_id < away_id:
            home_win_prob = predictions[(predictions['Season'] == year) & (predictions['TeamID'] == home_id) & (predictions['OppTeamID'] == away_id) & (predictions['Loc'] == 0)]['Pred'].values[0]
        else:
            home_win_prob = 1 - predictions[(predictions['Season'] == year) & (predictions['TeamID'] == away_id) & (predictions['OppTeamID'] == home_id) & (predictions['Loc'] == 0)]['Pred'].values[0]

    #print(home_win_prob)
    away_win_prob = 1 - home_win_prob
    matchup_probs = {
    "home_team": home_team,
    "away_team": away_team,
    "home_win_prob": home_win_prob,
    "away_win_prob": away_win_prob
    }

    #print(away_team, away_win_prob)
    #print(home_team, home_win_prob)
    #print(100/min(home_win_prob, away_win_prob) - 100)

    #print(home_win_prob)
    return home_win_prob

def build_comparison_df(matchups, teams, my_predictions):
    matchups['AwayProbOffered'] = np.where(matchups['AwayOddsOffered'] < 0, matchups['AwayOddsOffered'] / (
            matchups['AwayOddsOffered'] - 100), 100 / (matchups['AwayOddsOffered'] + 100))
    matchups['HomeProbOffered'] = np.where(matchups['HomeOddsOffered'] < 0, matchups['HomeOddsOffered'] / (
            matchups['HomeOddsOffered'] - 100), 100 / (matchups['HomeOddsOffered'] + 100))
    matchups['MatchupString'] = matchups['AwayTeam'] + " at " + matchups['HomeTeam']
    #print(matchups)
    # home_prob = pull_home_prediction(2025, teams, my_predictions, away_team = 'Northwestern', home_team = 'Minnesota', neutral_court = True)

    # kaggle_named['MyAwayWinProb'] = 1 - kaggle_named['HomeTeam'].apply(lambda x: pull_prediction(year=2025, all_teams=teams, predictions=my_predictions, home_team=x, away_team = kaggle_named['AwayTeam'], neutral_court=True))
    #TODO can probably just merge now, I used permutations instead of combinations when saving results
    matchups['MyAwayWinProb'] = 1 - matchups.apply(
        lambda row: pull_home_prediction(
            year=2025, all_teams=teams, predictions=my_predictions,
            home_team=row['HomeTeam'], away_team=row['AwayTeam'],
            neutral_court=True
        ), axis=1)
    matchups['MyHomeWinProb'] = 1 - matchups['MyAwayWinProb']
    matchups['AwayEdge'] = matchups['MyAwayWinProb'] - matchups['AwayProbOffered']
    matchups['HomeEdge'] = matchups['MyHomeWinProb'] - matchups['HomeProbOffered']
    matchups['MaxEdge'] = np.where(matchups['HomeEdge'] > matchups['AwayEdge'], matchups['HomeEdge'],
                                   matchups['AwayEdge'])
    matchups.sort_values(by=['MaxEdge'], ascending=False, inplace=True)
    return matchups

def main():
    #TODO should this just be a merge instead of pull_home_whatever?
    teams = pd.read_csv("kaggle_data/men/MTeams.csv")
    my_predictions = pd.read_csv("stored_csvs/m_lr_model_predictions.csv")
    offering_dict = scrape_website("https://www.oddstrader.com/ncaa-college-basketball/?eid&g=game&m=money")

    matchups = offering_dict_to_df(offering_dict)
    kaggle_named = convert_oddstrader_team_names(matchups)
    final_display = build_comparison_df(kaggle_named, teams, my_predictions)
    #combined
    print(final_display.head(10))

if __name__ == "__main__":
    main()