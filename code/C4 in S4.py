import networkx as nx
import plotly.graph_objs as go
from sympy.combinatorics import Permutation
import itertools
import math
from plotly.offline import plot

def perm_to_cycle_str(p):
    cycles = p.cyclic_form
    if not cycles:
        return 'e'
    return ''.join(['(' + ' '.join(str(i + 1) for i in cycle) + ')' for cycle in cycles])

def build_full_S4_graph_with_C4_highlight():
    G = nx.Graph()
    n = 4
    all_perms = [Permutation(p) for p in itertools.permutations(range(n))]
    perm_labels = {p: perm_to_cycle_str(p) for p in all_perms}

    # Generators
    gen_c4 = Permutation([[0, 1, 2, 3]])  # (1 2 3 4)
    gen_trans = Permutation([[0, 1]])     # (1 2)
    generators = [(gen_c4, '(1 2 3 4)'), (gen_trans, '(1 2)')]
    color_map = {'(1 2 3 4)': 'purple', '(1 2)': 'green'}

    # Construct C4
    identity = Permutation([0, 1, 2, 3])
    C4 = [identity]
    current = identity
    for _ in range(3):
        current = current * gen_c4
        C4.append(current)
    C4_labels = [perm_to_cycle_str(p) for p in C4]

    # Add all nodes
    for p in all_perms:
        label = perm_labels[p]
        G.add_node(label, in_C4=(p in C4))

    # Add all generator edges
    for gen, label in generators:
        for p in all_perms:
            q = p * gen
            u = perm_labels[p]
            v = perm_labels[q]
            if not G.has_edge(u, v):
                G.add_edge(u, v, generator=label)

    # Node positions
    pos = {}
    r_inner = 1.0
    r_outer = 2.5
    C4_nodes = [label for label in G.nodes if G.nodes[label]['in_C4']]
    other_nodes = [label for label in G.nodes if not G.nodes[label]['in_C4']]

    for i, label in enumerate(C4_nodes):
        angle = 2 * math.pi * i / len(C4_nodes)
        pos[label] = [r_inner * math.cos(angle), r_inner * math.sin(angle), 0]

    for i, label in enumerate(other_nodes):
        angle = 2 * math.pi * i / len(other_nodes)
        pos[label] = [r_outer * math.cos(angle), r_outer * math.sin(angle), 0.5]

    return G, [label for _, label in generators], color_map, pos

def visualize_full_S4_graph(G, gen_labels, color_map, pos):
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
        edge_traces.append(go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            mode='lines',
            line=dict(color=color_map[gen_label], width=3),
            name=gen_label,
            hoverinfo='none'
        ))

    node_x_c4, node_y_c4, node_z_c4, labels_c4 = [], [], [], []
    node_x_other, node_y_other, node_z_other, labels_other = [], [], [], []

    for node, data in G.nodes(data=True):
        x, y, z = pos[node]
        if data['in_C4']:
            node_x_c4.append(x)
            node_y_c4.append(y)
            node_z_c4.append(z)
            labels_c4.append(node)
        else:
            node_x_other.append(x)
            node_y_other.append(y)
            node_z_other.append(z)
            labels_other.append(node)

    trace_c4 = go.Scatter3d(
        x=node_x_c4, y=node_y_c4, z=node_z_c4,
        mode='markers+text',
        marker=dict(size=8, color='orange'),
        text=labels_c4,
        hoverinfo='text',
        textposition="top center",
        name="elements of C₄"
    )

    trace_other = go.Scatter3d(
        x=node_x_other, y=node_y_other, z=node_z_other,
        mode='markers+text',
        marker=dict(size=8, color='skyblue'),
        text=labels_other,
        hoverinfo='text',
        textposition="top center",
        name="other elements of S₄"
    )

    fig = go.Figure(data=edge_traces + [trace_c4, trace_other])
    fig.update_layout(
        #title=r"$\text{Cayley Graph of }S_4\text{ generated based on }C_4$",
        showlegend=True,
        legend_title="Generators",
        margin=dict(l=0, r=0, b=0, t=60),
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor='white'
        )
    )
    # fig.show()  # disabled for headless regeneration
    # two viewpoints for the paper figures (same graph, different camera)
    fig.update_layout(scene_camera=dict(eye=dict(x=0.7, y=0.7, z=1.8)))
    fig.write_image("cayley_graph_C4_in_S4_1.png", width=780, height=720, scale=2)
    fig.update_layout(scene_camera=dict(eye=dict(x=0.0, y=0.0, z=2.2), up=dict(x=0, y=1, z=0)))
    fig.write_image("cayley_graph_C4_in_S4_2.png", width=780, height=720, scale=2)
    plot(fig, filename='cayley_graph_S4_C4.html', auto_open=False, include_mathjax='cdn')

G, gen_labels, color_map, pos = build_full_S4_graph_with_C4_highlight()
visualize_full_S4_graph(G, gen_labels, color_map, pos)
