import networkx as nx
from cardinality import count
from colour import Color
from matplotlib.pyplot import show as show_graph
from networkx.classes.reportviews import NodeView
from ast import literal_eval


def init_graph_from_user_input() -> nx.Graph:
    '''Инициализация графа пользовательским вводом'''
    
    print('Введите планарный граф в виде кортежа кортежей его рёбер, перечисленных через запятую. Строки необходимо записывать с кавычками \'\'. Если указывается только одно ребро, после него должна стоять запятая')
    print('Учтите, что граф может состоять из нескольких несвязанных частей, но каждая часть должна быть планарным графом')
    print('Пример графа 1: (\'A\', \'B\'),')
    print('Пример графа 2: ((\'A\', \'B\'),)')
    print('Пример графа 3: (1, 2), (2, 3)')
    print('Пример графа 4: (\'A\', \'B\'), (\'B\', \'C\'), (\'B\', \'A\'), (1, 2), (2, 3), (3, 1), ...')

    while True:
        try:
            edges = literal_eval(input())
            graph = nx.Graph(edges)
            
            if not nx.is_planar(graph):
                raise Exception('Переданный граф не является планарным')
            
            return graph
        except ValueError:
            print('Некорректный ввод')
        except nx.NetworkXException:
            print('Некорректный ввод рёбер графа. ')
        except Exception as error:
            print(error)


def init_test_graph() -> nx.Graph:
    """Инициализация тестового графа"""
    
    graph = nx.Graph()
            
    graph.add_edges_from((
        (0, 1), (0, 2), (0, 3), (0, 4),
        (1, 2), (2, 3), (3, 4), (4, 1),
        (4, 5), (5, 1),
        (1, 6), (6, 2),
        (2, 7), (7, 3),
        (3, 8), (8, 4),
        (5, 6), (6, 7), (7, 8), (8,6)
        ))
    
    graph.add_node('A')
    
    graph.add_edge('B', 'C')
    
    graph.add_edges_from((
        ('D', 'E'), ('E', 'F'), ('F', 'D'),
        ))
    
    graph.add_edges_from((
        ('G', 'H'), ('H', 'I'), ('I', 'G'),
        ('J', 'G'), ('J', 'H'), ('J', 'I'),
        ))
    
    return graph


def draw_graph(graph:nx.Graph, color_map:dict[NodeView, Color]) -> None:
    """Отрисовка и показ графа, который будет раскрашен
       на основе переданной карты цветов"""

    draw_options = {
        'node_size': 1000,
        'width': 1, # Ширина линий рёбер
        'edge_color': 'black', # Цвет рёбер
        'with_labels': True,
        'edgecolors': 'black', # Цвет обводки узлов
        'node_color': [str(color_map[node]) for node in graph.nodes()],
    }
    
    nx.draw_planar(graph, **draw_options)
    show_graph()


def find_free_colors(colored_neighbors:tuple[tuple[NodeView, Color]], current_color_palette:list[Color]) -> tuple[Color]:
    """Нахождение из текущей палитры всех цветов, которые не заняты соседями. Если вернулся пустой кортёж, значит свободных цветов нет"""
    free_colors = []
    
    for color in current_color_palette:
        if all(color != neighbor_color[1] for neighbor_color in colored_neighbors):
            free_colors.append(color)
            
    
    return tuple(free_colors)


def backtracking(node:NodeView, graph:nx.Graph, color_map:dict[NodeView, Color], color_palette:list[Color]):
    """Рекурсивная функция перебора возможных цветов с возвратами"""
    colored_neighbors = tuple((neighbor, color_map[neighbor]) for neighbor in graph.neighbors(node) if neighbor in color_map.keys())
    free_colors = find_free_colors(colored_neighbors, color_palette)
        
    if len(free_colors) > 0:
        free_color_index = 0
        
        # Окрашивание узла, у которого все соседи уже закрашены. Возможно это можно сделать элегантнее?
        if all(neighbor in color_map.keys() for neighbor in graph.neighbors(node)):
            color_map[node] = free_colors[free_color_index]
        else:
            # Пока не будут покрашены все соседи или закончатся свободные цвета 
            while any(neighbor not in color_map.keys() for neighbor in graph.neighbors(node)) and free_color_index < len(free_colors):
                # Красим текущий узел
                color_map[node] = free_colors[free_color_index]
                free_color_index += 1

                # Проходим по оставшимся непокрашенным узлам
                uncolored_neighbors = tuple(neighbor for neighbor in graph.neighbors(node) if neighbor not in color_map.keys())
                for neighbor in uncolored_neighbors:
                    backtracking(neighbor, graph, color_map, color_palette)
                        
                    # Случай, когда сосед остался незакрашенным, потому что в цветовой палитре
                    # не осталось свободных цветов. Так мы очищаем карту в обратном ходе
                    # и доходим до узла, цвет которого можно изменить. После изменения идём
                    # ещё раз по тому же пути
                    if neighbor not in color_map.keys():
                        color_map.pop(node)
                        break;
                

def color_with_backtracking(graph:nx.Graph) -> dict[NodeView, Color]:
    '''Закрашивание карты (планарного графа) методом исчерпывающего поиска. При этом в графе может быть несколько несвязных друг с другом областей, каждая из которых должна быть планарной'''    

    # Любой планарный граф можно раскрасить 4 цветами
    full_color_palette = (Color('red'), Color('green'), Color('cyan'), Color('orange'))
    
    # Находим все разъединённые части графа
    subgraphs = tuple(nx.connected_components(graph))
    # Общая карта цвета для всего графа
    color_map:dict[NodeView, Color] = {}
    
    for subgraph_set in subgraphs:
        # На основе множества узлов получаем субграф со всеми связями
        subgraph = graph.subgraph(subgraph_set)
        
        # Нахождение узла с наименьшим количеством соседей
        nodes_with_neighbors = [(node, count(graph.neighbors(node))) for node in subgraph.nodes]
        first_node = min(nodes_with_neighbors, key=lambda t: t[1])[0]
    
        # Текущая палитра цветов, которая будет при необходимости расширяться
        color_palette = []
        subgraph_color_map: dict[NodeView, Color] = {}
        color_counter = 0

        # Пока не покрашены все узлы в подграфе
        while any(node not in subgraph_color_map.keys() for node in subgraph.nodes) and color_counter < len(full_color_palette):
            subgraph_color_map.clear()
            color_palette.append(full_color_palette[color_counter])
            color_counter += 1
            backtracking(first_node, subgraph, subgraph_color_map, color_palette)
        color_map.update(subgraph_color_map)

    return color_map
   

graph = init_test_graph() #init_graph_from_user_input()

color_map = color_with_backtracking(graph)

draw_graph(graph, color_map)