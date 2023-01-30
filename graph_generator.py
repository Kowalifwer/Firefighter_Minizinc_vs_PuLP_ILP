import networkx as nx
import random
from matplotlib import pyplot as plt

def generate_random_firefighter_graph_data(n_nodes_range):
    possible_graph_types = ["random", "complete", "tree", "caveman", "internet"]
    type = random.choice(possible_graph_types)

    n_nodes = random.randint(*n_nodes_range)

    if type == "random":
        if random.randrange(0, 1) == 1:
            graph = nx.gnp_random_graph(n_nodes, 0.5)
        else:
            graph = nx.barabasi_albert_graph(n_nodes, 2)
    
    elif type == "caveman":
        graph = nx.connected_caveman_graph(n_nodes, random.randint(3, 5))
    
    elif type == "internet":
        graph = nx.random_internet_as_graph(n_nodes)

    elif type == "complete":
        if random.randrange(0, 1) == 1:
            graph = nx.complete_bipartite_graph(n_nodes, 2)
        else:
            graph = nx.complete_graph(n_nodes)

    elif type == "tree":
        graph = nx.random_tree(n_nodes, random.randint(3, 5))

    FROM = [tuple[0] for tuple in graph.edges]
    TO = [tuple[1] for tuple in graph.edges]
    n_nodes = len(graph.nodes)
    n_edges = len(graph.edges)

    generate_start_fires = lambda : [random.choices([0,1], weights=[0.9, 0.1])[0] for _ in range(n_nodes)]

    START_FIRES = generate_start_fires()
    while sum(START_FIRES) == 0 or sum(START_FIRES) > int(n_nodes * 0.95) or sum(START_FIRES) < int(n_nodes * 0.05):
        START_FIRES = generate_start_fires()
        
    # MAX_TIME = min(max(random.randrange(int(int(n_edges / n_fires) / 2), int(n_edges / n_fires) if int(n_edges / n_fires) > 0 else int(n_edges)), 8), 30)
    MAX_TIME = random.randrange(4, 6) if n_nodes < 50 else random.randrange(7, 12)
    # budget_defenders = random.randrange(random.randrange(n_fires, n_fires*3), int(n_edges/2) if int(n_edges/2)>n_fires else n_edges) #  between 1/3 and 3/4 of the fires
    budget_defenders = max(int(sum(START_FIRES)/3) + random.randrange(0, max(1, int(sum(START_FIRES)/2))), 1) #  between 1/3 and 3/4 of the fires
    
    return {
        "solver_data": {"MAX_TIME": MAX_TIME, "budget_defenders": budget_defenders, "n_nodes": n_nodes, "n_edges": n_edges, "FROM": FROM, "TO": TO, "START_FIRES": START_FIRES},
        "graph": graph,
        "draw_graph_params": (graph, START_FIRES),
        "type": type
    }

def draw_graph(graph, START_FIRES):
    color_map = []  # color red the starting position with fire
    for node in graph.nodes:
        if START_FIRES[node]:
            color_map.append('red')
        else:
            color_map.append('green')
    
    nx.draw(graph, with_labels=True, labels={i: i+1 for i in range(len(graph.nodes))}, node_color=color_map)
    plt.show()