import os
import pandas as pd
import re
from docx import Document
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer

class GostDataProcessor:
    def __init__(self, data_dir="./data"):
        self.data_dir = data_dir
        self.gost_examples_dir = os.path.join(data_dir, "gost_examples")
        self.non_gost_examples_dir = os.path.join(data_dir, "non_gost_examples")
        
        # Создаем директории, если их нет
        os.makedirs(self.gost_examples_dir, exist_ok=True)
        os.makedirs(self.non_gost_examples_dir, exist_ok=True)
        
        # Словарь соответствия типов элементов и меток
        self.element_types = {
            "regular_text": 0,
            "heading1": 1,
            "heading2": 2,
            "heading3": 3,
            "list_item": 4,
            "table_caption": 5,
            "figure_caption": 6
        }
    
    def load_documents(self, directory):
        """Загружает все документы из указанной директории"""
        documents = []
        for filename in os.listdir(directory):
            if filename.endswith(".docx"):
                file_path = os.path.join(directory, filename)
                documents.append(self.extract_paragraphs(file_path))
        return documents
    
    def extract_paragraphs(self, docx_path):
        """Извлекает абзацы из документа с их стилями"""
        doc = Document(docx_path)
        paragraphs = []
        
        for para in doc.paragraphs:
            if para.text.strip():  # Пропускаем пустые абзацы
                # Извлекаем информацию о форматировании
                style_info = {
                    "text": para.text,
                    "style_name": para.style.name,
                    "bold": any(run.bold for run in para.runs),
                    "italic": any(run.italic for run in para.runs),
                    "alignment": para.alignment,
                    "font_size": para.runs[0].font.size.pt if para.runs and para.runs[0].font.size else None,
                    "font_name": para.runs[0].font.name if para.runs and para.runs[0].font.name else None
                }
                paragraphs.append(style_info)
        
        return paragraphs
    
    def label_paragraphs(self, paragraphs):
        """Размечает абзацы по типам элементов"""
        labeled_data = []
        
        for para in paragraphs:
            text = para["text"]
            label = self.determine_element_type(para)
            labeled_data.append({
                "text": text,
                "label": label
            })
        
        return labeled_data
    
    def determine_element_type(self, para_info):
        """Определяет тип элемента на основе стиля"""
        text = para_info["text"]
        style_name = para_info["style_name"].lower()
        bold = para_info["bold"]
        
        # Логика определения типа элемента
        if "заголовок 1" in style_name or "heading 1" in style_name:
            return self.element_types["heading1"]
        elif "заголовок 2" in style_name or "heading 2" in style_name:
            return self.element_types["heading2"]
        elif "заголовок 3" in style_name or "heading 3" in style_name:
            return self.element_types["heading3"]
        elif re.match(r"^(рис(унок)?\.?\s+\d+|\d+\.\s+)", text, re.IGNORECASE):
            return self.element_types["figure_caption"]
        elif re.match(r"^(табл(ица)?\.?\s+\d+|\d+\.\s+)", text, re.IGNORECASE):
            return self.element_types["table_caption"]
        elif re.match(r"^\s*[-•]\s+", text):
            return self.element_types["list_item"]
        else:
            return self.element_types["regular_text"]
    
    def prepare_dataset(self):
        """Подготавливает датасет для обучения"""
        gost_docs = self.load_documents(self.gost_examples_dir)
        non_gost_docs = self.load_documents(self.non_gost_examples_dir)
        
        labeled_data = []
        
        # Размечаем ГОСТ-документы
        for doc in gost_docs:
            labeled_data.extend(self.label_paragraphs(doc))
        
        # Размечаем не-ГОСТ документы (здесь можно реализовать другую логику)
        for doc in non_gost_docs:
            labeled_data.extend(self.label_paragraphs(doc))
            
        # Сохраняем датасет в формате CSV
        df = pd.DataFrame(labeled_data)
        df.to_csv(os.path.join(self.data_dir, "gost_dataset.csv"), index=False)
        
        return df

class GostDataset(Dataset):
    def __init__(self, data, tokenizer, max_length=512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        text = self.data.iloc[idx]["text"]
        label = self.data.iloc[idx]["label"]
        
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "label": torch.tensor(label, dtype=torch.long)
        }

def get_data_loaders(data_path, tokenizer, batch_size=16, train_ratio=0.8):
    """Создает загрузчики данных для обучения и валидации"""
    df = pd.read_csv(data_path)
    
    # Перемешиваем данные
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Разделяем на обучающую и валидационную выборки
    train_size = int(len(df) * train_ratio)
    train_data = df[:train_size]
    val_data = df[train_size:]
    
    # Создаем датасеты
    train_dataset = GostDataset(train_data, tokenizer)
    val_dataset = GostDataset(val_data, tokenizer)
    
    # Создаем загрузчики данных
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    
    return train_loader, val_loader
