from collections import deque
from pushrelabel import PushRelabel
from mincut import min_cut

def compute_vols_and_cut(G, S):
    degrees = {}
    volNotS = 0
    cut = 0
    for ver in G:
        if ver in S:
            count_of_neighbors_in_S = 0
            count_of_neighbors_not_in_S = 0
            for neighbor in G[ver]:
                if neighbor in S:
                    count_of_neighbors_in_S += 1
                if neighbor not in S:
                    count_of_neighbors_not_in_S += 1
                    cut += 1
            degrees[ver] = (count_of_neighbors_in_S, count_of_neighbors_not_in_S)
        if ver not in S:
            volNotS += len(G[ver])
    return cut, degrees, volNotS

def compute_vols_from_array(degrees):
    summ = 0
    for pair in degrees:
        summ += sum(degrees[pair])
    return summ

def make_subgraph(G, S, degrees, delta):
    S_subgraph = {}
    S_subgraph[-1] = {ver: sum(degrees[ver])*delta for ver in S}
    for ver in S:
        S_subgraph[ver] = {}
        S_subgraph[ver][-1] = sum(degrees[ver])*delta
        S_subgraph[ver].update({neighbor: 1 for neighbor in G[ver] if neighbor in S})
    S_subgraph[len(G) + 1] = {}
    for ver in S:
        weight = 0
        for neighbor in G[ver]:
            if neighbor not in S:
                weight += 1
        if weight != 0:
            S_subgraph[len(G) + 1].update({ver: weight})
            S_subgraph[ver].update({len(G) + 1: weight})
    return S_subgraph

def my_modularity(graph, cluster):
    m = sum([len(graph[node]) for node in graph]) // 2
    Q = 0

    not_cluster = set()
    for ver in graph:
        if ver not in cluster:
            not_cluster.add(ver)

    for c in [cluster, not_cluster]:

        lc = 0
        for node in c:
            for neighbor in graph[node]:
                if neighbor in c:
                    lc += 1

        kc = sum(len(graph[n]) for n in c)
        Q += lc / (2 * m) - (kc / (2 * m)) ** 2

    return Q

def MQI(G, R):
    k = 1
    S_old = R

    # degrees хранит для каждой вершины из S
    # количество ребер, соединяющих её с вершинами из S и не из S отдельно
    # чтобы посчитать vol(S) надо просто сложить все эти значения

    cut, degrees, volNotS = compute_vols_and_cut(G, S_old)
    volS = compute_vols_from_array(degrees)
    condNew = cut / min(volS, volNotS)
    condOld = condNew
    cond_of_R = condNew
    cond_of_S = condNew

    # print(f"cut = {cut}")
    # print(f"volS = {volS}")
    # print(f"volNotS = {volNotS}")
    # print(f"new cond = {condNew}")

    if condNew == 0:
        return S_old, cond_of_R, cond_of_S

    while True:

        tmp_subgraph = make_subgraph(G, S_old, degrees, condNew)
        pl = PushRelabel(tmp_subgraph, -1, len(G) + 1, len(tmp_subgraph), len(tmp_subgraph))
        pl.get_max_flow()
        S_new = min_cut(pl.graph, -1, len(G) + 1)[0]
        S_new.remove(-1)

        if len(S_new) == 0:
            return S_old, cond_of_R, cond_of_S

        cut, degrees, volNotS = compute_vols_and_cut(G, S_new)
        volS = compute_vols_from_array(degrees)
        condNew = cut / min(volS, volNotS)

        if condNew < condOld:
            condOld = condNew
            S_old = S_new
            cond_of_S = condNew
        else:
            cond_of_S = condOld
            break

    return S_old, cond_of_R, cond_of_S
