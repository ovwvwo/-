from formatting import load_docx, identify_elements, format_document
from interface import run_interface

def main():
    # Загружаем и форматируем документ
    file_path = 'your_document.docx'  # Здесь будет путь к вашему файлу
    text = load_docx(file_path)
    headings, lists = identify_elements(text)
    
    print("Identified Headings:", headings)
    print("Identified Lists:", lists)
    
    # Применяем форматирование
    format_document(file_path)
    
    print("Документ отформатирован и сохранен.")
    
# Запуск графического интерфейса
run_interface()
