#!/usr/bin/env python3
# Dashboard validator for Grafana dashboard JSON files
import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dashboard_validator")

# Schema definition for basic dashboard validation
# This is a simplified schema focusing on essential fields
DASHBOARD_SCHEMA = {
    "required_fields": [
        "annotations", 
        "editable", 
        "panels", 
        "schemaVersion", 
        "style", 
        "tags", 
        "title", 
        "uid"
    ],
    "array_fields": ["panels", "tags"],
    "numeric_fields": ["schemaVersion"],
    "boolean_fields": ["editable"],
    "string_fields": ["style", "title", "uid"]
}

def validate_dashboard_json(dashboard_path: str) -> List[str]:
    """
    Validate a Grafana dashboard JSON file
    
    Args:
        dashboard_path: Path to the dashboard JSON file
        
    Returns:
        List of validation errors, empty if valid
    """
    errors = []
    
    try:
        with open(dashboard_path, 'r') as f:
            dashboard = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    except Exception as e:
        return [f"Error reading file: {e}"]
    
    # Check required fields
    for field in DASHBOARD_SCHEMA['required_fields']:
        if field not in dashboard:
            errors.append(f"Missing required field: {field}")
    
    # Check field types
    for field in DASHBOARD_SCHEMA['array_fields']:
        if field in dashboard and not isinstance(dashboard[field], list):
            errors.append(f"Field {field} should be an array")
    
    for field in DASHBOARD_SCHEMA['numeric_fields']:
        if field in dashboard and not isinstance(dashboard[field], (int, float)):
            errors.append(f"Field {field} should be a number")
    
    for field in DASHBOARD_SCHEMA['boolean_fields']:
        if field in dashboard and not isinstance(dashboard[field], bool):
            errors.append(f"Field {field} should be a boolean")
    
    for field in DASHBOARD_SCHEMA['string_fields']:
        if field in dashboard and not isinstance(dashboard[field], str):
            errors.append(f"Field {field} should be a string")
    
    # Check for duplicate panel IDs
    if 'panels' in dashboard and isinstance(dashboard['panels'], list):
        panel_ids = {}
        for i, panel in enumerate(dashboard['panels']):
            if 'id' in panel:
                if panel['id'] in panel_ids:
                    errors.append(f"Duplicate panel ID {panel['id']} at positions {panel_ids[panel['id']]} and {i}")
                else:
                    panel_ids[panel['id']] = i
    
    # Check for mandatory tags
    if 'tags' in dashboard and isinstance(dashboard['tags'], list):
        if 'iracing' not in dashboard['tags']:
            errors.append("Missing required tag: 'iracing'")
    
    return errors

def validate_dashboards_directory(directory_path: str) -> Dict[str, List[str]]:
    """
    Validate all dashboard JSON files in a directory
    
    Args:
        directory_path: Directory containing dashboard JSON files
        
    Returns:
        Dictionary mapping filenames to lists of validation errors
    """
    results = {}
    
    directory = Path(directory_path)
    if not directory.exists() or not directory.is_dir():
        logger.error(f"Directory not found: {directory_path}")
        return {"error": [f"Directory not found: {directory_path}"]}
    
    # Find all JSON files recursively
    json_files = list(directory.glob('**/*.json'))
    
    if not json_files:
        logger.warning(f"No JSON files found in {directory_path}")
        return {}
    
    for json_file in json_files:
        logger.info(f"Validating {json_file}")
        errors = validate_dashboard_json(str(json_file))
        
        if errors:
            results[str(json_file)] = errors
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Validate Grafana dashboard JSON files.')
    parser.add_argument('directory', help='Directory containing dashboard JSON files')
    args = parser.parse_args()
    
    logger.info(f"Validating dashboards in {args.directory}")
    
    validation_results = validate_dashboards_directory(args.directory)
    
    if validation_results:
        logger.error("Validation errors found:")
        for filename, errors in validation_results.items():
            for error in errors:
                logger.error(f"{filename}: {error}")
        sys.exit(1)
    else:
        logger.info("All dashboards valid!")
        sys.exit(0)

if __name__ == "__main__":
    main()