# Discourse Data Analysis

A Jupyter Book site for analyzing discourse forum data
https://dgan11.github.io/discourse-analysis/intro.html


## 🚀 Quick Start

### Setup
1. Clone the repository:
```bash
git clone https://github.com/dgan11/discourse-analysis
cd discourse-analysis
```
2. Install dependencies:
```bash
pip install jupyter-book
```
### 📝 Making Changes

#### File Structure
```
discourse-analysis/
├── config.yml # Site configuration
├── toc.yml # Table of contents
├── intro.md # Landing page
├── notebooks/ # Jupyter notebooks
│ ├── 00_basics.ipynb
│ └── 01_data_collection.ipynb
└── templates/ # Custom HTML templates
└── footer.html
```

#### Adding New Content
1. Add new notebooks to the `notebooks/` directory
2. Update `_toc.yml` to include new pages
3. Run and build the book (see below)

### 🔨 Building the Book

1. Execute all notebooks:
```bash
jupyter nbconvert --to notebook --execute notebooks/.ipynb --inplace
```
2. Build the book:
```bash
jupyter-book build .

# For a clean build
rm -rf build/
jupyter-book build . --all
```

### 🌐 Publishing Updates

The site is published using GitHub Pages. After making changes:

1. Build the book
2. Push changes to GitHub:
3. The site will automatically update at: https://dgan11.github.io/discourse-analysis/

## 📚 Book Configuration

- Site settings are in `_config.yml`
- Navigation structure is in `_toc.yml`
- Custom templates are in `_templates/`

## 📖 Resources

- [Jupyter Book Documentation](https://jupyterbook.org/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)