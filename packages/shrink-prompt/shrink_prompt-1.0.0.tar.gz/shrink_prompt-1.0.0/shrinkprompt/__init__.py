"""ShrinkPrompt: Intelligent LLM prompt compression with domain-specific custom rules support.

A fast, offline compression library that reduces token costs while preserving semantic meaning.
Supports custom rules for domain-specific compression (legal, medical, technical, etc.).

Examples:
    Basic compression:
        >>> from shrinkprompt import compress, token_count
        >>> text = "Could you please help me understand this concept better?"
        >>> compressed = compress(text)
        >>> print(f"Saved {token_count(text) - token_count(compressed)} tokens")
    
    Domain-specific compression:
        >>> compressed = compress(legal_text, custom_rules_path="legal_rules.json")
        >>> compressed = compress(medical_text, custom_rules_path="medical_rules.yaml")
    
    Custom rules creation:
        >>> from shrinkprompt import create_custom_rules_template
        >>> create_custom_rules_template("my_domain_rules.json")
"""

from .core import compress, token_count, load_custom_rules, CustomRules
from .cli import main as cli_main

__version__ = "1.1.0"
__author__ = "ShrinkPrompt Contributors"
__description__ = "Intelligent LLM prompt compression with custom rules support"

# Public API
__all__ = [
    # Core compression functions
    "compress",
    "token_count", 
    
    # Custom rules system
    "load_custom_rules",
    "CustomRules",
    "create_custom_rules_template",
    
    # CLI entry point
    "cli_main",
    
    # Metadata
    "__version__",
]


def create_custom_rules_template(output_path: str, domain: str = "general") -> None:
    """Create a template custom rules file for a specific domain.
    
    Args:
        output_path: Path where the template file will be created
        domain: Domain type for pre-filled examples ("general", "legal", "medical", "technical")
    """
    import json
    from pathlib import Path
    
    # Domain-specific templates
    templates = {
        "general": {
            "abbreviations": {
                "application": "app",
                "information": "info", 
                "documentation": "docs",
                "configuration": "config",
                "environment": "env"
            },
            "replacements": {
                "as soon as possible": "ASAP",
                "for example": "e.g.",
                "that is": "i.e.",
                "and so on": "etc."
            },
            "removals": [
                "obviously",
                "clearly", 
                "of course",
                "needless to say"
            ],
            "domain_patterns": {
                r"\b(?:please )?(?:note|remember|keep in mind) that\b": "",
                r"\b(?:it is|it's) (?:important|worth noting) that\b": ""
            },
            "priority": "after_step3"
        },
        
        "legal": {
            "abbreviations": {
                "plaintiff": "π",
                "defendant": "Δ", 
                "contract": "K",
                "corporation": "corp",
                "incorporated": "inc",
                "limited liability company": "LLC",
                "versus": "v.",
                "section": "§",
                "paragraph": "¶",
                "United States": "US",
                "Supreme Court": "SCOTUS"
            },
            "replacements": {
                "Terms and Conditions": "T&C",
                "intellectual property": "IP",
                "non-disclosure agreement": "NDA",
                "standard operating procedure": "SOP",
                "reasonable person standard": "RPS"
            },
            "removals": [
                "heretofore",
                "hereinafter", 
                "aforementioned",
                "whereas"
            ],
            "domain_patterns": {
                r"\b(?:the )?party of the first part\b": "π",
                r"\b(?:the )?party of the second part\b": "Δ",
                r"\bpursuant to\b": "per",
                r"\bin accordance with\b": "per"
            },
            "priority": "after_step3"
        },
        
        "medical": {
            "abbreviations": {
                "patient": "pt",
                "history": "hx",
                "diagnosis": "dx", 
                "treatment": "tx",
                "prescription": "Rx",
                "symptoms": "sx",
                "examination": "exam",
                "laboratory": "lab",
                "blood pressure": "BP",
                "heart rate": "HR",
                "temperature": "temp",
                "milligrams": "mg",
                "milliliters": "mL"
            },
            "replacements": {
                "differential diagnosis": "DDx",
                "magnetic resonance imaging": "MRI",
                "computed tomography": "CT",
                "electrocardiogram": "ECG",
                "twice daily": "BID",
                "three times daily": "TID",
                "four times daily": "QID"
            },
            "removals": [
                "medically",
                "clinically",
                "therapeutically"
            ],
            "domain_patterns": {
                r"\bwith respect to the (?:patient|pt)\b": "re pt",
                r"\bin the context of (?:treatment|tx)\b": "during tx"
            },
            "priority": "after_step3"
        },
        
        "technical": {
            "abbreviations": {
                "application programming interface": "API",
                "software development kit": "SDK",
                "database": "DB",
                "server": "srv",
                "configuration": "config",
                "repository": "repo",
                "documentation": "docs",
                "specification": "spec",
                "architecture": "arch",
                "performance": "perf",
                "optimization": "opt"
            },
            "replacements": {
                "continuous integration": "CI",
                "continuous deployment": "CD", 
                "machine learning": "ML",
                "artificial intelligence": "AI",
                "natural language processing": "NLP",
                "user interface": "UI",
                "user experience": "UX",
                "application security": "AppSec"
            },
            "removals": [
                "basically",
                "essentially",
                "fundamentally"
            ],
            "domain_patterns": {
                r"\b(?:the )?(?:system|application) architecture\b": "sys arch",
                r"\bperformance optimization\b": "perf opt",
                r"\bdata structure\b": "data struct"
            },
            "priority": "after_step3"
        }
    }
    
    template = templates.get(domain, templates["general"])
    output_path = Path(output_path)
    
    # Add helpful comments for JSON format
    if output_path.suffix.lower() == '.json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
    else:
        # Default to JSON if no extension
        if not output_path.suffix:
            output_path = output_path.with_suffix('.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created {domain} custom rules template: {output_path}")
    print("📝 Edit the file to customize rules for your domain")
    print("🚀 Use with: compress(text, custom_rules_path='{}')".format(output_path))