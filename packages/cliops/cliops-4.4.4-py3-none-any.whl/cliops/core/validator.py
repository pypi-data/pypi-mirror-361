import re
from typing import Optional, List, Tuple
from difflib import get_close_matches

class InputValidator:
    """Input validation and sanitization for CliOps"""
    
    # Prompt constraints
    MIN_PROMPT_LENGTH = 5
    MAX_PROMPT_LENGTH = 5000
    
    # Dangerous characters to filter
    DANGEROUS_CHARS = ['<script', '<?php', '${', '`', ';rm ', ';del ']
    
    @staticmethod
    def validate_prompt(prompt: str) -> Tuple[bool, Optional[str]]:
        """Validate prompt input with length and content checks"""
        if not prompt or not prompt.strip():
            return False, "Prompt cannot be empty"
        
        prompt = prompt.strip()
        
        # Length validation
        if len(prompt) < InputValidator.MIN_PROMPT_LENGTH:
            return False, f"Prompt too short (minimum {InputValidator.MIN_PROMPT_LENGTH} characters)"
        
        if len(prompt) > InputValidator.MAX_PROMPT_LENGTH:
            return False, f"Prompt too long (maximum {InputValidator.MAX_PROMPT_LENGTH} characters)"
        
        # Content validation
        for dangerous in InputValidator.DANGEROUS_CHARS:
            if dangerous.lower() in prompt.lower():
                return False, f"Prompt contains potentially dangerous content: {dangerous}"
        
        return True, None
    
    @staticmethod
    def sanitize_prompt(prompt: str) -> str:
        """Sanitize prompt by removing dangerous patterns"""
        if not prompt:
            return ""
        
        # Remove null bytes and control characters
        prompt = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', prompt)
        
        # Normalize whitespace
        prompt = re.sub(r'\s+', ' ', prompt).strip()
        
        return prompt
    
    @staticmethod
    def validate_file_path(path: str) -> Tuple[bool, Optional[str]]:
        """Validate file paths to prevent directory traversal"""
        if not path:
            return False, "Path cannot be empty"
        
        # Check for directory traversal attempts
        if '..' in path or path.startswith('/') or ':' in path[1:3]:
            return False, "Invalid path: directory traversal detected"
        
        return True, None

class AutoCorrector:
    """Auto-correction for typos in commands and patterns"""
    
    COMMANDS = ['optimize', 'opt', 'analyze', 'an', 'patterns', 'ls', 'state', 'init']
    PATTERNS = ['adaptive_generation', 'precision_engineering', 'context_aware_generation']
    
    @staticmethod
    def correct_command(command: str) -> Optional[str]:
        """Auto-correct command typos using fuzzy matching"""
        if not command:
            return None
        
        matches = get_close_matches(command.lower(), AutoCorrector.COMMANDS, n=1, cutoff=0.6)
        return matches[0] if matches else None
    
    @staticmethod
    def correct_pattern(pattern: str) -> Optional[str]:
        """Auto-correct pattern name typos"""
        if not pattern:
            return None
        
        matches = get_close_matches(pattern.lower(), AutoCorrector.PATTERNS, n=1, cutoff=0.4)
        return matches[0] if matches else None
    
    @staticmethod
    def suggest_corrections(text: str, candidates: List[str], max_suggestions: int = 3) -> List[str]:
        """Get multiple correction suggestions"""
        if not text or not candidates:
            return []
        
        return get_close_matches(text.lower(), candidates, n=max_suggestions, cutoff=0.4)