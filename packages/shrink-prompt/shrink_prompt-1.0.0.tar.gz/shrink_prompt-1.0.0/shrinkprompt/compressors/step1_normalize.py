"""Step 1: Normalize & Clean - Comprehensive text normalization and cleanup."""

import re
import unicodedata


# Common typos and misspellings to fix during normalization
_COMMON_TYPOS = {
    "teh": "the",
    "adn": "and", 
    "nad": "and",
    "recieve": "receive",
    "definately": "definitely",
    "seperate": "separate",
    "occured": "occurred",
    "necesary": "necessary",
    "recomend": "recommend",
    "accomodate": "accommodate",
    "enviroment": "environment",
    "existance": "existence",
    "knowlege": "knowledge",
    "maintenence": "maintenance",
    "occassion": "occasion",
    "wierd": "weird",
    "thier": "their",
    "youre": "you're",
    "its'": "its",
    "wont": "won't",
    "dont": "don't",
    "cant": "can't",
    "isnt": "isn't",
    "wasnt": "wasn't",
    "werent": "weren't",
    "shouldnt": "shouldn't",
    "wouldnt": "wouldn't",
    "couldnt": "couldn't"
}

# Format standardizations
_FORMAT_PATTERNS = {
    # Standardize contractions
    r"\bi'm\b": "I'm",
    r"\byou're\b": "you're", 
    r"\bhe's\b": "he's",
    r"\bshe's\b": "she's",
    r"\bit's\b": "it's",
    r"\bwe're\b": "we're",
    r"\bthey're\b": "they're",
    r"\bwon't\b": "won't",
    r"\bcan't\b": "can't",
    r"\bdon't\b": "don't",
    
    # Fix common spacing issues
    r"\s*'\s*": "'",
    r"\s*`\s*": "'",
    r"'\s+": "'",
    r"\s+'": "'",
    
    # Standardize quotation marks
    r"[\u201c\u201d]": '"',  # Left and right double quotes
    r"[\u2018\u2019]": "'",  # Left and right single quotes
    
    # Fix number formatting
    r"(\d)\s*,\s*(\d{3})": r"\1,\2",  # Fix number commas
    r"(\d)\s*\.\s*(\d)": r"\1.\2",    # Fix decimals
    r"\$\s*(\d)": r"$\1",             # Fix currency spacing
    r"(\d)\s*%": r"\1%",              # Fix percentage spacing
    
    # Standardize time expressions
    r"(\d{1,2})\s*:\s*(\d{2})\s*(am|pm|AM|PM)": r"\1:\2\3",
    r"(\d{1,2})\s*(am|pm|AM|PM)": r"\1\2",
    
    # Fix common punctuation issues
    r"\s*;\s*": "; ",
    r"\s*:\s*": ": ",
    r"\s*\?\s*": "? ",
    r"\s*!\s*": "! ",
    r"\(\s*": "(",
    r"\s*\)": ")",
    r"\[\s*": "[",
    r"\s*\]": "]",
    r"\{\s*": "{",
    r"\s*\}": "}",
    
    # Remove redundant spacing around slashes
    r"\s*/\s*": "/",
    r"\s*\\\s*": r"\\",
    
    # Fix email and URL spacing
    r"(\w)\s*@\s*(\w)": r"\1@\2",
    r"(https?)\s*:\s*//": r"\1://",
    r"www\s*\.": "www.",
    r"\.com\s*": ".com",
    r"\.org\s*": ".org",
    r"\.net\s*": ".net",
}

# Advanced cleanup patterns
_CLEANUP_PATTERNS = {
    # Remove excessive punctuation
    r"[.]{3,}": "...",
    r"[!]{2,}": "!",
    r"[?]{2,}": "?",
    r"[,]{2,}": ",",
    r"[;]{2,}": ";",
    r"[:]{2,}": ":",
    
    # Fix spacing around punctuation marks
    r"\s*([,.!?;:])\s*": r"\1 ",
    r"([.!?])\s+([A-Z])": r"\1 \2",
    r"\s+([,.!?;:])": r"\1",
    
    # Clean up brackets and parentheses
    r"\s*\(\s*": " (",
    r"\s*\)\s*": ") ",
    r"\(\s+": "(",
    r"\s+\)": ")",
    
    # Remove extra whitespace
    r"\s{2,}": " ",
    r"\n\s*\n": "\n",
    r"\t+": " ",
    
    # Fix quote spacing
    r'"\s+': '"',
    r'\s+"': '"',
    r"'\s+": "'",
    r"\s+'": "'",
    
    # Remove trailing punctuation on empty lines
    r"^\s*[,.;:]\s*$": "",
    r"^\s*[,.;:]\s*": "",
}


def normalize_and_clean(text: str) -> str:
    """Step 1: Comprehensive normalization and cleanup.
    
    Args:
        text: Input text to process
        
    Returns:
        Text with comprehensive normalization applied
    """
    # Unicode normalization (handle special characters)
    text = unicodedata.normalize('NFKC', text)
    
    # Fix common typos and misspellings
    for typo, correction in _COMMON_TYPOS.items():
        pattern = rf'\b{re.escape(typo)}\b'
        text = re.sub(pattern, correction, text, flags=re.IGNORECASE)
    
    # Apply format standardizations
    for pattern, replacement in _FORMAT_PATTERNS.items():
        # Use IGNORECASE for patterns that need it
        if any(c in pattern for c in r"\bi'm\b \byou're\b \bhe's\b \bshe's\b \bit's\b \bwe're\b \bthey're\b \bwon't\b \bcan't\b \bdon't\b".split()):
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        else:
            text = re.sub(pattern, replacement, text)
    
    # Apply advanced cleanup patterns
    for pattern, replacement in _CLEANUP_PATTERNS.items():
        text = re.sub(pattern, replacement, text)
    
    # Additional specialized cleanups
    
    # Fix multiple spaces and normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Clean up line breaks
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Remove leading/trailing whitespace from each line
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)
    
    # Final whitespace cleanup
    text = text.strip()
    
    # Ensure proper sentence spacing
    text = re.sub(r'([.!?])\s+([A-Z])', r'\1 \2', text)
    
    # Remove any remaining problematic patterns
    text = re.sub(r'^\s*[,;.]\s*', '', text)  # Remove leading punctuation
    text = re.sub(r'\s*[,;]\s*$', '', text)   # Remove trailing punctuation
    
    return text 