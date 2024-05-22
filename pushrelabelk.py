from collections import deque
import networkx as nx

class Level:
    active: set
    inactive: set

    def __init__(self):
        self.active = set()
        self.inactive = set()

class Graph:
    V: int  # Количество вершин
    E: int  # Количество рёбер
    source: int  # Исток
    sink: int  # сток
    # key - vertex, value - set of vertexes
    edges: dict
    pred: dict
    # key - vertex, value - int
    heights: dict
    excesses: dict

    # key - tuple of vertexes, value - int
    capacities: dict
    flows: dict

    levels: list

    gr_freq: int
    gr_stat: int

    def __init__(self, source=0, sink=0):
        self.heights = {}
        self.excesses = {}
        self.edges = {}
        self.pred = {}
        self.capacities = {}
        self.flows = {}
        self.source = source
        self.sink = sink
        self.levels = []
        self.V = -1
        self.gr_freq = 10
        self.gr_stat = 0

    def get_from_dictionary(self, d: dict):
        for key in d.keys():
            if key not in self.edges.keys():
                self.add_vertex(key)
        for key in d.keys():
            for edge in d[key].keys():
                self.add_edge((key, edge, d[key][edge]))
    
    def set_E(self, E: int):
        self.E = E
        
    def set_V(self, V: int):
        self.V = V
        
    def set_global_relabel_freq(self, n: int):
        """
        Устанавиливает частоту для global relabeling
        """
        self.global_relabel_freq = n

    def add_vertex(self, v: int):
        """
        Добавление вершины в граф
        """
        if v in self.edges.keys() and v in self.pred.keys():
            print(f"Вершина {v} уже присутсвует в графе")
            return
        self.edges[v] = set()
        self.pred[v] = set()
        self.excesses[v] = 0
        self.heights[v] = 0

    def add_edge(self, edge: tuple):
        """
        Добавляет ребро в граф. Ребро имеет вид кортежа (src, dst, capacity)
        """
        if edge[0] not in self.edges.keys():
            print(f"Ошибка: Вершина {edge[0]} для добавления ребра ({edge[0]}-{edge[1]}) отсутствует в списке рёбер")
        elif edge[1] not in self.edges.keys():
            print(f"Ошибка: Вершина {edge[1]} для добавления ребра ({edge[0]}-{edge[1]}) отсутствует в списке рёбер")
        elif edge[0] == edge[1]:
            print(f"Ошибка: Ребро ({edge[0]}-{edge[1]}) является петлёй")
        elif edge[2] < 0:
            print(f"Ошибка: Ребро ({edge[0]}-{edge[1]}) имеет некорректную пропускную способность")
        else:
            self.edges[edge[0]].add(edge[1])
            self.edges[edge[1]].add(edge[0])
            self.capacities[(edge[0], edge[1])] = edge[2]  # Добавляем пропускную способность прямому ребру
            if (edge[1], edge[0]) not in self.capacities:  # Первое добавление
                self.capacities[(edge[1], edge[0])] = 0  # Пропускная способность обратного ребра = 0
                self.flows[(edge[0], edge[1])] = 0
                self.flows[(edge[1], edge[0])] = 0

    def get_vertices(self):
        """
        Возвращает список вершин графа
        """
        return self.edges.keys()

    def get_number_of_vertices(self):
        """
        Возвращает количество вершин
        """
        return len(self.edges.keys())

    def get_number_of_edges(self):
        """
        Возвращает количество рёбер
        """
        return len([i for i in self.capacities.keys() if self.capacities[i] != 0])

    def get_edges(self):
        """
        Возвращает список рёбер графа
        """
        return self.capacities.keys()

    def push(self, u, v, flow=-1):
        """
        Проталкивание
        """
        if flow == -1:
            delta_flow = min(self.capacities[(u, v)] - self.flows[(u, v)], self.excesses[u])
            self.flows[(u, v)] += delta_flow
            self.flows[(v, u)] -= delta_flow

            self.excesses[u] -= delta_flow
            self.excesses[v] += delta_flow
        else:
            self.flows[(u, v)] += flow
            self.flows[(v, u)] -= flow

            self.excesses[u] -= flow
            self.excesses[v] += flow

    def relabel(self, u: int):
        """
        Подъем вершины
        """
        self.gr_stat += len(self.edges[u])
        min_height = float('inf')
        for edge in self.edges[u]:
            if self.capacities[(u, edge)] > self.flows[(u, edge)]:
                min_height = min(min_height, self.heights[edge])

        return min_height + 1

    def discharge(self, u: int, on_preflow=False):
        """
        Разрядка вершины
        """
        height = self.heights[u]
        next_height = height
        self.levels[height].active.remove(u)
        leave = False
        while True:
            for edge in self.edges[u]:
                if self.capacities[(u, edge)] > self.flows[(u, edge)] and height == self.heights[edge] + 1:
                    self.push(u, edge)
                    # Активируем вершину
                    if edge != self.sink and edge != self.source:
                        level = self.levels[self.heights[edge]]
                        if edge in level.inactive:
                            level.inactive.remove(edge)
                            level.active.add(edge)
                    if self.excesses[u] <= 0:
                        self.levels[height].inactive.add(u)
                        leave = True
                        break
            if leave:
                break
            if self.excesses[u] > 0:
                height = self.relabel(u)
                if height >= self.V - 1 and on_preflow:
                    # Ситуация, когда узел находится во множестве S
                    self.levels[height].active.add(u)
                    break
                next_height = height
        self.heights[u] = height
        return next_height

    def reverse_bfs(self, src):
        temp_heights = {src: 0}
        dq = deque([(src, 0)])
        while dq:
            u, height = dq.popleft()
            height += 1
            for v in self.edges[u]:
                if self.capacities[(v, u)] > self.flows[(v, u)] and v not in temp_heights:
                    temp_heights[v] = height
                    dq.append((v, height))
        return temp_heights

    def global_relabeling(self, from_sink=False):
        src = self.source
        if from_sink:
            src = self.sink
        heights = self.reverse_bfs(src)
        if not from_sink:
            del heights[self.sink]
        max_height = max(heights.values())
        if from_sink:
            # Отмечает ребра, недостижимые из стока
            for u in self.edges.keys():
                if u not in heights and self.heights[u] < self.V:
                    heights[u] = self.V + 1
        else:
            # Сдвиг высот
            # Выполняется, по скольку высота истока должна быть V
            for u in heights:
                heights[u] += self.V
            max_height += self.V
        del heights[src]
        for u, new_height in heights.items():
            old_height = self.heights[u]
            if old_height != new_height:
                if u in self.levels[old_height].active:
                    self.levels[old_height].active.remove(u)
                    self.levels[new_height].active.add(u)
                else:
                    self.levels[old_height].inactive.remove(u)
                    self.levels[new_height].inactive.add(u)
                self.heights[u] = new_height

        return max_height

    def preflow(self, max_height: list):
        """
        Инициализация предпотока
        """
        height = max_height[0]

        while height > 0:
            # Разряжаем активые вершины текущего уровня
            while True:
                level = self.levels[height]
                if not level.active:
                    height -= 1
                    break
                u = (next(iter(level.active)))
                height = self.discharge(u, on_preflow=True)
                if self.gr_stat == self.gr_freq:  # условие частоты для global relabeling
                    height = self.global_relabeling(True)
                    max_height[0] = height
                    self.gr_stat = 0
                else:
                    max_height[0] = max(max_height[0], height)

    def push_relabel(self):
        heights = self.reverse_bfs(self.sink)
        if self.source not in heights:
            # сток не достижим из истока. Максимальный поток равен 0
            return 0
        
        self.V = self.get_number_of_vertices()
        self.set_global_relabel_freq = self.V

        max_height = max(heights[vertex] for vertex in heights if vertex != self.source)
        heights[self.source] = self.V

        # Инициализация высот
        for edge in self.edges.keys():
            self.heights[edge] = heights[edge] if edge in heights else self.V + 1

        self.levels = [Level() for _ in range(2 * self.V)]
        for v in self.edges[self.source]:
            flow = self.capacities[(self.source, v)]
            if flow > 0:
                self.push(self.source, v, flow)

        for u in self.edges.keys():
            if u != self.source and u != self.sink:
                level = self.levels[self.heights[u]]
                if self.excesses[u] > 0:
                    level.active.add(u)
                else:
                    level.inactive.add(u)

        self.preflow([max_height])


        height = self.global_relabeling()
        self.gr_stat = 0

        while height > 0:
            # Разряжаем активные вершины текущего уровня
            while True:
                level = self.levels[height]
                if not level.active:
                    # Все текущие вершины разряжены
                    # Идём на следующие уровень
                    height -= 1
                    break
                u = next(iter(level.active))
                height = self.discharge(u)
                if self.gr_stat == self.gr_freq:
                    height = self.global_relabeling()
                    self.gr_stat = 0
        return self.excesses[self.sink]
    
    def read_from_file(self, filename: str):
        with open(filename, 'r') as file:
            num_vertices, num_edges = map(int, file.readline().split())
            for _ in range(num_edges):
                u, v, capacity = map(int, file.readline().split())
                if u not in self.edges.keys():
                    self.add_vertex(u)
                if v not in self.edges.keys():
                    self.add_vertex(v)
                self.add_edge((u, v, capacity))
            self.set_E = num_edges
            self.set_V = num_vertices
            self.source = 1
            self.sink = num_vertices
        