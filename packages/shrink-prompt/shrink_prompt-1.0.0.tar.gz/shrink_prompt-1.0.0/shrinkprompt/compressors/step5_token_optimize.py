"""Step 5: Token Optimization - Basic token-aware optimizations and cleanup."""

import re
import tiktoken
from functools import lru_cache
from typing import Dict, List, Tuple


# Cache the encoder for performance
_enc = tiktoken.encoding_for_model("gpt-4o-mini")

@lru_cache(maxsize=1024)
def _token_count(text: str) -> int:
    """Count tokens (cached for performance)."""
    return len(_enc.encode(text))


# Basic contractions only
_BASIC_CONTRACTIONS = {
    ("do", "not"): ("don't", 2, 1),
    ("can", "not"): ("can't", 2, 1),
    ("will", "not"): ("won't", 2, 1),
    ("would", "not"): ("wouldn't", 2, 1),
    ("should", "not"): ("shouldn't", 2, 1),
    ("could", "not"): ("couldn't", 2, 1),
    ("is", "not"): ("isn't", 2, 1),
    ("are", "not"): ("aren't", 2, 1),
    ("was", "not"): ("wasn't", 2, 1),
    ("were", "not"): ("weren't", 2, 1),
    ("have", "not"): ("haven't", 2, 1),
    ("has", "not"): ("hasn't", 2, 1),
    ("had", "not"): ("hadn't", 2, 1),
    ("I", "am"): ("I'm", 2, 1),
    ("you", "are"): ("you're", 2, 1),
    ("he", "is"): ("he's", 2, 1),
    ("she", "is"): ("she's", 2, 1),
    ("it", "is"): ("it's", 2, 1),
    ("we", "are"): ("we're", 2, 1),
    ("they", "are"): ("they're", 2, 1),
    ("I", "will"): ("I'll", 2, 1),
    ("you", "will"): ("you'll", 2, 1),
    ("he", "will"): ("he'll", 2, 1),
    ("she", "will"): ("she'll", 2, 1),
    ("we", "will"): ("we'll", 2, 1),
    ("they", "will"): ("they'll", 2, 1),
}

# Basic safe word replacements
_SAFE_WORD_REPLACEMENTS = {
    "implementation": "impl",
    "configuration": "config",
    "documentation": "docs",
    "specification": "spec",
    "recommendation": "rec",
    "demonstration": "demo",
    "evaluation": "eval",
    "development": "dev",
    "modification": "change",
    "optimization": "tuning",
    "authorization": "auth",
    "authentication": "auth",
}

# Basic cleanup patterns only
_BASIC_CLEANUP = {
    r'\s{2,}': ' ',  # Multiple spaces to single space
    r'\s*,\s*': ', ',  # Fix comma spacing
    r'\s*\.\s*': '. ',  # Fix period spacing  
    r'\s*\?\s*': '? ',  # Fix question mark spacing
    r'\s*!\s*': '! ',  # Fix exclamation spacing
}


def _apply_basic_contractions(text: str) -> str:
    """Apply basic contractions."""
    words = text.split()
    result = []
    i = 0
    
    while i < len(words):
        matched = False
        
        # Try to match 2-word contractions
        if i + 1 < len(words):
            pattern = (words[i].lower(), words[i + 1].lower())
            if pattern in _BASIC_CONTRACTIONS:
                replacement, _, _ = _BASIC_CONTRACTIONS[pattern]
                result.append(replacement)
                i += 2
                matched = True
        
        if not matched:
            result.append(words[i])
            i += 1
    
    return ' '.join(result)


def token_optimization(text: str) -> str:
    """Step 5: Apply basic token optimizations and cleanup.
    
    Args:
        text: Input text to process
        
    Returns:
        Text with basic token optimizations applied
    """
    # Apply basic contractions
    text = _apply_basic_contractions(text)
    
    # Apply safe word replacements
    for word, replacement in _SAFE_WORD_REPLACEMENTS.items():
        pattern = rf'\b{re.escape(word)}\b'
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Apply basic cleanup
    for pattern, replacement in _BASIC_CLEANUP.items():
        text = re.sub(pattern, replacement, text)
    
    # Basic normalization
    text = text.strip()
    
    return text 