import json, numpy as np, networkx as nx
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from graphdef import *

R = json.load(open("results.json")); G = build()
INK, SUB, GRID = "#191919", "#666666", "#e3e3e3"
GC = {"A": "#257de0", "B": "#f47230", "C": "#008a17", "D": "#6a4ce2"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
    "axes.edgecolor": "#bbbbbb", "axes.labelcolor": INK, "xtick.color": SUB, "ytick.color": SUB,
    "axes.spines.top": False, "axes.spines.right": False})
# layout: Kamada-Kawai, rotated so the four groups read left to right
pos = nx.kamada_kawai_layout(G, scale=3.0)
pos = {v: (float(p[0])*1.5, float(p[1])) for v, p in pos.items()}
def halo(t): t.set_path_effects([pe.withStroke(linewidth=2.2, foreground=INK)])
def draw(ax, G_, node_colors, sizes=None, edge_colors=None, edge_w=None, removed=(), labels=True):
    nodes = [v for v in G_.nodes()]
    if edge_colors is None: edge_colors = ["#9a9a9a"]*G_.number_of_edges()
    if edge_w is None: edge_w = [1.4]*G_.number_of_edges()
    nx.draw_networkx_edges(G_, pos, ax=ax, edge_color=edge_colors, width=edge_w)
    ns = sizes or {v: 520 for v in nodes}
    nx.draw_networkx_nodes(G_, pos, ax=ax, nodelist=nodes, node_color=[node_colors[v] for v in nodes],
        node_size=[ns[v] for v in nodes], edgecolors="white", linewidths=1.6)
    if labels:
        for v in nodes:
            halo(ax.text(pos[v][0], pos[v][1], str(v), ha="center", va="center", color="white", fontsize=9, fontweight="bold"))
    ax.set_axis_off(); ax.set_aspect("equal")
deg = {int(k): v for k, v in R["deg"].items()}; bet = {int(k): v for k, v in R["bet"].items()}

# Fig 1: network by group, size by degree
fig, ax = plt.subplots(figsize=(8.0, 6.0))
draw(ax, G, {v: GC[group_of(v)] for v in G}, sizes={v: 200 + 85*deg[v] for v in G})
ax.legend(handles=[Line2D([0],[0], marker="o", ls="", color=GC[g], markersize=9, label=f"Group {g}: {GROUP_NAMES[g]}") for g in GROUPS],
          loc="lower left", frameon=False, fontsize=9, bbox_to_anchor=(-0.02, -0.04))
ax.set_title("Contact network of 22 students (node size = degree)", loc="left", fontsize=11, fontweight="bold")
fig.tight_layout(); fig.savefig("fig1_network.png", dpi=220); plt.close(fig)

# Fig 2: centralities
order = sorted(G.nodes(), key=lambda v: (-deg[v], v))[:10]
fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.6))
d_order = sorted(G.nodes(), key=lambda v: (-deg[v], v))[:8]
b_order = sorted(G.nodes(), key=lambda v: (-bet[v], v))[:8]
for ax, order, vals, title, fmt in [(axs[0], d_order, deg, "Degree (top 8)", "{:d}"), (axs[1], b_order, bet, "Betweenness (top 8)", "{:.2f}")]:
    y = np.arange(len(order))[::-1]
    ax.barh(y, [vals[v] for v in order], color="#257de0", height=0.62)
    ax.set_yticks(y); ax.set_yticklabels([f"Student {v}" for v in order], fontsize=9)
    for yy, v in zip(y, order): ax.text(vals[v] + (0.08 if fmt=="{:d}" else 0.008), yy, fmt.format(vals[v]), va="center", fontsize=8.5, color=SUB)
    ax.set_title(title, loc="left", fontsize=10, fontweight="bold"); ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
axs[0].set_xlim(0, 8.2); axs[1].set_xlim(0, 0.68)
fig.tight_layout(); fig.savefig("fig2_centrality.png", dpi=220); plt.close(fig)

# Fig 3: structure - cut vertices and bridge
art = set(R["articulation"]); br = {tuple(e) for e in R["bridges"]}
fig, ax = plt.subplots(figsize=(7.6, 4.9))
cols = {v: ("#ec4647" if v in art else "#b9b9b9") for v in G}
ecol = ["#ec4647" if tuple(sorted(e)) in br else "#9a9a9a" for e in G.edges()]
ew = [3.6 if tuple(sorted(e)) in br else 1.2 for e in G.edges()]
draw(ax, G, cols, edge_colors=ecol, edge_w=ew)
ax.annotate("Bridge (17,18):\nthe only link to Group D", xy=((pos[17][0]+pos[18][0])/2, (pos[17][1]+pos[18][1])/2), xytext=(1.7, 0.7),
            fontsize=9, color=INK, arrowprops=dict(arrowstyle="-", color=SUB, lw=0.9))
ax.set_title("Cut vertices (red) and the bridge", loc="left", fontsize=11, fontweight="bold")
fig.tight_layout(); fig.savefig("fig3_structure.png", dpi=220); plt.close(fig)

# Fig 4: BFS waves from hub 9 vs periphery 22
blues = ["#0e3d7e", "#1757ac", "#257de0", "#519ced", "#84b9f3", "#b6d5f8", "#cce3fd", "#e6f1fd", "#f2f8fe"]
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.5))
for ax, src in zip(axs, [9, 22]):
    dist = nx.single_source_shortest_path_length(G, src)
    cols = {v: blues[dist[v]] for v in G}
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#9a9a9a", width=1.2)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=[cols[v] for v in G], node_size=250, edgecolors="#555555", linewidths=0.9)
    for v in G: ax.text(pos[v][0], pos[v][1], str(dist[v]), ha="center", va="center", fontsize=8, color="white" if dist[v] <= 2 else INK, fontweight="bold")
    ax.set_title(f"Patient zero = student {src}\nfarthest student is {max(dist.values())} steps away", loc="left", fontsize=9.5, fontweight="bold")
    ax.set_axis_off(); ax.set_aspect("equal")
fig.text(0.01, 0.01, "Numbers inside nodes = shortest-path distance from patient zero (darker = closer).", fontsize=8.5, color=SUB)
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig("fig4_waves.png", dpi=220); plt.close(fig)

# Fig 5: epidemic curves
cur = np.array(R["curves"]); t = np.arange(cur.shape[1])
fig, ax = plt.subplots(figsize=(7.2, 3.8))
for row, name, c in [(0, "Susceptible", "#257de0"), (1, "Infectious", "#f47230"), (2, "Recovered", "#008a17")]:
    ax.plot(t, cur[row], color=c, lw=2.2, marker="o", ms=3.2, label=name)
ax.set_xlabel("Time step (day)"); ax.set_ylabel("Average number of students"); ax.set_xlim(0, 40); ax.set_ylim(0, 22)
ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
ax.legend(frameon=False, loc="center right")
ax.set_title("Average epidemic curves (10,000 runs, random patient zero)", loc="left", fontsize=11, fontweight="bold")
fig.tight_layout(); fig.savefig("fig5_curves.png", dpi=220); plt.close(fig)

# Fig 6: outbreak size by patient zero
e2 = {int(k): v for k, v in R["E2"].items()}
fig, ax = plt.subplots(figsize=(7.4, 3.5))
vs = list(range(1, 23))
ax.bar(vs, [e2[v] for v in vs], color=[GC[group_of(v)] for v in vs], width=0.7)
ax.axhline(R["E1"]["mean_size"], color=SUB, lw=1, ls="--"); ax.text(22.6, R["E1"]["mean_size"] + 0.15, "overall\naverage", fontsize=8, color=SUB, ha="right", va="bottom")
ax.set_xticks(vs); ax.set_xlabel("Patient zero (student)"); ax.set_ylabel("Average number infected")
ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True); ax.set_xlim(0.3, 22.7); ax.set_ylim(0, 10.5)
ax.legend(handles=[Line2D([0],[0], marker="s", ls="", color=GC[g], markersize=8, label=f"Group {g}") for g in GROUPS], frameon=False, ncol=4, loc="upper left", fontsize=8.5)
ax.set_title("Where the outbreak starts matters", loc="left", fontsize=11, fontweight="bold")
fig.tight_layout(); fig.savefig("fig6_patientzero.png", dpi=220); plt.close(fig)

# Fig 7: containment
ks = R["ks"]; E3 = R["E3"]
styles = {"Random": ("#6a4ce2", "o"), "Highest degree": ("#257de0", "s"), "Highest betweenness": ("#f47230", "^"), "Adaptive betweenness": ("#008a17", "D")}
fig, ax = plt.subplots(figsize=(7.2, 3.9))
for name, (c, mk) in styles.items(): ax.plot(ks, E3[name], color=c, lw=2, marker=mk, ms=5, label=name)
ax.set_xlabel("Number of students vaccinated (removed)"); ax.set_ylabel("Average number infected")
ax.set_xticks(ks); ax.set_ylim(0, 7.6); ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
ax.legend(frameon=False, loc="upper right", fontsize=9)
ax.set_title("Targeted vaccination beats random vaccination", loc="left", fontsize=11, fontweight="bold")
fig.tight_layout(); fig.savefig("fig7_containment.png", dpi=220); plt.close(fig)

# Fig 8: fragmentation panels
panels = [("Highest degree", R["rank_deg"][:3]), ("Highest betweenness", R["rank_bet"][:3]), ("Adaptive betweenness", R["rank_adapt"][:3])]
comp_cols = ["#257de0", "#f47230", "#008a17", "#6a4ce2"]
fig, axs = plt.subplots(1, 3, figsize=(7.6, 3.1))
for ax, (title, rem) in zip(axs, panels):
    H = G.copy(); H.remove_nodes_from(rem)
    comps = sorted(nx.connected_components(H), key=lambda c: -len(c))
    cmap = {v: comp_cols[i % 4] for i, c in enumerate(comps) for v in c}
    nx.draw_networkx_edges(H, pos, ax=ax, edge_color="#9a9a9a", width=1.1)
    nx.draw_networkx_nodes(H, pos, ax=ax, node_color=[cmap[v] for v in H], node_size=170, edgecolors="white", linewidths=0.8)
    for v in H: halo(ax.text(pos[v][0], pos[v][1], str(v), ha="center", va="center", color="white", fontsize=6, fontweight="bold"))
    for v in rem: ax.text(pos[v][0], pos[v][1], "X", ha="center", va="center", color="#999999", fontsize=11, fontweight="bold")
    ax.set_title(f"{title}\nremoves {', '.join(map(str, rem))}\n{len(comps)} piece{'s' if len(comps)>1 else ''}: sizes {', '.join(str(len(c)) for c in comps)}", loc="left", fontsize=8.6, fontweight="bold")
    ax.set_axis_off(); ax.set_aspect("equal")
fig.subplots_adjust(left=0.01, right=0.99, top=0.76, bottom=0.02, wspace=0.05); fig.savefig("fig8_fragments.png", dpi=220); plt.close(fig)

# Fig 9: threshold
e4 = R["E4"]
fig, ax = plt.subplots(figsize=(7.0, 3.6))
ax.plot(e4["T"], e4["size"], color="#257de0", lw=2.2, marker="o", ms=3.6)
ax.axvline(R["Tc"], color="#f47230", lw=1.4, ls="--"); ax.text(R["Tc"] + 0.012, 18.5, f"T_c = {R['Tc']:.2f}", color=INK, fontsize=9)
ax.axvline(R["T"], color="#008a17", lw=1.4, ls="--"); ax.text(R["T"] + 0.012, 3.2, f"our disease\nT = {R['T']:.2f}", color=INK, fontsize=9)
ax.set_xlabel("Transmissibility T (chance an infection crosses an edge)"); ax.set_ylabel("Average number infected")
ax.set_ylim(0, 22); ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
ax.set_title("Outbreak size grows with transmissibility", loc="left", fontsize=11, fontweight="bold")
fig.tight_layout(); fig.savefig("fig9_threshold.png", dpi=220); plt.close(fig)
print("ok")
