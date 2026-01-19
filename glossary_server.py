"""
Сервер gRPC для работы с графом терминов глоссария.
Загружает данные из terms.csv и links.csv и предоставляет API для работы с графом.
"""
import csv
import sys
from collections import defaultdict
from concurrent import futures

import grpc

# Импорты protobuf и gRPC
try:
    import glossary_pb2
    import glossary_pb2_grpc
    from google.protobuf import empty_pb2
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что сгенерированы файлы glossary_pb2.py и glossary_pb2_grpc.py")
    print("Команда для генерации:")
    print("python -m grpc_tools.protoc -I./protobufs --python_out=. --pyi_out=. --grpc_python_out=. ./protobufs/glossary.proto")
    sys.exit(1)


class GlossaryGraph:
    """Класс для работы с графом терминов."""
    
    def __init__(self, terms_file='terms.csv', links_file='links.csv'):
        """
        Инициализация графа из CSV файлов.
        
        Args:
            terms_file: путь к файлу с терминами
            links_file: путь к файлу со связями
        """
        self.terms = {}  # Словарь: название термина -> определение
        self.graph = defaultdict(list)  # Граф: термин -> [(связанный_термин, тип_связи), ...]
        self.reverse_graph = defaultdict(list)  # Обратный граф для двунаправленного поиска
        
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
                    
                    # Добавляем связь в граф
                    self.graph[source].append((target, relation))
                    # Добавляем обратную связь для двунаправленного поиска
                    self.reverse_graph[target].append((source, relation))
            print(f"Загружено связей: {sum(len(links) for links in self.graph.values())}")
        except FileNotFoundError:
            print(f"Ошибка: файл {filename} не найден")
            sys.exit(1)
    
    def get_term(self, term_name):
        """Получить информацию о термине."""
        if term_name in self.terms:
            return {
                'name': term_name,
                'definition': self.terms[term_name],
                'found': True
            }
        return {'found': False}
    
    def get_all_terms(self):
        """Получить все термины."""
        return [
            {'name': name, 'definition': definition}
            for name, definition in self.terms.items()
        ]
    
    def get_term_relations(self, term_name, max_depth=1):
        """
        Получить связи термина.
        
        Args:
            term_name: название термина
            max_depth: максимальная глубина поиска (пока используется только 1)
        """
        relations = []
        
        # Исходящие связи
        if term_name in self.graph:
            for target, relation_type in self.graph[term_name]:
                relations.append({
                    'source_term': term_name,
                    'target_term': target,
                    'relation_type': relation_type
                })
        
        # Входящие связи
        if term_name in self.reverse_graph:
            for source, relation_type in self.reverse_graph[term_name]:
                relations.append({
                    'source_term': source,
                    'target_term': term_name,
                    'relation_type': relation_type
                })
        
        return relations
    
    def find_path(self, source_term, target_term, max_depth=10):
        """
        Найти путь между двумя терминами используя BFS.
        
        Args:
            source_term: начальный термин
            target_term: целевой термин
            max_depth: максимальная глубина поиска
        """
        if source_term not in self.terms or target_term not in self.terms:
            return {'path_exists': False, 'message': 'Один или оба термина не найдены'}
        
        if source_term == target_term:
            return {'path_exists': True, 'path': [source_term], 'message': 'Термины совпадают'}
        
        # BFS для поиска пути
        queue = [(source_term, [source_term])]
        visited = {source_term}
        depth = 0
        
        while queue and depth < max_depth:
            next_level = []
            for current, path in queue:
                # Проверяем прямые связи
                if current in self.graph:
                    for neighbor, _ in self.graph[current]:
                        if neighbor == target_term:
                            return {
                                'path_exists': True,
                                'path': path + [neighbor],
                                'message': 'Путь найден'
                            }
                        if neighbor not in visited:
                            visited.add(neighbor)
                            next_level.append((neighbor, path + [neighbor]))
                
                # Проверяем обратные связи
                if current in self.reverse_graph:
                    for neighbor, _ in self.reverse_graph[current]:
                        if neighbor == target_term:
                            return {
                                'path_exists': True,
                                'path': path + [neighbor],
                                'message': 'Путь найден'
                            }
                        if neighbor not in visited:
                            visited.add(neighbor)
                            next_level.append((neighbor, path + [neighbor]))
            
            queue = next_level
            depth += 1
        
        return {'path_exists': False, 'path': [], 'message': 'Путь не найден в пределах максимальной глубины'}


class GlossaryService(glossary_pb2_grpc.GlossaryServiceServicer):
    """Реализация gRPC сервиса для работы с графом терминов."""
    
    def __init__(self, glossary_graph):
        self.graph = glossary_graph
    
    def GetTerm(self, request, context):
        """Получить информацию о термине."""
        result = self.graph.get_term(request.term_name)
        
        if result['found']:
            term = glossary_pb2.Term(
                name=result['name'],
                definition=result['definition']
            )
            return glossary_pb2.TermResponse(term=term, found=True)
        else:
            return glossary_pb2.TermResponse(found=False)
    
    def GetAllTerms(self, request, context):
        """Получить все термины."""
        terms_list = self.graph.get_all_terms()
        terms = [
            glossary_pb2.Term(name=t['name'], definition=t['definition'])
            for t in terms_list
        ]
        return glossary_pb2.AllTermsResponse(terms=terms, total_count=len(terms))
    
    def GetTermRelations(self, request, context):
        """Получить связи термина."""
        relations_list = self.graph.get_term_relations(
            request.term_name,
            request.max_depth if request.max_depth > 0 else 1
        )
        
        relations = [
            glossary_pb2.Relation(
                source_term=r['source_term'],
                target_term=r['target_term'],
                relation_type=r['relation_type']
            )
            for r in relations_list
        ]
        
        return glossary_pb2.RelationsResponse(
            relations=relations,
            total_count=len(relations)
        )
    
    def FindPath(self, request, context):
        """Найти путь между двумя терминами."""
        result = self.graph.find_path(
            request.source_term,
            request.target_term,
            request.max_depth if request.max_depth > 0 else 10
        )
        
        return glossary_pb2.PathResponse(
            path=result.get('path', []),
            path_exists=result['path_exists'],
            message=result.get('message', '')
        )


def serve():
    """Запуск gRPC сервера."""
    # Загружаем граф терминов
    graph = GlossaryGraph()
    
    # Создаем gRPC сервер
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    glossary_pb2_grpc.add_GlossaryServiceServicer_to_server(
        GlossaryService(graph), server
    )
    
    # Запускаем сервер на порту 50052 (чтобы не конфликтовать с рекомендациями)
    port = '50052'
    server.add_insecure_port('[::]:' + port)
    server.start()
    print(f"Glossary gRPC сервер запущен, слушает порт {port}")
    print(f"Загружено терминов: {len(graph.terms)}")
    print(f"Загружено связей: {sum(len(links) for links in graph.graph.values())}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
