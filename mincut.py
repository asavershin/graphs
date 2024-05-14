def min_cut(graph, source, sink):
    visited = {vertex: False for vertex in range(source, sink + 1)}
    queue = [source]
    visited[source] = True

    while queue:
        u = queue.pop(0)
        if u in graph:
            for v, capacity in graph[u].items():
                if capacity > 0 and not visited[v]:
                    queue.append(v)
                    visited[v] = True

    source_side = set()
    sink_side = set()
    for vertex, is_visited in visited.items():
        if is_visited:
            source_side.add(vertex)
        else:
            sink_side.add(vertex)

    return source_side, sink_side