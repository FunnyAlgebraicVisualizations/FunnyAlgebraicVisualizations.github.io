import networkx as nx
import plotly.graph_objs as go
from sympy.combinatorics import Permutation
from plotly.offline import plot

# Standalone Cayley graph of D4 (paper Figure 11), in the same 3D-spring Plotly
# style as the other graphs. Writes the interactive HTML here and the PNG into
# the paper's figures/ folder.
FIG = "cayley_graph_D4_alone.png"


def perm_to_cycle_str(p):
    cycles = p.cyclic_form
    if not cycles:
        return 'e'
    return ''.join(['(' + ' '.join(str(i + 1) for i in cycle) + ')' for cycle in cycles])


def build_d4_graph():
    n = 4
    gen_a = Permutation([[0, 3, 2, 1]])     # (1 4 3 2) rotation r
    gen_b = Permutation([[0, 1], [2, 3]])   # (1 2)(3 4) reflection s

    D4 = set()
    to_process = [Permutation(list(range(n)))]
    while to_process:
        current = to_process.pop()
        if current in D4:
            continue
        D4.add(current)
        to_process.extend([current * gen_a, current * gen_b])
    assert len(D4) == 8

    labels = {p: perm_to_cycle_str(p) for p in D4}
    G = nx.Graph()
    G.add_nodes_from(labels.values())
    generators = [(gen_a, '(1 4 3 2)'), (gen_b, '(1 2)(3 4)')]
    color_map = {'(1 4 3 2)': 'red', '(1 2)(3 4)': 'blue'}
    for gen, label in generators:
        for p in D4:
            G.add_edge(labels[p], labels[p * gen], generator=label)
    return G, [lbl for _, lbl in generators], color_map


def visualize(G, gen_labels, color_map):
    pos = nx.spring_layout(G, dim=3, seed=7)

    edge_traces = []
    for gl in gen_labels:
        ex, ey, ez = [], [], []
        for u, v, d in G.edges(data=True):
            if d['generator'] == gl:
                x0, y0, z0 = pos[u]
                x1, y1, z1 = pos[v]
                ex += [x0, x1, None]
                ey += [y0, y1, None]
                ez += [z0, z1, None]
        edge_traces.append(go.Scatter3d(
            x=ex, y=ey, z=ez, mode='lines',
            line=dict(color=color_map.get(gl, 'gray'), width=2),
            name=gl, hoverinfo='none'))

    node_x, node_y, node_z, labels = [], [], [], []
    for node in G.nodes():
        x, y, z = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        labels.append(node)
    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z, mode='markers+text',
        marker=dict(size=8, color='skyblue'),
        text=labels, textposition='top center', hoverinfo='text',
        name='elements of D₄')

    fig = go.Figure(edge_traces + [node_trace])
    fig.update_layout(
        showlegend=True, legend_title='Generators',
        margin=dict(l=0, r=0, b=0, t=10),
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False),
                   zaxis=dict(visible=False), bgcolor='white'))
    fig.write_image(FIG, width=820, height=720, scale=2)
    plot(fig, filename='cayley_graph_D4_alone.html', auto_open=False, include_mathjax='cdn')


G, gen_labels, color_map = build_d4_graph()
visualize(G, gen_labels, color_map)
print("wrote cayley_graph_D4_alone.png + .html")
