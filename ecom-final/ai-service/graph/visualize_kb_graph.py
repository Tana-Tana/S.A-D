"""
Sinh hinh anh truc quan hoa mot phan KB_Graph (Neo4j) de minh hoa cho bao cao.

Lay mau vai user + cac san pham/lien ket lien quan (VIEWED/CLICKED/ADDED_TO_CART/
PREDICTED_NEXT_ACTION/CO_OCCURS) va ve bang networkx + matplotlib.
"""

import os
import random

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import networkx as nx
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kb_graph_sample.png')

REL_COLORS = {
    'VIEWED': '#4C72B0',
    'CLICKED': '#DD8452',
    'ADDED_TO_CART': '#C44E52',
    'PREDICTED_NEXT_ACTION': '#8172B2',
    'CO_OCCURS': '#999999',
}

SAMPLE_USERS = [1, 2, 3, 4, 5]


def fetch_subgraph(driver):
    G = nx.MultiDiGraph()
    with driver.session() as session:
        result = session.run("""
            MATCH (u:User)-[r]->(p:Product)
            WHERE u.user_id IN $users
              AND type(r) IN ['VIEWED','CLICKED','ADDED_TO_CART','PREDICTED_NEXT_ACTION']
            RETURN u.user_id AS user_id, p.product_id AS product_id, type(r) AS rel_type
        """, users=SAMPLE_USERS)
        for rec in result:
            u, p = f"U{rec['user_id']}", f"P{rec['product_id']}"
            G.add_node(u, kind='user')
            G.add_node(p, kind='product')
            G.add_edge(u, p, rel=rec['rel_type'])

        product_ids = sorted({int(n[1:]) for n in G.nodes if n.startswith('P')})
        if product_ids:
            result = session.run("""
                MATCH (p1:Product)-[c:CO_OCCURS]->(p2:Product)
                WHERE p1.product_id IN $pids OR p2.product_id IN $pids
                RETURN p1.product_id AS p1, p2.product_id AS p2, c.weight AS weight
                ORDER BY c.weight DESC LIMIT 50
            """, pids=product_ids)
            for rec in result:
                p1, p2 = f"P{rec['p1']}", f"P{rec['p2']}"
                G.add_node(p1, kind='product')
                G.add_node(p2, kind='product')
                G.add_edge(p1, p2, rel='CO_OCCURS', weight=rec['weight'])

    return G


def draw(G):
    pos = nx.spring_layout(G, seed=7, k=2.2, iterations=300, scale=2.5)

    # Cac node co cung tap lang gieng se hoi tu ve cung mot diem -> nhich nhe
    # de nhan/diem khong de len nhau.
    jitter_rng = random.Random(123)
    for node in pos:
        pos[node] = (
            pos[node][0] + jitter_rng.uniform(-0.35, 0.35),
            pos[node][1] + jitter_rng.uniform(-0.35, 0.35),
        )

    user_nodes = [n for n, d in G.nodes(data=True) if d['kind'] == 'user']
    product_nodes = [n for n, d in G.nodes(data=True) if d['kind'] == 'product']

    fig, ax = plt.subplots(figsize=(16, 12))

    nx.draw_networkx_nodes(G, pos, nodelist=user_nodes, node_color='#4C72B0',
                            node_shape='o', node_size=700, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=product_nodes, node_color='#DD8452',
                            node_shape='s', node_size=1000, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, font_color='white', font_weight='bold', ax=ax)

    for rel_type, color in REL_COLORS.items():
        edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('rel') == rel_type]
        if edges:
            style = 'dashed' if rel_type == 'CO_OCCURS' else 'solid'
            nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=color, alpha=0.6,
                                    style=style, arrows=True, arrowsize=12,
                                    connectionstyle='arc3,rad=0.1', ax=ax)

    node_legend = [
        Patch(facecolor='#4C72B0', label='User'),
        Patch(facecolor='#DD8452', label='Product'),
    ]
    edge_legend = [
        Line2D([0], [0], color=c, lw=2,
               linestyle='dashed' if r == 'CO_OCCURS' else 'solid', label=r)
        for r, c in REL_COLORS.items()
    ]
    ax.legend(handles=node_legend + edge_legend, loc='upper left', fontsize=9)

    ax.set_title(f"KB_Graph (Neo4j) — mau {len(SAMPLE_USERS)} user dau tien "
                  f"({G.number_of_nodes()} nodes, {G.number_of_edges()} relationships)")
    ax.axis('off')
    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=120)
    plt.close(fig)


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    G = fetch_subgraph(driver)
    driver.close()
    draw(G)
    print(f"Da luu {OUTPUT_PATH} - {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")


if __name__ == '__main__':
    main()
