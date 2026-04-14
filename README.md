# 📚 Auto Documenter

An intelligent Python-based documentation generation system that automatically creates, organizes, and deploys comprehensive documentation for your projects. Auto Documenter uses MkDocs to generate beautiful static documentation websites and deploys them to GitHub Pages with a single push.

## ✨ Features

- **Automatic Documentation Generation** - Scan project files and auto-generate documentation
- **MkDocs Integration** - Build beautiful, responsive documentation sites
- **GitHub Pages Deployment** - One-click deployment directly to GitHub Pages
- **Markdown Support** - Write documentation in simple Markdown format
- **Multi-Page Navigation** - Automatic navigation menu generation
- **Search Functionality** - Full-text search across all documentation
- **Dark Mode Support** - Built-in dark theme support
- **Custom Styling** - Easily customize colors and branding
- **Version Control** - Track documentation changes alongside code
- **CI/CD Integration** - Automated builds and deployments via GitHub Actions

## 🛠 Tech Stack

- **Language**: Python 3.8+
- **Documentation Framework**: MkDocs
- **Deployment**: GitHub Pages
- **CI/CD**: GitHub Actions
- **Version Control**: Git & GitHub
- **Markdown**: Python-Markdown with extensions

## 📁 Project Structure
```
auto-documenter/ 
├── docs/ # Documentation source files 
│ ├── index.md # Homepage 
│ ├── getting-started.md # Getting started guide 
│ ├── installation.md # Installation instructions 
│ ├── usage.md # Usage guide 
│ └── api/ # API documentation 
├── mkdocs.yml # MkDocs configuration 
├── generate_docs.py # Documentation generation script 
├── requirements.txt # Python dependencies
├── .github/ │ └── workflows/ 
│ └── publish-docs.yml # GitHub Actions workflow
├── README.md # Project README 
└── .gitignore # Git ignore rules
```
Code

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- GitHub account (for Pages deployment)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sushversesai-pixel/auto-documenter.git
   cd auto-documenter
Create a virtual environment (recommended):

bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
Install dependencies:

bash
pip install -r requirements.txt
Quick Start
Generate documentation:

bash
python generate_docs.py
Start local development server:

bash
mkdocs serve
Visit http://localhost:8000 in your browser

Build documentation:

bash
mkdocs build
Documentation will be generated in the site/ directory

📖 Usage Guide
Creating Documentation
Add markdown files to the docs/ directory

Update mkdocs.yml to include your new pages:

YAML
nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - Your New Page: your-new-page.md
Write content in Markdown format

Customizing Appearance
Edit mkdocs.yml:

YAML
site_name: Your Project Name
theme:
  name: material
  palette:
    scheme: default
    primary: blue
    accent: red
  
nav:
  - Home: index.md
  - Documentation: docs.md
  - API: api/reference.md

plugins:
  - search
  - minify
Adding Navigation
Structure your mkdocs.yml:

YAML
nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Configuration: getting-started/config.md
  - User Guide:
    - Basic Usage: guide/usage.md
    - Advanced: guide/advanced.md
  - API Reference: api/reference.md
🔄 Automated Deployment
GitHub Actions Workflow
The project includes a GitHub Actions workflow (.github/workflows/publish-docs.yml) that:

Builds documentation automatically on push to main
Deploys to GitHub Pages
Makes documentation publicly accessible
Workflow triggers:

Push to main branch
Manual workflow dispatch
Manual Deployment
bash
# Build the site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
📝 Writing Documentation
Markdown Syntax
Markdown
# Heading 1
## Heading 2
### Heading 3

**Bold text**
*Italic text*
`Code snippet`

- Bullet point
- Another point
  - Nested point

1. Numbered list
2. Second item

[Link text](https://example.com)

![Image alt](path/to/image.png)

```code
Code block
Code

### Code Blocks with Syntax Highlighting

````markdown
```python
def hello_world():
    print("Hello, World!")
JavaScript
console.log("Hello, World!");
Code

## 🎨 Customization

### Theme Configuration

Edit `mkdocs.yml`:

```yaml
theme:
  name: material
  palette:
    primary: indigo
    accent: cyan
  logo: assets/logo.png
  favicon: assets/favicon.ico
```

### Adding Extensions

```yaml
markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - tables
  - attr_list
  - md_in_html
```

## 🔐 Best Practices

- **Keep docs updated** - Update documentation alongside code changes
- **Use clear headings** - Organize content with proper heading hierarchy
- **Include examples** - Provide code examples in documentation
- **Link between pages** - Create cross-references for better navigation
- **Review before deploy** - Test locally before pushing to production
- **Version your docs** - Consider versioning for major releases

## 📊 Site Analytics

To add analytics (Google Analytics):

```yaml
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX
```

## 🚢 Deployment Status

- **Documentation Site**: [Visit Live Documentation](https://sushversesai-pixel.github.io/auto-documenter/)
- **Status**: ✅ Active and Deployed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write/update documentation
4. Test locally: `mkdocs serve`
5. Commit changes: `git commit -m "Add documentation"`
6. Push: `git push origin feature/your-feature`
7. Submit a pull request

## 📚 Resources & Documentation

- [MkDocs Official Documentation](https://www.mkdocs.org)
- [Material for MkDocs Theme](https://squidfunk.github.io/mkdocs-material/)
- [Markdown Guide](https://www.markdownguide.org)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Guide](https://docs.github.com/en/actions)

## 📋 Dependencies

Key dependencies from `requirements.txt`:
- `mkdocs` - Documentation framework
- `mkdocs-material` - Material theme for MkDocs
- `pymdown-extensions` - Additional Markdown extensions
- `mkdocs-minify` - Minify HTML output

Install all dependencies:
```bash
pip install -r requirements.txt
```

## 🐛 Troubleshooting

### Port Already in Use

If port 8000 is already in use:
```bash
mkdocs serve -a 127.0.0.1:8001
```

### Build Failures

Check for YAML syntax errors in `mkdocs.yml`:
```bash
mkdocs build --verbose
```

### GitHub Pages Not Updating

1. Verify workflow completed successfully in Actions tab
2. Check GitHub Pages settings in repository settings
3. Ensure `gh-pages` branch exists

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

**Sai Susmitha**
