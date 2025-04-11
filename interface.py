import tkinter as tk
from tkinter import filedialog
from main import format_document

def upload_file():
    file_path = filedialog.askopenfilename(title="Выберите документ", filetypes=[("Word Documents", "*.docx")])
    if file_path:
        format_document(file_path)

def run_interface():
    root = tk.Tk()
    root.title("ГОСТ Форматирование")
    upload_button = tk.Button(root, text="Загрузить документ", command=upload_file)
    upload_button.pack(pady=20)
    root.mainloop()
