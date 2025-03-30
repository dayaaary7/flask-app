"""
Flask Application for Feature Management System

This module provides a Flask web application for managing and displaying feature comparisons.
It includes functionality to load features from a Word document or use default data if the document
is not found.

Dependencies:
    - Flask: Web framework
    - python-docx: For reading Word documents
    - os: For file and directory operations

Main Components:
    - load_features(): Loads feature data from a Word document or defaults
    - process_features(): Processes raw feature data into comparison format
    - index(): Main route handler for the web interface
"""

from flask import Flask, render_template, jsonify
from docx import Document
from collections import defaultdict
import os

app = Flask(__name__)

def load_features():
    """
    Load features from a Word document or return default features if file not found.
    
    Returns:
        tuple: (feature_comparisons, stats) processed by process_features()
        
    Raises:
        Exception: If there's an error processing the document
    """
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'data', 'features.docx')
        if not os.path.exists(file_path):
            print(f"Document not found at: {file_path}")
            # Fallback to default data matching the screenshot format
            default_features = [
                {
                    'feature': 'Login System',
                    'supported': 'User authentication with email and password',
                    'to_enhance': 'NA'
                },
                {
                    'feature': 'Data Export',
                    'supported': '',
                    'to_enhance': 'User authentication with email and password'
                },
                {
                    'feature': 'Dashboard',
                    'supported': 'User authentication with email and password',
                    'to_enhance': 'NA'
                },
                {
                    'feature': 'Mobile App',
                    'supported': 'User authentication with email and password',
                    'to_enhance': 'User authentication with email and password'
                },
                {
                    'feature': 'API Integration',
                    'supported': 'User authentication with email and password',
                    'to_enhance': 'User authentication with email and password'
                }
            ]
            return process_features(default_features)

        doc = Document(file_path)
        features = []
        
        for table in doc.tables:
            if len(table.columns) < 3:  # Need Feature, Supported, and Need to enhance columns
                continue
                
            for row in table.rows[1:]:  # Skip header row
                try:
                    feature = row.cells[0].text.strip()
                    supported = row.cells[1].text.strip()
                    to_enhance = row.cells[2].text.strip()
                    
                    features.append({
                        'feature': feature,
                        'supported': supported,
                        'to_enhance': to_enhance
                    })
                        
                except IndexError as e:
                    print(f"Error processing row: {e}")
                    continue
        
        return process_features(features)
    except Exception as e:
        print(f"Error loading features: {e}")
        raise

def process_features(features):
    """
    Process raw feature data into comparison format and calculate statistics.
    
    Args:
        features (list): List of feature dictionaries with 'feature', 'supported', and 'to_enhance' keys
        
    Returns:
        tuple: (feature_comparisons, stats)
            - feature_comparisons: Dictionary of processed feature comparisons
            - stats: Dictionary containing count statistics
    """
    feature_comparisons = {}
    supported_count = 0
    enhance_count = 0
    
    for feature in features:
        feature_name = feature['feature'].rstrip(':')  # Remove trailing colon if present
        feature_comparisons[feature_name] = {
            'supported': feature['supported'] if feature['supported'] != 'NA' else None,
            'to_enhance': feature['to_enhance'] if feature['to_enhance'] != 'NA' else None
        }
        
        if feature['supported'] and feature['supported'] != 'NA':
            supported_count += 1
        if feature['to_enhance'] and feature['to_enhance'] != 'NA':
            enhance_count += 1
    
    stats = {
        'supported': supported_count,
        'to_enhance': enhance_count,
        'total': supported_count + enhance_count
    }
    
    return feature_comparisons, stats

@app.route('/')
def index():
    """
    Main route handler for the web interface.
    
    Returns:
        str: Rendered HTML template with feature comparisons and stats
        tuple: Error response with 500 status code if an error occurs
    """
    try:
        feature_comparisons, stats = load_features()
        return render_template('index.html', 
                             feature_comparisons=feature_comparisons,
                             stats=stats)
    except Exception as e:
        print(f"Error in index route: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(debug=True)