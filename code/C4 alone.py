import networkx as nx
import plotly.graph_objs as go
from sympy.combinatorics import Permutation
import math
from plotly.offline import plot

# Standalone Cayley graph of C4 (paper Figure 13): a single square, the four
# powers of (1 2 3 4) joined in a cycle. Writes the interactive HTML here and
# the PNG into the paper's figures/ folder.
FIG = "cayley_graph_C4_alone.png"


def perm_to_cycle_str(p):
    cycles = p.cyclic_form
    if not cycles:
        return 'e'
    return ''.join(['(' + ' '.join(str(i + 1) for i in cycle) + ')' for cycle in cycles])


def build_c4_graph():
    gen_c4 = Permutation([[0, 1, 2, 3]])    # (1 2 3 4)
    identity = Permutation([0, 1, 2, 3])
    C4 = [identity]
    current = identity
    for _ in range(3):
        current = current * gen_c4
        C4.append(current)
    assert len(C4) == 4

    labels = {p: perm_to_cycle_str(p) for p in C4}
    pos = {}
    for i, p in enumerate(C4):
        ang = math.pi / 2 * i
        pos[labels[p]] = [math.cos(ang), math.sin(ang), 0.0]
    G = nx.Graph()
    G.add_nodes_from(labels.values())
    for p in C4:
        G.add_edge(labels[p], labels[p * gen_c4], generator='(1 2 3 4)')
    return G, pos


def visualize(G, pos):
    ex, ey, ez = [], [], []
    for u, v in G.edges():
        x0, y0, z0 = pos[u]
        x1, y1, z1 = pos[v]
        ex += [x0, x1, None]
        ey += [y0, y1, None]
        ez += [z0, z1, None]
    edge_trace = go.Scatter3d(
        x=ex, y=ey, z=ez, mode='lines',
        line=dict(color='purple', width=3), name='(1 2 3 4)', hoverinfo='none')

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
        name='elements of C₄')

    fig = go.Figure([edge_trace, node_trace])
    camera = dict(eye=dict(x=0, y=0, z=2.4), up=dict(x=0, y=1, z=0))
    fig.update_layout(
        showlegend=True, legend_title='Generators',
        margin=dict(l=0, r=0, b=0, t=10),
        scene=dict(xaxis=dict(visible=False, range=[-1.7, 1.7]),
                   yaxis=dict(visible=False, range=[-1.7, 1.7]),
                   zaxis=dict(visible=False), bgcolor='white',
                   aspectmode='data', camera=camera))
    fig.write_image(FIG, width=760, height=680, scale=2)
    plot(fig, filename='cayley_graph_C4_alone.html', auto_open=False, include_mathjax='cdn')


G, pos = build_c4_graph()
visualize(G, pos)
print("wrote cayley_graph_C4_alone.png + .html")
