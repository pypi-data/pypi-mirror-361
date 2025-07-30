#!/usr/bin/env python3
"""
Command-line interface for FactCheckr.
"""

import argparse
import json
import sys
from .core import CompleteFactCheckr

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="FactCheckr - AI-powered fact-checking tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  factcheckr "The sky is blue"
  factcheckr --interactive
  echo "Cats have 6 legs" | factcheckr --stdin
        """
    )
    
    parser.add_argument(
        "claim",
        nargs="?",
        help="The claim to fact-check"
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive mode"
    )
    
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read claim from stdin"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON (default: formatted)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="FactCheckr 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Initialize fact checker
    fc = CompleteFactCheckr()
    
    if not fc.ai_available:
        print("Error: AI service is not available. Please check your internet connection.", file=sys.stderr)
        sys.exit(1)
    
    # Handle different input modes
    if args.interactive:
        interactive_mode(fc, args.json)
    elif args.stdin:
        stdin_mode(fc, args.json)
    elif args.claim:
        single_claim_mode(fc, args.claim, args.json)
    else:
        parser.print_help()
        sys.exit(1)

def interactive_mode(fc, json_output=False):
    """Interactive mode for continuous fact-checking"""
    print("FactCheckr Interactive Mode")
    print("Enter claims to fact-check (or 'quit' to exit):")
    print("-" * 50)
    
    while True:
        try:
            claim = input("\n> ").strip()
            if claim.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if claim:
                result = fc.fact_check(claim)
                if json_output:
                    print(result)
                else:
                    format_output(result)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

def stdin_mode(fc, json_output=False):
    """Read claim from stdin"""
    try:
        claim = sys.stdin.read().strip()
        if claim:
            result = fc.fact_check(claim)
            if json_output:
                print(result)
            else:
                format_output(result)
        else:
            print("Error: No input provided", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def single_claim_mode(fc, claim, json_output=False):
    """Process a single claim"""
    try:
        result = fc.fact_check(claim)
        if json_output:
            print(result)
        else:
            format_output(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def format_output(json_result):
    """Format JSON output for human reading"""
    try:
        data = json.loads(json_result)
        claims = data.get('claims', [])
        
        for i, claim_data in enumerate(claims, 1):
            if len(claims) > 1:
                print(f"\nClaim {i}:")
            
            claim = claim_data.get('claim', 'Unknown')
            verdict = claim_data.get('verdict', 'Unknown')
            evidence = claim_data.get('evidence', 'No evidence')
            confidence = claim_data.get('confidence', 0.0)
            
            print(f"Claim: {claim}")
            print(f"Verdict: {verdict}")
            print(f"Evidence: {evidence}")
            print(f"Confidence: {confidence:.1f}")
            
            if i < len(claims):
                print("-" * 40)
                
    except json.JSONDecodeError:
        print("Error: Invalid JSON response")
        print(json_result)
    except Exception as e:
        print(f"Error formatting output: {e}")
        print(json_result)

if __name__ == "__main__":
    main()