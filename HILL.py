import networkx as nx
import matplotlib.pyplot as plt


# ============================================================
#  Clase abstracta Problem
# ============================================================
class Problem:
    def __init__(self, initial, goal):
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        raise NotImplementedError

    def result(self, state, action):
        raise NotImplementedError

    def is_goal(self, state):
        return self.goal == state

    def action_cost(self, state1, action, state2):
        return 1

    def h(self, state):
        return 0


# ============================================================
#  GraphProblem (con heurística h para Hill Climbing)
# ============================================================
class GraphProblem(Problem):
    def __init__(self, initial, goal, graph):
        super().__init__(initial, goal)
        self.graph = graph

    def actions(self, state):
        lista = []
        for key in self.graph[state].keys():
            lista.append(key)
        return lista

    def result(self, state, action):
        return action

    def action_cost(self, state1, action, state2):
        return self.graph[state1][state2]

    def h(self, state):
        return straight_line_distance[state]


# ============================================================
#  Clase Node
# ============================================================
class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

    def path(self):
        lista_path = []
        node = self
        while node:
            lista_path.append(node.state)
            node = node.parent
        return lista_path[::-1]

    def expand(self, problem):
        lista = []
        for action in problem.actions(self.state):
            lista.append(self.child_node(problem, action))
        return lista

    def child_node(self, problem, action):
        next_state = problem.result(self.state, action)
        step_cost = problem.action_cost(self.state, action, next_state)
        return Node(next_state, self, action, self.path_cost + step_cost)


# ============================================================
# Grafo de Romania
# ============================================================
romania = {
    'Arad': {'Zerind': 75, 'Sibiu': 140, 'Timisoara': 118},
    'Zerind': {'Arad': 75, 'Oradea': 71},
    'Oradea': {'Zerind': 71, 'Sibiu': 151},
    'Sibiu': {'Arad': 140, 'Oradea': 151, 'Fagaras': 99, 'Rimnicu Vilcea': 80},
    'Timisoara': {'Arad': 118, 'Lugoj': 111},
    'Lugoj': {'Timisoara': 111, 'Mehadia': 70},
    'Mehadia': {'Lugoj': 70, 'Dobreta': 75},
    'Dobreta': {'Mehadia': 75, 'Craiova': 120},
    'Craiova': {'Dobreta': 120, 'Rimnicu Vilcea': 146, 'Pitesti': 138},
    'Rimnicu Vilcea': {'Sibiu': 80, 'Craiova': 146, 'Pitesti': 97},
    'Fagaras': {'Sibiu': 99, 'Bucarest': 211},
    'Pitesti': {'Rimnicu Vilcea': 97, 'Craiova': 138, 'Bucarest': 101},
    'Bucarest': {'Fagaras': 211, 'Pitesti': 101, 'Giurgiu': 90, 'Urziceni': 85},
    'Giurgiu': {'Bucarest': 90},
    'Urziceni': {'Bucarest': 85, 'Hirsova': 98, 'Vaslui': 142},
    'Hirsova': {'Urziceni': 98, 'Eforie': 86},
    'Eforie': {'Hirsova': 86},
    'Vaslui': {'Urziceni': 142, 'Iasi': 92},
    'Iasi': {'Vaslui': 92, 'Neamt': 87},
    'Neamt': {'Iasi': 87},
}

straight_line_distance = {
    'Arad': 366, 'Bucarest': 0, 'Craiova': 160, 'Dobreta': 242,
    'Eforie': 161, 'Fagaras': 178, 'Giurgiu': 77, 'Hirsova': 151,
    'Iasi': 226, 'Lugoj': 244, 'Mehadia': 241, 'Neamt': 234,
    'Oradea': 380, 'Pitesti': 98, 'Rimnicu Vilcea': 193, 'Sibiu': 253,
    'Timisoara': 329, 'Urziceni': 80, 'Vaslui': 199, 'Zerind': 374,
}

pos = {
    'Oradea': (0.5, 7), 'Zerind': (0, 6), 'Arad': (0, 5),
    'Timisoara': (0.3, 3.5), 'Lugoj': (1.2, 2.7), 'Mehadia': (1.3, 1.8),
    'Dobreta': (1, 1), 'Sibiu': (2.2, 5.3), 'Rimnicu Vilcea': (2.2, 4),
    'Craiova': (2.4, 2), 'Fagaras': (3.6, 5.3), 'Pitesti': (3.4, 3),
    'Bucarest': (4.8, 2.3), 'Giurgiu': (4.5, 1), 'Urziceni': (6, 3),
    'Hirsova': (7.3, 3), 'Eforie': (7.5, 2), 'Vaslui': (6.7, 4.7),
    'Iasi': (6.2, 6), 'Neamt': (5, 6.7),
}


# ============================================================
# Hill Climbing
# ============================================================
def hill_climbing(problem):
    """Busqueda local informada (descenso de h)."""
    current = Node(problem.initial)

    while True:
        if problem.is_goal(current.state):
            return current, True

        vecinos = current.expand(problem)
        if not vecinos:
            return current, False

        mejor = min(vecinos, key=lambda node: problem.h(node.state))

        if problem.h(mejor.state) >= problem.h(current.state):
            return current, False

        current = mejor


def dibujar_ruta(graph, ruta, inicio, meta, encontrado,
                  archivo='hill_climbing_ruta.png'):
    aristas_ruta = list(zip(ruta, ruta[1:]))

    G = nx.Graph()
    for ciudad, vecinos in graph.items():
        for vecino, costo in vecinos.items():
            G.add_edge(ciudad, vecino, weight=costo)

    plt.figure(figsize=(12, 9))
    nx.draw_networkx_edges(G, pos, edge_color='lightgray', width=1.5)

    color_ruta = 'red' if encontrado else 'orangered'
    nx.draw_networkx_edges(G, pos, edgelist=aristas_ruta,
                            edge_color=color_ruta, width=4)

    colores_nodos = []
    for nodo in G.nodes():
        if nodo == inicio:
            colores_nodos.append('gold')
        elif nodo == meta and encontrado:
            colores_nodos.append('limegreen')
        elif nodo == ruta[-1] and not encontrado:
            colores_nodos.append('tomato')
        elif nodo in ruta:
            colores_nodos.append('orange')
        else:
            colores_nodos.append('lightsteelblue')

    nx.draw_networkx_nodes(G, pos, node_color=colores_nodos,
                            node_size=1400, edgecolors='black')
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')

    edge_labels_ruta = {edge: graph[edge[0]][edge[1]] for edge in aristas_ruta}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels_ruta,
                                  font_size=10, font_color='darkred',
                                  font_weight='bold')

    estado_txt = "META ALCANZADA" if encontrado else "CIMA LOCAL (sin llegar a la meta)"
    plt.title(f"Hill Climbing: {inicio} → {meta}\n"
              f"Ruta: {' → '.join(ruta)}   |   {estado_txt}",
              fontsize=13, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(archivo, dpi=150, bbox_inches='tight')
    plt.show()



problem = GraphProblem('Arad', 'Bucarest', romania)
current, encontrado = hill_climbing(problem)
ruta = current.path()

print(ruta, encontrado)

dibujar_ruta(romania, ruta, problem.initial, problem.goal, encontrado)
