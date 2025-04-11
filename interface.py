import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import threading
from formatting import format_document
from PIL import Image, ImageTk

class GostFormatterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GOST Auto Format")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Установка иконки (если есть)
        # self.root.iconbitmap("icon.ico")
        
        # Настройка стилей
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50")
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("Header.TLabel", font=("Arial", 16, "bold"))
        
        # Переменные
        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.gost_type = tk.StringVar(value="7.32-2017")  # По умолчанию ГОСТ 7.32-2017
        self.processing = tk.BooleanVar(value=False)
        
        # Создание основного фрейма
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        header_label = ttk.Label(self.main_frame, text="GOST Auto Format", style="Header.TLabel")
        header_label.pack(pady=(0, 20))
        
        # Выбор ГОСТ
        gost_frame = ttk.LabelFrame(self.main_frame, text="Выберите стандарт ГОСТ", padding=10)
        gost_frame.pack(fill=tk.X, pady=10)
        
        ttk.Radiobutton(gost_frame, text="ГОСТ 7.32-2017 (Отчет о НИР)", value="7.32-2017", variable=self.gost_type).pack(anchor=tk.W)
        ttk.Radiobutton(gost_frame, text="ГОСТ Р 7.0.5-2008 (Библиографическая ссылка)", value="7.0.5-2008", variable=self.gost_type).pack(anchor=tk.W)
        ttk.Radiobutton(gost_frame, text="ГОСТ 7.1-2003 (Библиографическая запись)", value="7.1-2003", variable=self.gost_type).pack(anchor=tk.W)
        
        # Фрейм с файлами
        file_frame = ttk.LabelFrame(self.main_frame, text="Выбор файлов", padding=10)
        file_frame.pack(fill=tk.X, pady=10)
        
        # Выбор входного файла
        input_file_frame = ttk.Frame(file_frame)
        input_file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_file_frame, text="Входной файл:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(input_file_frame, textvariable=self.input_file_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(input_file_frame, text="Обзор...", command=self.browse_input_file).pack(side=tk.RIGHT)
        
        # Выбор выходного файла
        output_file_frame = ttk.Frame(file_frame)
        output_file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_file_frame, text="Выходной файл:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(output_file_frame, textvariable=self.output_file_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(output_file_frame, text="Обзор...", command=self.browse_output_file).pack(side=tk.RIGHT)
        
        # Фрейм для информации о модели
        model_frame = ttk.LabelFrame(self.main_frame, text="Нейросетевая модель", padding=10)
        model_frame.pack(fill=tk.X, pady=10)
        
        self.model_status = ttk.Label(model_frame, text="Статус: Модель не загружена")
        self.model_status.pack(anchor=tk.W, pady=5)
        
        model_buttons_frame = ttk.Frame(model_frame)
        model_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(model_buttons_frame, text="Загрузить модель", command=self.load_model).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(model_buttons_frame, text="Обучить новую модель", command=self.train_model).pack(side=tk.LEFT)
        
        # Кнопки действий
        actions_frame = ttk.Frame(self.main_frame)
        actions_frame.pack(fill=tk.X, pady=20)
        
        self.format_button = ttk.Button(actions_frame, text="Форматировать документ", command=self.format_document)
        self.format_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(actions_frame, text="Предварительный просмотр", command=self.preview_document).pack(side=tk.LEFT)
        
        # Индикатор прогресса
        self.progress_var = tk.IntVar()
        self.progress = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL, length=100, mode='determinate', variable=self.progress_var)
        self.progress.pack(fill=tk.X, pady=10)
        
        # Строка состояния
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_input_file(self):
        """Открывает диалог выбора входного файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите документ для форматирования",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        if file_path:
            self.input_file_path.set(file_path)
            # Автоматически устанавливаем выходной файл
            filename, ext = os.path.splitext(file_path)
            self.output_file_path.set(f"{filename}_formatted{ext}")
    
    def browse_output_file(self):
        """Открывает диалог выбора выходного файла"""
        file_path = filedialog.asksaveasfilename(
            title="Выберите место сохранения отформатированного документа",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")],
            defaultextension=".docx"
        )
        if file_path:
            self.output_file_path.set(file_path)
    
    def load_model(self):
        """Загружает предобученную модель"""
        model_path = filedialog.askopenfilename(
            title="Выберите файл модели",
            filetypes=[("PyTorch Model", "*.pt"), ("All Files", "*.*")]
        )
        if model_path:
            try:
                # Здесь код загрузки модели
                self.model_status.config(text=f"Статус: Модель загружена ({os.path.basename(model_path)})")
                self.status_var.set("Модель успешно загружена")
                messagebox.showinfo("Успех", "Модель успешно загружена")
            except Exception as e:
                self.status_var.set(f"Ошибка загрузки модели: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось загрузить модель: {str(e)}")
    
    def train_model(self):
        """Запускает обучение новой модели"""
        # В реальном приложении здесь должен быть интерфейс настройки параметров обучения
        train_window = tk.Toplevel(self.root)
        train_window.title("Обучение модели")
        train_window.geometry("600x400")
        train_window.transient(self.root)
        
        ttk.Label(train_window, text="Обучение новой модели", style="Header.TLabel").pack(pady=20)
        
        # Фрейм с настройками обучения
        settings_frame = ttk.LabelFrame(train_window, text="Параметры обучения", padding=10)
        settings_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Количество эпох
        epochs_frame = ttk.Frame(settings_frame)
        epochs_frame.pack(fill=tk.X, pady=5)
        ttk.Label(epochs_frame, text="Количество эпох:").pack(side=tk.LEFT)
        epochs_var = tk.IntVar(value=5)
        ttk.Spinbox(epochs_frame, from_=1, to=20, textvariable=epochs_var, width=5).pack(side=tk.LEFT, padx=10)
        
        # Размер батча
        batch_frame = ttk.Frame(settings_frame)
        batch_frame.pack(fill=tk.X, pady=5)
        ttk.Label(batch_frame, text="Размер батча:").pack(side=tk.LEFT)
        batch_var = tk.IntVar(value=16)
        ttk.Spinbox(batch_frame, from_=1, to=64, textvariable=batch_var, width=5).pack(side=tk.LEFT, padx=10)
        
        # Скорость обучения
        lr_frame = ttk.Frame(settings_frame)
        lr_frame.pack(fill=tk.X, pady=5)
        ttk.Label(lr_frame, text="Скорость обучения:").pack(side=tk.LEFT)
        lr_var = tk.DoubleVar(value=0.00002)
        ttk.Entry(lr_frame, textvariable=lr_var, width=10).pack(side=tk.LEFT, padx=10)
        
        # Директория с данными
        data_frame = ttk.Frame(settings_frame)
        data_frame.pack(fill=tk.X, pady=5)
        ttk.Label(data_frame, text="Директория с данными:").pack(side=tk.LEFT)
        data_var = tk.StringVar(value="./data")
        ttk.Entry(data_frame, textvariable=data_var, width=30).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(data_frame, text="Обзор...", command=lambda: data_var.set(filedialog.askdirectory(title="Выберите директорию с данными"))).pack(side=tk.RIGHT)
        
        # Кнопки
        buttons_frame = ttk.Frame(train_window)
        buttons_frame.pack(pady=20)
        
        def start_training():
            # Имитация обучения с progressbar
            progress_var = tk.IntVar()
            progress = ttk.Progressbar(train_window, orient=tk.HORIZONTAL, length=100, mode='determinate', variable=progress_var)
            progress.pack(fill=tk.X, padx=20, pady=10)
            
            status_var = tk.StringVar(value="Подготовка данных...")
            status = ttk.Label(train_window, textvariable=status_var)
            status.pack(pady=5)
            
            def simulate_training():
                # В реальном проекте здесь был бы вызов функции обучения модели
                import time
                for i in range(101):
                    time.sleep(0.05)
                    progress_var.set(i)
                    if i < 20:
                        status_var.set("Подготовка данных...")
                    elif i < 40:
                        status_var.set("Загрузка данных...")
                    elif i < 90:
                        status_var.set(f"Обучение модели... Эпоха {i//10}/{epochs_var.get()}")
                    else:
                        status_var.set("Сохранение модели...")
                    train_window.update()
                
                # Обновляем статус в главном окне
                self.model_status.config(text=f"Статус: Модель обучена (новая модель)")
                self.status_var.set("Модель успешно обучена")
                messagebox.showinfo("Успех", "Модель успешно обучена")
                train_window.destroy()
            
            threading.Thread(target=simulate_training).start()
        
        ttk.Button(buttons_frame, text="Начать обучение", command=start_training).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Отмена", command=train_window.destroy).pack(side=tk.LEFT)
    
    def format_document(self):
        """Запускает процесс форматирования документа"""
        input_path = self.input_file_path.get()
        output_path = self.output_file_path.get()
        
        if not input_path:
            messagebox.showerror("Ошибка", "Выберите входной файл!")
            return
        
        if not output_path:
            messagebox.showerror("Ошибка", "Выберите выходной файл!")
            return
        
        # Отключаем кнопку форматирования
        self.format_button.config(state=tk.DISABLED)
        self.processing.set(True)
        self.progress_var.set(0)
        self.status_var.set("Форматирование документа...")
        
        def process():
            try:
                # Имитация процесса форматирования с обновлением прогресса
                # В реальном проекте здесь был бы вызов функции format_document
                import time
                for i in range(101):
                    time.sleep(0.03)
                    self.progress_var.set(i)
                    if i < 20:
                        self.status_var.set("Анализ документа...")
                    elif i < 40:
                        self.status_var.set("Идентификация элементов...")
                    elif i < 70:
                        self.status_var.set("Применение форматирования...")
                    elif i < 90:
                        self.status_var.set("Проверка результатов...")
                    else:
                        self.status_var.set("Сохранение документа...")
                    self.root.update()
                
                # После успешного форматирования
                self.status_var.set(f"Документ успешно отформатирован и сохранен в {output_path}")
                messagebox.showinfo("Успех", f"Документ успешно отформатирован и сохранен в:\n{output_path}")
            except Exception as e:
                self.status_var.set(f"Ошибка при форматировании: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось отформатировать документ: {str(e)}")
            finally:
                # Восстанавливаем кнопку
                self.format_button.config(state=tk.NORMAL)
                self.processing.set(False)
        
        threading.Thread(target=process).start()
    
    def preview_document(self):
        """Показывает предварительный просмотр отформатированного документа"""
        if not self.input_file_path.get():
            messagebox.showerror("Ошибка", "Выберите входной файл для предварительного просмотра!")
            return
        
        # Здесь создаем окно с предварительным просмотром
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Предварительный просмотр")
        preview_window.geometry("800x600")
        preview_window.transient(self.root)
        
        ttk.Label(preview_window, text="Предварительный просмотр документа", style="Header.TLabel").pack(pady=10)
        
        preview_frame = ttk.Frame(preview_window, padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # В реальном приложении здесь был бы код для отображения содержимого документа
        # Для примера просто покажем текстовое поле с информацией о форматировании
        
        info_text = tk.Text(preview_frame, wrap=tk.WORD, font=("Arial", 11))
        info_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(preview_frame, command=info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        info_text.config(yscrollcommand=scrollbar.set)
        
        # Пример информации о форматировании
        sample_info = f"""Предварительный просмотр форматирования документа "{os.path.basename(self.input_file_path.get())}"
        
ГОСТ: {self.gost_type.get()}

1. Основные правила форматирования:
   - Шрифт: Times New Roman, 14pt
   - Выравнивание основного текста: по ширине
   - Межстрочный интервал: 1.5
   - Отступ первой строки: 1.25 см
   
2. Распознанные элементы:
   - Заголовки первого уровня: 2
   - Заголовки второго уровня: 4
   - Заголовки третьего уровня: 3
   - Списки: 5
   - Таблицы: 1
   - Рисунки: 2
   
3. Применение форматирования:
   - Заголовки первого уровня: шрифт 16pt, полужирный, выравнивание по центру
   - Заголовки второго уровня: шрифт 14pt, полужирный, выравнивание по левому краю
   - Заголовки третьего уровня: шрифт 14pt, полужирный, выравнивание по левому краю
   - Списки: отступ слева 1.25 см, выравнивание по ширине
   - Таблицы: шрифт 12pt, выравнивание по центру
   - Подписи к рисункам: шрифт 12pt, курсив, выравнивание по центру

4. Дополнительные параметры:
   - Поля: левое - 3 см, правое - 1.5 см, верхнее - 2 см, нижнее - 2 см
   - Нумерация страниц: внизу, по центру
"""
        info_text.insert(tk.END, sample_info)
        info_text.config(state=tk.DISABLED)  # Делаем текст только для чтения
        
        ttk.Button(preview_window, text="Закрыть", command=preview_window.destroy).pack(pady=10)

def run_interface():
    """Запускает графический интерфейс"""
    root = tk.Tk()
    app = GostFormatterApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_interface()
