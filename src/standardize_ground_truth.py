#!/usr/bin/env python3
"""
Standardize ground_truth_enhanced.json files to match the unified schema.
This script:
1. Renames question_id to id
2. Ensures question field exists (reads from question.json if missing)
3. Standardizes change object field order and removes non-schema fields
4. Ensures proper top-level field order
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

# Schema-defined field order
TOP_LEVEL_ORDER = [
    "$schema",
    "id",
    "question",
    "change",
    "breaking_patterns",
    "impacted_files",
    "false_positives",
    "impact_summary"
]

CHANGE_FIELDS_ORDER = [
    "module",
    "source_repo",
    "source_file",
    "before",
    "after",
    "description"
]

def reorder_dict(data: Dict[str, Any], field_order: list) -> Dict[str, Any]:
    """Reorder dictionary keys according to specified order, keeping extra fields at end."""
    ordered = {}
    
    # Add fields in specified order if they exist
    for key in field_order:
        if key in data:
            ordered[key] = data[key]
    
    # Add any remaining fields not in the order list
    for key, value in data.items():
        if key not in ordered:
            ordered[key] = value
    
    return ordered

def standardize_change_object(change: Dict[str, Any]) -> Dict[str, Any]:
    """Standardize the change object to match schema."""
    standardized = {}
    
    # Map fields to their standard names and extract only schema-defined fields
    for field in CHANGE_FIELDS_ORDER:
        if field in change:
            standardized[field] = change[field]
    
    # Ensure all required fields exist
    required_fields = ["module", "source_repo", "source_file", "before", "after", "description"]
    missing = [f for f in required_fields if f not in standardized]
    if missing:
        print(f"  WARNING: Missing required change fields: {missing}")
    
    return standardized

def load_question_text(question_folder: Path) -> str:
    """Load question text from question.json in the folder."""
    question_file = question_folder / "question.json"
    if question_file.exists():
        with open(question_file, 'r') as f:
            question_data = json.load(f)
            return question_data.get('question', '')
    return ''

def standardize_ground_truth_file(file_path: Path, question_folder: Path) -> bool:
    """Standardize a single ground_truth_enhanced.json file."""
    try:
        # Read the file
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        original_data = json.dumps(data, indent=2)
        modified = False
        
        # 1. Handle question_id -> id rename
        if 'question_id' in data:
            data['id'] = data.pop('question_id')
            modified = True
            print(f"  ✓ Renamed question_id to id")
        
        # 2. Add question field if missing
        if 'question' not in data or not data['question']:
            question_text = load_question_text(question_folder)
            if question_text:
                data['question'] = question_text
                modified = True
                print(f"  ✓ Added question field from question.json")
            else:
                print(f"  ⚠ WARNING: Could not find question text")
        
        # 3. Standardize change object
        if 'change' in data:
            original_change = json.dumps(data['change'])
            data['change'] = standardize_change_object(data['change'])
            if json.dumps(data['change']) != original_change:
                modified = True
                print(f"  ✓ Standardized change object")
        
        # 4. Ensure all required top-level fields exist with defaults if needed
        if 'breaking_patterns' not in data:
            data['breaking_patterns'] = []
            modified = True
        if 'impacted_files' not in data:
            data['impacted_files'] = []
            modified = True
        if 'false_positives' not in data:
            data['false_positives'] = []
            modified = True
        if 'impact_summary' not in data:
            data['impact_summary'] = {
                "total_impacted_files": len(data.get('impacted_files', [])),
                "total_false_positives": len(data.get('false_positives', [])),
                "repos_affected": [],
                "by_pattern": {},
                "by_severity": {}
            }
            modified = True
        
        # 5. Reorder top-level fields
        original_order = list(data.keys())
        data = reorder_dict(data, TOP_LEVEL_ORDER)
        if list(data.keys()) != original_order:
            modified = True
            print(f"  ✓ Reordered top-level fields")
        
        # Write back if modified
        if modified:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"  ✅ Standardized and saved")
            return True
        else:
            print(f"  ℹ Already compliant")
            return False
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

def main():
    results_dir = Path(__file__).parent.parent / "results" / "KubeCluster45"
    
    if not results_dir.exists():
        print(f"❌ Results directory not found: {results_dir}")
        return
    
    print(f"Scanning {results_dir}")
    print("=" * 80)
    
    question_folders = [d for d in results_dir.iterdir() if d.is_dir() and d.name.startswith('question_')]
    question_folders.sort()
    
    total = 0
    modified = 0
    errors = 0
    
    for folder in question_folders:
        gt_file = folder / "ground_truth_enhanced.json"
        if gt_file.exists():
            print(f"\n{folder.name}:")
            total += 1
            if standardize_ground_truth_file(gt_file, folder):
                modified += 1
        else:
            print(f"\n{folder.name}:")
            print(f"  ⚠ No ground_truth_enhanced.json found")
    
    print("\n" + "=" * 80)
    print(f"Summary:")
    print(f"  Total processed: {total}")
    print(f"  Modified: {modified}")
    print(f"  Already compliant: {total - modified}")
    print("=" * 80)

if __name__ == "__main__":
    main()
