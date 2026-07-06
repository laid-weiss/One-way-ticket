# run_tests.py
import sys
import os
import unittest

if __name__ == "__main__":
    # Динамически добавляем src в пути поиска, чтобы не настраивать PYTHONPATH руками
    sys.path.insert(0, os.path.abspath("src"))
    
    print("=== Поиск и запуск тестов ===")
    
    # Настраиваем загрузчик тестов (эквивалент discover в консоли)
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests")
    
    # Запускаем текстовый раннер
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Возвращаем non-zero код, если тесты упали (полезно для будущего CI/CD)
    sys.exit(not result.wasSuccessful())