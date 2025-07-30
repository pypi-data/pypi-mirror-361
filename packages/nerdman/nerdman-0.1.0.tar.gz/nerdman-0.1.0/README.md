# NerdMan 🎨

A powerful Python library and command-line tool for working with Nerd Fonts icons. NerdMan provides easy access to thousands of Nerd Fonts icons with search, filtering, and export capabilities.

## 🚀 Features

- **🔍 Icon Search**: Search icons by name with literal or regex patterns
- **📊 Icon Information**: Get detailed information about any icon including Unicode codes
- **🎲 Random Icons**: Generate random icons for testing or inspiration
- **📁 Category Organization**: Browse icons organized by prefix categories
- **🔗 Similar Icon Finding**: Find icons with similar names using Levenshtein distance
- **💾 Export Capabilities**: Export icon lists in multiple formats (simple, detailed, CSV)
- **🌐 HTML Cheatsheet**: Generate beautiful, interactive HTML cheatsheets
- **🔄 Auto-Updates**: Automatically update icon data from Nerd Fonts repository
- **⚙️ Configurable**: Flexible configuration with multiple update modes
- **🎯 Unicode Search**: Find icons by Unicode code points
- **✅ Validation**: Validate icon names and check data integrity

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install nerdman
```

### From Source

```bash
git clone https://github.com/yourusername/nerdman.git
cd nerdman
pip install -e .
```

## 🏃‍♂️ Quick Start

### As a Python Library

```python
import nerdman

# Get an icon by name
home_icon = nerdman.icon("cod-home")
print(f"Home icon: {home_icon}")

# Search for icons
file_icons = nerdman.search_icons("file")
print(f"Found {len(file_icons)} file-related icons")

# Get detailed icon information
info = nerdman.icon_data("dev-git")
if info:
    print(f"Name: {info['name']}")
    print(f"Character: {info['char']}")
    print(f"Unicode: {info['code']}")

# Get random icons
random_icons = nerdman.get_random_icons(5)
for name, char in random_icons:
    print(f"{name}: {char}")
```

### Command Line Interface

```bash
# Show help
nerdman help

# Show specific icon details
nerdman show cod-home

# Generate HTML cheatsheet
nerdman cheat

# Export icons to file
nerdman export simple
nerdman export detailed
nerdman export csv

# Check for updates
nerdman update

# View current configuration
nerdman view-config

# Verify JSON data integrity
nerdman verify-json

# Show version information
nerdman version
```

## 📚 API Reference

### Core Functions

#### `icon(name: str) -> str`

Returns the icon character for a given name, or '?' if not found.

```python
home_icon = nerdman.icon("cod-home")
# Returns: ''
```

#### `icon_data(name: str) -> dict | None`

Returns detailed information about an icon.

```python
info = nerdman.icon_data("cod-home")
# Returns: {
#     'name': 'cod-home',
#     'char': '',
#     'rendered': '',
#     'code': 'ea60'
# }
```

#### `search_icons(query: str, use_regex: bool = False) -> dict`

Search for icons matching a query.

```python
# Literal search
results = nerdman.search_icons("home")

# Regex search
results = nerdman.search_icons(r"file.*", use_regex=True)
```

#### `get_categories() -> Dict[str, List[str]]`

Get icons organized by category prefixes.

```python
categories = nerdman.get_categories()
print(f"Categories: {list(categories.keys())}")
```

#### `get_random_icons(count: int = 5) -> List[Tuple[str, str]]`

Get random icons for testing or inspiration.

```python
random_icons = nerdman.get_random_icons(10)
```

#### `find_similar_icons(name: str, limit: int = 10) -> List[Tuple[str, str, int]]`

Find icons with similar names using Levenshtein distance.

```python
similar = nerdman.find_similar_icons("cod-home", limit=5)
```

### Export Functions

#### `export_icon_list(filename: str = None, format_type: str = "simple")`

Export icons to a file in various formats.

```python
# Export simple list
nerdman.export_icon_list("icons.txt", "simple")

# Export detailed information
nerdman.export_icon_list("icons_detailed.txt", "detailed")

# Export as CSV
nerdman.export_icon_list("icons.csv", "csv")
```

#### `create_icon_cheatsheet(output_file: str = "nerd_fonts_cheatsheet.html")`

Generate an interactive HTML cheatsheet.

```python
nerdman.create_icon_cheatsheet("my_cheatsheet.html")
```

### Update Functions

#### `update_nerdfonts_data(url: str = None, force: bool = False) -> bool`

Update the Nerd Fonts data.

```python
# Update from default source
success = nerdman.update_nerdfonts_data()

# Force update even if current
success = nerdman.update_nerdfonts_data(force=True)
```

#### `check_for_updates(url: str = None) -> Dict[str, Any]`

Check for available updates without downloading.

```python
update_info = nerdman.check_for_updates()
if update_info['update_available']:
    print("Update available!")
```

### Utility Functions

#### `validate_icon_name(name: str) -> bool`

Check if an icon name exists.

```python
exists = nerdman.validate_icon_name("cod-home")  # True
```

#### `get_icon_count() -> int`

Get the total number of available icons.

```python
total = nerdman.get_icon_count()
print(f"Total icons: {total}")
```

#### `search_by_unicode(unicode_code: str) -> Optional[Tuple[str, str]]`

Find an icon by its Unicode code.

```python
result = nerdman.search_by_unicode("ea60")
if result:
    name, char = result
    print(f"Found: {name} = {char}")
```

## ⚙️ Configuration

NerdMan creates a configuration file at `~/.nerdman/config.ini` with the following options:

```ini
[updates]
update_mode = notify
```

### Update Modes

- **auto**: Automatically download updates when available
- **notify**: Prompt user before downloading updates (default)
- **manual**: Never auto-update, require explicit calls

## 🎨 HTML Cheatsheet

The HTML cheatsheet feature generates a beautiful, interactive webpage with:

- **Searchable Interface**: Real-time search filtering
- **Category Organization**: Icons grouped by prefixes
- **Copy to Clipboard**: Click any icon to copy its name
- **Responsive Design**: Works on desktop and mobile
- **Statistics**: Shows total icons and categories
- **Modern UI**: Beautiful gradients and smooth animations

## 📁 File Structure

After installation, NerdMan creates the following directory structure:

```plaintext
~/nerdman/
├── config.ini                 # Configuration file
├── nerdfonts_complete.json    # Icon data (auto-downloaded)
└── nerdfonts_complete.json.backup  # Backup of previous data
```

## 🔧 Development

### Setting up for Development

```bash
git clone https://github.com/yourusername/nerdman.git
cd nerdman
pip install -e ".[dev]"
```

### Running Tests

```bash
python -m pytest tests/
```

### Building Documentation

```bash
python -m sphinx docs/ docs/_build/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Nerd Fonts](https://www.nerdfonts.com/) for providing the amazing icon fonts
- [Ryan L McIntyre](https://github.com/ryanoasis) for creating and maintaining Nerd Fonts
- The open-source community for inspiration and feedback

## 🐛 Issue Reporting

If you encounter any issues or have feature requests, please [open an issue](https://github.com/yourusername/nerdman/issues) on GitHub.

## 📊 Statistics

- **Supported Icons**: 8000+ icons from Nerd Fonts
- **Categories**: 20+ icon categories (cod, dev, fa, oct, etc.)
- **Export Formats**: 3 formats (simple, detailed, CSV)
- **Search Types**: Literal and regex search
- **Python Versions**: 3.7+

---

**Made with ❤️ for the developer community**
