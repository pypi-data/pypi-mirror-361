# CallMeFair Documentation

This directory contains the documentation for the CallMeFair project, a comprehensive framework for automatic bias mitigation in AI systems.

## Documentation Setup

### Recommended Tool: Sphinx

For this project, we recommend using **Sphinx** with the following configuration:

- **Sphinx**: The most robust and widely-used Python documentation generator
- **Google-style docstrings**: Already implemented in the codebase
- **Read the Docs theme**: Modern, responsive design
- **AutoAPI**: Automatic API documentation generation
- **Intersphinx**: Links to external documentation (AIF360, scikit-learn, etc.)

### Setup Instructions

1. **Install Sphinx and dependencies:**
   ```bash
   pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints sphinx-autoapi
   ```

2. **Initialize Sphinx documentation:**
   ```bash
   cd docs
   sphinx-quickstart
   ```

3. **Configure conf.py** (see `conf.py` in this directory)

4. **Build documentation:**
   ```bash
   sphinx-build -b html . _build/html
   ```

### Documentation Structure

```
docs/
├── README.md                 # This file
├── conf.py                   # Sphinx configuration
├── index.rst                 # Main documentation page
├── api/                      # API documentation
│   ├── mitigation.rst       # Bias mitigation modules
│   ├── util.rst             # Utility modules
│   └── search.rst           # Search modules
├── user_guide/              # User guides
│   ├── installation.rst     # Installation guide
│   ├── quickstart.rst       # Quick start guide
│   └── examples.rst         # Usage examples
├── theory/                  # Theoretical background
│   ├── bias_mitigation.rst  # Bias mitigation techniques
│   └── fairness_metrics.rst # Fairness metrics
└── _build/                  # Generated HTML (gitignored)
```

### Key Features

- **Comprehensive API Documentation**: All classes, methods, and functions documented
- **Interactive Examples**: Code examples that can be executed
- **Theoretical Background**: Explanation of bias mitigation techniques
- **User Guides**: Step-by-step instructions for common tasks
- **Search Functionality**: Full-text search across all documentation
- **Mobile Responsive**: Works on all devices

### Building the Website

```bash
# Generate HTML documentation
make html

# Generate PDF documentation (optional)
make latexpdf

# Serve locally for testing
python -m http.server _build/html
```

### Deployment

The documentation can be deployed to:
- **GitHub Pages**: Free hosting for open-source projects
- **Read the Docs**: Professional documentation hosting
- **Netlify/Vercel**: Modern static site hosting

### Documentation Standards

- **Google-style docstrings**: Already implemented in codebase
- **Type hints**: All functions include type annotations
- **Examples**: Every public method includes usage examples
- **Cross-references**: Links between related documentation sections
- **Version control**: Documentation versioned with code

### Next Steps

1. Set up the Sphinx configuration
2. Create the documentation structure
3. Add comprehensive user guides
4. Include theoretical background on bias mitigation
5. Add interactive examples and tutorials
6. Deploy to a hosting service

This documentation will serve as both a reference manual and a learning resource for users of the CallMeFair framework. 