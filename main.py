import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "workouts.json"

class TrainingPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x600")

        # Данные
        self.workouts = []
        self.load_data()

        # --- Интерфейс ввода ---
        input_frame = ttk.LabelFrame(root, text="Добавить тренировку", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

        # Тип тренировки
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.type_combo = ttk.Combobox(input_frame, values=["Бег", "Плавание", "Силовая", "Йога", "Велосипед"])
        self.type_combo.grid(row=1, column=1, padx=5, pady=5)
        self.type_combo.current(0)

        # Длительность (минуты)
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.duration_entry = ttk.Entry(input_frame)
        self.duration_entry.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка добавления
        add_btn = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_workout)
        add_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # --- Интерфейс фильтрации ---
        filter_frame = ttk.LabelFrame(root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Фильтр по типу:").grid(row=0, column=0, sticky="w", padx=5)
        self.filter_type_var = tk.StringVar(value="Все")
        filter_types = ["Все"] + ["Бег", "Плавание", "Силовая", "Йога", "Велосипед"]
        self.filter_type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var, values=filter_types)
        self.filter_type_combo.grid(row=0, column=1, padx=5)
        self.filter_type_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        ttk.Label(filter_frame, text="Фильтр по дате (ДД.ММ.ГГГГ):").grid(row=0, column=2, sticky="w", padx=5)
        self.filter_date_entry = ttk.Entry(filter_frame)
        self.filter_date_entry.grid(row=0, column=3, padx=5)
        self.filter_date_entry.bind("<KeyRelease>", self.apply_filters)

        clear_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.clear_filters)
        clear_filter_btn.grid(row=0, column=4, padx=5)

        # --- Таблица данных ---
        table_frame = ttk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("date", "type", "duration")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип")
        self.tree.heading("duration", text="Длительность (мин)")

        self.tree.column("date", width=150)
        self.tree.column("type", width=200)
        self.tree.column("duration", width=150)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопка удаления
        del_btn = ttk.Button(root, text="Удалить выбранную запись", command=self.delete_workout)
        del_btn.pack(pady=5)

        # Первоначальная отрисовка
        self.refresh_table()

    def validate_input(self, date_str, duration_str):
        """Проверка корректности ввода."""
        # Проверка даты
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            return False, "Неверный формат даты. Используйте ДД.ММ.ГГГГ."
        
        # Проверка длительности
        try:
            duration = int(duration_str)
            if duration <= 0:
                return False, "Длительность должна быть положительным числом."
        except ValueError:
            return False, "Длительность должна быть целым числом."
        
        return True, ""

    def add_workout(self):
        date_str = self.date_entry.get().strip()
        workout_type = self.type_combo.get()
        duration_str = self.duration_entry.get().strip()

        is_valid, error_msg = self.validate_input(date_str, duration_str)
        if not is_valid:
            messagebox.showerror("Ошибка ввода", error_msg)
            return

        workout = {
            "date": date_str,
            "type": workout_type,
            "duration": int(duration_str)
        }

        self.workouts.append(workout)
        self.save_data()
        self.refresh_table()
        
        # Очистка поля длительности для удобства
        self.duration_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", "Тренировка добавлена!")

    def delete_workout(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите запись для удаления.")
            return
        
        item = self.tree.item(selected_item[0])
        # Находим запись в списке по значениям (упрощенно, так как ID может меняться при фильтрации)
        # Для надежности лучше хранить ID в дереве, но здесь сделаем поиск по совпадению
        date_val = item['values'][0]
        type_val = item['values'][1]
        dur_val = item['values'][2]

        for w in self.workouts:
            if w['date'] == date_val and w['type'] == type_val and w['duration'] == dur_val:
                self.workouts.remove(w)
                break
        
        self.save_data()
        self.refresh_table()

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.workouts, f, ensure_ascii=False, indent=4)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.workouts = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.workouts = []
        else:
            self.workouts = []

    def apply_filters(self, event=None):
        self.refresh_table()

    def clear_filters(self):
        self.filter_type_var.set("Все")
        self.filter_date_entry.delete(0, tk.END)
        self.refresh_table()

    def refresh_table(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Получение значений фильтров
        filter_type = self.filter_type_var.get()
        filter_date = self.filter_date_entry.get().strip()

        for workout in self.workouts:
            # Фильтрация по типу
            if filter_type != "Все" and workout["type"] != filter_type:
                continue
            
            # Фильтрация по дате (точное совпадение или частичное, если введено)
            if filter_date:
                if filter_date not in workout["date"]:
                    continue

            self.tree.insert("", tk.END, values=(
                workout["date"],
                workout["type"],
                workout["duration"]
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlannerApp(root)
    root.mainloop()
