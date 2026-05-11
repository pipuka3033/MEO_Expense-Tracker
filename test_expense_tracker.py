import unittest
import json
import os
import sys
from datetime import datetime

# Импортируем класс приложения, чтобы получить доступ к логике валидации
# Так как main.py запускает GUI, нам нужно аккуратно импортировать логику.
# Для упрощения тестирования, мы продублируем логику валидации здесь 
# или импортируем сам класс, если он правильно структурирован.
# В данном случае, так как класс определен в main.py, мы можем импортировать его.

from main import TrainingPlannerApp 
import tkinter as tk

class TestTrainingPlannerLogic(unittest.TestCase):
    
    def setUp(self):
        # Создаем скрытое окно Tkinter для инициализации класса, 
        # но не запускаем mainloop
        self.root = tk.Tk()
        self.root.withdraw() # Скрываем окно
        self.app = TrainingPlannerApp(self.root)
        # Очищаем данные перед тестом
        self.app.workouts = []

    def tearDown(self):
        self.root.destroy()
        if os.path.exists("workouts.json"):
            os.remove("workouts.json")

    def test_validate_correct_input(self):
        """Позитивный тест: корректная дата и длительность"""
        is_valid, msg = self.app.validate_input("12.05.2026", "45")
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")

    def test_validate_invalid_date_format(self):
        """Негативный тест: неверный формат даты"""
        is_valid, msg = self.app.validate_input("2026-05-12", "45")
        self.assertFalse(is_valid)
        self.assertIn("формат даты", msg.lower())

    def test_validate_invalid_date_value(self):
        """Негативный тест: несуществующая дата"""
        is_valid, msg = self.app.validate_input("32.01.2026", "45")
        self.assertFalse(is_valid)

    def test_validate_negative_duration(self):
        """Негативный тест: отрицательная длительность"""
        is_valid, msg = self.app.validate_input("12.05.2026", "-10")
        self.assertFalse(is_valid)
        self.assertIn("положительным", msg.lower())

    def test_validate_zero_duration(self):
        """Граничный тест: нулевая длительность"""
        is_valid, msg = self.app.validate_input("12.05.2026", "0")
        self.assertFalse(is_valid)

    def test_validate_non_numeric_duration(self):
        """Негативный тест: текст вместо числа"""
        is_valid, msg = self.app.validate_input("12.05.2026", "abc")
        self.assertFalse(is_valid)

    def test_add_and_save_load(self):
        """Интеграционный тест: добавление, сохранение и загрузка"""
        # Эмулируем добавление
        self.app.workouts.append({"date": "12.05.2026", "type": "Бег", "duration": 30})
        self.app.save_data()
        
        # Создаем новый экземпляр для проверки загрузки
        new_root = tk.Tk()
        new_root.withdraw()
        new_app = TrainingPlannerApp(new_root)
        
        self.assertEqual(len(new_app.workouts), 1)
        self.assertEqual(new_app.workouts[0]["type"], "Бег")
        
        new_root.destroy()
        if os.path.exists("workouts.json"):
            os.remove("workouts.json")

if __name__ == '__main__':
    unittest.main()
