#!/usr/bin/env python3
"""
Dead Code Detection Script for Budget Tracker App

This script uses vulture to detect unused code and dead files in the project.
Run this script regularly to maintain clean codebase.

Usage:
    python detect_dead_code.py [--confidence LEVEL]

Requirements:
    pip install vulture
"""

import subprocess
import sys
import argparse
import os


def run_vulture(confidence=70):
    """Run vulture on the project to detect dead code."""
    print(f"🔍 Scanning for dead code with {confidence}% confidence...")
    
    # Directories to scan
    scan_dirs = [".", "beeware_app/", "static/", "templates/"]
    
    for scan_dir in scan_dirs:
        if os.path.exists(scan_dir):
            print(f"\n📁 Scanning {scan_dir}...")
            try:
                result = subprocess.run(
                    ["python", "-m", "vulture", "--min-confidence", str(confidence), scan_dir],
                    capture_output=True,
                    text=True
                )
                
                if result.stdout.strip():
                    print(f"⚠️  Found potential dead code in {scan_dir}:")
                    print(result.stdout)
                else:
                    print(f"✅ No dead code found in {scan_dir}")
                    
            except FileNotFoundError:
                print("❌ vulture not found. Install with: pip install vulture")
                return False
    
    return True


def check_template_usage():
    """Check if all templates are used in Flask routes."""
    print("\n🔍 Checking template usage...")
    
    if not os.path.exists("templates/"):
        print("✅ No templates directory found")
        return
    
    # Get all template files
    templates = [f for f in os.listdir("templates/") if f.endswith('.html')]
    
    # Check flask_app.py for template usage
    if os.path.exists("flask_app.py"):
        with open("flask_app.py", 'r') as f:
            flask_content = f.read()
        
        unused_templates = []
        for template in templates:
            if template not in flask_content:
                unused_templates.append(template)
        
        if unused_templates:
            print("⚠️  Unused templates found:")
            for template in unused_templates:
                print(f"   - templates/{template}")
        else:
            print("✅ All templates are used")
    else:
        print("⚠️  flask_app.py not found")


def check_static_files():
    """Check for unused static files."""
    print("\n🔍 Checking static file usage...")
    
    if not os.path.exists("static/"):
        print("✅ No static directory found")
        return
    
    static_files = [f for f in os.listdir("static/") if not f.startswith('.')]
    
    # Check for references in templates and app files
    referenced_files = set()
    
    # Check templates
    if os.path.exists("templates/"):
        for template_file in os.listdir("templates/"):
            if template_file.endswith('.html'):
                with open(f"templates/{template_file}", 'r') as f:
                    content = f.read()
                    for static_file in static_files:
                        if static_file in content:
                            referenced_files.add(static_file)
    
    # Check manifest.json and sw.js
    for check_file in ["static/manifest.json", "static/sw.js"]:
        if os.path.exists(check_file):
            with open(check_file, 'r') as f:
                content = f.read()
                for static_file in static_files:
                    if static_file in content:
                        referenced_files.add(static_file)
    
    unused_static = set(static_files) - referenced_files - {"manifest.json", "sw.js"}  # Exclude PWA files
    
    if unused_static:
        print("⚠️  Potentially unused static files:")
        for file in unused_static:
            print(f"   - static/{file}")
    else:
        print("✅ All static files appear to be used")


def main():
    parser = argparse.ArgumentParser(description="Detect dead code in Budget Tracker App")
    parser.add_argument(
        "--confidence",
        type=int,
        default=70,
        help="Confidence level for vulture (default: 70)"
    )
    
    args = parser.parse_args()
    
    print("🧹 Budget Tracker Dead Code Detection")
    print("=" * 40)
    
    # Run vulture analysis
    if not run_vulture(args.confidence):
        sys.exit(1)
    
    # Check template usage
    check_template_usage()
    
    # Check static file usage
    check_static_files()
    
    print("\n✅ Dead code analysis complete!")


if __name__ == "__main__":
    main()