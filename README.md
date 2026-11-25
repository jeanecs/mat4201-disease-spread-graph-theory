# Disease spread on a contact network (MAT 4201)

## Run order
    pip install networkx numpy matplotlib
    python analysis.py     # graph measures + all simulations -> results.json (takes a few seconds)
    python figures.py      # reads results.json -> fig1..fig9 PNG files

## Files
- graphdef.py : the 22-student network (groups, edge list, build() -> NetworkX graph)
- analysis.py : structural analysis (degree, betweenness, cut vertices, cliques, communities,
                distances) and every simulation (SIR runs, vaccination, edge removal, T sweep)
- figures.py  : all report figures

## Key parameters (analysis.py)
beta = 0.2 (chance an infectious student infects a susceptible neighbor per day)
gamma = 0.3 (chance an infectious student recovers per day)
Seeds are fixed, so results are reproducible.
