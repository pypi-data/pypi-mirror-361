# nerdman.py
# Version V0.1.0

import json
import re
import random
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union, Any
from collections import defaultdict
import configparser
import os

os.makedirs(Path.home() / "nerdman", exist_ok=True)

CONFIG = configparser.ConfigParser()

if not os.path.exists(Path.home() / "nerdman" / "config.ini"):
    with open(Path.home() / "nerdman" / "config.ini", 'w') as f:
        f.write("[updates]\nupdate_mode = auto\n")
        
CONFIG.read(Path.home() / "nerdman" / "config.ini")

# Default GitHub URL for Nerd Fonts complete JSON
DEFAULT_NERDFONTS_URL = "https://raw.githubusercontent.com/ryanoasis/nerd-fonts/refs/heads/master/glyphnames.json"

UPDATE_MODE = CONFIG.get("updates", "update_mode", fallback=None)

if UPDATE_MODE is None or UPDATE_MODE not in ["auto", "notify", "manual"]:
    print("⚠️  No/invalid update mode configured. Defaulting to 'auto'.")
    UPDATE_MODE = "auto"

def update(required: bool = False, manual: bool = False) -> bool:
    """Update Nerd Fonts data based on the configured update mode."""
    if manual:
        print("🔔 An update is available!")
        if input("Update now? (y/N): ").strip().lower() == 'y':
            return update_nerdfonts_data()
        else:
            print("Update skipped.")
            if required:
                raise ValueError("Update required but user chose to skip. Please run update_nerdfonts_data() explicitly.")
            return False
    elif UPDATE_MODE == "auto":
        print("🔄 Auto-updating Nerd Fonts data...")
        return update_nerdfonts_data()
    elif UPDATE_MODE == "notify":
        print("🔔 An update is available!")
        if input("Update now? (y/N): ").strip().lower() == 'y':
            return update_nerdfonts_data()
        else:
            print("Update skipped.")
            if required:
                raise ValueError("Update required but user chose to skip. Please run update_nerdfonts_data() explicitly.")
            return False
    elif UPDATE_MODE == "manual":
        if required:
            raise ValueError("Manual update required but 'manual' mode is set. Please run update_nerdfonts_data() explicitly.")
        return False
    else:
        raise ValueError(f"Invalid update mode: {UPDATE_MODE}")

if UPDATE_MODE not in ["auto", "notify", "manual"]:
    raise ValueError(f"Invalid update mode: {UPDATE_MODE}")

# File path for the JSON data
JSON_FILE_PATH = Path.home() / "nerdman" / "nerdfonts_complete.json"

def download_nerdfonts_data(url: str = DEFAULT_NERDFONTS_URL, output_file: Optional[Union[str, Path]] = None) -> bool:
    """Download Nerd Fonts JSON data from a URL.
    
    Args:
        url: URL to download the JSON from
        output_file: Output file path (defaults to nerdfonts_complete.json)
    
    Returns:
        True if successful, False otherwise
    """
    if output_file is None:
        output_file = JSON_FILE_PATH
    else:
        output_file = Path(output_file)
    
    try:
        print(f"📥 Downloading Nerd Fonts data from: {url}")
        
        # Create a request with headers to avoid blocking
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                data = response.read()
                
                # Validate it's valid JSON
                try:
                    json_data = json.loads(data.decode('utf-8'))
                    
                    # Basic validation - check if it looks like Nerd Fonts data
                    if not isinstance(json_data, dict):
                        raise ValueError("Downloaded data is not a JSON object")
                    
                    # Look for some expected patterns
                    has_metadata = "METADATA" in json_data
                    has_icons = any(key.startswith(('cod-', 'dev-', 'fa-', 'oct-')) for key in json_data.keys())
                    
                    if not (has_metadata or has_icons):
                        print("⚠️  Warning: Downloaded data doesn't look like Nerd Fonts JSON")
                        response_text = input("Continue anyway? (y/N): ")
                        if response_text.lower() != 'y':
                            return False
                    
                    # Write to file
                    with open(output_file, 'wb') as f:
                        f.write(data)
                    
                    print(f"✅ Successfully downloaded to: {output_file}")
                    print(f"📊 Found {len(json_data)} items in the data")
                    
                    if has_metadata and "METADATA" in json_data:
                        metadata = json_data["METADATA"]
                        if "version" in metadata:
                            print(f"🏷️  Version: {metadata['version']}")
                        if "date" in metadata:
                            print(f"📅 Date: {metadata['date']}")
                    
                    return True
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Downloaded data is not valid JSON: {e}")
                    return False
                except ValueError as e:
                    print(f"❌ Data validation error: {e}")
                    return False
                    
            else:
                print(f"❌ HTTP Error: {response.status}")
                return False
                
    except urllib.error.URLError as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def update_nerdfonts_data(url: str = DEFAULT_NERDFONTS_URL, force: bool = False) -> bool:
    """Update the Nerd Fonts data file.
    
    Args:
        url: URL to download from
        force: If True, update even if file exists and is recent
    
    Returns:
        True if update was successful, False otherwise
    """
    global data, ICON_MAP, METADATA
    
    # Create backup if file exists
    if JSON_FILE_PATH.exists():
        backup_path = JSON_FILE_PATH.with_suffix('.json.backup')
        try:
            import shutil
            shutil.copy2(JSON_FILE_PATH, backup_path)
            print(f"💾 Created backup: {backup_path}")
        except Exception as e:
            print(f"⚠️  Could not create backup: {e}")
    
    # Download new data
    if download_nerdfonts_data(url):
        try:
            # Reload the data
            print("🔄 Reloading data...")
            data = _load_data()
            
            # Apply duplicate filtering
            print("🔄 Processing updated data and filtering duplicates...")
            raw_icons = {k: v for k, v in data.items() if k != "METADATA"}
            original_count = len(raw_icons)
            
            # Filter duplicates by Unicode character
            seen_chars = set()
            ICON_MAP = {}
            duplicates_removed = 0
            
            for name, icon_info in raw_icons.items():
                char = icon_info["char"]
                if char not in seen_chars:
                    seen_chars.add(char)
                    ICON_MAP[name] = char
                else:
                    duplicates_removed += 1
            
            print(f"📊 Filtered {duplicates_removed} duplicate icons (kept {len(ICON_MAP)} unique icons from {original_count} total)")
            
            METADATA = data.get("METADATA", {})
            print("✅ Data successfully updated and reloaded!")
            return True
        except Exception as e:
            print(f"❌ Error reloading data: {e}")
            # Restore backup if available
            backup_path = JSON_FILE_PATH.with_suffix('.json.backup')
            if backup_path.exists():
                try:
                    import shutil
                    shutil.copy2(backup_path, JSON_FILE_PATH)
                    print("🔄 Restored from backup")
                except Exception as restore_error:
                    print(f"❌ Could not restore backup: {restore_error}")
            return False
    else:
        print("❌ Update failed")
        return False

def _load_data():
    """Load icon data from JSON file, auto-update if missing."""
    if not JSON_FILE_PATH.exists():
        print("⚠️  Nerd Fonts JSON file not found.")
        update(required=True)
    
    try:
        with open(JSON_FILE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"❌ Error loading JSON file: {e}")
        print("🔄 Attempting to re-download...")
        update(required=True)
        with open(JSON_FILE_PATH, encoding="utf-8") as f:
            return json.load(f)

# Load data
data = _load_data()

# Strip metadata and filter duplicates
print("🔄 Processing icon data and filtering duplicates...")
raw_icons = {k: v for k, v in data.items() if k != "METADATA"}
original_count = len(raw_icons)

# Filter duplicates by Unicode character - keep the first occurrence (usually the primary name)
seen_chars = set()
ICON_MAP = {}
duplicates_removed = 0

for name, icon_info in raw_icons.items():
    char = icon_info["char"]
    if char not in seen_chars:
        seen_chars.add(char)
        ICON_MAP[name] = char
    else:
        duplicates_removed += 1

print(f"📊 Filtered {duplicates_removed} duplicate icons (kept {len(ICON_MAP)} unique icons from {original_count} total)")

# Get metadata for version info
METADATA = data.get("METADATA", {})

def icon(name: str) -> str:
    """Return icon glyph by Nerd Font name, or '?' if not found."""
    return ICON_MAP.get(name, "?")

def icon_data(name: str) -> dict | None:
    """Return icon data by Nerd Font name, or None if not found."""
    info = data.get(name)
    if info:
        char = info["char"]
        # Try to display the character properly, with fallback
        try:
            rendered_char = char
        except UnicodeEncodeError:
            rendered_char = f"[Unicode: {info['code']}]"
        
        info = {
            "name": name,
            "char": char,
            "rendered": rendered_char,
            "code": info["code"],
        }
        return info
    return None

def search_icons(query: str, use_regex: bool = False):
    """List icons with names matching the query.
    
    Args:
        query: Search pattern (literal string or regex if use_regex=True)
        use_regex: If True, treat query as regex pattern; if False, literal substring match
    """
    results = {}
    
    if use_regex:
        try:
            # Try to compile as regex
            pattern = re.compile(query, re.IGNORECASE)
            for k, v in ICON_MAP.items():
                if pattern.search(k):
                    try:
                        results[k] = v
                    except UnicodeEncodeError:
                        results[k] = f"[{v}]"
        except re.error:
            # If regex is invalid, fall back to literal search
            print(f"Invalid regex '{query}', falling back to literal search")
            for k, v in ICON_MAP.items():
                if query.lower() in k.lower():
                    try:
                        results[k] = v
                    except UnicodeEncodeError:
                        results[k] = f"[{v}]"
    else:
        # Simple substring search (case-insensitive)
        for k, v in ICON_MAP.items():
            if query.lower() in k.lower():
                try:
                    results[k] = v
                except UnicodeEncodeError:
                    results[k] = f"[{v}]"
    
    return results

def list_icons():
    """Return all icons as a sorted list."""
    return sorted(ICON_MAP.items())

def get_categories() -> Dict[str, List[str]]:
    """Group icons by their prefix categories."""
    categories = defaultdict(list)
    for name in ICON_MAP.keys():
        if '-' in name:
            prefix = name.split('-')[0]
            categories[prefix].append(name)
        else:
            categories['misc'].append(name)
    return dict(categories)

def get_random_icon() -> Tuple[str, str]:
    """Get a random icon name and character."""
    name = random.choice(list(ICON_MAP.keys()))
    return name, ICON_MAP[name]

def get_random_icons(count: int = 5) -> List[Tuple[str, str]]:
    """Get multiple random icons."""
    names = random.sample(list(ICON_MAP.keys()), min(count, len(ICON_MAP)))
    return [(name, ICON_MAP[name]) for name in names]

def find_similar_icons(name: str, limit: int = 10) -> List[Tuple[str, str, int]]:
    """Find icons with similar names using Levenshtein distance."""
    def levenshtein_distance(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    similarities = []
    name_lower = name.lower()
    
    for icon_name in ICON_MAP.keys():
        distance = levenshtein_distance(name_lower, icon_name.lower())
        if distance <= 5 and icon_name != name:  # Only include reasonably similar names
            similarities.append((icon_name, ICON_MAP[icon_name], distance))
    
    # Sort by distance (most similar first) and limit results
    similarities.sort(key=lambda x: x[2])
    return similarities[:limit]

def get_icon_count() -> int:
    """Get total number of available icons."""
    return len(ICON_MAP)

def validate_icon_name(name: str) -> bool:
    """Check if an icon name exists."""
    return name in ICON_MAP

def get_version_info() -> Dict[str, str]:
    """Get Nerd Fonts version information."""
    return METADATA

def search_by_unicode(unicode_code: str) -> Optional[Tuple[str, str]]:
    """Find icon by Unicode code (e.g., 'ea60', 'f015')."""
    unicode_code = unicode_code.lower()
    for name, icon_data in data.items():
        if name != "METADATA" and icon_data.get("code", "").lower() == unicode_code:
            return name, icon_data["char"]
    return None

def export_icon_list(filename: str | None = None, format_type: str = "simple") -> None:
    """Export icon list to a file in various formats.
    
    Args:
        filename: Output filename
        format_type: 'simple', 'detailed', or 'csv'
    """
    if filename is None:
        if format_type == "csv":
            filename = "nerdfonts_icons.csv"
        else:
            filename = "nerdfonts_icons.txt"
    file_path = Path.home() / "nerdman" / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        if format_type == "simple":
            for name, char in sorted(ICON_MAP.items()):
                f.write(f"{name}: {char}\n")
        elif format_type == "detailed":
            for name in sorted(ICON_MAP.keys()):
                icon_info = icon_data(name)
                if icon_info:
                    f.write(f"Name: {icon_info['name']}\n")
                    f.write(f"Character: {icon_info['char']}\n")
                    f.write(f"Unicode Code: {icon_info['code']}\n")
                    f.write("-" * 30 + "\n")
        elif format_type == "csv":
            f.write("name,character,unicode_code\n")
            for name in sorted(ICON_MAP.keys()):
                icon_info = icon_data(name)
                if icon_info:
                    f.write(f"{name},{icon_info['char']},{icon_info['code']}\n")
    
    print(f"Icons exported to {file_path}")

def create_icon_cheatsheet(output_file: str = "nerd_fonts_cheatsheet.html") -> None:
    """Create an HTML cheatsheet of all icons organized by category."""
    print("📝 Creating HTML cheatsheet... This may take some time.")
    categories = get_categories()
    output_path = Path.home() / "nerdman" / output_file
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nerd Fonts Cheatsheet</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/hack-font@3.3.0/build/web/hack.css" rel="stylesheet">
    <style>
        @font-face {{
            font-family: 'Nerd Font';
            src: url('https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/JetBrainsMono/Ligatures/Regular/JetBrainsMonoNerdFont-Regular.ttf') format('truetype');
            font-display: swap;
        }}
        
        body {{ 
            font-family: 'JetBrains Mono', 'Hack', 'Courier New', monospace; 
            margin: 20px; 
            line-height: 1.6;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .category {{ 
            margin-bottom: 40px; 
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .category h2 {{ 
            color: #333; 
            background: #f8f9fa;
            margin: 0;
            padding: 20px;
            border-bottom: 3px solid #007bff;
            font-size: 1.5em;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .category-count {{
            font-size: 0.8em;
            color: #666;
            background: #fff;
            padding: 4px 8px;
            border-radius: 12px;
            border: 1px solid #ddd;
        }}
        .all-icons-grid {{
            display: none;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 15px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .icon-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); 
            gap: 15px; 
            padding: 20px;
        }}
        .icon-item {{ 
            border: 1px solid #e0e0e0; 
            padding: 15px; 
            text-align: center; 
            border-radius: 8px;
            background: #ffffff;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
        }}
        .icon-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border-color: #007bff;
        }}
        .icon-char {{ 
            font-size: 32px; 
            margin-bottom: 8px; 
            color: #333;
            font-family: 'Nerd Font', 'JetBrains Mono', 'Hack', monospace;
            min-height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .icon-fallback {{
            font-size: 14px;
            color: #666;
            background: #fffacd;
            padding: 4px;
            border-radius: 4px;
            border: 1px solid #ddd;
            margin-bottom: 8px;
        }}
        .icon-name {{ 
            font-size: 11px; 
            color: #666; 
            word-break: break-all; 
            font-family: 'Courier New', monospace;
            background: #f8f9fa;
            padding: 4px 8px;
            border-radius: 4px;
            margin-top: 8px;
        }}
        .unicode-code {{
            font-size: 10px;
            color: #999;
            margin-top: 4px;
            font-family: monospace;
        }}
        .search-box {{
            position: sticky;
            top: 20px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            z-index: 100;
        }}
        .search-input {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 16px;
            box-sizing: border-box;
            margin-bottom: 15px;
        }}
        .search-input:focus {{
            outline: none;
            border-color: #007bff;
        }}
        .controls {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .toggle-btn {{
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.3s;
        }}
        .toggle-btn:hover {{
            background: #0056b3;
        }}
        .toggle-btn.active {{
            background: #28a745;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            text-align: center;
        }}
        .stat-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex: 1;
            margin: 0 10px;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        @media (max-width: 768px) {{
            .icon-grid {{ 
                grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); 
                gap: 10px; 
                padding: 15px;
            }}
            .header h1 {{ font-size: 2em; }}
            .stats {{ flex-direction: column; }}
            .stat-item {{ margin: 5px 0; }}
        }}
    </style>
</head>
<body>    
    <div class="header">
        <h1>🎨 Nerd Fonts Cheatsheet</h1>
        <p>Complete icon reference with {total_count} icons</p>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{total_count}</div>
                <div class="stat-label">Total Icons</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{category_count}</div>
                <div class="stat-label">Categories</div>
            </div>
        </div>
    </div>
    
    <div class="search-box">
        <input type="text" class="search-input" placeholder="🔍 Search icons... (e.g., 'home', 'file', 'git')" 
               onkeyup="filterIcons(this.value)">
        <div class="controls">
            <button class="toggle-btn" onclick="toggleCategories()" id="categoryToggle">
                📁 Show All Icons
            </button>
        </div>
    </div>
    
    <div id="allIconsSection" style="display: none;">
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;">
            <h2 style="margin: 0; display: flex; justify-content: space-between; align-items: center;">
                🎨 All Icons
                <span class="category-count" id="allIconsCount">{total_count} icons</span>
            </h2>
        </div>
        <div class="all-icons-grid" id="allIconsGrid">
        </div>
    </div>
    
    <div id="categoriesSection">
""".format(total_count=get_icon_count(), category_count=len(categories))
    
    for category, icons in sorted(categories.items()):
        html_content += f"""
    <div class="category" data-category="{category}">
        <h2>
            📁 {category.upper()}
            <span class="category-count" data-total="{len(icons)}" id="count-{category}">{len(icons)} icons</span>
        </h2>
        <div class="icon-grid">
        """
        
        for icon_name in sorted(icons):
            char = ICON_MAP[icon_name]
            # Escape HTML characters and make search-friendly
            escaped_name = icon_name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Get unicode code for fallback display
            icon_info = icon_data(icon_name)
            unicode_code = icon_info['code'] if icon_info else 'N/A'
            
            # Add to both category and all icons grid
            icon_html = f"""
            <div class="icon-item" data-name="{escaped_name.lower()}" data-category="{category}"
                 onclick="copyToClipboard('{escaped_name}')" 
                 title="Click to copy icon name: {escaped_name}">
                <div class="icon-char" data-unicode="\\u{unicode_code}">{char}</div>
                <div class="icon-fallback">U+{unicode_code.upper()}</div>
                <div class="icon-name">{escaped_name}</div>
                <div class="unicode-code">\\u{unicode_code}</div>
            </div>
            """
            
            html_content += icon_html
        
        html_content += """
        </div>
    </div>
        """
    
    html_content += """
    </div>
        """
    
    html_content += """
    <script>
        let showingCategories = true;
        let allIconsPopulated = false;
        
        // Check if Nerd Fonts are available
        function checkNerdFontSupport() {
            // Simplified detection - always return false to hide notice
            return false;
        }
        
        function populateAllIconsGrid() {{
            if (allIconsPopulated) return;
            
            const allIconsGrid = document.getElementById('allIconsGrid');
            const categoryItems = document.querySelectorAll('.category .icon-item');
            
            // Clone all icons into the all icons grid
            categoryItems.forEach(item => {{
                const clone = item.cloneNode(true);
                allIconsGrid.appendChild(clone);
            }});
            
            allIconsPopulated = true;
        }}
        
        function toggleCategories() {{
            const categoriesSection = document.getElementById('categoriesSection');
            const allIconsSection = document.getElementById('allIconsSection');
            const allIconsGrid = document.getElementById('allIconsGrid');
            const toggleBtn = document.getElementById('categoryToggle');
            
            showingCategories = !showingCategories;
            
            if (showingCategories) {{
                // Show categories
                categoriesSection.style.display = 'block';
                allIconsSection.style.display = 'none';
                allIconsGrid.style.display = 'none';
                toggleBtn.textContent = '📁 Show All Icons';
                toggleBtn.classList.remove('active');
            }} else {{
                // Show all icons
                populateAllIconsGrid();
                categoriesSection.style.display = 'none';
                allIconsSection.style.display = 'block';
                allIconsGrid.style.display = 'grid';
                toggleBtn.textContent = '📂 Show Categories';
                toggleBtn.classList.add('active');
            }}
            
            // Re-apply current search
            const searchInput = document.querySelector('.search-input');
            filterIcons(searchInput.value);
        }}
        
        function updateCounters() {
            let totalVisible = 0;
            let visibleCategories = 0;
            
            if (showingCategories) {
                // Update category counters
                const categories = document.querySelectorAll('.category');
                categories.forEach(category => {
                    const categoryName = category.getAttribute('data-category');
                    const counter = document.getElementById(`count-${categoryName}`);
                    const visibleItems = category.querySelectorAll('.icon-item[style*="display: block"], .icon-item:not([style*="display: none"])');
                    const totalItems = counter.getAttribute('data-total');
                    
                    if (visibleItems.length > 0) {
                        counter.textContent = `${visibleItems.length} of ${totalItems} icons`;
                        category.style.display = 'block';
                        visibleCategories++;
                        totalVisible += visibleItems.length;
                    } else {
                        category.style.display = 'none';
                    }
                });
            } else {
                // Update all icons counter
                const allIconsGrid = document.getElementById('allIconsGrid');
                const visibleItems = allIconsGrid.querySelectorAll('.icon-item[style*="display: block"], .icon-item:not([style*="display: none"])');
                const allIconsCount = document.getElementById('allIconsCount');
                const totalItems = document.querySelectorAll('.category .icon-item').length;
                
                allIconsCount.textContent = `${visibleItems.length} of ${totalItems} icons`;
                totalVisible = visibleItems.length;
            }
            
            return totalVisible;
        }
        
        function filterIcons(searchTerm) {{
            searchTerm = searchTerm.toLowerCase();
            
            if (showingCategories) {{
                // Filter in categories view
                const categories = document.querySelectorAll('.category');
                categories.forEach(category => {{
                    const categoryItems = category.querySelectorAll('.icon-item');
                    
                    categoryItems.forEach(item => {{
                        const name = item.getAttribute('data-name');
                        if (!searchTerm || name.includes(searchTerm)) {{
                            item.style.display = 'block';
                        }} else {{
                            item.style.display = 'none';
                        }}
                    }});
                }});
            }} else {{
                // Filter in all icons view
                const allIconsGrid = document.getElementById('allIconsGrid');
                const allItems = allIconsGrid.querySelectorAll('.icon-item');
                
                allItems.forEach(item => {{
                    const name = item.getAttribute('data-name');
                    if (!searchTerm || name.includes(searchTerm)) {{
                        item.style.display = 'block';
                    }} else {{
                        item.style.display = 'none';
                    }}
                }});
            }}
            
            // Update counters after filtering
            updateCounters();
        }}
        
        function copyToClipboard(iconName) {{
            navigator.clipboard.writeText(iconName).then(() => {{
                // Create toast notification
                const toast = document.createElement('div');
                toast.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #28a745;
                    color: white;
                    padding: 12px 20px;
                    border-radius: 6px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    z-index: 1000;
                    font-family: Arial, sans-serif;
                    animation: slideIn 0.3s ease;
                `;
                toast.textContent = `Copied: ${iconName}`;
                document.body.appendChild(toast);
                
                setTimeout(() => {{
                    toast.remove();
                }}, 2000);
            }}).catch(err => {{
                console.error('Failed to copy: ', err);
                alert(`Icon name: ${iconName}`);
            }});
        }}
        
        // Add CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        // Add keyboard shortcut for search
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'f') {
                e.preventDefault();
                document.querySelector('.search-input').focus();
            }
            if (e.key === 'Escape') {
                document.querySelector('.search-input').value = '';
                filterIcons('');
            }
        });
        
        // Initialize page
        window.addEventListener('load', () => {
            // Auto-focus search
            document.querySelector('.search-input').focus();
            
            // Initialize counters
            updateCounters();
        });
    </script>
</body>
</html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML cheatsheet created: {output_path}")
    print(f"Open it in your browser via: file://{output_path.resolve()}")

def check_for_updates(url: str = DEFAULT_NERDFONTS_URL) -> Dict[str, Any]:
    """Check if updates are available without downloading.
    
    Args:
        url: URL to check for updates
    
    Returns:
        Dictionary with update information
    """
    result = {
        "update_available": False,
        "current_version": None,
        "remote_version": None,
        "current_date": None,
        "remote_date": None,
        "error": None
    }
    
    try:
        # Get current version info
        current_metadata = get_version_info()
        result["current_version"] = current_metadata.get("version", "unknown")
        result["current_date"] = current_metadata.get("date", "unknown")
        
        # Check remote version
        print("🔍 Checking for updates...")
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                # Only read first few KB to get metadata
                sample_data = response.read(8192).decode('utf-8')
                
                # Try to extract metadata without loading full file
                if '"METADATA"' in sample_data:
                    # Basic regex to find version and date
                    import re
                    version_match = re.search(r'"version":\s*"([^"]+)"', sample_data)
                    date_match = re.search(r'"date":\s*"([^"]+)"', sample_data)
                    
                    if version_match:
                        result["remote_version"] = version_match.group(1)
                    if date_match:
                        result["remote_date"] = date_match.group(1)
                    
                    # Compare versions
                    if (result["remote_version"] and result["current_version"] and 
                        result["remote_version"] != result["current_version"]):
                        result["update_available"] = True
                    elif (result["remote_date"] and result["current_date"] and 
                          result["remote_date"] != result["current_date"]):
                        result["update_available"] = True
                
    except Exception as e:
        result["error"] = str(e)
    
    return result

def set_custom_url(new_url: str) -> bool:
    """Set a custom URL for Nerd Fonts data updates.
    
    Args:
        new_url: The new URL to use for updates
    
    Returns:
        True if URL is valid and accessible, False otherwise
    """
    global DEFAULT_NERDFONTS_URL
    
    try:
        # Test the URL
        req = urllib.request.Request(
            new_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                # Test first few bytes to see if it's JSON
                sample = response.read(512)
                if sample.strip().startswith(b'{'):
                    DEFAULT_NERDFONTS_URL = new_url
                    print(f"✅ Custom URL set: {new_url}")
                    
                    # Save to a config file for persistence
                    config_path = Path.home() / "nerdman" / "nerdfonts_config.json"
                    config = {"custom_url": new_url}
                    with open(config_path, 'w') as f:
                        json.dump(config, f)
                    
                    return True
                else:
                    print("❌ URL does not appear to serve JSON data")
                    return False
            else:
                print(f"❌ URL returned status {response.status}")
                return False
    except Exception as e:
        print(f"❌ Error testing URL: {e}")
        return False

# Load custom URL from config if available
def _load_custom_url():
    """Load custom URL from config file if it exists."""
    global DEFAULT_NERDFONTS_URL
    config_path = Path.home() / "nerdman" / "nerdfonts_config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                if "custom_url" in config:
                    DEFAULT_NERDFONTS_URL = config["custom_url"]
        except Exception:
            pass  # Ignore config errors

# Initialize custom URL
_load_custom_url()


# ================================
# EXAMPLE USAGE AND DEMONSTRATIONS
# ================================

def main():
    """Demonstrate all features of the Nerd Font module."""
    
    from sys import argv
    if len(argv) > 1:
        arg = argv[1]
        if arg == "cheat":
            create_icon_cheatsheet()
            return
        elif arg == "export":
            if len(argv) < 3:
                print("Usage: nerdman export <simple|detailed|csv>")
                return
            format_type = argv[2]
            if format_type not in ["simple", "detailed", "csv"]:
                print("Invalid format type. Use 'simple', 'detailed', or 'csv'.")
                return
            export_icon_list(format_type=format_type)
            return
        elif arg == "update":
            update_info = check_for_updates()
            if update_info.get("error"):
                print(f"Error checking updates: {update_info['error']}")
            else:
                print(f"Current version: {update_info.get('current_version', 'unknown')}")
                print(f"Remote version: {update_info.get('remote_version', 'unknown')}")
                if update_info.get("update_available"):
                    update_nerdfonts_data(force=True)
                else:
                    print("You are up to date!")
            return
        elif arg == "version":
            version_info = get_version_info()
            print("NerdMan Version V0.1.0\n")
            print(f"Nerd Fonts Version: {version_info.get('version', 'unknown')}")
            print(f"Date: {version_info.get('date', 'unknown')}")
            return
        elif arg == "view-config":
            print("Current Nerd Fonts Configuration:")
            for section in CONFIG.sections():
                print(f"{section.upper()}:")
                for k, v in CONFIG.items(section):
                    print(f"  {k}: {v}")
            return
        elif arg == "verify-json":
            try:
                with open(Path.home() / "nerdman" / "nerdfonts_complete.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print("JSON data is valid.")
                print(f"Total icons: {len(data) - 1}")
            except json.JSONDecodeError as e:
                print(f"JSON data is invalid: {e}")
            except FileNotFoundError:
                print("JSON file not found. Please ensure 'nerdfonts_complete.json' exists in the same directory.")
            except Exception as e:
                print(f"An error occurred while verifying JSON: {e}")
            return
        elif arg == "show":
            if len(argv) < 3:
                print("Usage: nerdman show <icon_name>")
                return
            icon_name = argv[2]
            info = icon_data(icon_name)
            if info:
                print(f"Icon Name: {info['name']}")
                print(f"Character (rendered): {info['char']}")
                print(f"Unicode Code: {info['code']}")
            else:
                print(f"No icon found with name '{icon_name}'")
            return
        elif arg == "help":
            print("Usage: nerdman [command]")
            print("Commands:")
            print("  <blank> - Run the demo")
            print("  cheat - Create HTML cheatsheet")
            print("  export <simple|detailed|csv> - Export icons to file")
            print("  verify-json - Verify JSON data integrity")
            print("  view-config - View current Nerd Fonts configuration")
            print("  show <icon_name> - Show detailed information about an icon")
            print("  update - Check for updates and download if available")
            print("  version - Show version information")
            print("  help - Show this help message")
            return
    
    print("🚀 NERD FONTS MODULE DEMO")
    print("=" * 50)
    
    # Version information
    print("\n📋 VERSION INFO:")
    version_info = get_version_info()
    for key, value in version_info.items():
        print(f"  {key}: {value}")
    
    # Basic icon lookup
    print(f"\n🔍 BASIC ICON LOOKUP:")
    test_icons = ["cod-home", "cod-folder", "cod-file", "dev-git", "fa-star"]
    for icon_name in test_icons:
        char = icon(icon_name)
        print(f"  {icon_name}: {char}")
    
    # Detailed icon information
    print(f"\n📊 DETAILED ICON INFO:")
    detail_icon = "cod-home"
    info = icon_data(detail_icon)
    if info:
        print(f"  Name: {info['name']}")
        print(f"  Character: {info['char']}")
        print(f"  Unicode Code: {info['code']}")
        print(f"  Rendered: {info['rendered']}")
    
    # Search functionality
    print(f"\n🔎 SEARCH EXAMPLES:")
    search_results = search_icons("home", use_regex=False)
    print(f"  Found {len(search_results)} icons containing 'home':")
    for name, char in list(search_results.items())[:5]:  # Show first 5
        print(f"    {name}: {char}")
    
    # Regex search
    print(f"\n🔍 REGEX SEARCH (icons ending with 'file'):");
    regex_results = search_icons(r"file$", use_regex=True)
    for name, char in list(regex_results.items())[:5]:
        print(f"    {name}: {char}")
    
    # Categories
    print(f"\n📁 ICON CATEGORIES:")
    categories = get_categories()
    for category, icons in list(categories.items())[:5]:  # Show first 5 categories
        print(f"  {category}: {len(icons)} icons")
    
    # Random icons
    print(f"\n🎲 RANDOM ICONS:")
    random_icons = get_random_icons(5)
    for name, char in random_icons:
        print(f"  {name}: {char}")
    
    # Similar icons
    print(f"\n🔗 SIMILAR ICONS (to 'cod-home'):");
    similar = find_similar_icons("cod-home", limit=5)
    for name, char, distance in similar:
        print(f"  {name}: {char} (distance: {distance})")
    
    # Unicode search
    print(f"\n🔢 UNICODE SEARCH:");
    unicode_result = search_by_unicode("ea60")
    if unicode_result:
        name, char = unicode_result
        print(f"  Unicode 'ea60': {name} = {char}")
    
    # Statistics
    print(f"\n📈 STATISTICS:")
    print(f"  Total icons: {get_icon_count()}")
    print(f"  Total categories: {len(get_categories())}")
    
    # Validation
    print(f"\n✅ VALIDATION:")
    test_names = ["cod-home", "invalid-icon", "dev-git"]
    for name in test_names:
        is_valid = validate_icon_name(name)
        print(f"  '{name}' exists: {is_valid}")
    
    # Export examples (commented out to avoid creating files automatically)
    print(f"\n💾 EXPORT CAPABILITIES:")
    print("  - export_icon_list('icons.txt', 'simple')")
    print("  - export_icon_list('icons.csv', 'csv')")
    print("  - export_icon_list('icons_detailed.txt', 'detailed')")
    print("  - create_icon_cheatsheet('cheatsheet.html')")
    
    # Update features demonstration
    print(f"\n🔄 UPDATE FEATURES:")
    print(f"  Current URL: {DEFAULT_NERDFONTS_URL}")
    
    # Check for updates (quick check)
    print("  Checking for updates...")
    update_info = check_for_updates()
    if update_info.get("error"):
        print(f"    ❌ Error checking updates: {update_info['error']}")
    else:
        print(f"    📋 Current version: {update_info.get('current_version', 'unknown')}")
        print(f"    📅 Current date: {update_info.get('current_date', 'unknown')}")
        if update_info.get("remote_version"):
            print(f"    � Remote version: {update_info['remote_version']}")
        if update_info.get("update_available"):
            print("    🆕 Update available!")
        else:
            print("    ✅ Up to date!")
    
    print(f"\n💡 UPDATE COMMANDS:")
    print("  - update_nerdfonts_data()  # Manual update")
    print("  - update_nerdfonts_data(force=True)  # Force update")
    print("  - check_for_updates()  # Check without downloading")
    print("  - set_custom_url('your_github_url')  # Use custom source")
    
    print(f"\n�🎉 Demo complete! This module provides:")
    print("  ✓ Basic icon lookup and validation")
    print("  ✓ Advanced search (literal and regex)")
    print("  ✓ Category organization")
    print("  ✓ Random icon selection")
    print("  ✓ Similar icon finding")
    print("  ✓ Unicode code lookup")
    print("  ✓ Export capabilities")
    print("  ✓ HTML cheatsheet generation")
    print("  ✓ Comprehensive icon statistics")
    print("  ✓ Automatic updates from GitHub")
    print("  ✓ Custom URL support")
    print("  ✓ Update checking and version management")


if __name__ == "__main__":
    main()