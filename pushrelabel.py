import heapq

class Vertex3:
    def __init__(self, index, h, e_flow):
        self.index = index
        self.h = h
        self.e_flow = e_flow

    def __lt__(self, other):
        return self.h > other.h

    def __eq__(self, other):
        return self.h == other.h

class PriorityQueue:
    def __init__(self):
        self.queue = []

    def push(self, vertex):
        heapq.heappush(self.queue, vertex)

    def pop(self):
        if self.queue:
            return heapq.heappop(self.queue)
        else:
            return None

    def sort(self):
        heapq.heapify(self.queue)


class PushRelabel:

    def __init__(self, G: dict[int, dict[int, int]], source: int, sink: int, num_edges: int, num_vertices: int):
        self.graph: dict[int, dict[int, int]] = G
        self.num_edges: int = num_edges
        self.num_vertices: int = num_vertices
        self.source: int = source
        self.sink: int = sink
        self.vertices: dict[int, Vertex3] = {index: Vertex3(index, 0, 0) for index in range(source, sink + 1)}
        self.active: PriorityQueue = PriorityQueue()

    def preFlow(self):
        for key, capacity in self.graph[self.source].items():
            tmp = self.vertices[key]
            tmp.e_flow = capacity
            self.graph[self.source][key] -= capacity
            self.vertices[self.source].e_flow -= capacity
            if key not in self.graph:
                self.graph[key] = {}
            if self.source not in self.graph[key]:
                self.graph[key][self.source] = 0
            self.graph[key][self.source] += capacity
            if tmp.index != self.sink:
                self.active.push(tmp)

        self.vertices[self.source].h = self.num_vertices

    def globalRelabeling(self):
        # BFS от стока
        queue = [self.sink]
        distance_to_sink = {self.sink: 0}
        while queue:
            current_vertex = queue.pop(0)
            for neighbor, _ in self.graph[current_vertex].items():
                if neighbor not in distance_to_sink and self.graph[neighbor][current_vertex] > 0:
                    distance_to_sink[neighbor] = distance_to_sink[current_vertex] + 1
                    queue.append(neighbor)

        # Обновление высоты вершин
        for index, distance in distance_to_sink.items():
            if index == self.source or index == self.source:
                continue
            tmp = self.vertices[index]
            tmp.h = distance

        self.active.sort()


    def push(self, vert: Vertex3):

        for key, capacity in self.graph[vert.index].items():
            if self.vertices[vert.index].e_flow <= 0:
                return True

            if capacity > 0 and self.vertices[vert.index].h > self.vertices[key].h:
                flow = min(self.vertices[vert.index].e_flow, capacity)
                self.graph[vert.index][key] -= flow
                if key not in self.graph:
                    self.graph[key] = {}
                if vert.index not in self.graph[key]:
                    self.graph[key][vert.index] = 0
                self.graph[key][vert.index] += flow
                self.vertices[vert.index].e_flow -= flow
                tmp = self.vertices[key]
                if tmp.e_flow > 0 or tmp.index == self.source or tmp.index == self.sink:
                    tmp.e_flow += flow
                else:
                    tmp.e_flow += flow
                    self.active.push(self.vertices[key])

        return vert.e_flow == 0

    def relabel(self, vert: Vertex3):
        min_height = float('inf')
        for v, capacity in self.graph[vert.index].items():
            if capacity > 0:
                min_height = min(min_height, self.vertices[v].h)
        vert.h = min_height + 1
        self.active.push(vert)

    def overFlowVertex(self) -> None | Vertex3:

        if len(self.active.queue) == 0:
            return None

        return self.active.pop()

    def get_max_flow(self):
        self.preFlow()
        self.globalRelabeling()
        iteration = 0
        while True:
            if iteration >= self.num_edges:
                self.globalRelabeling()
                iteration = 0
            vert = self.overFlowVertex()
            if vert is None:
                break
            if not self.push(vert):
                self.relabel(vert)
            iteration += 1

        return self.vertices[self.sink].e_flow



