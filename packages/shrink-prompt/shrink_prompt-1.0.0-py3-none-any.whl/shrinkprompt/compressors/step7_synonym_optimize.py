import json
import re
from pathlib import Path
import tiktoken
from typing import Dict, List

_enc = tiktoken.get_encoding("cl100k_base")

class SynonymOptimizer:
    def __init__(self):
        data_path = Path(__file__).parent / 'data' / 'synonym_graph.json'
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        self.synonym_map: Dict[str, List[str]] = {}
        for pos in ['n', 'v', 'adj', 'adv']:
            if pos in data:
                for word, synonyms in data[pos].items():
                    lower_word = word.lower()
                    if lower_word not in self.synonym_map:
                        self.synonym_map[lower_word] = []
                    # Filter to single-word synonyms only
                    self.synonym_map[lower_word].extend([s.lower() for s in synonyms if s.lower() != lower_word and ' ' not in s])
        
        # Deduplicate and sort synonyms by token length
        for word in self.synonym_map:
            unique_syns = list(set(self.synonym_map[word]))
            unique_syns.sort(key=lambda s: len(_enc.encode(s)))
            self.synonym_map[word] = unique_syns

    def compress(self, text: str) -> str:
        def replace_match(m):
            word = m.group(0)
            lower = word.lower()
            if lower in self.synonym_map:
                candidates = self.synonym_map[lower]
                if not candidates:
                    return word
                # Find the synonym with smallest token count
                best = min(candidates, key=lambda s: len(_enc.encode(s)))
                orig_tokens = len(_enc.encode(word))
                repl_tokens = len(_enc.encode(best))
                if repl_tokens < orig_tokens:
                    # Preserve case
                    if word.isupper():
                        return best.upper()
                    elif word.istitle():
                        return best.capitalize()
                    elif word.islower():
                        return best
                    else:
                        return best
            return word

        # Replace words, preserving punctuation around them
        text = re.sub(r'\b\w+\b', replace_match, text)
        return text

def synonym_optimize(text: str) -> str:
    return SynonymOptimizer().compress(text) 