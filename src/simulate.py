import pandas as pd
import json
from src.predict import append_predictions_to_matchups
import numpy as np
from collections import defaultdict



def get_seeds_slots(year, side):
    """
    Retrieve the seed and slot data for the given year and side (Men or Women).
    """
    # Load the appropriate seed and slot data based on the side (Men/Women)
    if side == 'Men':
        seeds = pd.read_csv('kaggle_data/men/tournament/MNCAATourneySeeds.csv')
        slots = pd.read_csv('kaggle_data/men/tournament/MNCAATourneySlots.csv')
    elif side == 'Women':
        seeds = pd.read_csv('kaggle_data/women/tournament/WNCAATourneySeeds.csv')
        slots = pd.read_csv('kaggle_data/women/tournament/WNCAATourneySlots.csv')

    # Filter by the specified year and return the data
    return seeds[seeds['Season'] == year].copy(), slots[slots['Season'] == year].copy()


def convert_to_probabilities(count_dict):
    """
    Convert a count dictionary to a probability distribution.
    """
    prob_dict = {}
    # Loop through each key (event) in the count dictionary
    for key, value_counts in count_dict.items():
        total = sum(value_counts.values())  # Get the total occurrences of the event
        # Calculate probabilities for each value of the event
        prob_dict[key] = {val: count / total for val, count in value_counts.items()}
    return prob_dict


def simulate_single_tourney(seeds, slots, model_type):
    """
    Simulate a single tournament bracket.
    """
    # Initialize the 'decided' dictionary with team seeds as keys and team IDs as values
    decided = seeds.set_index('Seed')['TeamID'].to_dict()
    undecided = slots.copy()

    # Continue simulation until all matchups are decided
    while len(undecided) > 0:
        # Map teams to their slots and predict outcomes
        undecided['TeamID'] = undecided['StrongSeed'].map(decided)
        undecided['OppTeamID'] = undecided['WeakSeed'].map(decided)

        # Append predictions to the matchups
        undecided = append_predictions_to_matchups(undecided, model_type)
        # Simulate winners based on predictions
        undecided['SimulatedWinner'] = np.where(np.random.rand(len(undecided)) < undecided['Pred'], undecided['TeamID'],
                                                undecided['OppTeamID'])
        newly_decided = undecided.copy().dropna()  # Store newly decided results
        decided.update(
            newly_decided.set_index('Slot')['SimulatedWinner'].astype(int).to_dict())  # Update the 'decided' dictionary
        # Filter out matchups that have been decided
        undecided = undecided[undecided.isna().any(axis=1)].copy()
        undecided = undecided[undecided.columns.intersection(slots.columns)]  # Keep only relevant columns

    return decided

def simulate_bracket(year, side, model_type, num_simulations):
    """
    Simulate an entire tournament bracket multiple times and calculate advancement probabilities.
    """
    # Get seed and slot data for the tournament
    seeds, slots = get_seeds_slots(year, side)
    slots['Loc'] = 0  # Set the location field
    slots['Side'] = side  # Set the side field

    compiled_simulated_results = defaultdict(lambda: defaultdict(int))  # Initialize a dictionary to store simulation results

    # Run the simulations and store the results
    for _ in range(num_simulations):
        new_simulated_results = simulate_single_tourney(seeds, slots, model_type)
        # Update results by incrementing the count of simulated winners
        for key, value in new_simulated_results.items():
            compiled_simulated_results[key][value] += 1

    # Convert the results into probabilities
    advancement_probs = convert_to_probabilities(compiled_simulated_results)

    # Load team names and map team IDs to team names
    m_team_names = pd.read_csv('kaggle_data/men/MTeams.csv')
    w_team_names = pd.read_csv('kaggle_data/women/WTeams.csv')
    team_names = pd.concat([m_team_names, w_team_names])
    id_to_name = dict(zip(team_names['TeamID'], team_names['TeamName']))

    team_name_prob_dict = {}
    # Map the team names to probabilities
    for slot, team_probs in advancement_probs.items():
        team_name_prob_dict[slot] = {id_to_name.get(int(team_id), int(team_id)): prob for team_id, prob in
                                     team_probs.items()}

    # Save the simulated probabilities to a JSON file
    with open(f"simulated_tournaments/{side[0]}_{year}_{model_type}_{num_simulations}.json", "w") as file:
        json.dump(team_name_prob_dict, file)

def find_team_seed(team_id, seeds):
    """
    Find the seed for a given team ID.
    """
    # Extract the seed for the specified team ID
    return int(seeds[seeds['TeamID'] == team_id]['Seed'].iloc[0][1:3])  # Extract seed number from the 'Seed' string


def predict_matchup_proba(team_probs, opp_probs, year, side, predictions, slot, seeds):
    """
    Predict the probability of a team winning a matchup based on historical predictions.
    """
    slot_probs = {}  # Dictionary to store slot probabilities

    # Loop through each team in the matchup
    for team, appearance1 in team_probs.items():
        for opp_team, appearance2 in opp_probs.items():
            # Special handling for women’s tournament in the first and second rounds
            if side ==  'Women' and (slot[:2] == 'R1' or slot[:2] == 'R2') and (find_team_seed(team, seeds) <= 4):
                team_win_prob = predictions[(predictions['Season'] == year) & (predictions['TeamID'] == team) & (
                            predictions['OppTeamID'] == opp_team) & (predictions['Loc'] == 1)]['Pred'].iloc[0]
            elif side ==  'Women' and (slot[:2] == 'R1' or slot[:2] == 'R2') and (find_team_seed(opp_team, seeds) <= 4):
                team_win_prob = predictions[(predictions['Season'] == year) & (predictions['TeamID'] == team) & (
                            predictions['OppTeamID'] == opp_team) & (predictions['Loc'] == -1)]['Pred'].iloc[0]
            else:
                team_win_prob = predictions[(predictions['Season'] == year) & (predictions['TeamID'] == team) & (predictions['OppTeamID'] == opp_team) & (predictions['Loc'] == 0)]['Pred'].iloc[0]

            # Calculate the probability for the current team to win and update the slot probabilities
            win_prob = appearance1 * appearance2 * team_win_prob
            slot_probs[team] = slot_probs.get(team, 0) + win_prob
            slot_probs[opp_team] = slot_probs.get(opp_team, 0) + (appearance1 * appearance2 * (1 - team_win_prob))

    return slot_probs

def simulate_proba(year, side, model_type):
    """
    Simulate the tournament and predict the probabilities of each team advancing.
    """
    # Load the predictions based on the model type
    predictions = pd.read_csv(f"stored_csvs/{side[0].lower()}_{model_type}_model_predictions.csv")
    seeds, slots = get_seeds_slots(year, side)

    slots['Loc'] = 0  # Set the location field
    slots['Side'] = side  # Set the side field

    decided = seeds.set_index('Seed')['TeamID'].apply(lambda x: {x: 1.0}).to_dict()  # Initialize with team IDs and probabilities of 1.0
    undecided = slots.copy()

    # Continue until all matchups are decided
    while len(undecided) > 0:
        undecided['TeamProbs'] = undecided['StrongSeed'].map(decided)
        undecided['OppTeamProbs'] = undecided['WeakSeed'].map(decided)

        new_decided = {}

        # Iterate through each undecided matchup
        for _, row in undecided.iterrows():
            slot = row['Slot']
            team_probs = row['TeamProbs']
            opp_probs = row['OppTeamProbs']

            if not isinstance(team_probs, dict) or not isinstance(opp_probs, dict):
                continue  # Skip if missing probabilities

            new_decided[slot] = predict_matchup_proba(team_probs, opp_probs, year, side, predictions, slot, seeds)

        # Update the 'decided' dictionary with new results
        decided.update(new_decided)
        # Remove already decided matchups from the undecided list
        undecided = undecided[~undecided['Slot'].isin(new_decided)].copy()

    # Load team names and map team IDs to team names
    m_team_names = pd.read_csv('kaggle_data/men/MTeams.csv')
    w_team_names = pd.read_csv('kaggle_data/women/WTeams.csv')
    team_names = pd.concat([m_team_names, w_team_names])
    id_to_name = dict(zip(team_names['TeamID'], team_names['TeamName']))

    team_name_prob_dict = {}
    # Map the team names to probabilities
    for slot, team_probs in decided.items():
        team_name_prob_dict[slot] = {id_to_name.get(int(team_id), int(team_id)): prob for team_id, prob in
                                     team_probs.items()}

    # Save the results to a JSON file
    with open(f"simulated_tournaments/{side[0]}_{year}_{model_type}_proba.json", "w") as file:
        json.dump(team_name_prob_dict, file)


if __name__ == "__main__":
    year = 2025
    side = 'Men'
    simulate_proba(year, side, 'lr')


