"""Load and cache JSONL data files."""
import json
from pathlib import Path
from typing import List, Dict
from config import settings


class DataItem:
    """Represents a single data item from JSONL."""
    def __init__(self, entry_id: str, secret_text: str, question_for_secret: str, **kwargs):
        self.item_id = entry_id
        self.secret_text = secret_text
        self.question_for_secret = question_for_secret
        # Store any extra fields
        self.extra = kwargs


class DataLoader:
    """Loads and caches JSONL data on startup."""
    
    def __init__(self):
        self.zh_items: List[DataItem] = []
        self.en_items: List[DataItem] = []
        self._load_data()
    
    def _load_jsonl(self, file_path: Path) -> List[DataItem]:
        """Load a JSONL file into a list of DataItem objects."""
        items = []
        if not file_path.exists():
            print(f"Warning: {file_path} not found!")
            return items
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    # Use entry_id if present, otherwise use line number
                    if 'entry_id' not in data:
                        data['entry_id'] = str(line_num)
                    items.append(DataItem(**data))
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num + 1}: {e}")
        
        return items
    
    def _load_data(self):
        """Load both Chinese and English JSONL files."""
        print(f"Loading Chinese data from: {settings.zh_jsonl_path}")
        self.zh_items = self._load_jsonl(settings.zh_jsonl_path)
        print(f"Loaded {len(self.zh_items)} Chinese items")
        
        print(f"Loading English data from: {settings.en_jsonl_path}")
        self.en_items = self._load_jsonl(settings.en_jsonl_path)
        print(f"Loaded {len(self.en_items)} English items")
    
    def get_items(self, language: str) -> List[DataItem]:
        """Get items for a specific language."""
        if language == "zh":
            return self.zh_items
        elif language == "en":
            return self.en_items
        else:
            raise ValueError(f"Unknown language: {language}")
    
    def get_item_by_id(self, language: str, item_id: str) -> DataItem:
        """Get a specific item by ID."""
        items = self.get_items(language)
        for item in items:
            if item.item_id == item_id:
                return item
        raise ValueError(f"Item {item_id} not found in {language} data")


# Global data loader instance
data_loader = DataLoader()

