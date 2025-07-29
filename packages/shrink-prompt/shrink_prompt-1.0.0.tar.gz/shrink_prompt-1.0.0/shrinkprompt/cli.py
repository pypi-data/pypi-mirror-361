#!/usr/bin/env python3
"""Command-line interface for ShrinkPrompt with custom rules support."""

import argparse
import sys
from pathlib import Path
from .core import compress, token_count


def main():
    """Main CLI entry point with enhanced custom rules support."""
    parser = argparse.ArgumentParser(
        description="ShrinkPrompt: Compress text prompts for token cost reduction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  shrinkprompt "Could you please help me understand this?"
  shrinkprompt "Legal document text..." --rules legal_rules.json
  echo "Text to compress" | shrinkprompt --stdin
  shrinkprompt --file document.txt --rules medical_rules.yaml --verbose
  
Custom Rules:
  Create JSON/YAML files with domain-specific compression rules:
  - abbreviations: Map long terms to short forms
  - replacements: Replace domain phrases  
  - removals: Remove domain-specific filler words
  - domain_patterns: Advanced regex patterns
  - priority: When to apply (before_step1, after_step3, after_step6)
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        'prompt', 
        nargs='?', 
        help='Text to compress (use quotes for multi-word text)'
    )
    input_group.add_argument(
        '--file', '-f',
        type=Path,
        help='Read input from file'
    )
    input_group.add_argument(
        '--stdin',
        action='store_true',
        help='Read input from standard input'
    )
    
    # Custom rules options
    parser.add_argument(
        '--rules', '--custom-rules',
        type=Path,
        help='Path to custom rules JSON/YAML file for domain-specific compression'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Write compressed output to file'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed compression statistics'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Output only the compressed text (no statistics)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    # Advanced options
    parser.add_argument(
        '--validate-rules',
        action='store_true',
        help='Validate custom rules file format and exit'
    )
    parser.add_argument(
        '--show-stages',
        action='store_true',
        help='Show text after each compression stage (debug mode)'
    )
    
    args = parser.parse_args()
    
    # Validate custom rules if requested
    if args.validate_rules:
        if not args.rules:
            print("Error: --validate-rules requires --rules argument", file=sys.stderr)
            sys.exit(1)
        
        try:
            from .core import load_custom_rules
            custom_rules = load_custom_rules(str(args.rules))
            if custom_rules:
                print(f"✅ Custom rules file '{args.rules}' is valid")
                print(f"   - {len(custom_rules.abbreviations)} abbreviations")
                print(f"   - {len(custom_rules.replacements)} replacements") 
                print(f"   - {len(custom_rules.removals)} removals")
                print(f"   - {len(custom_rules.domain_patterns)} domain patterns")
                print(f"   - Priority: {custom_rules.priority}")
            else:
                print("❌ No rules loaded")
        except Exception as e:
            print(f"❌ Custom rules validation failed: {e}", file=sys.stderr)
            sys.exit(1)
        return
    
    # Get input text
    try:
        if args.prompt:
            original_text = args.prompt
        elif args.file:
            if not args.file.exists():
                print(f"Error: File '{args.file}' not found", file=sys.stderr)
                sys.exit(1)
            original_text = args.file.read_text(encoding='utf-8')
        elif args.stdin:
            original_text = sys.stdin.read()
        else:
            parser.print_help()
            sys.exit(1)
            
        original_text = original_text.strip()
        if not original_text:
            print("Error: No input text provided", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Show compression stages if requested (debug mode)
    if args.show_stages:
        from .compressors import COMPRESSION_STAGES
        from .core import load_custom_rules, apply_custom_rules_to_pipeline
        
        custom_rules = None
        if args.rules:
            try:
                custom_rules = load_custom_rules(str(args.rules))
            except Exception as e:
                print(f"Warning: Failed to load custom rules: {e}", file=sys.stderr)
        
        print("🔍 COMPRESSION STAGES DEBUG MODE")
        print("=" * 60)
        print(f"Original ({token_count(original_text)} tokens): {original_text}")
        print()
        
        text = original_text
        
        # Show custom rules before pipeline
        if custom_rules and custom_rules.priority == 'before_step1':
            text = apply_custom_rules_to_pipeline(text, custom_rules, 'before_step1')
            print(f"After custom rules (before_step1) ({token_count(text)} tokens): {text}")
            print()
        
        # Show each compression stage
        for i, (stage, stage_name) in enumerate(zip(COMPRESSION_STAGES, [
            "Step 1: Normalize", "Step 2: Mass Removal", "Step 3: Abbreviate/Symbolize", 
            "Step 4: Smart Context", "Step 5: Token Optimize", "Step 6: Advanced Optimization"
        ])):
            text = stage(text)
            print(f"After {stage_name} ({token_count(text)} tokens): {text}")
            
            # Show custom rules after step 3
            if i == 2 and custom_rules and custom_rules.priority == 'after_step3':
                text = apply_custom_rules_to_pipeline(text, custom_rules, 'after_step3')
                print(f"After custom rules (after_step3) ({token_count(text)} tokens): {text}")
            print()
        
        # Show custom rules after pipeline
        if custom_rules and custom_rules.priority == 'after_step6':
            text = apply_custom_rules_to_pipeline(text, custom_rules, 'after_step6')
            print(f"After custom rules (after_step6) ({token_count(text)} tokens): {text}")
            print()
        
        print("=" * 60)
        return
    
    # Perform compression
    try:
        rules_path = str(args.rules) if args.rules else None
        compressed_text = compress(original_text, rules_path)
    except Exception as e:
        print(f"Error during compression: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Calculate statistics
    orig_tokens = token_count(original_text)
    comp_tokens = token_count(compressed_text)
    pct_saved = round(100 * (1 - comp_tokens / max(1, orig_tokens)), 1)
    
    # Prepare output
    if args.json:
        import json
        result = {
            "original": original_text,
            "compressed": compressed_text,
            "orig_tokens": orig_tokens,
            "comp_tokens": comp_tokens,
            "tokens_saved": orig_tokens - comp_tokens,
            "pct_saved": pct_saved,
            "custom_rules": str(args.rules) if args.rules else None
        }
        output_text = json.dumps(result, indent=2)
    elif args.quiet:
        output_text = compressed_text
    elif args.verbose:
        output_text = f"""ShrinkPrompt Compression Results
{'=' * 40}
Original text ({orig_tokens} tokens):
{original_text}

Compressed text ({comp_tokens} tokens):
{compressed_text}

Statistics:
- Tokens saved: {orig_tokens - comp_tokens}
- Compression ratio: {pct_saved}%
- Custom rules: {args.rules if args.rules else 'None'}
"""
    else:
        output_text = f"""Compressed ({comp_tokens} tokens, {pct_saved}% savings): {compressed_text}"""
    
    # Write output
    if args.output:
        try:
            args.output.write_text(output_text, encoding='utf-8')
            if not args.quiet:
                print(f"Output written to {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_text)


if __name__ == "__main__":
    main()