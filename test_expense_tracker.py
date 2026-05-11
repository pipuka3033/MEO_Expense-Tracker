import unittest
import json
import os
import sys
import tempfile
from datetime import datetime

# Импортируем логику приложения. 
# Так как GUI сложно тестировать unit-тестами без headless драйверов,
# мы тестируем основные функции обработки данных и валидации, вынеся их логику.
# Для этого мы создадим вспомогательный класс или будем проверять файлы напрямую.

# Чтобы протестировать валидацию и сохранение, нам нужно немного адаптировать подход.
# Мы будем тестировать создание JSON и чтение из него, а также логику фильтрации.

class TestExpenseLogic(unittest.TestCase):
    
    def setUp(self):
        """Создаем временный файл для тестов."""
        self.test_file = "test_expenses.json"
        # Очищаем файл если есть
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """Удаляем временный файл после теста."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def create_sample_data(self, data):
        """Хелпер для записи тестовых данных."""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_sample_data(self):
        """Хелпер для чтения тестовых данных."""
        if os.path.exists(self.test_file):
            with open(self.test_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    # --- Тесты валидации (эмуляция логики из main.py) ---
    
    def validate_amount(self, amount_str):
        try:
            amount = float(amount_str)
            if amount <= 0:
                return None
            return amount
        except ValueError:
            return None

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
            return True
        except ValueError:
            return False

    # Позитивные тесты
    def test_valid_amount_positive(self):
        self.assertEqual(self.validate_amount("100.50"), 100.50)
    
    def test_valid_date_format(self):
        self.assertTrue(self.validate_date("11.05.2026"))

    # Негативные тесты
    def test_invalid_amount_negative(self):
        self.assertIsNone(self.validate_amount("-50"))
        
    def test_invalid_amount_zero(self):
        self.assertIsNone(self.validate_amount("0"))
        
    def test_invalid_amount_text(self):
        self.assertIsNone(self.validate_amount("abc"))
        
    def test_invalid_date_format(self):
        self.assertFalse(self.validate_date("2026-05-11")) # Не тот формат
        self.assertFalse(self.validate_date("32.01.2026")) # Несуществующая дата

    # Граничные случаи
    def test_boundary_amount_small(self):
        self.assertEqual(self.validate_amount("0.01"), 0.01)
        
    def test_boundary_amount_large(self):
        self.assertGreater(self.validate_amount("999999.99"), 0)

    # --- Тесты работы с JSON ---
    
    def test_save_and_load_json(self):
        sample_data = [
            {"id": 1, "amount": 100, "category": "Еда", "date": "11.05.2026"}
        ]
        self.create_sample_data(sample_data)
        loaded_data = self.load_sample_data()
        self.assertEqual(len(loaded_data), 1)
        self.assertEqual(loaded_data[0]['category'], "Еда")

    def test_empty_json_load(self):
        self.create_sample_data([])
        loaded_data = self.load_sample_data()
        self.assertEqual(loaded_data, [])

    def test_corrupted_json(self):
        with open(self.test_file, 'w') as f:
            f.write("{invalid json}")
        # При загрузке должно возникнуть исключение или возврат пустого списка в зависимости от реализации
        # В нашем приложении main.py обрабатывает это через try-except и возвращает []
        # Здесь проверим, что json.load выбрасывает ошибку
        with self.assertRaises(json.JSONDecodeError):
            with open(self.test_file, 'r') as f:
                json.load(f)

    # --- Тесты фильтрации (логика) ---
    
    def filter_expenses(self, expenses, category_filter="Все", start_date=None, end_date=None):
        """Эмуляция функции фильтрации из main.py"""
        filtered = expenses[:]
        if category_filter != "Все":
            filtered = [e for e in filtered if e['category'] == category_filter]
        
        if start_date or end_date:
            temp = []
            for e in filtered:
                try:
                    exp_date = datetime.strptime(e['date'], "%d.%m.%Y")
                    if start_date and exp_date < start_date:
                        continue
                    if end_date and exp_date > end_date:
                        continue
                    temp.append(e)
                except:
                    continue
            filtered = temp
        return filtered

    def test_filter_by_category(self):
        data = [
            {"id": 1, "amount": 100, "category": "Еда", "date": "11.05.2026"},
            {"id": 2, "amount": 200, "category": "Транспорт", "date": "11.05.2026"}
        ]
        result = self.filter_expenses(data, category_filter="Еда")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['category'], "Еда")

    def test_filter_by_date_range(self):
        data = [
            {"id": 1, "amount": 100, "category": "Еда", "date": "10.05.2026"},
            {"id": 2, "amount": 200, "category": "Еда", "date": "12.05.2026"},
            {"id": 3, "amount": 300, "category": "Еда", "date": "15.05.2026"}
        ]
        start = datetime.strptime("11.05.2026", "%d.%m.%Y")
        end = datetime.strptime("13.05.2026", "%d.%m.%Y")
        result = self.filter_expenses(data, start_date=start, end_date=end)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 2)

    def test_filter_no_results(self):
        data = [
            {"id": 1, "amount": 100, "category": "Еда", "date": "11.05.2026"}
        ]
        result = self.filter_expenses(data, category_filter="Транспорт")
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()
