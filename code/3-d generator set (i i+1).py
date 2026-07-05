import networkx as nx
import plotly.graph_objs as go
from sympy.combinatorics import Permutation
import itertools
from plotly.offline import plot

def perm_to_cycle_str(p):
    cycles = p.cyclic_form
    if not cycles:
        return 'e'
    return ''.join(['(' + ' '.join(str(i+1) for i in cycle) + ')' for cycle in cycles])

def build_cayley_graph(n):
    G = nx.Graph()
    perms = [Permutation(p) for p in itertools.permutations(range(n))]
    perm_labels = {p: perm_to_cycle_str(p) for p in perms}
    G.add_nodes_from(perm_labels.values())
    generators = [Permutation([[i, i + 1]], size=n) for i in range(n - 1)]
    gen_labels = [f'({i+1} {i+2})' for i in range(n - 1)]

    for gen, gen_label in zip(generators, gen_labels):
        for perm in perms:
            neighbor = perm * gen
            G.add_edge(perm_labels[perm], perm_labels[neighbor], generator=gen_label)

    return G, gen_labels

def visualize_3d_graph(G, gen_labels):
    pos = nx.spring_layout(G, dim=3, seed=42)

    color_map = {'(1 2)': 'red', '(2 3)': 'blue', '(3 4)': 'green', '(4 5)': 'purple', '(5 6)': 'orange'}

    edge_traces = []
    for gen_label in gen_labels:
        edge_x, edge_y, edge_z = [], [], []
        for u, v, d in G.edges(data=True):
            if d['generator'] == gen_label:
                x0, y0, z0 = pos[u]
                x1, y1, z1 = pos[v]
                edge_x += [x0, x1, None]
                edge_y += [y0, y1, None]
                edge_z += [z0, z1, None]
        edge_trace = go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            mode='lines',
            line=dict(color=color_map.get(gen_label, 'black'), width=2),
            name=gen_label,
            hoverinfo='none'
        )
        edge_traces.append(edge_trace)

    node_x, node_y, node_z, labels = [], [], [], []

    for node in G.nodes():
        x, y, z = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        labels.append(node)

    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        marker=dict(size=8, color='lightblue'),
        text=labels,
        hoverinfo='text',
        textposition="top center",
        name=r"$\text{elements in } S_{4}$"
    )

    fig = go.Figure(data=edge_traces + [node_trace])

    fig.update_layout(
        #title=r"$\text{Cayley Graph of } S_{4} \text{ with generator set of adjacent transpositions}$",
        showlegend=True,
        legend_title="Generators",
        margin=dict(l=0, r=0, b=0, t=50),
        scene=dict(
            xaxis=dict(showbackground=False, visible=False),
            yaxis=dict(showbackground=False, visible=False),
            zaxis=dict(showbackground=False, visible=False)
        )
    )

    # fig.show()  # disabled for headless regeneration
    plot(fig, filename='cayley_graph_S4_gs_1.html', auto_open=False, include_mathjax='cdn')

n = 4
G, gen_labels = build_cayley_graph(n)
visualize_3d_graph(G, gen_labels)
