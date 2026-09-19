"""
Metro de la CDMX
"""

from collections import deque
import unicodedata
import networkx as nx
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. DATOS: estaciones por línea (en orden del mapa real)
# ---------------------------------------------------------------------------
LINEAS = {
    "1": ["Observatorio", "Tacubaya", "Juanacatlán", "Chapultepec", "Sevilla",
          "Insurgentes", "Cuauhtémoc", "Balderas", "Salto del Agua",
          "Isabel la Católica", "Pino Suárez", "Merced", "Candelaria",
          "San Lázaro", "Moctezuma", "Balbuena", "Boulevard Puerto Aéreo",
          "Gómez Farías", "Zaragoza", "Pantitlán"],

    "2": ["Cuatro Caminos", "Panteones", "Tacuba", "Cuitláhuac", "Popotla",
          "Colegio Militar", "Normal", "San Cosme", "Revolución", "Hidalgo",
          "Bellas Artes", "Allende", "Zócalo", "Pino Suárez",
          "San Antonio Abad", "Chabacano", "Viaducto", "Xola",
          "Villa de Cortés", "Nativitas", "Portales", "Ermita",
          "General Anaya", "Tasqueña"],

    "3": ["Indios Verdes", "Deportivo 18 de Marzo", "Potrero", "La Raza",
          "Tlatelolco", "Guerrero", "Hidalgo", "Juárez", "Balderas",
          "Niños Héroes", "Hospital General", "Centro Médico", "Etiopía",
          "Eugenia", "División del Norte", "Zapata", "Coyoacán", "Viveros",
          "Miguel Ángel de Quevedo", "Copilco", "Universidad"],

    "4": ["Martín Carrera", "Talismán", "Bondojito", "Consulado",
          "Canal del Norte", "Morelos", "Candelaria", "Fray Servando",
          "Jamaica", "Santa Anita"],

    "5": ["Politécnico", "Instituto del Petróleo", "Autobuses del Norte",
          "La Raza", "Misterios", "Valle Gómez", "Consulado",
          "Eduardo Molina", "Aragón", "Oceanía", "Terminal Aérea",
          "Hangares", "Pantitlán"],

    "6": ["El Rosario", "Tezozómoc", "Azcapotzalco", "Ferrería", "Norte 45",
          "Vallejo", "Instituto del Petróleo", "Lindavista",
          "Deportivo 18 de Marzo", "La Villa", "Martín Carrera"],

    "7": ["El Rosario", "Aquiles Serdán", "Camarones", "Refinería", "Tacuba",
          "San Joaquín", "Polanco", "Auditorio", "Constituyentes",
          "Tacubaya", "San Pedro de los Pinos", "San Antonio", "Mixcoac",
          "Barranca del Muerto"],

    "8": ["Garibaldi", "Bellas Artes", "San Juan de Letrán", "Salto del Agua",
          "Doctores", "Obrera", "Chabacano", "La Viga", "Santa Anita",
          "Coyuya", "Iztacalco", "Apatlaco", "Aculco", "Escuadrón 201",
          "Atlalilco", "Iztapalapa", "Cerro de la Estrella", "UAM-I",
          "Constitución de 1917"],

    "9": ["Tacubaya", "Patriotismo", "Chilpancingo", "Centro Médico",
          "Lázaro Cárdenas", "Chabacano", "Jamaica", "Mixiuhca", "Velódromo",
          "Ciudad Deportiva", "Puebla", "Pantitlán"],

    "A": ["Pantitlán", "Agrícola Oriental", "Canal de San Juan", "Tepalcates",
          "Guelatao", "Peñón Viejo", "Acatitla", "Santa Marta", "Los Reyes",
          "La Paz"],

    "B": ["Buenavista", "Guerrero", "Garibaldi", "Lagunilla", "Tepito",
          "Morelos", "San Lázaro", "Ricardo Flores Magón", "Romero Rubio",
          "Oceanía", "Deportivo Oceanía", "Bosque de Aragón",
          "Villa de Aragón", "Nezahualcóyotl", "Impulsora",
          "Río de los Remedios", "Múzquiz", "Ecatepec", "Olímpica",
          "Plaza Aragón", "Ciudad Azteca"],

    "12": ["Mixcoac", "Insurgentes Sur", "Hospital 20 de Noviembre", "Zapata",
           "Parque de los Venados", "Eje Central", "Ermita", "Mexicaltzingo",
           "Atlalilco", "Culhuacán", "San Andrés Tomatlán", "Lomas Estrella",
           "Calle 11", "Periférico Oriente", "Tezonco", "Olivos", "Nopalera",
           "Zapotitlán", "Tlaltenco", "Tláhuac"],
}

# Colores oficiales aproximados de cada línea (para el dibujo del grafo)
COLORES_LINEA = {
    "1": "#f74d9f",
    "2": "#0d5db6",
    "3": "#a3822c",
    "4": "#7ac2c2",
    "5": "#fdd000",
    "6": "#e2231a",
    "7": "#e56917",
    "8": "#0e7c3e",
    "9": "#4c4c4c",
    "A": "#8b2f8b",
    "B": "#a3a3a3",
    "12": "#a3822c",
}

# Nombres alternativos 
ALIAS = {
    "taxquena": "Tasqueña",
    "ocenia": "Oceanía",
}


# ---------------------------------------------------------------------------
# 2. CONSTRUCCIÓN DEL GRAFO (METRO CDMX)
# ---------------------------------------------------------------------------
def construir_grafo(lineas):
    """
    Devuelve:
      grafo: {estacion: [vecinos]}            (no dirigido, peso 1 por arista)
      lineas_arista: {(a, b): {lineas}}       (para describir transbordos)
    Las estaciones con el mismo nombre en varias líneas (correspondencias)
    son un único nodo, por eso las líneas quedan conectadas solas.
    """
    grafo = {}
    lineas_arista = {}

    for linea, estaciones in lineas.items():
        for est in estaciones:
            grafo.setdefault(est, [])
        for a, b in zip(estaciones, estaciones[1:]):
            if b not in grafo[a]:
                grafo[a].append(b)
            if a not in grafo[b]:
                grafo[b].append(a)
            lineas_arista.setdefault((a, b), set()).add(linea)
            lineas_arista.setdefault((b, a), set()).add(linea)

    return grafo, lineas_arista


# ---------------------------------------------------------------------------
# 3. ALGORITMOS NECESARIOS BFS Y DFS
# ---------------------------------------------------------------------------
def _reconstruir(padres, destino):
    camino = []
    nodo = destino
    while nodo is not None:
        camino.append(nodo)
        nodo = padres[nodo]
    return camino[::-1]


def bfs(grafo, origen, destino):
    """
    Búsqueda en anchura. Con costo unitario garantiza la ruta con
    MENOS estaciones (ruta óptima).
    """
    cola = deque([origen])
    padres = {origen: None}          # también sirve como "visitados"

    while cola:
        actual = cola.popleft()
        if actual == destino:
            return _reconstruir(padres, destino)
        for vecino in grafo[actual]:
            if vecino not in padres:
                padres[vecino] = actual
                cola.append(vecino)
    return None


def dfs(grafo, origen, destino):
    """
    Búsqueda en profundidad (iterativa, con pila). Encuentra UNA ruta,
    pero NO garantiza que sea la más corta.
    """
    pila = [origen]
    padres = {origen: None}
    visitados = set()

    while pila:
        actual = pila.pop()
        if actual in visitados:
            continue
        visitados.add(actual)
        if actual == destino:
            return _reconstruir(padres, destino)
        # reversed para explorar los vecinos en el orden en que están listados
        for vecino in reversed(grafo[actual]):
            if vecino not in visitados:
                padres[vecino] = actual
                pila.append(vecino)
    return None


# ---------------------------------------------------------------------------
# 4. UTILIDADES
# ---------------------------------------------------------------------------
def _normalizar(texto):
    sin_acentos = unicodedata.normalize("NFD", texto)
    sin_acentos = "".join(c for c in sin_acentos
                          if unicodedata.category(c) != "Mn")
    return sin_acentos.lower().strip()


def resolver_estacion(nombre, grafo):
    """Acepta el nombre sin acentos, en minúsculas o con alias."""
    n = _normalizar(nombre)
    if n in ALIAS:
        return ALIAS[n]
    for est in grafo:
        if _normalizar(est) == n:
            return est
    raise ValueError(f"Estación no encontrada: {nombre!r}")


def tramos_por_linea(camino, lineas_arista):
    """Agrupa el camino en tramos [linea, estacion_inicio, estacion_fin]."""
    tramos = []
    actual = None
    for a, b in zip(camino, camino[1:]):
        posibles = lineas_arista[(a, b)]
        if actual in posibles:
            tramos[-1][2] = b
        else:
            actual = sorted(posibles)[0]
            tramos.append([actual, a, b])
    return tramos


def imprimir_resultado(nombre_algoritmo, camino, lineas_arista):
    if camino is None:
        print(f"  {nombre_algoritmo}: no hay ruta")
        return
    costo = len(camino) - 1          # costo unitario = # de movimientos
    tramos = tramos_por_linea(camino, lineas_arista)
    print(f"  {nombre_algoritmo}: costo = {costo} movimientos "
          f"({len(camino)} estaciones), transbordos = {len(tramos) - 1}")
    for linea, ini, fin in tramos:
        print(f"      Línea {linea}: {ini} -> {fin}")
    if len(camino) <= 30:
        print("      Ruta completa: " + " -> ".join(camino))


# ---------------------------------------------------------------------------
# 5. REP GRAFO
# ---------------------------------------------------------------------------
def dibujar_grafo(lineas, colores_linea, ruta_salida="metro_cdmx.png"):
    """
    Dibuja el grafo completo del Metro CDMX usando networkx, coloreando
    cada tramo según su línea. Las estaciones de correspondencia (que
    aparecen en más de una línea) se marcan más grandes.
    """
    G = nx.Graph()
    conteo_linea = {}  # estacion -> cuántas líneas la usan

    for linea, estaciones in lineas.items():
        for est in estaciones:
            conteo_linea[est] = conteo_linea.get(est, 0) + 1
        for a, b in zip(estaciones, estaciones[1:]):
            # si la arista ya existe (comparte tramo con otra línea) se
            # conserva la línea con la que se dibujó primero
            if not G.has_edge(a, b):
                G.add_edge(a, b, linea=linea)

    pos = nx.spring_layout(G, seed=42, k=0.6, iterations=200)

    plt.figure(figsize=(20, 16))

    # Dibujar aristas agrupadas por línea 
    for linea in lineas:
        aristas_linea = [(a, b) for a, b, d in G.edges(data=True)
                          if d["linea"] == linea]
        nx.draw_networkx_edges(
            G, pos, edgelist=aristas_linea,
            edge_color=colores_linea.get(linea, "#999999"),
            width=2.5, label=f"Línea {linea}"
        )

    # Nodos: más grandes y remarcados si son correspondencia
    tamanos = [220 if conteo_linea[n] > 1 else 90 for n in G.nodes()]
    colores_nodo = ["white" if conteo_linea[n] > 1 else "#333333"
                     for n in G.nodes()]
    bordes = ["black" if conteo_linea[n] > 1 else "none" for n in G.nodes()]

    nx.draw_networkx_nodes(
        G, pos, node_size=tamanos, node_color=colores_nodo,
        edgecolors=bordes, linewidths=1.2
    )

    # Etiquetas solo en correspondencias
    etiquetas = {n: n for n in G.nodes() if conteo_linea[n] > 1}
    nx.draw_networkx_labels(G, pos, labels=etiquetas, font_size=7)

    plt.legend(scatterpoints=1, loc="lower left", fontsize=8,
               title="Líneas", framealpha=0.9)
    plt.title("Grafo del Metro de la Ciudad de México", fontsize=16)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=200)
    plt.show()
    print(f"\nGrafo guardado en: {ruta_salida}")


# ---------------------------------------------------------------------------
# 6. PROGRAMA MENU INICIAL
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    grafo, lineas_arista = construir_grafo(LINEAS)

    n_aristas = sum(len(v) for v in grafo.values()) // 2
    print(f"Grafo del Metro CDMX: {len(grafo)} estaciones, "
          f"{n_aristas} conexiones\n")

    consultas = [
        ("Cuatro Caminos", "Pantitlán"),
        ("Politécnico", "Taxqueña"),
        ("Zapata", "Ocenia"),
    ]

    for i, (o, d) in enumerate(consultas, start=1):
        origen = resolver_estacion(o, grafo)
        destino = resolver_estacion(d, grafo)
        print(f"{i}. {origen} -> {destino}")
        imprimir_resultado("BFS", bfs(grafo, origen, destino), lineas_arista)
        imprimir_resultado("DFS", dfs(grafo, origen, destino), lineas_arista)
        print()

    dibujar_grafo(LINEAS, COLORES_LINEA)
