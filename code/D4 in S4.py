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

def build_cayley_graph_custom():
    G = nx.Graph()
    n = 4
    perms = [Permutation(p) for p in itertools.permutations(range(n))]
    perm_labels = {p: perm_to_cycle_str(p) for p in perms}
    G.add_nodes_from(perm_labels.values())
    gen_a = Permutation([[0, 3, 2, 1]])       # (1 4 3 2)
    gen_b = Permutation([[0, 1], [2, 3]])     # (1 2)(3 4)
    gen_c = Permutation([[2, 3]])             # (3 4)

    D4 = set()
    to_process = [Permutation(range(n))]
    while to_process:
        current = to_process.pop()
        if current in D4:
            continue
        D4.add(current)
        to_process.extend([current * gen_a, current * gen_b])

    S4 = set(D4)
    to_process = list(D4)
    while to_process:
        current = to_process.pop()
        new = current * gen_c
        if new not in S4:
            S4.add(new)
            to_process.append(new)

    generators = [gen_a, gen_b, gen_c]
    gen_labels = ['(1 4 3 2)', '(1 2)(3 4)', '(3 4)']
    color_map = {'(1 4 3 2)': 'red', '(1 2)(3 4)': 'blue', '(3 4)': 'green'}

    for gen, label in zip(generators, gen_labels):
        for perm in S4:
            neighbor = perm * gen
            G.add_edge(perm_labels[perm], perm_labels[neighbor], generator=label)

    D4_labels = set(perm_labels[p] for p in D4)

    return G, gen_labels, color_map, D4_labels


def visualize_3d_graph(G, gen_labels, color_map, D4_labels):
    pos = nx.spring_layout(G, dim=3, seed=45)

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

    node_traces = []

    # D4 Nodes
    node_x, node_y, node_z, labels = [], [], [], []
    for node in D4_labels:
        x, y, z = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        labels.append(node)

    node_traces.append(go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        marker=dict(size=8, color='orange'),
        text=labels,
        hoverinfo='text',
        textposition="top center",
        name="elements of D₄"
    ))

    # S4 \ D4 Nodes
    node_x, node_y, node_z, labels = [], [], [], []
    for node in set(G.nodes()) - D4_labels:
        x, y, z = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        labels.append(node)

    node_traces.append(go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        marker=dict(size=8, color='skyblue'),
        text=labels,
        hoverinfo='text',
        textposition="top center",
        name="other elements of S₄"
    ))

    fig = go.Figure(data=edge_traces + node_traces)
    fig.update_layout(
        #title=r"$\text{Cayley Graph of }S_4\text{ generated based on }D_4$",
        showlegend=True,
        legend_title="Generators",
        margin=dict(l=0, r=0, b=0, t=50),
        scene=dict(
            xaxis=dict(showbackground=False, visible=False),
            yaxis=dict(showbackground=False, visible=False),
            zaxis=dict(showbackground=False, visible=False)
        )
    )

    fig.write_image("cayley_graph_D4_in_S4.png",
                    width=900, height=820, scale=2)
    plot(fig, filename='cayley_graph_S4_D4.html', auto_open=False, include_mathjax='cdn')

G, gen_labels, color_map, D4_labels = build_cayley_graph_custom()
visualize_3d_graph(G, gen_labels, color_map, D4_labels)