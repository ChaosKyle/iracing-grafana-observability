#!/usr/bin/env python3
# Script to check for unique dashboard IDs across all dashboard files
import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Set, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dashboard_id_validator")

def extract_dashboard_ids(dashboard_path: str) -> Tuple[str, Dict[str, str]]:
    """
    Extract dashboard ID and UIDs from a dashboard file
    
    Args:
        dashboard_path: Path to the dashboard JSON file
    
    Returns:
        Tuple of (file_path, {id_type: id_value})
    """
    ids = {}
    
    try:
        with open(dashboard_path, 'r') as f:
            dashboard = json.load(f)
        
        # Extract dashboard ID if present
        if 'id' in dashboard and dashboard['id'] is not None:
            ids['id'] = str(dashboard['id'])
        
        # Extract dashboard UID if present
        if 'uid' in dashboard and dashboard['uid'] is not None:
            ids['uid'] = dashboard['uid']
        
        # Extract dashboard title for reference
        if 'title' in dashboard:
            ids['title'] = dashboard['title']
        
        return dashboard_path, ids
    
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {dashboard_path}")
        return dashboard_path, {}
    except Exception as e:
        logger.error(f"Error processing file {dashboard_path}: {e}")
        return dashboard_path, {}

def check_dashboard_ids(directory_path: str) -> bool:
    """
    Check for duplicate dashboard IDs across all dashboard files
    
    Args:
        directory_path: Directory containing dashboard JSON files
        
    Returns:
        True if all IDs are unique, False otherwise
    """
    directory = Path(directory_path)
    if not directory.exists() or not directory.is_dir():
        logger.error(f"Directory not found: {directory_path}")
        return False
    
    # Find all JSON files recursively
    json_files = list(directory.glob('**/*.json'))
    
    if not json_files:
        logger.warning(f"No JSON files found in {directory_path}")
        return True
    
    # Dictionaries to track IDs and UIDs
    dashboard_ids = {}  # numeric ID -> file path
    dashboard_uids = {}  # string UID -> file path
    
    # Extract IDs from all files
    for json_file in json_files:
        file_path, ids = extract_dashboard_ids(str(json_file))
        
        if 'id' in ids and ids['id'] is not None and ids['id'] != 'null':
            if ids['id'] in dashboard_ids:
                logger.error(f"Duplicate dashboard ID '{ids['id']}' found in:")
                logger.error(f"  - {dashboard_ids[ids['id']]}")
                logger.error(f"  - {file_path}")
                return False
            dashboard_ids[ids['id']] = file_path
        
        if 'uid' in ids and ids['uid']:
            if ids['uid'] in dashboard_uids:
                logger.error(f"Duplicate dashboard UID '{ids['uid']}' found in:")
                logger.error(f"  - {dashboard_uids[ids['uid']]}")
                logger.error(f"  - {file_path}")
                return False
            dashboard_uids[ids['uid']] = file_path
    
    # Success if we reach here
    logger.info(f"Validated {len(json_files)} dashboard files")
    logger.info(f"Found {len(dashboard_ids)} unique dashboard IDs")
    logger.info(f"Found {len(dashboard_uids)} unique dashboard UIDs")
    return True

def main():
    parser = argparse.ArgumentParser(description='Check for unique dashboard IDs.')
    parser.add_argument('directory', help='Directory containing dashboard JSON files')
    args = parser.parse_args()
    
    logger.info(f"Checking dashboard IDs in {args.directory}")
    
    if check_dashboard_ids(args.directory):
        logger.info("All dashboard IDs are unique!")
        sys.exit(0)
    else:
        logger.error("Duplicate dashboard IDs found!")
        sys.exit(1)

if __name__ == "__main__":
    main()