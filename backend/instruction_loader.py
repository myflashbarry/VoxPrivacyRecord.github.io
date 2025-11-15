"""Load instruction TXT files and assign them to users."""
import random
from pathlib import Path
from typing import List, Dict
from config import settings


class InstructionLoader:
    """Loads and manages instruction txt files."""
    
    def __init__(self):
        self.instructions: Dict[str, List[str]] = {}
        self._load_instructions()
        # Store user assignments (username -> {file_type: [indices]})
        self.user_assignments: Dict[str, Dict[str, List[int]]] = {}
    
    def _load_txt_file(self, file_path: Path) -> List[str]:
        """Load lines from a txt file."""
        if not file_path.exists():
            print(f"Warning: {file_path} not found!")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        return lines
    
    def _load_instructions(self):
        """Load all instruction files."""
        self.instructions['zh_nobody'] = self._load_txt_file(settings.zh_nobody_txt)
        self.instructions['zh_onlyme'] = self._load_txt_file(settings.zh_onlyme_txt)
        self.instructions['en_nobody'] = self._load_txt_file(settings.en_nobody_txt)
        self.instructions['en_onlyme'] = self._load_txt_file(settings.en_onlyme_txt)
        
        print(f"Loaded instructions: zh_nobody={len(self.instructions['zh_nobody'])}, "
              f"zh_onlyme={len(self.instructions['zh_onlyme'])}, "
              f"en_nobody={len(self.instructions['en_nobody'])}, "
              f"en_onlyme={len(self.instructions['en_onlyme'])}")
    
    def get_user_instructions(self, username: str, inst_type: str, count: int = 5) -> List[tuple]:
        """
        Get assigned instructions for a user.
        Returns list of (index, text) tuples.
        
        inst_type: 'zh_nobody', 'zh_onlyme', 'en_nobody', 'en_onlyme'
        """
        # Initialize user assignments if not exists
        if username not in self.user_assignments:
            self.user_assignments[username] = {}
        
        # If this user doesn't have assignments for this type, create them
        if inst_type not in self.user_assignments[username]:
            available_instructions = self.instructions.get(inst_type, [])
            if len(available_instructions) < count:
                print(f"Warning: Not enough instructions in {inst_type}")
                count = len(available_instructions)
            
            # Randomly sample indices (fixed for this user)
            all_indices = list(range(len(available_instructions)))
            random.seed(hash(username + inst_type))  # Deterministic for same user+type
            selected_indices = random.sample(all_indices, count)
            self.user_assignments[username][inst_type] = selected_indices
        
        # Get the assigned instructions
        indices = self.user_assignments[username][inst_type]
        texts = self.instructions.get(inst_type, [])
        
        return [(idx, texts[idx]) for idx in indices if idx < len(texts)]


# Global instruction loader instance
instruction_loader = InstructionLoader()

