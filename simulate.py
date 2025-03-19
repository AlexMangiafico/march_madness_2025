import pandas as pd
import json
from src.predict import append_predictions_to_matchups
import numpy as np
from collections import defaultdict



def get_seeds_slots(year, side):
    if side == 'Men':
        seeds = pd.read_csv('kaggle_data/men/tournament/MNCAATourneySeeds.csv')
        slots = pd.read_csv('kaggle_data/men/tournament/MNCAATourneySlots.csv')
    elif side == 'Women':
        seeds = pd.read_csv('kaggle_data/women/tournament/WNCAATourneySeeds.csv')
        slots = pd.read_csv('kaggle_data/women/tournament/WNCAATourneySlots.csv')

    return seeds[seeds['Season'] == year].copy(), slots[slots['Season'] == year].copy()

def convert_to_probabilities(count_dict):
    prob_dict = {}
    for key, value_counts in count_dict.items():
        total = sum(value_counts.values())  # Total occurrences for this key
        prob_dict[key] = {val: count / total for val, count in value_counts.items()}
    return prob_dict

def simulate_single_tourney(seeds, slots):
    decided =  seeds.set_index('Seed')['TeamID'].to_dict()
    undecided = slots.copy()

    while len(undecided) > 0:
        undecided['TeamID'] = undecided['StrongSeed'].map(decided)
        undecided['OppTeamID'] = undecided['WeakSeed'].map(decided)

        undecided = append_predictions_to_matchups(undecided, 'lr')
        undecided['SimulatedWinner'] = np.where(np.random.rand(len(undecided)) < undecided['Pred'], undecided['TeamID'], undecided['OppTeamID'])
        newly_decided = undecided.copy().dropna()
        decided.update(newly_decided.set_index('Slot')['SimulatedWinner'].astype(int).to_dict())
        undecided = undecided[undecided.isna().any(axis=1)].copy()
        undecided = undecided[undecided.columns.intersection(slots.columns)]
    # print(decided)
    return decided

def simulate_bracket(year, side, num_simulations):
    seeds, slots = get_seeds_slots(year, side)
    slots['Loc'] = 0
    slots['Side'] = side
    compiled_simulated_results = defaultdict(lambda: defaultdict(int))
    for _ in range(num_simulations):
        new_simulated_results = simulate_single_tourney(seeds, slots)
        for key, value in new_simulated_results.items():
            compiled_simulated_results[key][value] += 1  # Increment count for value occurrence

    advancement_probs = convert_to_probabilities(compiled_simulated_results)
    print(advancement_probs)
    with open(f"simulated_tournaments/{side[0]}_{year}_{num_simulations}.json", "w") as file:
        json.dump(advancement_probs, file)

    #return advancement_probs

def find_team_seed(team_id, seeds):
    print(team_id)
    print(seeds)
    return int(seeds[seeds['TeamID'] == team_id]['Seed'].iloc[0][1:3])

def predict_matchup_proba(team_probs, opp_probs, year, side, predictions, slot, seeds):
    slot_probs = {}

    for team, appearance1 in team_probs.items():
        for opp_team, appearance2 in opp_probs.items():
            if side ==  'Women' and (slot[:2] == 'R1' or slot[:2] == 'R2') and (find_team_seed(team, seeds) <= 4):
                team_win_prob = predictions[(predictions['Season'] == year) & (predictions['TeamID'] == team) & (
                            predictions['OppTeamID'] == opp_team) & (predictions['Loc'] == 1)]['Pred'].iloc[0]
            elif side ==  'Women' and (slot[:2] == 'R1' or slot[:2] == 'R2') and (find_team_seed(opp_team, seeds) <= 4):
                team_win_prob = predictions[(predictions['Season'] == year) & (predictions['TeamID'] == team) & (
                            predictions['OppTeamID'] == opp_team) & (predictions['Loc'] == -1)]['Pred'].iloc[0]
            else:
                team_win_prob = predictions[(predictions['Season'] == year) & (predictions['TeamID'] == team) & (predictions['OppTeamID'] == opp_team) & (predictions['Loc'] == 0)]['Pred'].iloc[0]

            win_prob = appearance1 * appearance2 * team_win_prob
            slot_probs[team] = slot_probs.get(team, 0) + win_prob
            slot_probs[opp_team] = slot_probs.get(opp_team, 0) + (appearance1 * appearance2 * (1 - team_win_prob))
    return slot_probs

def simulate_proba(year, side, model_type):
    predictions = pd.read_csv(f"stored_csvs/{side[0].lower()}_{model_type}_model_predictions.csv")
    seeds, slots = get_seeds_slots(year, side)

    slots['Loc'] = 0
    slots['Side'] = side

    decided = seeds.set_index('Seed')['TeamID'].apply(lambda x: {x: 1.0}).to_dict()
    undecided = slots.copy()
    while len(undecided) > 0:
        undecided['TeamProbs'] = undecided['StrongSeed'].map(decided)
        undecided['OppTeamProbs'] = undecided['WeakSeed'].map(decided)

        new_decided = {}

        for _, row in undecided.iterrows():
            slot = row['Slot']
            team_probs = row['TeamProbs']
            opp_probs = row['OppTeamProbs']

            if not isinstance(team_probs, dict) or not isinstance(opp_probs, dict):
                continue  # Skip if missing probabilities

            new_decided[slot] = predict_matchup_proba(team_probs, opp_probs, year, side, predictions, slot, seeds)

        decided.update(new_decided)
        undecided = undecided[~undecided['Slot'].isin(new_decided)].copy()

        m_team_names = pd.read_csv('kaggle_data/men/MTeams.csv')
        w_team_names = pd.read_csv('kaggle_data/women/WTeams.csv')
        team_names = pd.concat([m_team_names, w_team_names])
        id_to_name = dict(zip(team_names['TeamID'], team_names['TeamName']))
        team_name_prob_dict = {}
        for slot, team_probs in decided.items():
            team_name_prob_dict[slot] = {id_to_name.get(int(team_id), int(team_id)): prob for team_id, prob in
                                         team_probs.items()}

        with open(f"simulated_tournaments/{side[0]}_{year}_{model_type}_proba.json", "w") as file:
            json.dump(team_name_prob_dict, file)


if __name__ == "__main__":
    year = 2024
    side = 'Men'
    simulate_proba(year, side, 'lr')


