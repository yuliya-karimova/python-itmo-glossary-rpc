"""
Клиент для тестирования Glossary gRPC сервиса.
Демонстрирует различные операции с графом терминов.
"""
import sys

import grpc

# Импорты будут добавлены после генерации proto файлов
# import glossary_pb2
# import glossary_pb2_grpc
# from google.protobuf import empty_pb2


def run_client():
    """Запуск клиента и демонстрация работы с сервисом."""
    try:
        import glossary_pb2
        import glossary_pb2_grpc
        from google.protobuf import empty_pb2
    except ImportError:
        print("Ошибка: файлы glossary_pb2.py и glossary_pb2_grpc.py не найдены.")
        print("Сначала сгенерируйте их командой:")
        print("python -m grpc_tools.protoc -I./protobufs --python_out=. --pyi_out=. --grpc_python_out=. ./protobufs/glossary.proto")
        sys.exit(1)
    
    # Подключаемся к серверу
    channel = grpc.insecure_channel('localhost:50052')
    stub = glossary_pb2_grpc.GlossaryServiceStub(channel)
    
    print("=" * 60)
    print("Клиент Glossary gRPC сервиса")
    print("=" * 60)
    print()
    
    # 1. Получить все термины
    print("1. Получение списка всех терминов:")
    print("-" * 60)
    try:
        response = stub.GetAllTerms(empty_pb2.Empty())
        print(f"Всего терминов: {response.total_count}")
        print(f"Первые 5 терминов:")
        for i, term in enumerate(response.terms[:5], 1):
            print(f"  {i}. {term.name}")
        print()
    except grpc.RpcError as e:
        print(f"Ошибка: {e.code()} - {e.details()}")
        print()
    
    # 2. Получить информацию о конкретном термине
    print("2. Получение информации о термине:")
    print("-" * 60)
    term_name = "Backend-Driven UI"
    try:
        request = glossary_pb2.TermRequest(term_name=term_name)
        response = stub.GetTerm(request)
        if response.found:
            print(f"Термин: {response.term.name}")
            print(f"Определение: {response.term.definition}")
        else:
            print(f"Термин '{term_name}' не найден")
        print()
    except grpc.RpcError as e:
        print(f"Ошибка: {e.code()} - {e.details()}")
        print()
    
    # 3. Получить связи термина
    print("3. Получение связей термина:")
    print("-" * 60)
    term_name = "Backend-Driven UI"
    try:
        request = glossary_pb2.RelationsRequest(term_name=term_name, max_depth=1)
        response = stub.GetTermRelations(request)
        print(f"Термин: {term_name}")
        print(f"Всего связей: {response.total_count}")
        print("Связи:")
        for relation in response.relations:
            print(f"  {relation.source_term} --[{relation.relation_type}]--> {relation.target_term}")
        print()
    except grpc.RpcError as e:
        print(f"Ошибка: {e.code()} - {e.details()}")
        print()
    
    # 4. Найти путь между терминами
    print("4. Поиск пути между терминами:")
    print("-" * 60)
    source = "Подход к разработке интерфейса"
    target = "Интерпретатор UI"
    try:
        request = glossary_pb2.PathRequest(
            source_term=source,
            target_term=target,
            max_depth=10
        )
        response = stub.FindPath(request)
        if response.path_exists:
            print(f"Путь от '{source}' к '{target}':")
            print(" -> ".join(response.path))
        else:
            print(f"Путь не найден: {response.message}")
        print()
    except grpc.RpcError as e:
        print(f"Ошибка: {e.code()} - {e.details()}")
        print()
    
    # 5. Еще один пример поиска пути
    print("5. Поиск другого пути:")
    print("-" * 60)
    source = "Классическая разработка UI"
    target = "Клиентский рендеринг"
    try:
        request = glossary_pb2.PathRequest(
            source_term=source,
            target_term=target,
            max_depth=10
        )
        response = stub.FindPath(request)
        if response.path_exists:
            print(f"Путь от '{source}' к '{target}':")
            print(" -> ".join(response.path))
        else:
            print(f"Путь не найден: {response.message}")
        print()
    except grpc.RpcError as e:
        print(f"Ошибка: {e.code()} - {e.details()}")
        print()
    
    print("=" * 60)
    print("Демонстрация завершена")
    print("=" * 60)
    
    channel.close()


if __name__ == '__main__':
    run_client()
