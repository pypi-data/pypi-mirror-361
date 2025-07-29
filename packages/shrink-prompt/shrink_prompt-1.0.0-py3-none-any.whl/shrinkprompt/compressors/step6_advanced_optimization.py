"""Step 6: Advanced Optimization - Token-aware and domain-specific compression."""

import re
import tiktoken
from functools import lru_cache
from typing import Dict, List, Tuple, Set


# Cache the encoder for performance
_enc = tiktoken.encoding_for_model("gpt-4o-mini")

@lru_cache(maxsize=2048)
def _token_count(text: str) -> int:
    """Count tokens efficiently with caching."""
    return len(_enc.encode(text))


# Token-efficient phrase replacements (measured for actual token savings)
_TOKEN_EFFICIENT_PHRASES = {
    # High-value replacements (3+ tokens → 1 token)
    "as soon as possible": "ASAP",  # 5→1 tokens
    "frequently asked questions": "FAQ",  # 4→1 tokens  
    "return on investment": "ROI",  # 4→1 tokens
    "artificial intelligence": "AI",  # 3→1 tokens
    "machine learning": "ML",  # 3→1 tokens
    "user interface": "UI",  # 3→1 tokens
    "step by step": "step-by-step",  # 4→3 tokens
    "end to end": "end-to-end",  # 4→3 tokens
    
    # Math and calculation terms
    "calculate the": "calc",  # 3→1 tokens
    "determine the": "find",  # 3→1 tokens
    "what is the total": "total?",  # 5→2 tokens
    "what is the answer": "answer?",  # 5→2 tokens
    "solve this step by step": "solve:",  # 6→2 tokens
    "give the final answer": "answer:",  # 5→2 tokens
    "show your work": "show work:",  # 4→3 tokens
    "find the value of": "find:",  # 5→2 tokens
    
    # Question patterns
    "how many": "qty",  # 3→1 tokens
    "how much": "amt",  # 3→1 tokens
    "what is": "what's",  # 3→2 tokens
    "where is": "where's",  # 3→2 tokens
    "when is": "when's",  # 3→2 tokens
    "why is": "why's",  # 3→2 tokens
    "who is": "who's",  # 3→2 tokens
    
    # Technical efficiency
    "in order to": "to",  # 4→1 tokens
    "due to the fact that": "because",  # 6→1 tokens
    "for the purpose of": "to",  # 5→1 tokens
    "with regard to": "about",  # 4→1 tokens
    "in spite of": "despite",  # 4→1 tokens
    "as a result of": "from",  # 5→1 tokens
    "on the other hand": "however",  # 5→1 tokens
    "at the same time": "meanwhile",  # 5→1 tokens
    "in the middle of": "during",  # 5→1 tokens
    "in the process of": "while",  # 5→1 tokens
    "take into account": "consider",  # 4→1 tokens
    "make sure that": "ensure",  # 4→1 tokens
    "keep in mind": "remember",  # 4→1 tokens
    "bear in mind": "remember",  # 4→1 tokens
}

# Number word to digit conversion (high token efficiency)
_NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
    "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
    "eighteen": "18", "nineteen": "19", "twenty": "20", "thirty": "30",
    "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70",
    "eighty": "80", "ninety": "90", "hundred": "100", "thousand": "1K",
    "million": "1M", "billion": "1B", "trillion": "1T"
}

# Mathematical expression optimizations
_MATH_EXPRESSIONS = {
    r"\b(\d+)\s+plus\s+(\d+)\b": r"\1+\2",
    r"\b(\d+)\s+minus\s+(\d+)\b": r"\1-\2", 
    r"\b(\d+)\s+times\s+(\d+)\b": r"\1×\2",
    r"\b(\d+)\s+divided by\s+(\d+)\b": r"\1÷\2",
    r"\b(\d+)\s+percent\b": r"\1%",
    r"\b(\d+)\s+dollars?\b": r"$\1",
    r"\b(\d+)\s+cents?\b": r"\1¢",
    r"\bequals?\s+(\d+)\b": r"=\1",
    r"\bis equal to\s+(\d+)\b": r"=\1",
    r"\bmore than\s+(\d+)\b": r">\1",
    r"\bless than\s+(\d+)\b": r"<\1",
    r"\bgreater than\s+(\d+)\b": r">\1",
    r"\bfewer than\s+(\d+)\b": r"<\1",
}

# Advanced template patterns for aggressive compression
_ADVANCED_TEMPLATES = {
    # Remove verbose question starters
    r"^(?:Can you |Could you |Would you |Will you )?(?:please )?(?:help me )?(?:to )?(.+?)(?:\?|$)": r"\1?",
    
    # Remove instruction padding
    r"^(?:I need you to |I want you to |I'd like you to |Please )?(.+?)(?:\.|!|$)": r"\1",
    
    # Math problem intro removal
    r"^(?:Here's a|This is a|Consider this|Look at this|Solve this) (?:math )?(?:problem|question|scenario|exercise):\s*": "",
    
    # Context setup removal
    r"^(?:Let's say|Imagine|Suppose|Assume|Consider) (?:that )?": "",
    
    # Solve instruction consolidation
    r"(?:Solve this|Work through this|Calculate this|Figure out this|Determine this)(?:\s+(?:step by step|carefully|completely))?": "Solve:",
    
    # Answer request consolidation
    r"(?:Give me|Show me|Tell me|Provide) (?:the )?(?:final )?(?:numerical )?answer": "Answer:",
    
    # Explanation request removal
    r"(?:and )?(?:please )?(?:explain|show) (?:your work|your steps|how you got this|the process)": "",
}

# Context-dependent word removal patterns
_CONTEXT_DEPENDENT_REMOVALS = {
    # Remove articles before common technical terms
    r"\bthe\s+(algorithm|method|approach|solution|result|answer|value|number|total|sum|difference|product|quotient)\b": r"\1",
    
    # Remove redundant prepositions in math contexts
    r"\bof the\s+(total|sum|difference|product|quotient|result|answer)\b": r"\1",
    
    # Remove filler in question contexts
    r"\b(?:exactly |precisely |specifically )?what is\b": "what's",
    r"\b(?:exactly |precisely |specifically )?how much is\b": "how much",
    r"\b(?:exactly |precisely |specifically )?how many are\b": "how many",
}

# Special qualifier removal patterns (handled separately)
_QUALIFIER_REMOVALS = [
    r"\b(?:total |final |complete |entire |whole |full )(sum|total|amount|value|number|answer)\b",
]

# High-value compound optimizations  
_COMPOUND_OPTIMIZATIONS = {
    "pros and cons": "pros/cons",
    "advantages and disadvantages": "pros/cons", 
    "strengths and weaknesses": "strengths/weaknesses",
    "benefits and drawbacks": "pros/cons",
    "costs and benefits": "costs/benefits",
    "risks and rewards": "risks/rewards",
    "supply and demand": "supply/demand",
    "cause and effect": "cause/effect",
    "trial and error": "trial/error",
    "give and take": "give/take",
    "back and forth": "back/forth",
    "up and down": "up/down",
    "in and out": "in/out",
    "on and off": "on/off",
    "here and there": "here/there",
    "now and then": "now/then",
    "sooner or later": "eventually",
    "more or less": "roughly",
    "all or nothing": "binary",
    "yes or no": "binary",
}


def _apply_token_efficient_replacements(text: str) -> str:
    """Apply replacements that are proven to save tokens."""
    for phrase, replacement in _TOKEN_EFFICIENT_PHRASES.items():
        # Only apply if it actually saves tokens
        original_tokens = _token_count(phrase)
        replacement_tokens = _token_count(replacement)
        
        if replacement_tokens < original_tokens:
            pattern = rf'\b{re.escape(phrase)}\b'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def _apply_number_optimizations(text: str) -> str:
    """Convert number words to digits for token efficiency."""
    # Apply number word conversions
    for word, digit in _NUMBER_WORDS.items():
        pattern = rf'\b{re.escape(word)}\b'
        text = re.sub(pattern, digit, text, flags=re.IGNORECASE)
    
    # Apply mathematical expressions
    for pattern, replacement in _MATH_EXPRESSIONS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def _apply_advanced_templates(text: str) -> str:
    """Apply aggressive template pattern removal."""
    for pattern, replacement in _ADVANCED_TEMPLATES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def _apply_context_removals(text: str) -> str:
    """Apply context-dependent removals."""
    # Apply standard context removals
    for pattern, replacement in _CONTEXT_DEPENDENT_REMOVALS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Apply qualifier removals (extract the main word)
    for pattern in _QUALIFIER_REMOVALS:
        def replacement_func(match):
            return match.group(1)  # Return just the main word without qualifiers
        text = re.sub(pattern, replacement_func, text, flags=re.IGNORECASE)
    
    return text


def _apply_compound_optimizations(text: str) -> str:
    """Apply compound phrase optimizations."""
    for compound, optimized in _COMPOUND_OPTIMIZATIONS.items():
        pattern = rf'\b{re.escape(compound)}\b'
        text = re.sub(pattern, optimized, text, flags=re.IGNORECASE)
    
    return text


def advanced_optimization(text: str) -> str:
    """Step 6: Apply advanced token-aware and domain-specific optimizations.
    
    Args:
        text: Input text to process
        
    Returns:
        Text with advanced optimizations applied
    """
    # Apply token-efficient replacements first (highest impact)
    text = _apply_token_efficient_replacements(text)
    
    # Apply number optimizations (high impact for math)
    text = _apply_number_optimizations(text)
    
    # Apply advanced template removal
    text = _apply_advanced_templates(text)
    
    # Apply compound optimizations
    text = _apply_compound_optimizations(text)
    
    # Apply context-dependent removals
    text = _apply_context_removals(text)
    
    # Advanced cleanup
    text = re.sub(r'\s+', ' ', text)  # Normalize spaces
    text = re.sub(r'\s*([.!?])\s*', r'\1 ', text)  # Fix punctuation spacing
    text = re.sub(r'\s*,\s*', ', ', text)  # Fix comma spacing
    text = re.sub(r'^\s*[,.]', '', text)  # Remove leading punctuation
    text = re.sub(r'\s*[,;]\s*$', '', text)  # Remove trailing punctuation
    
    return text.strip() 