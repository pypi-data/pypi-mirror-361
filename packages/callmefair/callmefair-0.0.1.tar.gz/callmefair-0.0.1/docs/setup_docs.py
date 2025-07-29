#!/usr/bin/env python3
"""
Setup script for CallMeFair documentation.

This script helps you set up and build the documentation for the CallMeFair project.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'sphinx',
        'sphinx_rtd_theme',
        'sphinx_autodoc_typehints',
        'sphinx_autoapi'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'
        ] + missing_packages)
        print("Dependencies installed successfully!")
    else:
        print("All dependencies are already installed.")

def create_directories():
    """Create necessary directories for documentation."""
    directories = [
        '_static',
        '_templates',
        'api',
        'user_guide',
        'theory',
        'advanced',
        'contributing'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")

def create_placeholder_files():
    """Create placeholder files for documentation structure."""
    files_to_create = [
        ('user_guide/installation.rst', 'Installation Guide\n==================\n\n.. toctree::\n   :maxdepth: 2\n\nInstallation instructions for CallMeFair.'),
        ('user_guide/examples.rst', 'Examples\n========\n\n.. toctree::\n   :maxdepth: 2\n\nComprehensive examples of CallMeFair usage.'),
        ('user_guide/overview.rst', 'Overview\n========\n\n.. toctree::\n   :maxdepth: 2\n\nOverview of the CallMeFair framework.'),
        ('user_guide/bias_mitigation_guide.rst', 'Bias Mitigation Guide\n====================\n\n.. toctree::\n   :maxdepth: 2\n\nDetailed guide to bias mitigation techniques.'),
        ('user_guide/evaluation_guide.rst', 'Evaluation Guide\n================\n\n.. toctree::\n   :maxdepth: 2\n\nGuide to evaluating fairness in machine learning models.'),
        ('user_guide/grid_search_guide.rst', 'Grid Search Guide\n================\n\n.. toctree::\n   :maxdepth: 2\n\nComprehensive guide to grid search functionality for bias mitigation evaluation.'),
        ('user_guide/utility_guide.rst', 'Utility Functions Guide\n========================\n\n.. toctree::\n   :maxdepth: 2\n\nGuide to utility functions including fairness score calculation and dataset management.'),
        ('user_guide/bias_search_guide.rst', 'Bias Search Guide\n================\n\n.. toctree::\n   :maxdepth: 2\n\nComprehensive guide to bias search functionality for evaluating bias in datasets and models.'),
        ('api/mitigation.rst', 'Bias Mitigation API\n==================\n\n.. toctree::\n   :maxdepth: 2\n\nAPI documentation for bias mitigation modules.'),
        ('api/util.rst', 'Utility API\n==========\n\n.. toctree::\n   :maxdepth: 2\n\nAPI documentation for utility modules.'),
        ('api/search.rst', 'Search API\n==========\n\n.. toctree::\n   :maxdepth: 2\n\nAPI documentation for search modules.'),
        ('theory/bias_mitigation.rst', 'Bias Mitigation Theory\n======================\n\n.. toctree::\n   :maxdepth: 2\n\nTheoretical background on bias mitigation techniques.'),
        ('theory/fairness_metrics.rst', 'Fairness Metrics\n================\n\n.. toctree::\n   :maxdepth: 2\n\nMathematical definitions of fairness metrics.'),
        ('theory/evaluation_methods.rst', 'Evaluation Methods\n==================\n\n.. toctree::\n   :maxdepth: 2\n\nMethods for evaluating fairness in machine learning.'),
        ('advanced/custom_mitigation.rst', 'Custom Bias Mitigation\n========================\n\n.. toctree::\n   :maxdepth: 2\n\nGuide to implementing custom bias mitigation techniques.'),
        ('advanced/performance_optimization.rst', 'Performance Optimization\n==========================\n\n.. toctree::\n   :maxdepth: 2\n\nTips for optimizing performance with CallMeFair.'),
        ('advanced/deployment.rst', 'Deployment Guide\n================\n\n.. toctree::\n   :maxdepth: 2\n\nGuide to deploying CallMeFair in production.'),
        ('contributing/development_guide.rst', 'Development Guide\n==================\n\n.. toctree::\n   :maxdepth: 2\n\nGuide for contributing to CallMeFair development.'),
        ('contributing/code_of_conduct.rst', 'Code of Conduct\n================\n\n.. toctree::\n   :maxdepth: 2\n\nCode of conduct for the CallMeFair community.'),
        ('contributing/roadmap.rst', 'Development Roadmap\n===================\n\n.. toctree::\n   :maxdepth: 2\n\nFuture development plans for CallMeFair.'),
    ]
    
    for file_path, content in files_to_create:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"Created file: {file_path}")

def build_documentation():
    """Build the documentation."""
    print("Building documentation...")
    try:
        subprocess.check_call(['make', 'html'])
        print("Documentation built successfully!")
        print("You can view it by opening _build/html/index.html in your browser.")
    except subprocess.CalledProcessError as e:
        print(f"Error building documentation: {e}")
        print("Please check the error messages above and fix any issues.")

def serve_documentation():
    """Serve the documentation locally."""
    print("Starting local server at http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    try:
        subprocess.run(['python', '-m', 'http.server', '8000'], 
                      cwd='_build/html')
    except KeyboardInterrupt:
        print("\nServer stopped.")

def main():
    """Main setup function."""
    print("Setting up CallMeFair documentation...")
    
    # Check and install dependencies
    check_dependencies()
    
    # Create directories
    create_directories()
    
    # Create placeholder files
    create_placeholder_files()
    
    # Build documentation
    build_documentation()
    
    # Ask if user wants to serve documentation
    response = input("\nWould you like to serve the documentation locally? (y/n): ")
    if response.lower() in ['y', 'yes']:
        serve_documentation()

if __name__ == '__main__':
    main() 