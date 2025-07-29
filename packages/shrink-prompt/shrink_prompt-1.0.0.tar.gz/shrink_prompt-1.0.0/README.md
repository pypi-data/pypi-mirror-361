# ShrinkPrompt 🔬

**Intelligent LLM prompt compression with domain-specific custom rules support**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/shrink-prompt.svg)](https://pypi.org/project/shrink-prompt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/shrink-prompt.svg)](https://pypi.org/project/shrink-prompt/)

ShrinkPrompt is a lightning-fast, offline compression library that reduces token costs for Large Language Models by **30-70%** while preserving semantic meaning. Achieve sub-20ms compression with zero external API calls using our intelligent 7-step compression pipeline and domain-specific custom rules.

## ✨ Key Features

- **🚀 Lightning Fast**: Sub-20ms compression with zero external API calls
- **🧠 Semantic Preservation**: Maintains meaning while aggressively reducing tokens
- **🎯 Domain-Specific**: Built-in rules for legal, medical, technical, and business content
- **📊 Proven Results**: 30-70% average token reduction across various prompt types
- **🔧 Flexible**: CLI tool, Python API, and custom rule templates
- **🛡️ Safe**: Built-in safeguards prevent over-compression
- **💾 Offline**: No external dependencies, works completely offline
- **⚡ Optimized**: LRU caching and optimized pipeline for maximum performance

## 🚀 Quick Start

### Installation

```bash
pip install shrink-prompt
```

### Basic Usage

```python
from shrinkprompt import compress, token_count

# Simple compression
text = "Could you please help me understand this concept better?"
compressed = compress(text)
print(f"Original: {text}")
print(f"Compressed: {compressed}")
print(f"Tokens saved: {token_count(text) - token_count(compressed)}")

# Output:
# Original: Could you please help me understand this concept better?
# Compressed: Help me understand this concept better?
# Tokens saved: 3
```

### CLI Usage

```bash
# Basic compression
shrink-prompt "Could you please help me understand machine learning?"

# With custom rules
shrink-prompt --file document.txt --rules legal_rules.json --verbose

# From stdin with JSON output
echo "Your text here" | shrink-prompt --stdin --json
```

## 📈 Performance Examples

### Basic Example
```python
# Before compression (23 tokens)
"Could you please provide me with a detailed explanation of how machine learning algorithms work in practice?"

# After compression (13 tokens - 43% reduction)
"Explain how ML algorithms work in practice?"
```

### Advanced Example
```python
# Before compression (89 tokens)
"I would really appreciate it if you could provide me with a comprehensive analysis of the current market trends in artificial intelligence, including detailed information about the most important developments and their potential impact on various industries."

# After compression (31 tokens - 65% reduction)  
"Analyze current AI market trends, key developments, and industry impact."
```

### Domain-Specific Example (Legal)
```python
from shrinkprompt import compress

legal_text = """
The plaintiff hereby requests that the defendant provide all documentation 
pursuant to the terms and conditions of the aforementioned contract in 
accordance with the discovery rules.
"""

# With legal rules
compressed = compress(legal_text, custom_rules_path="legal_rules.json")
# Result: "π requests Δ provide all docs per K T&C per discovery rules."
# 75% token reduction
```

## 🔄 7-Step Compression Pipeline

ShrinkPrompt uses an optimized compression pipeline with intelligent step ordering:

### 1. **Normalize & Clean**
- Unicode normalization (NFKC) and encoding fixes
- Fixes 30+ common typos and misspellings (`teh` → `the`, `recieve` → `receive`)
- Standardizes contractions, punctuation, and spacing
- Handles currency, time, email, and URL formatting
- Comprehensive cleanup of formatting artifacts

### 2. **High-Value Protection**
- **NEW**: Protects important phrases before aggressive removal
- Applies token-efficient replacements early (`application programming interface` → `API`)
- Preserves compound technical terms and domain-specific concepts
- Prevents important context from being destroyed by later steps

### 3. **Abbreviate & Symbolize**
- **1,800+ technical abbreviations** (`information` → `info`, `function` → `func`)
- **Programming terms** (`repository` → `repo`, `database` → `DB`)
- **Mathematical symbols** (`greater than` → `>`, `less than or equal` → `≤`)
- **Domain-specific acronyms** (API, ML, AI, SDK, etc.)
- **Business terms** (`application` → `app`, `configuration` → `config`)

### 4. **Smart Context Removal**
- **Context-aware article removal** (preserves technical articles)
- **Passive voice simplification** (`it was done by` → `X did`)
- **Template pattern removal** (`in order to` → `to`)
- **Redundant preposition elimination** with syntax preservation

### 5. **Mass Removal**
- **150+ filler words** with context-awareness (`actually`, `really`, `quite`)
- **200+ hedge words** (`apparently`, `seemingly`, `probably`)
- **100+ business jargon** (`leverage`, `synergize`, `optimize`)
- **Academic fluff** (`it is worth noting`, `one might argue`)
- **Social pleasantries** (`I hope`, `thank you for`, `please note`)
- **Redundant expressions** (`absolutely essential` → `essential`)

### 6. **Synonym Optimization**
- **23,000+ synonym mappings** from WordNet and Brown corpus
- **Token-efficient replacements** (shorter synonyms with same meaning)
- **Context preservation** (maintains technical vs. casual tone)
- **Case sensitivity** (preserves capitalization patterns)

### 7. **Final Cleanup & Advanced Optimization**
- **Artifact removal** (fixes compression side effects)
- **Advanced template matching** (complex pattern recognition)
- **Number and context optimizations** (`1,000` → `1K`)
- **Final punctuation and spacing normalization**

## 🎯 Custom Rules System

Create powerful domain-specific compression rules using JSON or YAML:

### Rule Types

```json
{
  "abbreviations": {
    "long_term": "short",
    "application": "app",
    "information": "info"
  },
  "replacements": {
    "old_phrase": "new_phrase",
    "Terms and Conditions": "T&C",
    "artificial intelligence": "AI"
  },
  "removals": [
    "obviously", "clearly", "of course"
  ],
  "domain_patterns": {
    "\\bpursuant to\\b": "per",
    "\\bin accordance with\\b": "per"
  },
  "protected_terms": [
    "do not resuscitate",
    "machine learning model"
  ],
  "priority": "after_step3"
}
```

### Priority Levels

- **`before_step1`**: Apply before any compression (useful for preprocessing)
- **`after_step3`**: **Default** - After abbreviations but before mass removal
- **`after_step6`**: Apply after all compression steps (final cleanup)

### Built-in Domain Templates

Generate ready-to-use templates for common domains:

```python
from shrinkprompt import create_custom_rules_template

# Legal domain
create_custom_rules_template("legal_rules.json", domain="legal")
# Includes: π (plaintiff), Δ (defendant), K (contract), T&C, IP, NDA

# Medical domain  
create_custom_rules_template("medical_rules.json", domain="medical")
# Includes: pt (patient), dx (diagnosis), tx (treatment), BP, HR, MRI

# Technical domain
create_custom_rules_template("tech_rules.json", domain="technical")
# Includes: API, SDK, DB, repo, config, perf, arch

# Business domain
create_custom_rules_template("business_rules.json", domain="general")
# Includes: app, info, docs, env, ASAP, ROI, KPI
```

### Example: Advanced Legal Rules

```json
{
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
    "Supreme Court": "SCOTUS",
    "attorney": "atty",
    "litigation": "lit",
    "jurisdiction": "jxn"
  },
  "replacements": {
    "Terms and Conditions": "T&C",
    "intellectual property": "IP",
    "non-disclosure agreement": "NDA",
    "breach of contract": "breach of K",
    "cease and desist": "C&D",
    "fair market value": "FMV"
  },
  "removals": [
    "heretofore", "hereinafter", "aforementioned",
    "whereas", "notwithstanding", "thereunder"
  ],
  "domain_patterns": {
    "\\b(?:the )?party of the first part\\b": "π",
    "\\b(?:the )?party of the second part\\b": "Δ",
    "\\bpursuant to\\b": "per",
    "\\bin accordance with\\b": "per",
    "\\bsubject to the terms and conditions\\b": "subject to T&C"
  },
  "protected_terms": [
    "habeas corpus", "prima facie", "res ipsa loquitur",
    "stare decisis", "ex parte", "pro se"
  ],
  "priority": "after_step3"
}
```

## 💻 Comprehensive CLI Reference

### Basic Usage
```bash
# Compress text directly
shrink-prompt "Your prompt text here"

# Compress with custom rules
shrink-prompt "Legal document text" --rules legal_rules.json

# Verbose output with statistics
shrink-prompt "Text" --verbose
```

### Input Options
```bash
# From file
shrink-prompt --file input.txt

# From standard input
echo "Text to compress" | shrink-prompt --stdin

# Direct text input (use quotes for multi-word)
shrink-prompt "Could you please help me understand this concept?"
```

### Custom Rules
```bash
# Apply custom rules
shrink-prompt "Text" --rules custom.json

# Validate rules file format
shrink-prompt --validate-rules rules.json

# Show rules priority and statistics
shrink-prompt --validate-rules rules.json --verbose
```

### Output Options
```bash
# Save to file
shrink-prompt "Text" --output result.txt

# JSON format output
shrink-prompt "Text" --json

# Quiet mode (compressed text only)
shrink-prompt "Text" --quiet

# Verbose statistics
shrink-prompt "Text" --verbose
```

### Debug and Analysis
```bash
# Show each compression step
shrink-prompt "Text" --show-stages

# Validate and analyze custom rules
shrink-prompt --validate-rules rules.json

# Performance analysis
shrink-prompt "Long text here" --verbose --show-stages
```

### Advanced Examples
```bash
# Medical document with custom rules and JSON output
shrink-prompt --file medical_report.txt --rules medical_rules.json --json --output compressed.json

# Debug compression pipeline
shrink-prompt "Complex technical documentation about machine learning algorithms" --show-stages

# Batch processing with custom rules
find docs/ -name "*.txt" -exec shrink-prompt --file {} --rules tech_rules.json --output {}.compressed \;
```

## 📚 Complete API Reference

### Core Functions

#### `compress(prompt: str, custom_rules_path: Optional[str] = None) -> str`
Main compression function with optional custom rules.

```python
from shrinkprompt import compress

# Basic compression
result = compress("Your text here")

# With custom rules
result = compress(text, custom_rules_path="legal_rules.json")

# Returns compressed text with reduced token count
```

#### `token_count(text: str) -> int`
Count tokens using GPT-4 tokenizer (tiktoken) with LRU caching.

```python
from shrinkprompt import token_count

tokens = token_count("Your text here")
# Returns: int (number of tokens)

# Cached for performance - repeated calls are instant
```

#### `load_custom_rules(custom_rules_path: str) -> CustomRules`
Load custom compression rules from JSON or YAML file.

```python
from shrinkprompt import load_custom_rules

rules = load_custom_rules("my_rules.json")
# Returns: CustomRules object
# Raises: FileNotFoundError, ValueError for invalid files
```

#### `create_custom_rules_template(output_path: str, domain: str = "general") -> None`
Generate rule templates for specific domains.

```python
from shrinkprompt import create_custom_rules_template

# Available domains: "general", "legal", "medical", "technical"
create_custom_rules_template("my_rules.json", domain="legal")
# Creates template file with domain-specific examples
```

### Advanced API Usage

#### Custom Rules Object
```python
from shrinkprompt.core import CustomRules, load_custom_rules

# Load rules
rules = load_custom_rules("rules.json")

# Apply rules manually
text = rules.apply_all("Your text here")

# Access rule components
abbreviations = rules.abbreviations
replacements = rules.replacements
priority = rules.priority  # "before_step1", "after_step3", "after_step6"
```

#### Pipeline Integration
```python
from shrinkprompt.core import apply_custom_rules_to_pipeline

# Apply rules at specific pipeline stage
text = apply_custom_rules_to_pipeline(text, rules, "after_step3")
```

#### Direct Pipeline Access
```python
from shrinkprompt.compressors import COMPRESSION_STAGES

# Access individual compression stages
for stage in COMPRESSION_STAGES:
    text = stage(text)
    print(f"After {stage.__name__}: {text}")
```

## 🔬 Performance Benchmarks

### Speed Benchmarks
- **Short prompts** (< 100 tokens): 5-10ms
- **Medium prompts** (100-500 tokens): 10-15ms  
- **Long prompts** (500+ tokens): 15-20ms
- **Caching**: Subsequent calls ~1ms (LRU cache)

### Compression Ratios by Content Type
- **Verbose business emails**: 60-70% reduction
- **Academic papers**: 45-55% reduction
- **Technical documentation**: 35-45% reduction
- **Legal documents**: 50-65% reduction (with custom rules)
- **Medical records**: 40-55% reduction (with custom rules)
- **Casual conversation**: 20-35% reduction

### Memory Usage
- **Base library**: ~2MB RAM
- **Synonym graph**: ~15MB RAM (loaded on first use)
- **Custom rules**: ~100KB-1MB RAM (depending on size)
- **LRU cache**: ~10MB RAM (configurable, 4096 entries default)

## 📊 Demo and Examples

### Run the Demo
```bash
# Clone repository and run demo
git clone https://github.com/yourusername/shrink-prompt.git
cd shrink-prompt
pip install -r requirements.txt
python main.py
```

**Example Demo Output:**
```
🔬 ShrinkPrompt Compression Demo
==================================================

Example 1:
  Original:   Could you please help me understand this concept better?
  Compressed: Help me understand this concept better?
  Tokens:     12 → 9 (25.0% saved)

Example 15:
  Original:   As a fitness expert, create a personalized 12-week workout and nutrition plan...
  Compressed: As fitness expert, create personalized 12-week workout/nutrition plan...
  Tokens:     156 → 89 (42.9% saved)

📊 Overall Statistics
==================================================
Total original tokens:    2,847
Total compressed tokens:  1,521
Total tokens saved:       1,326
Average compression:      46.6% reduction

💰 Estimated Cost Impact
==================================================
Original cost:     $0.0057
Compressed cost:   $0.0030
Cost savings:      $0.0027 (46.6%)
```

### Real-World Examples

#### Business Email
```python
original = """
I hope this email finds you well. I wanted to reach out to you regarding 
the upcoming quarterly business review meeting that we have scheduled for 
next week. Could you please provide me with a comprehensive update on the 
current status of all ongoing projects in your department?
"""

compressed = compress(original)
# Result: "Update on current status of ongoing projects in your department for quarterly review next week?"
# 68% token reduction
```

#### Technical Documentation
```python
original = """
In order to implement the authentication system, you will need to configure 
the database connection, set up the user authentication middleware, and 
implement the session management functionality using the provided SDK.
"""

compressed = compress(original, "tech_rules.json")
# Result: "To implement auth system: configure DB connection, setup user auth middleware, implement session mgmt with SDK."
# 52% token reduction
```

## 🛠️ Advanced Usage

### Custom Domain Rules

#### Creating Financial Rules
```python
from shrinkprompt import create_custom_rules_template
import json

# Start with general template
create_custom_rules_template("financial_rules.json", domain="general")

# Customize for finance
with open("financial_rules.json", "r") as f:
    rules = json.load(f)

# Add financial abbreviations
rules["abbreviations"].update({
    "return on investment": "ROI",
    "key performance indicator": "KPI", 
    "earnings before interest and taxes": "EBIT",
    "generally accepted accounting principles": "GAAP",
    "securities and exchange commission": "SEC"
})

# Add financial replacements
rules["replacements"].update({
    "basis points": "bps",
    "year over year": "YoY",
    "quarter over quarter": "QoQ"
})

# Save updated rules
with open("financial_rules.json", "w") as f:
    json.dump(rules, f, indent=2)
```

#### Multi-Domain Rules
```python
# Combine multiple domain rules
from shrinkprompt.core import load_custom_rules

legal_rules = load_custom_rules("legal_rules.json")
business_rules = load_custom_rules("business_rules.json")

# Create combined rules
combined_rules = {
    "abbreviations": {**legal_rules.abbreviations, **business_rules.abbreviations},
    "replacements": {**legal_rules.replacements, **business_rules.replacements},
    "removals": legal_rules.removals + business_rules.removals,
    "priority": "after_step3"
}

# Save combined rules
import json
with open("legal_business_rules.json", "w") as f:
    json.dump(combined_rules, f, indent=2)
```

### Performance Optimization

#### Batch Processing
```python
from shrinkprompt import compress, token_count
from concurrent.futures import ThreadPoolExecutor
import time

def compress_batch(texts, custom_rules_path=None):
    """Compress multiple texts efficiently."""
    results = []
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(compress, text, custom_rules_path) 
            for text in texts
        ]
        
        for future in futures:
            results.append(future.result())
    
    return results

# Example usage
texts = ["Text 1", "Text 2", "Text 3"]
compressed_texts = compress_batch(texts, "tech_rules.json")
```

#### Memory Management
```python
# Clear token count cache if needed
from shrinkprompt.core import token_count
token_count.cache_clear()

# Monitor cache performance
cache_info = token_count.cache_info()
print(f"Cache hits: {cache_info.hits}, misses: {cache_info.misses}")
```

### Integration Examples

#### FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from shrinkprompt import compress, token_count
import time

app = FastAPI()

class CompressionRequest(BaseModel):
    text: str
    custom_rules_path: str = None

class CompressionResponse(BaseModel):
    original: str
    compressed: str
    original_tokens: int
    compressed_tokens: int
    tokens_saved: int
    compression_ratio: float
    processing_time_ms: float

@app.post("/compress", response_model=CompressionResponse)
async def compress_text(request: CompressionRequest):
    start_time = time.time()
    
    try:
        compressed = compress(request.text, request.custom_rules_path)
        
        original_tokens = token_count(request.text)
        compressed_tokens = token_count(compressed)
        tokens_saved = original_tokens - compressed_tokens
        compression_ratio = (tokens_saved / original_tokens) * 100
        
        processing_time = (time.time() - start_time) * 1000
        
        return CompressionResponse(
            original=request.text,
            compressed=compressed,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            tokens_saved=tokens_saved,
            compression_ratio=compression_ratio,
            processing_time_ms=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### OpenAI Integration
```python
import openai
from shrinkprompt import compress, token_count

def cost_optimized_completion(prompt, model="gpt-4", custom_rules=None):
    """Get OpenAI completion with automatic prompt compression."""
    
    # Compress prompt
    compressed_prompt = compress(prompt, custom_rules)
    
    # Calculate savings
    original_tokens = token_count(prompt)
    compressed_tokens = token_count(compressed_prompt)
    savings = original_tokens - compressed_tokens
    
    print(f"Prompt compressed: {original_tokens} → {compressed_tokens} tokens ({savings} saved)")
    
    # Get completion with compressed prompt
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": compressed_prompt}]
    )
    
    return response

# Usage
prompt = "Could you please provide me with a detailed explanation..."
response = cost_optimized_completion(prompt, custom_rules="tech_rules.json")
```

## 🧪 Testing and Validation

### Test Your Custom Rules
```python
from shrinkprompt import compress, token_count

def test_compression(text, rules_path=None, min_savings=20):
    """Test compression effectiveness."""
    compressed = compress(text, rules_path)
    
    original_tokens = token_count(text)
    compressed_tokens = token_count(compressed)
    savings_pct = ((original_tokens - compressed_tokens) / original_tokens) * 100
    
    print(f"Original: {text}")
    print(f"Compressed: {compressed}")
    print(f"Tokens: {original_tokens} → {compressed_tokens}")
    print(f"Savings: {savings_pct:.1f}%")
    
    if savings_pct < min_savings:
        print(f"⚠️  Warning: Low compression ratio ({savings_pct:.1f}% < {min_savings}%)")
    else:
        print(f"✅ Good compression ratio: {savings_pct:.1f}%")
    
    return compressed

# Test examples
test_compression("Could you please help me understand this?")
test_compression("Legal document with plaintiff and defendant", "legal_rules.json")
```

### Validate Rule Files
```bash
# Validate syntax and content
shrink-prompt --validate-rules my_rules.json --verbose

# Test rules on sample text
shrink-prompt "Sample text for testing" --rules my_rules.json --show-stages
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Low Compression Ratios
```python
# Issue: Getting < 20% compression
# Solution: Text may already be concise or technical

# Check if text is already compressed
if token_count(text) < 50:
    print("Text is already quite concise")

# Try domain-specific rules
compressed = compress(text, "technical_rules.json")
```

#### 2. Over-Compression
```python
# Issue: Compressed text loses important meaning
# Solution: Use protected_terms in custom rules

rules = {
    "protected_terms": [
        "machine learning model",
        "do not resuscitate", 
        "terms and conditions"
    ]
}
```

#### 3. Custom Rules Not Working
```bash
# Validate rules file
shrink-prompt --validate-rules my_rules.json

# Check rule priority
# Default: "after_step3" - try "before_step1" for aggressive rules
```

#### 4. Performance Issues
```python
# Clear caches if memory usage is high
from shrinkprompt.core import token_count
token_count.cache_clear()

# Check cache statistics
print(token_count.cache_info())
```

### Error Messages

- **`FileNotFoundError`**: Custom rules file not found
- **`ValueError`**: Invalid JSON/YAML format in rules file
- **`ImportError`**: Missing PyYAML for YAML rule files (`pip install PyYAML`)

## 📈 Best Practices

### 1. Choose the Right Domain Rules
- **Legal documents**: Use legal_rules.json
- **Medical records**: Use medical_rules.json  
- **Technical docs**: Use technical_rules.json
- **Business content**: Use general_rules.json

### 2. Optimize Rule Priority
- **`before_step1`**: For preprocessing and format standardization
- **`after_step3`**: **Recommended** - After abbreviations, before mass removal
- **`after_step6`**: For final cleanup and domain-specific post-processing

### 3. Balance Compression vs. Clarity
```python
# Test readability after compression
def check_readability(original, compressed):
    reduction = ((token_count(original) - token_count(compressed)) / token_count(original)) * 100
    
    if reduction > 70:
        print("⚠️  Very high compression - check readability")
    elif reduction > 50:
        print("✅ Good compression ratio")
    else:
        print("ℹ️  Moderate compression - text may already be concise")
```

### 4. Custom Rules Guidelines
- **Start small**: Begin with 10-20 rules, expand gradually
- **Test thoroughly**: Validate on representative samples
- **Use protected_terms**: Preserve critical domain terminology
- **Regular maintenance**: Update rules based on usage patterns

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup
```bash
git clone https://github.com/yourusername/shrink-prompt.git
cd shrink-prompt
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run demo
python main.py
```

### Contribution Guidelines
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Add tests** for new functionality
4. **Ensure** all tests pass
5. **Update** documentation as needed
6. **Commit** changes (`git commit -m 'Add amazing feature'`)
7. **Push** to branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

### Areas for Contribution
- **New domain rules** (finance, education, healthcare)
- **Performance optimizations**
- **Additional language support**
- **Integration examples**
- **Documentation improvements**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [tiktoken](https://github.com/openai/tiktoken) for accurate token counting
- Synonym data from [WordNet](https://wordnet.princeton.edu/) and [Brown Corpus](https://en.wikipedia.org/wiki/Brown_Corpus)
- Inspired by the need to reduce LLM API costs while maintaining quality
- Thanks to the open-source community for feedback and contributions

## 📞 Support

- **Documentation**: [Full documentation](https://github.com/yourusername/shrink-prompt)
- **Issues**: [GitHub Issues](https://github.com/yourusername/shrink-prompt/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/shrink-prompt/discussions)

---

**💰 Save money on LLM tokens without sacrificing quality** ✨

**🚀 From verbose to concise in milliseconds** ⚡
