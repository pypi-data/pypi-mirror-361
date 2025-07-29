"""Core compression pipeline — zero external calls, sub‑20 ms latency."""
import tiktoken
import json
import re
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Optional, Union, Any
from .compressors import COMPRESSION_STAGES

# ───────────────────────────────────────── Constants
_enc = tiktoken.encoding_for_model("gpt-4o-mini")  # change if needed

# ───────────────────────────────────────── Custom Rules System

class CustomRules:
    """Container for custom compression rules loaded from external files."""
    
    def __init__(self, rules_data: Dict[str, Any]):
        self.abbreviations = rules_data.get('abbreviations', {})
        self.replacements = rules_data.get('replacements', {})
        self.removals = rules_data.get('removals', [])
        self.protected_terms = rules_data.get('protected_terms', [])
        self.domain_patterns = rules_data.get('domain_patterns', {})
        self.priority = rules_data.get('priority', 'after_step3')  # When to apply: before_step1, after_step3, after_step6
        
    def apply_abbreviations(self, text: str) -> str:
        """Apply domain-specific abbreviations."""
        for long_form, short_form in self.abbreviations.items():
            # Use word boundaries and case-insensitive matching
            pattern = rf'\b{re.escape(long_form)}\b'
            text = re.sub(pattern, short_form, text, flags=re.IGNORECASE)
        return text
    
    def apply_replacements(self, text: str) -> str:
        """Apply domain-specific replacements."""
        for old_phrase, new_phrase in self.replacements.items():
            pattern = rf'\b{re.escape(old_phrase)}\b'
            text = re.sub(pattern, new_phrase, text, flags=re.IGNORECASE)
        return text
    
    def apply_removals(self, text: str) -> str:
        """Remove domain-specific filler words."""
        for removal in self.removals:
            pattern = rf'\b{re.escape(removal)}\b'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text
    
    def apply_domain_patterns(self, text: str) -> str:
        """Apply complex domain-specific regex patterns."""
        for pattern, replacement in self.domain_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text
    
    def apply_all(self, text: str) -> str:
        """Apply all custom rules in optimal order."""
        # Apply removals first
        text = self.apply_removals(text)
        
        # Apply domain patterns
        text = self.apply_domain_patterns(text)
        
        # Apply replacements
        text = self.apply_replacements(text)
        
        # Apply abbreviations last (to protect abbreviated forms)
        text = self.apply_abbreviations(text)
        
        # Clean up spacing
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

def load_custom_rules(custom_rules_path: Optional[str]) -> Optional[CustomRules]:
    """Load custom compression rules from JSON or YAML file.
    
    Args:
        custom_rules_path: Path to JSON/YAML file containing custom rules
        
    Returns:
        CustomRules object or None if no rules file provided
    """
    if not custom_rules_path:
        return None
    
    rules_path = Path(custom_rules_path)
    if not rules_path.exists():
        raise FileNotFoundError(f"Custom rules file not found: {custom_rules_path}")
    
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            if rules_path.suffix.lower() in ['.yaml', '.yml']:
                try:
                    import yaml
                    rules_data = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML is required for YAML rule files. Install with: pip install PyYAML")
            else:
                rules_data = json.load(f)
        
        return CustomRules(rules_data)
    
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        raise ValueError(f"Invalid format in custom rules file {custom_rules_path}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error loading custom rules from {custom_rules_path}: {e}")

def apply_custom_rules_to_pipeline(text: str, custom_rules: Optional[CustomRules], stage: str) -> str:
    """Apply custom rules at the appropriate pipeline stage.
    
    Args:
        text: Text to process
        custom_rules: Custom rules to apply
        stage: Current pipeline stage ('before_step1', 'after_step3', 'after_step6')
        
    Returns:
        Text with custom rules applied (if applicable)
    """
    if not custom_rules or custom_rules.priority != stage:
        return text
    
    return custom_rules.apply_all(text)

# ───────────────────────────────────────── Public API

def compress(prompt: str, custom_rules_path: Optional[str] = None) -> str:
    """Return a compressed version of *prompt* after running all stages.
    
    Args:
        prompt: Input text to compress
        custom_rules_path: Optional path to JSON/YAML file with domain-specific rules
        
    Returns:
        Compressed text with reduced token count
    """
    # Load custom rules if provided
    custom_rules = load_custom_rules(custom_rules_path)
    
    text = prompt
    
    # Apply custom rules before pipeline if specified
    text = apply_custom_rules_to_pipeline(text, custom_rules, 'before_step1')
    
    # Apply compression stages
    for i, stage in enumerate(COMPRESSION_STAGES):
        text = stage(text)
        if not text.strip():  # Safety check
            return prompt  # Return original if we accidentally destroyed everything
        
        # Apply custom rules after step 3 (default position - after abbreviation/symbolization)
        if i == 2:  # After step 3 (abbreviate_and_symbolize)
            text = apply_custom_rules_to_pipeline(text, custom_rules, 'after_step3')
    
    # Apply custom rules after all stages if specified
    text = apply_custom_rules_to_pipeline(text, custom_rules, 'after_step6')
    
    # Safeguard: Revert if no token savings
    if token_count(text) >= token_count(prompt):
        return prompt
    
    return text

@lru_cache(maxsize=4096)
def token_count(text: str) -> int:
    """Count tokens using the model's native BPE encoding (cached).
    
    Args:
        text: Input text to count tokens for
        
    Returns:
        Number of tokens in the text
    """
    return len(_enc.encode(text))

# ───────────────────────────────────────── CLI utility (optional)
if __name__ == "__main__":  # python -m shrinkprompt.core "Prompt here" --rules rules.json
    import sys, json, argparse

    parser = argparse.ArgumentParser(description="Compress text using ShrinkPrompt")
    parser.add_argument("prompt", help="Text to compress")
    parser.add_argument("--rules", "--custom-rules", help="Path to custom rules JSON/YAML file")
    
    args = parser.parse_args()

    original = args.prompt
    compressed = compress(original, args.rules)
    stats = {
        "orig_tokens": token_count(original),
        "new_tokens": token_count(compressed),
        "pct_saved": round(100 * (1 - token_count(compressed) / max(1, token_count(original))), 1),
    }
    print(json.dumps({"compressed": compressed, **stats}, indent=2))