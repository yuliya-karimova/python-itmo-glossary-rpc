"""
Интерактивная визуализация графа терминов глоссария.
Создает HTML файл с возможностью масштабирования и прокрутки.
"""
import csv
import sys
import math
from collections import defaultdict

try:
    import networkx as nx
    import plotly.graph_objects as go
    from plotly.offline import plot
except ImportError:
    print("Ошибка: Необходимо установить библиотеки для визуализации")
    print("Установите их командой:")
    print("pip install matplotlib networkx plotly")
    sys.exit(1)


class InteractiveGraphVisualizer:
    """Класс для интерактивной визуализации графа терминов."""
    
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
    
    def visualize(self, output_file='glossary_graph_interactive.html', layout='spring'):
        """
        Создает интерактивную визуализацию графа.
        
        Args:
            output_file: имя HTML файла для сохранения
            layout: тип раскладки графа ('spring', 'circular', 'kamada_kawai')
        """
        # Создаем ориентированный граф
        G = nx.DiGraph()
        
        # Добавляем узлы (термины)
        for term in self.terms.keys():
            G.add_node(term)
        
        # Добавляем связи с метками
        for source, connections in self.graph.items():
            for target, relation_type in connections:
                G.add_edge(source, target, label=relation_type)
        
        # Создаем автоматическую раскладку графа
        # Используем увеличенные параметры для предотвращения пересечений узлов
        # k - оптимальное расстояние между узлами (учитывая размер узла 100 пикселей)
        if layout == 'spring':
            # Значительно увеличиваем k для предотвращения пересечений (узлы размером 100)
            # Минимальное расстояние между центрами узлов должно быть > 100 (размер узла)
            pos = nx.spring_layout(
                G, 
                k=5,  # Значительно увеличено для предотвращения пересечений
                iterations=300,  # Больше итераций для лучшей конвергенции
                seed=42
            )
        elif layout == 'circular':
            # Для circular layout масштабируем область размещения
            pos = nx.circular_layout(G, scale=3)
        elif layout == 'kamada_kawai':
            # Kamada-Kawai обычно лучше предотвращает пересечения
            pos = nx.kamada_kawai_layout(G, scale=3)
        else:
            # По умолчанию используем kamada_kawai, так как он лучше предотвращает пересечения
            pos = nx.kamada_kawai_layout(G, scale=3)
        
        # Post-processing: проверяем и исправляем пересечения узлов
        # Минимальное расстояние между центрами узлов = размер узла (100)
        node_size = 100
        min_distance = node_size * 1.2  # Добавляем 20% запас
        
        # Исправляем пересечения итеративно
        max_iterations = 50
        for iteration in range(max_iterations):
            overlaps_found = False
            nodes_list = list(G.nodes())
            
            for i, node1 in enumerate(nodes_list):
                if node1 not in pos:
                    continue
                x1, y1 = pos[node1]
                
                for j, node2 in enumerate(nodes_list[i+1:], start=i+1):
                    if node2 not in pos:
                        continue
                    x2, y2 = pos[node2]
                    
                    # Вычисляем расстояние между узлами
                    distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                    
                    # Если узлы слишком близко, раздвигаем их
                    if distance < min_distance:
                        overlaps_found = True
                        # Вычисляем направление раздвижения
                        if distance > 0:
                            dx = (x2 - x1) / distance
                            dy = (y2 - y1) / distance
                        else:
                            # Если узлы в одной точке, раздвигаем случайно
                            import random
                            random.seed(42 + iteration)
                            angle = random.uniform(0, 2 * math.pi)
                            dx = math.cos(angle)
                            dy = math.sin(angle)
                        
                        # Раздвигаем узлы
                        move_distance = (min_distance - distance) / 2
                        pos[node1] = (x1 - dx * move_distance, y1 - dy * move_distance)
                        pos[node2] = (x2 + dx * move_distance, y2 + dy * move_distance)
            
            # Если пересечений не найдено, выходим
            if not overlaps_found:
                break
        
        # Подготавливаем данные для edges
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_info.append({
                'source': edge[0],
                'target': edge[1],
                'relation': edge[2].get('label', '')
            })
        
        # Создаем trace для edges
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines',
            showlegend=False
        )
        
        # Подготавливаем данные для nodes
        node_x = []
        node_y = []
        node_text = []
        node_info = []
        node_degrees = dict(G.degree())
        max_degree = max(node_degrees.values()) if node_degrees else 1
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(float(x))
            node_y.append(float(y))
            # Текст для hover
            definition = self.terms.get(node, '')
            # Сокращаем определение для hover
            short_def = definition[:100] + '...' if len(definition) > 100 else definition
            node_text.append(f"<b>{node}</b><br>Определение: {short_def}<br>Связей: {node_degrees[node]}")
            node_info.append({
                'name': node,
                'definition': definition,
                'degree': node_degrees[node]
            })
        
        # Все узлы одинакового размера - 100 пикселей
        node_sizes = [100] * len(G.nodes())
        
        # Создаем trace для nodes с переносом текста на несколько строк
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[self._wrap_text(node, max_chars_per_line=18) for node in G.nodes()],
            textposition="middle center",
            textfont=dict(size=10, color='black', family='Arial'),  # Размер текста адаптирован
            hovertext=node_text,
            marker=dict(
                size=node_sizes,
                color=[node_degrees[node] for node in G.nodes()],
                colorscale='Blues',
                showscale=False,  # Убираем цветовую шкалу
                line=dict(width=2, color='black')
            ),
            showlegend=False
        )
        
        # Создаем аннотации для связей (метки)
        annotations = []
        for i, edge in enumerate(G.edges(data=True)):
            source, target, data = edge
            x0, y0 = pos[source]
            x1, y1 = pos[target]
            # Средняя точка для метки
            x_mid = (x0 + x1) / 2
            y_mid = (y0 + y1) / 2
            relation_label = data.get('label', '')
            if relation_label:
                annotations.append(
                    dict(
                        x=x_mid,
                        y=y_mid,
                        text=relation_label[:20] + '...' if len(relation_label) > 20 else relation_label,
                        showarrow=False,
                        font=dict(size=9, color='darkblue'),
                        bgcolor='yellow',
                        bordercolor='darkblue',
                        borderwidth=1,
                        borderpad=2
                    )
                )
        
        # Создаем figure
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=dict(
                    text='<b>Интерактивный граф терминов глоссария</b><br><sub>Используйте колесико мыши для масштабирования, перетаскивайте для перемещения</sub>',
                    x=0.5,
                    font=dict(size=16)
                ),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=80),
                annotations=annotations,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white',
                paper_bgcolor='white',
                # Настройки для интерактивности
                dragmode='pan',
                hoverlabel=dict(bgcolor='white', bordercolor='black', font_size=12)
            )
        )
        
        # Сохраняем в HTML
        plot(fig, filename=output_file, auto_open=False)
        print(f"Интерактивный граф сохранен в файл: {output_file}")
        print(f"Откройте файл в браузере для просмотра")
        
        return fig
    
    def _shorten_label(self, text, max_len=20):
        """Сокращает длинные названия для лучшей читаемости."""
        if len(text) <= max_len:
            return text
        return text[:max_len-3] + '...'
    
    def _wrap_text(self, text, max_chars_per_line=15):
        """Разбивает текст на несколько строк для лучшей читаемости."""
        if len(text) <= max_chars_per_line:
            return text
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # Если добавление слова не превышает лимит
            if len(current_line) == 0:
                current_line = word
            elif len(current_line) + len(word) + 1 <= max_chars_per_line:
                current_line += " " + word
            else:
                # Сохраняем текущую строку и начинаем новую
                lines.append(current_line)
                current_line = word
        
        # Добавляем последнюю строку
        if current_line:
            lines.append(current_line)
        
        # Возвращаем текст с переносами для plotly (через <br>)
        return "<br>".join(lines)
    
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
    """Главная функция для запуска интерактивной визуализации."""
    print("Создание интерактивной визуализации графа терминов...")
    print()
    
    visualizer = InteractiveGraphVisualizer()
    
    # Выводим статистику
    visualizer.print_statistics()
    
    # Создаем интерактивную визуализацию
    print("Создание интерактивной визуализации...")
    visualizer.visualize(
        output_file='glossary_graph_interactive.html',
        layout='spring'
    )
    
    print("\nИнтерактивная визуализация завершена!")
    print("Откройте файл glossary_graph_interactive.html в браузере")


if __name__ == '__main__':
    main()
