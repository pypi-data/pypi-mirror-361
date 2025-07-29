"""Optimized 6-step compression pipeline for shrinkprompt."""

from .step1_normalize import normalize_and_clean
from .step2_mass_removal import mass_removal
from .step3_abbreviate_symbolize import abbreviate_and_symbolize
from .step4_smart_context import smart_context_removal
from .step5_token_optimize import token_optimization
from .step6_advanced_optimization import advanced_optimization
from .step7_synonym_optimize import synonym_optimize

# New intermediate functions for optimized pipeline
from .step6_advanced_optimization import _apply_token_efficient_replacements, _apply_compound_optimizations
from .step5_token_optimize import _apply_basic_contractions

def high_value_protection(text: str) -> str:
    """Early protection of high-value phrases before aggressive removal."""
    # Apply token-efficient replacements first to protect important phrases
    text = _apply_token_efficient_replacements(text)
    
    # Apply compound optimizations to protect multi-word concepts
    text = _apply_compound_optimizations(text)
    
    return text

def final_cleanup(text: str) -> str:
    """Final cleanup and optimization pass."""
    # Apply basic contractions
    text = _apply_basic_contractions(text)
    
    # Apply remaining token optimizations
    text = token_optimization(text)
    
    # Final advanced cleanup (without the parts moved to early protection)
    from .step6_advanced_optimization import _apply_number_optimizations, _apply_advanced_templates, _apply_context_removals
    text = _apply_number_optimizations(text)
    text = _apply_advanced_templates(text)
    text = _apply_context_removals(text)
    
    # Final spacing and artifact cleanup
    import re
    
    # Fix common artifacts from aggressive compression
    text = re.sub(r'\s*-\s*', ' ', text)  # Remove stray hyphens
    text = re.sub(r'\s*\*\s*', ' ', text)  # Remove stray asterisks
    text = re.sub(r'\bbecause\s+because\b', 'because', text)  # Remove doubled "because"
    text = re.sub(r'\breturn\s+return\b', 'return', text)  # Remove doubled "return"
    
    # Standard spacing cleanup
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s*([.!?])\s*', r'\1 ', text)
    text = re.sub(r'\s*,\s*', ', ', text)
    text = re.sub(r'^\s*[,.]', '', text)
    text = re.sub(r'\s*[,;]\s*$', '', text)
    
    # Fix question mark spacing and formatting
    text = re.sub(r'\s*\?\s*', '?', text)
    text = re.sub(r'([.!?])\s*$', r'\1', text)  # Remove trailing space after final punctuation
    
    return text.strip()

__all__ = [
    "normalize_and_clean",
    "high_value_protection",
    "abbreviate_and_symbolize", 
    "smart_context_removal",
    "mass_removal",
    "final_cleanup",
    # Legacy exports for backward compatibility
    "token_optimization",
    "advanced_optimization"
]

# OPTIMIZED 6-step compression pipeline with improved order
# 
# Rationale for new order:
# 1. Normalize first (always required)
# 2. Protect high-value phrases EARLY before removal steps can break them
# 3. Apply abbreviations while source phrases are still intact
# 4. Simplify sentence structure with context awareness
# 5. Remove fluff/filler AFTER important concepts are protected
# 6. Final cleanup and optimization pass
#
COMPRESSION_STAGES = (
    # Step 1: Basic normalization and cleanup (unchanged)
    normalize_and_clean,
    
    # Step 2: HIGH-VALUE PROTECTION - Protect important phrases before removal
    # Convert "application programming interface" → "API" before mass removal
    # can break up the source phrase
    high_value_protection,
    
    # Step 3: Abbreviations, symbols, and acronyms (moved up from position 3)
    # Apply while text structure is still intact
    abbreviate_and_symbolize,
    
    # Step 4: Smart context-aware removals (stays in middle)
    # Simplify sentence structure while phrases are condensed but text is readable
    smart_context_removal,
    
    # Step 5: Mass removal (moved down from position 2)
    # Now safe to aggressively remove fluff since important concepts are protected
    mass_removal,
    
    # New Step 7: Synonym optimization for token savings
    synonym_optimize,
    
    # Step 6: Final cleanup and optimization
    # Handle artifacts, apply final optimizations, clean spacing
    final_cleanup
) 