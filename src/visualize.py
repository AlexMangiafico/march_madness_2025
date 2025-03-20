import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import graphviz
import networkx as nx
import matplotlib.pyplot as plt

from src.simulate import get_seeds_slots



def advancement_heatmap(year, side, model_type):
    """
    Generates a heatmap showing the probability of each team advancing to each round in the tournament.
    """
    formatted_probabilities = get_advancement_dict(year, side, model_type)

    data = []
    # Iterate through each slot and round probabilities
    for slot, round_probs in formatted_probabilities.items():
        round_name = slot[:2]  # Extract round (e.g., "R1", "R2")
        for team, prob in round_probs.items():
            data.append([round_name, team, prob])  # Add round, team, and probability to data

    # Create a DataFrame
    df = pd.DataFrame(data, columns=["Round", "Team", "Probability"])

    # Pivot the DataFrame to organize data by teams and rounds
    df_pivot = df.pivot(index="Team", columns="Round", values="Probability").fillna(0)

    rounds = sorted([col for col in df_pivot.columns if col.startswith("R")], reverse=True)
    df_pivot = df_pivot.sort_values(by=rounds, ascending=False)

    # Plot the heatmap
    plt.figure(figsize=(12, 14))
    sns.heatmap(df_pivot, annot=True, cmap="Blues", linewidths=0.5)

    plt.title("Probability of Advancing to Each Round in March Madness")
    plt.xlabel("Round")
    plt.ylabel("Team")

    # Rotate tick labels to avoid overlap
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels
    plt.yticks(rotation=0, ha='right')  # Keep y-axis labels readable

    plt.tight_layout()  # Ensure there's space for labels

    filename = f'heatmap_{side}_{year}.png'
    plt.savefig(filename, format='png', dpi=300)  # Save the heatmap as a PNG image
    plt.show()  # Display the plot

def get_advancement_dict(year, side, model_type):
    """
    Loads and filters the simulated tournament data to return the probability of each team advancing.
    """

    #Change proba to 1 here to see a single heatmap instead of the probability ones
    with open(f"simulated_tournaments/{side[0]}_{year}_{model_type}_proba.json", "r") as file:
        slot_probabilities = json.load(file)

    # Filter out slots with 'a' or 'b' suffix
    filtered_probabilities = {
        key: value for key, value in slot_probabilities.items() if not key[-1] in {'a', 'b'}
    }

    # Add "R0" prefix to round names that don't already start with "R"
    formatted_probabilities = {
        (f"R0{key}" if not key.startswith("R") else key): value
        for key, value in filtered_probabilities.items()
    }
    return formatted_probabilities

def prefix_r0_to_seeds(slots):
    """
    Adds "R0" to the beginning of any value in 'StrongSeed' and 'WeakSeed' that doesn't start with 'R'.
    """
    slots['Slot'] = slots['Slot'].apply(lambda x: f'R0{x}' if isinstance(x, str) and not x.startswith('R') else x)
    slots['StrongSeed'] = slots['StrongSeed'].apply(
        lambda x: f'R0{x}' if isinstance(x, str) and not x.startswith('R') and 'a' not in x and 'b' not in x else x
    )
    slots['WeakSeed'] = slots['WeakSeed'].apply(
        lambda x: f'R0{x}' if isinstance(x, str) and not x.startswith('R') and 'a' not in x and 'b' not in x else x
    )
    return slots

def tree_diagram(year, side, model_type):
    """
    Creates a tree diagram (bracket-style visualization) showing the teams and their probabilities of advancing.
    """
    probs = get_advancement_dict(year, side, model_type)  # Get advancement probabilities
    seeds, slots = get_seeds_slots(year, side)  # Get seed and slot information
    slots = prefix_r0_to_seeds(slots)  # Add "R0" to relevant columns

    existing_slots = slots['Slot'].values.tolist()

    new_rows = []
    # Identify and add missing slots to the DataFrame
    for slot_name in probs:
        if slot_name not in existing_slots:
            new_row = {
                "Season": year,
                "Slot": slot_name,
                "StrongSeed": None,  # No strong seed for this new slot
                "WeakSeed": None  # No weak seed for this new slot
            }
            new_rows.append(new_row)

    # Add the new rows to the existing slots DataFrame
    if new_rows:
        new_rows_df = pd.DataFrame(new_rows)
        slots = pd.concat([slots, new_rows_df], ignore_index=True)

    slots = slots.sort_values(by="Slot")

    # Create a directed graph for the bracket
    graph = graphviz.Digraph(node_attr={'shape': 'box', 'style': 'filled', 'fillcolor': 'lightblue'}, graph_attr={'rankdir': 'LR'})
    # Iterate over each slot to build the graph
    for _, row in slots.iterrows():
        slot_name = row["Slot"]
        teams_probabilities = probs.get(slot_name, {})
        formatted_teams = "\n".join([f"{team}: {prob*100:.2f}%" for team, prob in sorted(teams_probabilities.items(), key=lambda x: x[1], reverse=True)])

        # Add node for the current slot with team probabilities
        graph.node(slot_name, label=f"{slot_name}\n{formatted_teams}", style="filled", fillcolor="lightyellow")

        # Add directed edges to and from strong/weak seeds if they exist
        if pd.notna(row["StrongSeed"]):
            graph.edge(row["StrongSeed"], slot_name, color="blue", style="solid")
        if pd.notna(row["WeakSeed"]):
            graph.edge(row["WeakSeed"], slot_name, color="red", style="solid")

    # Render and display the bracket diagram
    graph.render(f'bracket_{side}_{year}', format='png', cleanup=True)
    graph.view()