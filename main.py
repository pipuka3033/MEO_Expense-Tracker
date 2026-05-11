import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# Константы
DATA_FILE = "expenses.json"
CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Жилье", "Здоровье", "Другое"]


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("800x600")

        # Загрузка данных
        self.expenses = self.load_data()

        # --- Интерфейс ввода ---
        input_frame = tk.LabelFrame(root, text="Добавить новый расход", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        tk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.amount_entry = tk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=2)

        # Категория
        tk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, values=CATEGORIES, state="readonly")
        self.category_combo.grid(row=0, column=3, padx=5, pady=2)

        # Дата
        tk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=4, sticky="w", padx=5, pady=2)
        self.date_entry = tk.Entry(input_frame)
        # Установка текущей даты по умолчанию
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.date_entry.grid(row=0, column=5, padx=5, pady=2)

        # Кнопка добавления
        add_btn = tk.Button(input_frame, text="Добавить расход", command=self.add_expense, bg="#4CAF50", fg="white")
        add_btn.grid(row=0, column=6, padx=10, pady=2)

        # --- Интерфейс фильтрации и статистики ---
        filter_frame = tk.LabelFrame(root, text="Фильтры и Статистика", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Фильтр по категории:").grid(row=0, column=0, sticky="w", padx=5)
        self.filter_category_var = tk.StringVar(value="Все")
        filter_categories = ["Все"] + CATEGORIES
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, values=filter_categories, state="readonly")
        self.filter_category_combo.grid(row=0, column=1, padx=5)
        self.filter_category_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        tk.Label(filter_frame, text="Дата с (ДД.ММ.ГГГГ):").grid(row=0, column=2, sticky="w", padx=5)
        self.start_date_entry = tk.Entry(filter_frame, width=12)
        self.start_date_entry.grid(row=0, column=3, padx=5)

        tk.Label(filter_frame, text="Дата по (ДД.ММ.ГГГГ):").grid(row=0, column=4, sticky="w", padx=5)
        self.end_date_entry = tk.Entry(filter_frame, width=12)
        self.end_date_entry.grid(row=0, column=5, padx=5)

        filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filters)
        filter_btn.grid(row=0, column=6, padx=10)

        # Метка для отображения суммы
        self.total_label = tk.Label(filter_frame, text="Итого: 0.00", font=("Arial", 12, "bold"), fg="blue")
        self.total_label.grid(row=1, column=0, columnspan=7, sticky="w", pady=5)

        # --- Таблица расходов ---
        table_frame = tk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Дата", "Категория", "Сумма")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Сумма", text="Сумма")

        self.tree.column("ID", width=50)
        self.tree.column("Дата", width=100)
        self.tree.column("Категория", width=150)
        self.tree.column("Сумма", width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # Кнопка удаления
        delete_btn = tk.Button(root, text="Удалить выбранный расход", command=self.delete_expense, bg="#f44336", fg="white")
        delete_btn.pack(pady=5)

        # Первоначальная отрисовка
        self.refresh_table()

    def validate_input(self, amount_str, date_str):
        """Валидация ввода: сумма и дата."""
        # Проверка суммы
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной.")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Некорректная сумма. Введите положительное число.")
            return None, None

        # Проверка даты
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Некорректный формат даты. Используйте ДД.ММ.ГГГГ.")
            return None, None

        return amount, date_obj

    def add_expense(self):
        amount_str = self.amount_entry.get()
        category = self.category_var.get()
        date_str = self.date_entry.get()

        amount, date_obj = self.validate_input(amount_str, date_str)
        if amount is None:
            return

        new_expense = {
            "id": len(self.expenses) + 1,  # Простой ID, можно улучшить
            "amount": amount,
            "category": category,
            "date": date_str
        }
        
        self.expenses.append(new_expense)
        self.save_data()
        self.refresh_table()
        
        # Очистка поля суммы и сброс даты на сегодня
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        
        messagebox.showinfo("Успех", "Расход добавлен!")

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите расход для удаления.")
            return
        
        item = self.tree.item(selected_item[0])
        expense_id = item['values'][0]
        
        # Удаляем из списка
        self.expenses = [e for e in self.expenses if e['id'] != expense_id]
        
        # Пересчитываем ID для корректности (опционально, но лучше для чистоты)
        for i, e in enumerate(self.expenses):
            e['id'] = i + 1
            
        self.save_data()
        self.refresh_table()

    def get_filtered_expenses(self):
        """Возвращает список расходов, прошедших фильтрацию."""
        filtered = self.expenses[:]
        
        cat_filter = self.filter_category_var.get()
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()

        # Фильтр по категории
        if cat_filter != "Все":
            filtered = [e for e in filtered if e['category'] == cat_filter]

        # Фильтр по дате
        try:
            start_date = datetime.strptime(start_date_str, "%d.%m.%Y") if start_date_str else None
            end_date = datetime.strptime(end_date_str, "%d.%m.%Y") if end_date_str else None
        except ValueError:
            messagebox.showerror("Ошибка фильтра", "Неверный формат даты в фильтре.")
            return []

        if start_date or end_date:
            temp_filtered = []
            for e in filtered:
                try:
                    exp_date = datetime.strptime(e['date'], "%d.%m.%Y")
                    if start_date and exp_date < start_date:
                        continue
                    if end_date and exp_date > end_date:
                        continue
                    temp_filtered.append(e)
                except ValueError:
                    continue # Пропускаем записи с некорректной датой в БД
            filtered = temp_filtered

        return filtered

    def apply_filters(self, event=None):
        """Обновляет таблицу и сумму на основе фильтров."""
        self.refresh_table()

    def refresh_table(self):
        """Очищает и заполняет таблицу данными с учетом фильтров."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtered_expenses = self.get_filtered_expenses()
        
        total_sum = 0
        for expense in filtered_expenses:
            self.tree.insert("", tk.END, values=(
                expense['id'],
                expense['date'],
                expense['category'],
                f"{expense['amount']:.2f}"
            ))
            total_sum += expense['amount']
            
        self.total_label.config(text=f"Итого: {total_sum:.2f}")

    def save_data(self):
        """Сохраняет данные в JSON файл."""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except IOError as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        """Загружает данные из JSON файла."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить данные: {e}")
                return []
        return []


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
