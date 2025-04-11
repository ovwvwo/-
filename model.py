import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
import numpy as np

class DocumentElementClassifier(nn.Module):
    def __init__(self, model_name="DeepPavlov/rubert-base-cased", num_classes=7):
        super(DocumentElementClassifier, self).__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)
        
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        return logits

class GostFormatter:
    def __init__(self, model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")
        
        # Классы элементов документа
        self.element_classes = {
            0: "regular_text",
            1: "heading1",
            2: "heading2",
            3: "heading3",
            4: "list_item",
            5: "table_caption",
            6: "figure_caption"
        }
        
        # Загрузка обученной модели или создание новой
        if model_path and torch.cuda.is_available():
            self.model = DocumentElementClassifier().to(self.device)
            self.model.load_state_dict(torch.load(model_path))
        else:
            self.model = DocumentElementClassifier().to(self.device)
        
        self.model.eval()
    
    def classify_paragraph(self, text):
        """Классифицирует абзац текста на один из элементов документа"""
        inputs = self.tokenizer(text, return_tensors="pt", max_length=512, 
                                truncation=True, padding="max_length")
        input_ids = inputs["input_ids"].to(self.device)
        attention_mask = inputs["attention_mask"].to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask)
            predictions = torch.argmax(outputs, dim=1)
        
        element_type = self.element_classes[predictions.item()]
        return element_type
    
    def get_gost_formatting_rules(self, element_type):
        """Возвращает правила форматирования для данного типа элемента по ГОСТ"""
        formatting_rules = {
            "regular_text": {
                "font": "Times New Roman",
                "size": 14,
                "alignment": "JUSTIFY",
                "first_line_indent": 1.25,
                "line_spacing": 1.5
            },
            "heading1": {
                "font": "Times New Roman",
                "size": 16,
                "bold": True,
                "alignment": "CENTER",
                "space_after": 12,
                "keep_with_next": True
            },
            "heading2": {
                "font": "Times New Roman",
                "size": 14,
                "bold": True,
                "alignment": "LEFT",
                "space_before": 12,
                "space_after": 6,
                "keep_with_next": True
            },
            "heading3": {
                "font": "Times New Roman",
                "size": 14,
                "bold": True,
                "alignment": "LEFT",
                "space_before": 6,
                "space_after": 6,
                "keep_with_next": True
            },
            "list_item": {
                "font": "Times New Roman",
                "size": 14,
                "alignment": "JUSTIFY",
                "line_spacing": 1.5,
                "left_indent": 1.25
            },
            "table_caption": {
                "font": "Times New Roman",
                "size": 12,
                "alignment": "CENTER",
                "space_before": 6,
                "space_after": 6,
                "italic": True
            },
            "figure_caption": {
                "font": "Times New Roman",
                "size": 12,
                "alignment": "CENTER",
                "space_before": 6,
                "space_after": 12,
                "italic": True
            }
        }
        
        return formatting_rules.get(element_type, formatting_rules["regular_text"])
