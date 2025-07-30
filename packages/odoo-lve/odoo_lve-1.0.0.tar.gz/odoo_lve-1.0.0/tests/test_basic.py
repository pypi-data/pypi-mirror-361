"""
Basic tests for odoo_lve package
"""

import pytest
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_manifest_file():
    """Test that manifest file exists and can be read"""
    manifest_path = os.path.join(os.path.dirname(__file__), '..', 'odoo_lve', '__manifest__.py')
    assert os.path.exists(manifest_path), f"Manifest file not found at {manifest_path}"
    
    # Read and evaluate the manifest
    with open(manifest_path, 'r') as f:
        manifest_content = f.read()
    
    # Create a safe environment to evaluate the manifest
    manifest_dict = eval(manifest_content)
    
    assert isinstance(manifest_dict, dict), "Manifest should be a dictionary"
    assert 'name' in manifest_dict, "Manifest should have 'name' field"
    assert 'version' in manifest_dict, "Manifest should have 'version' field"
    assert 'author' in manifest_dict, "Manifest should have 'author' field"


def test_package_structure():
    """Test that the package has the correct structure"""
    package_dir = os.path.join(os.path.dirname(__file__), '..', 'odoo_lve')
    
    # Check required directories exist
    required_dirs = ['models', 'data', 'views', 'security']
    for dir_name in required_dirs:
        dir_path = os.path.join(package_dir, dir_name)
        assert os.path.exists(dir_path), f"Required directory {dir_name} not found"
        assert os.path.isdir(dir_path), f"{dir_name} should be a directory"
    
    # Check required files exist
    required_files = ['__init__.py', '__manifest__.py']
    for file_name in required_files:
        file_path = os.path.join(package_dir, file_name)
        assert os.path.exists(file_path), f"Required file {file_name} not found"
        assert os.path.isfile(file_path), f"{file_name} should be a file"


def test_manifest_content():
    """Test manifest content"""
    manifest_path = os.path.join(os.path.dirname(__file__), '..', 'odoo_lve', '__manifest__.py')
    
    with open(manifest_path, 'r') as f:
        manifest_content = f.read()
    
    manifest = eval(manifest_content)
    
    # Check required fields
    assert manifest['name'] == 'Venezuela Location'
    assert manifest['author'] == 'Carlos Parada'
    assert manifest['category'] == 'Sales'
    assert manifest['license'] == 'LGPL-3'
    assert manifest['installable'] is True
    assert manifest['application'] is True
    assert manifest['auto_install'] is False
    
    # Check dependencies
    assert 'depends' in manifest
    assert isinstance(manifest['depends'], list)
    assert 'base_setup' in manifest['depends']
    assert 'base_import_module' in manifest['depends']
    
    # Check data files
    assert 'data' in manifest
    assert isinstance(manifest['data'], list)
    assert len(manifest['data']) > 0


 