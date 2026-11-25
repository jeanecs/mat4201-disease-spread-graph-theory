import networkx as nx

GROUPS = {
    "A": [1, 2, 3, 4, 5, 6],        # Basketball team
    "B": [7, 8, 9, 10, 11, 12],     # Dorm floor
    "C": [13, 14, 15, 16, 17],      # Student council
    "D": [18, 19, 20, 21, 22],      # Research club
}
GROUP_NAMES = {"A": "Basketball team", "B": "Dorm floor", "C": "Student council", "D": "Research club"}
EDGES = [
    # Group A
    (1,2),(1,3),(1,4),(2,3),(2,4),(3,4),(3,5),(4,5),(5,6),(4,6),
    # Group B
    (7,8),(7,9),(8,9),(8,10),(9,10),(9,11),(10,11),(10,12),(11,12),(9,12),
    # Group C
    (13,14),(13,15),(14,15),(14,16),(15,16),(15,17),(16,17),(13,17),
    # Group D
    (18,19),(18,20),(19,20),(19,21),(20,21),(20,22),(21,22),
    # Links between groups
    (6,7),(5,9),(12,13),(9,15),(17,18),
]
def build():
    G = nx.Graph()
    G.add_nodes_from(range(1, 23))
    G.add_edges_from(EDGES)
    return G
def group_of(v):
    for g, vs in GROUPS.items():
        if v in vs: return g
