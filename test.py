import networkx as nx
import matplotlib.pyplot as plt

# Initialize the directed graph
G = nx.DiGraph()

# Define the regions and round identifiers
regions = ['W', 'X', 'Y', 'Z']
rounds = ['R1', 'R2', 'R3', 'R4', 'R5']  # Round 1, Round 2, Sweet 16, Elite 8, Final 4

# Create nodes for the games
for region in regions:
    for round_ in rounds:
        if round_ == 'R1':
            # Round 1 has 16 games per region
            for i in range(1, 17):
                slot = f'{round_}{region}{i}'
                G.add_node(slot, label=slot)
                # Add edges to next rounds for progression
                if round_ == 'R1':
                    # Round 1 games feed into Round 2
                    next_round = f'R2{region}{(i + 1) // 2}'  # Matches R1W1 -> R2W1, R1W2 -> R2W2, etc.
                    G.add_edge(slot, next_round)

        elif round_ == 'R2':
            # Round 2 has 8 games per region
            for i in range(1, 9):
                slot = f'{round_}{region}{i}'
                G.add_node(slot, label=slot)
                # Round 2 games feed into Sweet 16
                next_round = f'R3{region}{i // 2}'  # Matches R2W1 -> R3W1, etc.
                G.add_edge(slot, next_round)

        elif round_ == 'R3':
            # Round 3 (Sweet 16) has 4 games per region
            for i in range(1, 5):
                slot = f'{round_}{region}{i}'
                G.add_node(slot, label=slot)
                # Round 3 games feed into Elite 8
                next_round = f'R4{region}{i // 2}'  # Matches R3W1 -> R4W1, etc.
                G.add_edge(slot, next_round)

        elif round_ == 'R4':
            # Round 4 (Elite 8) has 2 games per region
            for i in range(1, 3):
                slot = f'{round_}{region}{i}'
                G.add_node(slot, label=slot)
                # Round 4 games feed into Final 4
                next_round = f'R5{region}{i // 2}'  # Matches R4W1 -> R5W1, etc.
                G.add_edge(slot, next_round)

        elif round_ == 'R5':
            # Round 5 (Final 4) has 1 game for each pair of regions
            if region == 'W':
                slot = f'{round_}W1'
                G.add_node(slot, label=slot)
            elif region == 'X':
                slot = f'{round_}X1'
                G.add_node(slot, label=slot)
            elif region == 'Y':
                slot = f'{round_}Y1'
                G.add_node(slot, label=slot)
            elif region == 'Z':
                slot = f'{round_}Z1'
                G.add_node(slot, label=slot)

            # Final 4 games feed into Championship Game (1 final node)
            G.add_edge(slot, 'Championship')

# Now we plot the graph
plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G, k=0.2, iterations=50)  # Positioning layout
nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=8, font_weight='bold', alpha=0.7,
        edge_color='gray')

# Customize the plot
plt.title("March Madness Tournament Bracket", fontsize=16)
plt.show()