"""
Скрипт для визуализации графа терминов глоссария.
Создает визуальное представление графа с узлами (термины) и связями между ними.
"""
import csv
import sys
from collections import defaultdict

try:
    import matplotlib.pyplot as plt
    import networkx as nx
except ImportError:
    print("Ошибка: Необходимо установить библиотеки для визуализации")
    print("Установите их командой:")
    print("pip install matplotlib networkx")
    sys.exit(1)


class GraphVisualizer:
    """Класс для визуализации графа терминов."""
    
    def __init__(self, terms_file='terms.csv', links_file='links.csv'):
        """Инициализация с загрузкой данных из CSV."""
        self.terms = {}
        self.graph = defaultdict(list)
        self._load_terms(terms_file)
        self._load_links(links_file)
    
    def _load_terms(self, filename):
        """Загружает термины из CSV файла."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    term_name = row['term']
                    definition = row['definition']
                    self.terms[term_name] = definition
            print(f"Загружено терминов: {len(self.terms)}")
        except FileNotFoundError:
            print(f"Ошибка: файл {filename} не найден")
            sys.exit(1)
    
    def _load_links(self, filename):
        """Загружает связи между терминами из CSV файла."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    source = row['source']
                    target = row['target']
                    relation = row['relation']
                    self.graph[source].append((target, relation))
            print(f"Загружено связей: {sum(len(links) for links in self.graph.values())}")
        except FileNotFoundError:
            print(f"Ошибка: файл {filename} не найден")
            sys.exit(1)
    
    def visualize(self, output_file='glossary_graph.png', layout='spring', figsize=(24, 16)):
        """
        Создает визуализацию графа.
        
        Args:
            output_file: имя файла для сохранения изображения
            layout: тип раскладки графа ('spring', 'hierarchical', 'circular', 'kamada_kawai')
            figsize: размер фигуры (width, height)
        """
        # Создаем ориентированный граф
        G = nx.DiGraph()
        
        # Добавляем узлы (термины)
        for term in self.terms.keys():
            G.add_node(term)
        
        # Добавляем связи
        for source, connections in self.graph.items():
            for target, relation_type in connections:
                G.add_edge(source, target, label=relation_type)
        
        # Создаем фигуру
        plt.figure(figsize=figsize)
        plt.title('Граф терминов глоссария', fontsize=16, fontweight='bold', pad=20)
        
        # Выбираем раскладку
        if layout == 'spring':
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        elif layout == 'hierarchical':
            try:
                pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
            except:
                print("Warning: graphviz не найден, используем spring layout")
                pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        elif layout == 'circular':
            pos = nx.circular_layout(G)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(G)
        else:
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        
        # Определяем цвета узлов в зависимости от степени (количества связей)
        node_degrees = dict(G.degree())
        max_degree = max(node_degrees.values()) if node_degrees else 1
        
        # Цвета: более связанные узлы - темнее
        node_colors = [plt.cm.Blues(0.3 + 0.7 * node_degrees[node] / max_degree) 
                      for node in G.nodes()]
        
        # Размеры узлов пропорциональны степени
        node_sizes = [300 + 500 * node_degrees[node] / max_degree for node in G.nodes()]
        
        # Рисуем граф
        nx.draw_networkx_nodes(G, pos, 
                              node_color=node_colors,
                              node_size=node_sizes,
                              alpha=0.9,
                              edgecolors='black',
                              linewidths=2)
        
        # Рисуем связи
        nx.draw_networkx_edges(G, pos,
                              edge_color='gray',
                              arrows=True,
                              arrowsize=20,
                              alpha=0.6,
                              width=1.5,
                              connectionstyle='arc3,rad=0.1')
        
        # Подписи узлов (сокращенные названия)
        labels = {node: self._shorten_label(node, max_len=25) for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, 
                               labels,
                               font_size=8,
                               font_weight='bold',
                               bbox=dict(boxstyle='round,pad=0.3', 
                                       facecolor='white', 
                                       alpha=0.8,
                                       edgecolor='none'))
        
        # Подписи связей (названия типов отношений)
        edge_labels = {}
        for u, v, d in G.edges(data=True):
            label = d.get('label', '')
            # Сокращаем длинные названия связей для лучшей читаемости
            if len(label) > 25:
                label = label[:22] + '...'
            edge_labels[(u, v)] = label
        
        # Рисуем подписи связей с улучшенной видимостью
        nx.draw_networkx_edge_labels(G, pos, 
                                     edge_labels,
                                     font_size=8,
                                     font_color='darkblue',
                                     font_weight='bold',
                                     alpha=0.9,
                                     bbox=dict(boxstyle='round,pad=0.3',
                                             facecolor='yellow',
                                             alpha=0.8,
                                             edgecolor='darkblue',
                                             linewidth=1.0),
                                     rotate=False)
        
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Граф сохранен в файл: {output_file}")
        plt.show()
    
    def _shorten_label(self, text, max_len=25):
        """Сокращает длинные названия для лучшей читаемости."""
        if len(text) <= max_len:
            return text
        return text[:max_len-3] + '...'
    
    def print_statistics(self):
        """Выводит статистику по графу."""
        G = nx.DiGraph()
        
        for term in self.terms.keys():
            G.add_node(term)
        
        for source, connections in self.graph.items():
            for target, relation_type in connections:
                G.add_edge(source, target)
        
        print("\n" + "="*60)
        print("Статистика графа:")
        print("="*60)
        print(f"Всего узлов (терминов): {G.number_of_nodes()}")
        print(f"Всего связей (ребер): {G.number_of_edges()}")
        print(f"Средняя степень узла: {2 * G.number_of_edges() / G.number_of_nodes():.2f}")
        
        # Самые связанные термины
        degrees = dict(G.degree())
        top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:5]
        print("\nТоп-5 наиболее связанных терминов:")
        for term, degree in top_nodes:
            print(f"  - {term}: {degree} связей")
        
        # Компоненты связности
        undirected_G = G.to_undirected()
        components = list(nx.connected_components(undirected_G))
        print(f"\nКомпонент связности: {len(components)}")
        if len(components) == 1:
            print("  Граф полностью связный")
        else:
            print(f"  Самый большой компонент: {len(max(components, key=len))} узлов")
        
        print("="*60 + "\n")


def main():
    """Главная функция для запуска визуализации."""
    print("Создание визуализации графа терминов...")
    print()
    
    visualizer = GraphVisualizer()
    
    # Выводим статистику
    visualizer.print_statistics()
    
    # Создаем визуализацию
    print("Создание визуализации...")
    visualizer.visualize(
        output_file='glossary_graph.png',
        layout='spring',  # Можно изменить на 'circular', 'kamada_kawai'
        figsize=(20, 14)
    )
    
    print("\nВизуализация завершена!")


if __name__ == '__main__':
    main()
