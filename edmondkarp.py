from collections import deque
def bfs(graph: dict[int, dict[int, int]], source, target, parent: dict[int, int]):
    visited = set()  # Используем множество для отслеживания посещенных вершин
    queue = deque()
    queue.append(source)
    visited.add(source)
    while queue:
        u = queue.popleft()
        if u in graph:  # Проверяем, существует ли вершина u в графе
            for v, capacity in graph[u].items():
                if v not in visited and capacity > 0:
                    queue.append(v)
                    parent[v] = u
                    visited.add(v)  # Добавляем вершину в множество посещенных

    return target in visited

def edmonds_karp(graph: dict[int, dict[int, int]], source, sink):
    parent = {}
    max_flow = 0

    while bfs(graph, source, sink, parent):
        path_flow = float("Inf")
        s = sink
        while s != source:
            path_flow = min(path_flow, graph[parent[s]][s])
            s = parent[s]

        max_flow += path_flow
        v = sink
        while v != source:
            u = parent[v]
            graph[u][v] -= path_flow
            if v not in graph:
                graph[v] = {}
            if u not in graph[v]:
                graph[v][u] = 0
            graph[v][u] += path_flow
            v = parent[v]

    return max_flow