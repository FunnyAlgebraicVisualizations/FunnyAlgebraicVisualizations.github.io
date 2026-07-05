import networkx as nx
import plotly.graph_objs as go
from sympy.combinatorics import Permutation
import itertools
from plotly.offline import plot

def perm_to_cycle_str(p):
    cycles = p.cyclic_form
    if not cycles:
        return 'e'
    return ''.join(['(' + ' '.join(str(i + 1) for i in cycle) + ')' for cycle in cycles])

def build_cayley_graph_S4_with_A4_marked():
    G = nx.Graph()
    n = 4
    all_perms = [Permutation(p) for p in itertools.permutations(range(n))]
    A4 = {p for p in all_perms if p.signature() == 1}
    S4 = set(all_perms)

    perm_labels = {p: perm_to_cycle_str(p) for p in S4}
    label_lookup = {v: p for p, v in perm_labels.items()}

    for p in S4:
        label = perm_labels[p]
        G.add_node(label, in_A4=(p in A4))

    # Generators
    gen_a = Permutation([[0, 1, 2]])       # (1 2 3)
    gen_b = Permutation([[0, 1], [2, 3]])  # (1 2)(3 4)
    gen_c = Permutation([[0, 1]])          # (1 2)

    generators = [(gen_a, '(1 2 3)'), (gen_b, '(1 2)(3 4)'), (gen_c, '(1 2)')]
    color_map = {'(1 2 3)': 'red', '(1 2)(3 4)': 'blue', '(1 2)': 'green'}

    for gen, label in generators:
        for perm in S4:
            neighbor = perm * gen
            if neighbor in S4:
                u = perm_labels[perm]
                v = perm_labels[neighbor]
                if G.nodes[u]['in_A4'] or G.nodes[v]['in_A4']:
                    G.add_edge(u, v, generator=label)

    return G, [label for _, label in generators], color_map

def visualize_filtered_graph(G, gen_labels, color_map):
    pos = nx.spring_layout(G, dim=3, seed=46)

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
        if edge_x:
            edge_trace = go.Scatter3d(
                x=edge_x, y=edge_y, z=edge_z,
                mode='lines',
                line=dict(color=color_map.get(gen_label, 'gray'), width=2),
                name=gen_label,
                hoverinfo='none'
            )
            edge_traces.append(edge_trace)

    node_x_A4, node_y_A4, node_z_A4 = [], [], []
    node_x_S4, node_y_S4, node_z_S4 = [], [], []
    node_labels, label_x, label_y, label_z = [], [], [], []

    for node, data in G.nodes(data=True):
        x, y, z = pos[node]
        node_labels.append(node)
        label_x.append(x)
        label_y.append(y)
        label_z.append(z)
        if data['in_A4']:
            node_x_A4.append(x)
            node_y_A4.append(y)
            node_z_A4.append(z)
        else:
            node_x_S4.append(x)
            node_y_S4.append(y)
            node_z_S4.append(z)

    trace_A4 = go.Scatter3d(
        x=node_x_A4, y=node_y_A4, z=node_z_A4,
        mode='markers',
        marker=dict(size=8, color='skyblue'),
        hoverinfo='none',
        name=r"$\text{even permutations }(A_4)$"
    )

    trace_S4 = go.Scatter3d(
        x=node_x_S4, y=node_y_S4, z=node_z_S4,
        mode='markers',
        marker=dict(size=8, color='orange'),
        hoverinfo='none',
        name=r"$\text{odd permutations}$"
    )

    label_trace = go.Scatter3d(
        x=label_x, y=label_y, z=label_z,
        mode='text',
        text=node_labels,
        textposition="top center",
        name=r"$\text{permutation labels}$",
        visible=True
    )

    fig = go.Figure(data=edge_traces + [trace_A4, trace_S4, label_trace])
    fig.update_layout(
        #title=r"$\text{Cayley Graph of }S_4 \text{ generated based on }A_4$",
        showlegend=True,
        legend_title="Generators",
        margin=dict(l=0, r=0, b=0, t=60),
        scene=dict(
            xaxis=dict(showbackground=False, visible=False),
            yaxis=dict(showbackground=False, visible=False),
            zaxis=dict(showbackground=False, visible=False)
        )
    )
    # fig.show()  # disabled for headless regeneration
    plot(fig, filename='cayley_graph_S4_A4.html', auto_open=False, include_mathjax='cdn')

G, gen_labels, color_map = build_cayley_graph_S4_with_A4_marked()
visualize_filtered_graph(G, gen_labels, color_map)
