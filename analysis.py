import json, random, statistics as st, itertools
import networkx as nx, numpy as np
from graphdef import *

G = build()
R = {}
n, m = G.number_of_nodes(), G.number_of_edges()
deg = dict(G.degree())
R["n"], R["m"] = n, m
R["sum_deg"] = sum(deg.values())
R["density"] = nx.density(G)
R["avg_deg"] = np.mean(list(deg.values()))
R["max_deg"] = max(deg.values()); R["min_deg"] = min(deg.values())
R["deg_dist"] = {k: sum(1 for d in deg.values() if d==k) for k in sorted(set(deg.values()))}
R["connected"] = nx.is_connected(G)
R["diameter"] = nx.diameter(G); R["radius"] = nx.radius(G)
R["center"] = nx.center(G); R["periphery"] = nx.periphery(G)
R["avg_path"] = nx.average_shortest_path_length(G)
R["avg_clustering"] = nx.average_clustering(G)
R["transitivity"] = nx.transitivity(G)
R["assortativity"] = nx.degree_assortativity_coefficient(G)
bet = nx.betweenness_centrality(G, normalized=True)
clo = nx.closeness_centrality(G)
R["deg"] = deg; R["bet"] = bet; R["clo"] = clo
R["articulation"] = sorted(nx.articulation_points(G))
R["bridges"] = sorted(tuple(sorted(e)) for e in nx.bridges(G))
R["node_conn"] = nx.node_connectivity(G); R["edge_conn"] = nx.edge_connectivity(G)
cl = list(nx.find_cliques(G)); R["max_cliques"] = sorted([sorted(c) for c in cl], key=lambda c:(-len(c), c))
R["clique_number"] = max(len(c) for c in cl)
R["triangles"] = sum(nx.triangles(G).values())//3
comms = nx.community.greedy_modularity_communities(G)
R["communities"] = [sorted(c) for c in comms]
R["modularity_found"] = nx.community.modularity(G, comms)
R["modularity_groups"] = nx.community.modularity(G, [set(v) for v in GROUPS.values()])
R["sp_1_22"] = nx.shortest_path(G, 1, 22); R["sp_1_22_len"] = nx.shortest_path_length(G,1,22)
R["all_sp_1_22"] = [p for p in nx.all_shortest_paths(G,1,22)]
ecc = nx.eccentricity(G); R["ecc"] = ecc
# Tc
k1 = np.mean(list(deg.values())); k2 = np.mean([d*d for d in deg.values()])
R["k2"] = k2; R["Tc"] = k1/(k2-k1)
beta, gamma = 0.2, 0.3
R["beta"], R["gamma"] = beta, gamma
R["T"] = beta/(beta+gamma-beta*gamma)
R["R0_net"] = R["T"]*(k2-k1)/k1

adj = {v: list(G[v]) for v in G}
def sim(removed, p0, beta, gamma, rng, T=40, series=False):
    state = {v: 0 for v in adj}
    for v in removed: state[v] = 3
    state[p0] = 1; inf = [p0]; ever = 1; peak = 1; tpeak = 0
    S = [n-len(removed)-1]; I = [1]; Rr = [0]
    for t in range(1, T+1):
        if not inf:
            if series: S.append(S[-1]); I.append(0); Rr.append(Rr[-1])
            continue
        new = []
        for i in inf:
            for j in adj[i]:
                if state[j]==0 and rng.random()<beta:
                    state[j] = 1; new.append(j)   # marked immediately (not infectious until next step)
        stay = []
        for i in inf:
            if rng.random()<gamma: state[i] = 2
            else: stay.append(i)
        inf = stay + new   # new infections become infectious next step
        ever += len(new)
        if len(inf) > peak: peak = len(inf); tpeak = t
        if series:
            Rr.append(sum(1 for v in state.values() if v==2))
            I.append(len(inf)); S.append(sum(1 for v in state.values() if v==0))
    return ever, peak, tpeak, (S,I,Rr)
# NOTE: marking new infections immediately prevents double attempts; they only transmit next step.

# E1: random patient zero, no intervention
rng = random.Random(2026)
runs = 10000; T = 40
acc = np.zeros((3, T+1)); sizes = []; peaks = []; tpeaks = []
for _ in range(runs):
    p0 = rng.randint(1, n)
    e, pk, tp, (S,I,Rr) = sim(set(), p0, beta, gamma, rng, T, True)
    acc += np.array([S,I,Rr]); sizes.append(e); peaks.append(pk); tpeaks.append(tp)
acc /= runs
R["E1"] = {"mean_size": float(np.mean(sizes)), "median_size": float(np.median(sizes)),
           "mean_peak": float(np.mean(peaks)), "mean_tpeak": float(np.mean(tpeaks)),
           "frac_major": float(np.mean(np.array(sizes) >= 0.5*n)),
           "frac_fizzle": float(np.mean(np.array(sizes) <= 3)), "runs": runs}
R["curves"] = acc.tolist()
# E2: by patient zero
rng = random.Random(7); e2 = {}
for p0 in range(1, n+1):
    s = [sim(set(), p0, beta, gamma, rng)[0] for _ in range(3000)]
    e2[p0] = float(np.mean(s))
R["E2"] = e2
# E3: containment
def top(score, k, G_):
    return [v for v,_ in sorted(score.items(), key=lambda kv:(-kv[1], kv[0]))[:k]]
deg_rank = sorted(G.nodes(), key=lambda v:(-deg[v], -bet[v], v))
bet_rank = sorted(G.nodes(), key=lambda v:(-bet[v], -deg[v], v))
# adaptive betweenness
def adaptive(k):
    H = G.copy(); chosen = []
    for _ in range(k):
        b = nx.betweenness_centrality(H)
        v = sorted(H.nodes(), key=lambda x:(-b[x], x))[0]
        chosen.append(v); H.remove_node(v)
    return chosen
adapt_rank = adaptive(6)
R["rank_deg"] = deg_rank[:6]; R["rank_bet"] = bet_rank[:6]; R["rank_adapt"] = adapt_rank
rng = random.Random(99); runs3 = 4000; ks = list(range(0, 7))
E3 = {"Random": [], "Highest degree": [], "Highest betweenness": [], "Adaptive betweenness": []}
for k in ks:
    for name in E3:
        tot = []
        for _ in range(runs3):
            if name=="Random": rem = set(rng.sample(range(1,n+1), k))
            elif name=="Highest degree": rem = set(deg_rank[:k])
            elif name=="Highest betweenness": rem = set(bet_rank[:k])
            else: rem = set(adapt_rank[:k])
            cand = [v for v in range(1,n+1) if v not in rem]
            p0 = rng.choice(cand)
            tot.append(sim(rem, p0, beta, gamma, rng)[0])
        E3[name].append(float(np.mean(tot)))
R["E3"] = E3; R["ks"] = ks
# components after k=3
def comps_after(rem):
    H = G.copy(); H.remove_nodes_from(rem)
    return sorted([sorted(c) for c in nx.connected_components(H)], key=lambda c:-len(c))
for name, rank in [("deg", deg_rank), ("bet", bet_rank), ("adapt", adapt_rank)]:
    R["comps3_"+name] = comps_after(rank[:3])
R["comps_remove17"] = comps_after([17]); R["comps_remove9"] = comps_after([9])
# E4: threshold curve
rng = random.Random(5); Ts = [round(x,3) for x in np.linspace(0.02, 0.9, 23)]
e4 = []
for Tt in Ts:
    b = Tt*gamma/(1-Tt*(1-gamma))
    s = [sim(set(), rng.randint(1,n), b, gamma, rng)[0] for _ in range(3000)]
    e4.append(float(np.mean(s)))
R["E4"] = {"T": Ts, "size": e4}
# E5: edge removal (distancing) - cut the bridges between groups vs random 5 edges
rng = random.Random(11)
def sim_edges(rem_edges, runs=4000):
    H = G.copy(); H.remove_edges_from(rem_edges)
    global adj
    old = adj; adj = {v: list(H[v]) for v in H}
    tot = [sim(set(), rng.randint(1,n), beta, gamma, rng)[0] for _ in range(runs)]
    adj = old
    return float(np.mean(tot))
inter = [(6,7),(5,9),(12,13),(9,15),(17,18)]
R["E5"] = {"none": sim_edges([]), "remove_bridge_17_18": sim_edges([(17,18)]),
           "remove_all_5_links": sim_edges(inter),
           "remove_5_random": float(np.mean([sim_edges(rng.sample(list(G.edges()),5), 400) for _ in range(40)]))}
json.dump(R, open("results.json","w"), default=lambda o: o.item() if hasattr(o,"item") else list(o), indent=1)
print(json.dumps({k:v for k,v in R.items() if k not in ("curves","deg","bet","clo","E4","ecc")}, default=lambda o:o.item() if hasattr(o,"item") else list(o), indent=1))
print("deg", deg); print("bet", {k:round(v,3) for k,v in bet.items()})
