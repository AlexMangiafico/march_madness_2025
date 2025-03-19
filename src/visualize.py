import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import graphviz
import networkx as nx
import matplotlib.pyplot as plt

from src.simulate import get_seeds_slots



def advancement_heatmap(year, side, model_type):
    formatted_probabilities = get_advancement_dict(year, side, model_type)

    data = []
    for slot, round_probs in formatted_probabilities.items():
        round_name = slot[:2]  # Extract round (e.g., "R1", "R2")
        for team, prob in round_probs.items():
            data.append([round_name, team, prob])  # Only add actual probabilities

    # Create DataFrame
    df = pd.DataFrame(data, columns=["Round", "Team", "Probability"])

    # Pivot the DataFrame
    df_pivot = df.pivot(index="Team", columns="Round", values="Probability").fillna(0)  # Fill missing values with 0

    rounds = sorted([col for col in df_pivot.columns if col.startswith("R")], reverse=True)  # Sort in descending order
    df_pivot = df_pivot.sort_values(by=rounds, ascending=False)

    # Plot heatmap
    plt.figure(figsize=(12, 14))
    sns.heatmap(df_pivot, annot=True, cmap="Blues", linewidths=0.5)

    # Set the title and labels
    plt.title("Probability of Advancing to Each Round in March Madness")
    plt.xlabel("Round")
    plt.ylabel("Team")

    # Rotate the x-ticks and y-ticks to avoid overlapping
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels
    plt.yticks(rotation=0, ha='right')  # Ensure y-axis labels are readable

    # To show all the team names, adjust the tick parameters
    plt.tight_layout()  # Ensures there's enough space to show labels

    filename = f'heatmap_{side}_{year}.png'
    plt.savefig(filename, format='png', dpi=300)  # Save as PNG with high resolution
    plt.show()  # Show the plot

def get_advancement_dict(year, side, model_type):
    with open(f"simulated_tournaments/{side[0]}_{year}_{model_type}_proba.json", "r") as file:
        slot_probabilities = json.load(file)


    filtered_probabilities = {
        key: value for key, value in slot_probabilities.items() if not key[-1] in {'a', 'b'}
    }

    formatted_probabilities = {
        (f"R0{key}" if not key.startswith("R") else key): value
        for key, value in filtered_probabilities.items()
    }
    return formatted_probabilities

def prefix_r0_to_seeds(slots):
    # Add "R0" to the beginning of any value in StrongSeed and WeakSeed that doesn't start with "R"
    slots['Slot'] = slots['Slot'].apply(lambda x: f'R0{x}' if isinstance(x, str) and not x.startswith('R') else x)
    slots['StrongSeed'] = slots['StrongSeed'].apply(
        lambda x: f'R0{x}' if isinstance(x, str) and not x.startswith('R') and 'a' not in x and 'b' not in x else x
    )
    slots['WeakSeed'] = slots['WeakSeed'].apply(
        lambda x: f'R0{x}' if isinstance(x, str) and not x.startswith('R') and 'a' not in x and 'b' not in x else x
    )
    return slots

def tree_diagram(year, side, model_type):
    # Assuming get_advancement_dict() and get_seeds_slots() are already defined
    probs = get_advancement_dict(year, side, model_type)  # Probability data
    seeds, slots = get_seeds_slots(year, side)  # Slot and seed info
    slots = prefix_r0_to_seeds(slots)

    existing_slots = slots['Slot'].values.tolist()

    new_rows = []

    for slot_name in probs:
        if slot_name not in existing_slots:
            # If the slot is not in the 'slots' DataFrame, add a new row with no seeds
            new_row = {
                "Season": year,
                "Slot": slot_name,
                "StrongSeed": None,  # No strong seed for this new node
                "WeakSeed": None  # No weak seed for this new node
            }
            new_rows.append(new_row)  # Collect new rows in a list

    # Concatenate the new rows with the existing slots DataFrame
    if new_rows:
        new_rows_df = pd.DataFrame(new_rows)
        slots = pd.concat([slots, new_rows_df], ignore_index=True)  # Add the new rows to 'slots'

    slots = slots.sort_values(by="Slot")

    # Create a directed graph
    graph = graphviz.Digraph(node_attr={'shape': 'box', 'style': 'filled', 'fillcolor': 'lightblue'}, graph_attr={'rankdir': 'LR'})
    # Loop through each slot in the slots DataFrame
    for _, row in slots.iterrows():
        # Get the teams and their probabilities for the current slot (e.g., "R5WX")
        slot_name = row["Slot"]
        teams_probabilities = probs.get(slot_name, {})
        formatted_teams = "\n".join([f"{team}: {prob*100:.2f}%" for team, prob in sorted(teams_probabilities.items(), key=lambda x: x[1], reverse=True)])


        # Format the node label to include team names and their probabilities

        # Add nodes with the teams' names and their probabilities
        graph.node(slot_name, label=f"{slot_name}\n{formatted_teams}", style="filled", fillcolor="lightyellow")
        #graph.node(row["StrongSeed"], label=row["StrongSeed"], style="filled", fillcolor="lightgreen")
        #graph.node(row["WeakSeed"], label=row["WeakSeed"], style="filled", fillcolor="lightpink")

        # Add directed edges from the strong and weak seed to the current slot, if they exist
        if pd.notna(row["StrongSeed"]):
            graph.edge(row["StrongSeed"], slot_name, color="blue", style="solid")
        if pd.notna(row["WeakSeed"]):
            graph.edge(row["WeakSeed"], slot_name, color="red", style="solid")

    # Render and view the graph
    graph.render(f'bracket_{side}_{year}', format='png', cleanup=True)
    graph.view()