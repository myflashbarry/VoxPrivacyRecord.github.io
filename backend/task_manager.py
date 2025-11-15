"""Task assignment and management logic."""
import random
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from database import get_user_progress, get_user_recorded_items
from data_loader import data_loader, DataItem
from instruction_loader import instruction_loader
from config import settings


class TaskManager:
    """Manages task assignment based on user progress."""
    
    def get_next_task(self, db: Session, username: str) -> Optional[Dict]:
        """
        Determine the next task for a user based on their progress.
        
        Priority:
        1. zh_nobody instructions (5)
        2. zh_onlyme instructions (5)
        3. Chinese pairs (20)
        4. Chinese extra questions (10)
        5. en_nobody instructions (5)
        6. en_onlyme instructions (5)
        7. English pairs (20)
        8. English extra questions (10)
        
        Returns None if all tasks are complete.
        """
        progress = get_user_progress(db, username)
        
        # Check if all tasks complete
        if (progress["zh_nobody_done"] >= settings.zh_nobody_quota and
            progress["zh_onlyme_done"] >= settings.zh_onlyme_quota and
            progress["zh_pairs_done"] >= settings.zh_pairs_quota and
            progress["zh_extra_questions_done"] >= settings.zh_extra_quota and
            progress["en_nobody_done"] >= settings.en_nobody_quota and
            progress["en_onlyme_done"] >= settings.en_onlyme_quota and
            progress["en_pairs_done"] >= settings.en_pairs_quota and
            progress["en_extra_questions_done"] >= settings.en_extra_quota):
            return None  # All done!
        
        # Priority 1: zh_nobody instructions
        if progress["zh_nobody_done"] < settings.zh_nobody_quota:
            task = self._assign_instruction_task(db, username, "zh", "nobody", progress)
            if task:
                return task
        
        # Priority 2: zh_onlyme instructions
        if progress["zh_onlyme_done"] < settings.zh_onlyme_quota:
            task = self._assign_instruction_task(db, username, "zh", "onlyme", progress)
            if task:
                return task
        
        # Priority 3: Chinese pairs
        if progress["zh_pairs_done"] < settings.zh_pairs_quota:
            task = self._assign_pair_task(db, username, "zh", progress)
            if task:
                return task
        
        # Priority 4: Chinese extra questions
        if progress["zh_extra_questions_done"] < settings.zh_extra_quota:
            task = self._assign_extra_question_task(db, username, "zh", progress)
            if task:
                return task
        
        # Priority 5: en_nobody instructions
        if progress["en_nobody_done"] < settings.en_nobody_quota:
            task = self._assign_instruction_task(db, username, "en", "nobody", progress)
            if task:
                return task
        
        # Priority 6: en_onlyme instructions
        if progress["en_onlyme_done"] < settings.en_onlyme_quota:
            task = self._assign_instruction_task(db, username, "en", "onlyme", progress)
            if task:
                return task
        
        # Priority 7: English pairs
        if progress["en_pairs_done"] < settings.en_pairs_quota:
            task = self._assign_pair_task(db, username, "en", progress)
            if task:
                return task
        
        # Priority 8: English extra questions
        if progress["en_extra_questions_done"] < settings.en_extra_quota:
            task = self._assign_extra_question_task(db, username, "en", progress)
            if task:
                return task
        
        return None
    
    def _assign_instruction_task(self, db: Session, username: str, language: str, inst_type: str, progress: Dict) -> Optional[Dict]:
        """
        Assign an instruction task (nobody or onlyme) for the given language.
        
        inst_type: 'nobody' or 'onlyme'
        """
        # Get the set of already recorded instruction items for this type
        items_key = f"_{language}_{inst_type}_items"
        recorded_items = progress.get(items_key, set())
        
        # Get user's assigned instructions for this type
        full_inst_type = f"{language}_{inst_type}"
        instructions = instruction_loader.get_user_instructions(username, full_inst_type, count=5)
        
        # Find next instruction to record (not yet recorded)
        for idx, text in instructions:
            item_id = f"{full_inst_type}_{idx}"
            if item_id not in recorded_items:
                return {
                    "language": language,
                    "task_type": "instruction",
                    "role": inst_type,  # 'nobody' or 'onlyme'
                    "item_id": item_id,
                    "text": text
                }
        
        return None
    
    def _assign_pair_task(self, db: Session, username: str, language: str, progress: Dict) -> Optional[Dict]:
        """Assign a pair task (secret or question) for the given language."""
        pairs_dict_key = f"_{language}_pairs_dict"
        pairs_dict = progress.get(pairs_dict_key, {})
        
        # Check if there's an incomplete pair (secret done but question not, or vice versa)
        for item_id, status in pairs_dict.items():
            if status["secret"] and not status["question"]:
                # Need to record question for this item
                item = data_loader.get_item_by_id(language, item_id)
                return {
                    "language": language,
                    "task_type": "pair",
                    "role": "question",
                    "item_id": item_id,
                    "text": item.question_for_secret
                }
            elif not status["secret"] and status["question"]:
                # Need to record secret for this item (unusual but possible)
                item = data_loader.get_item_by_id(language, item_id)
                return {
                    "language": language,
                    "task_type": "pair",
                    "role": "secret",
                    "item_id": item_id,
                    "text": item.secret_text
                }
        
        # No incomplete pairs, start a new pair with secret_text
        all_items = data_loader.get_items(language)
        used_item_ids = set(pairs_dict.keys())
        available_items = [item for item in all_items if item.item_id not in used_item_ids]
        
        if not available_items:
            # Fallback: reuse items if we've exhausted the pool
            available_items = all_items
        
        if available_items:
            item = random.choice(available_items)
            return {
                "language": language,
                "task_type": "pair",
                "role": "secret",
                "item_id": item.item_id,
                "text": item.secret_text
            }
        
        return None
    
    def _assign_extra_question_task(self, db: Session, username: str, language: str, progress: Dict) -> Optional[Dict]:
        """Assign an extra question task for the given language."""
        pairs_dict_key = f"_{language}_pairs_dict"
        extra_items_key = f"_{language}_extra_items"
        
        pairs_dict = progress.get(pairs_dict_key, {})
        extra_items = progress.get(extra_items_key, set())
        
        # Get all items
        all_items = data_loader.get_items(language)
        
        # Exclude items already used in pairs or extra questions
        used_in_pairs = set(pairs_dict.keys())
        used_in_extra = extra_items
        used_item_ids = used_in_pairs.union(used_in_extra)
        
        available_items = [item for item in all_items if item.item_id not in used_item_ids]
        
        if not available_items:
            # Fallback: allow items used in pairs, but not in extra yet
            available_items = [item for item in all_items if item.item_id not in used_in_extra]
        
        if not available_items:
            # Last resort: reuse any item
            available_items = all_items
        
        if available_items:
            item = random.choice(available_items)
            return {
                "language": language,
                "task_type": "extra_question",
                "role": "question",
                "item_id": item.item_id,
                "text": item.question_for_secret
            }
        
        return None


# Global task manager instance
task_manager = TaskManager()

