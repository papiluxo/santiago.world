#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import xml.etree.ElementTree as ET
from pdf2image import convert_from_path
import logging
import random
import signal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
SITE_ROOT = Path(__file__).parent
ARCHIVE_DIR = SITE_ROOT / 'archive'
TOOLBOX_DIR = SITE_ROOT / 'toolbox'
OUTPUT_DIR = SITE_ROOT

# Projects data
projects = {
    'ad_barnes_nature_reserve': {
        'tags': ['team', 'rhino', 'fall \'23', 'miami, fl', 'arc604'],
        'description': 'nature reserve proposal for public park, a.d. (doug) barnes, with offices, exhibit gallery (discovery room), auditorium and public congregation (resiliency room).'
    },
    'cannabis_farm': {
        'tags': ['individual', 'rhino', 'spring \'24', 'miami, fl', 'arc605'],
        'description': 'cannabis farm proposal equipped with flower cultivation and processing facilities, and public program for education.'
    },
    'chil_bookshelf': {
        'tags': ['individual', 'rhino', 'spring \'24', 'miami, fl', 'chil'],
        'description': 'modular bookshelf for chil (community, housing and identity lab) studio space. comprised of 13 aluminum pieces.'
    },
    'icosahedron_explosion': {
        'tags': ['individual', 'rhino', 'fall \'23', 'arc611'],
        'description': 'geometrical exploration of an icosahedron, a 20 face polyhedron.'
    },
    'illinois_institute_of_technology_dorms': {
        'tags': ['individual', 'rhino', 'grasshopper', 'kangaroo', 'fall \'24', 'chicago, il'],
        'link': 'grasshopper',
        'description': 'residential college building proposal for iit campus, with <a href="toolbox.html#illinois_institute_of_technology_truss_system" class="project-link" onclick="expandToolboxProject(event, \'illinois_institute_of_technology_truss_system\')">parametric truss system</a>.'
    },
    'janus_house': {
        'tags': ['individual', 'rhino', 'spring \'24', 'precedent', 'arc605'],
        'description': 'precedent study of studio sean canty\'s conceptual janus house.'
    },
    'lego_bridge': {
        'tags': ['individual', 'rhino', 'grasshopper', 'wasp', 'fall \'24', 'miami, fl', 'arc656'],
        'link': 'grasshopper',
        'description': 'bridge proposal, only using lego blocks, to go over lake osceola in the university of miami\'s campus. <a href="toolbox.html#lego_bridge_aggregation" class="project-link" onclick="expandToolboxProject(event, \'lego_bridge_aggregation\')">computational aggregation</a> used to develop form and path.'
    },
    'moca_playhouse': {
        'tags': ['team', 'rhino', 'summer \'24', 'miami, fl', 'chil'],
        'description': 'community activation with temporary install of a lumber house, in moca (museum of contemporary art, miami), inspired by miami\'s shotgun house vernacular.'
    },
    'nervi_dome': {
        'tags': ['individual', 'rhino', 'grasshopper', 'fall \'24', 'turin, it', 'arc656'],
        'link': 'grasshopper',
        'description': '<a href="toolbox.html#nervi_dome" class="project-link" onclick="expandToolboxProject(event, \'nervi_dome\')">form study</a> of pier luigi nervi\'s palazzetto dello sport, in turin, italy.'
    },
    'parametric_cup': {
        'tags': ['individual', 'rhino', 'grasshopper', 'fall \'24', 'arc656'],
        'link': 'grasshopper',
        'description': '<a href="toolbox.html#parametric_cup" class="project-link" onclick="expandToolboxProject(event, \'parametric_cup\')">form exploration</a> of a cup/glass.'
    },
    'parametric_remapping': {
        'tags': ['individual', 'rhino', 'grasshopper', 'fall \'24', 'arc656'],
        'link': 'grasshopper',
        'description': 'automated shape <a href="toolbox.html#parametric_remapping" class="project-link" onclick="expandToolboxProject(event, \'parametric_remapping\')">remapping exercise</a>.'
    },
    'parametric_stop': {
        'tags': ['individual', 'rhino', 'grasshopper', 'spring \'24', 'arc613'],
        'link': 'grasshopper',
        'description': 'bus stop proposal for university of miami\'s campus with <a href="toolbox.html#parametric_cup" class="project-link" onclick="expandToolboxProject(event, \'parametric_cup\')">scripted form definition</a>.'
    },
    'remote_research_center': {
        'tags': ['individual', 'rhino', 'grasshopper', 'fall \'24', 'la tortuga, venezuela', 'arc662'],
        'link': 'thermal_study',
        'description': 'off-grid marine biology research center proposal located in isla la tortuga, venezuela. environmental/comfort efficiency achieved through <a href="toolbox.html#thermal_study" class="project-link" onclick="expandToolboxProject(event, \'thermal_study\')">thermal study</a> and passive systems.'
    },
    'renault_center': {
        'tags': ['individual', 'rhino', 'fall \'24', 'swindon, uk', 'precedent', 'arc607'],
        'description': 'precedent study of foster + partners\' renault center, in swindon, uk.'
    },
    'rome_artist_residence': {
        'tags': ['team', 'rhino', 'summer \'24', 'rome, it', 'arc606'],
        'description': 'adaptive reuse proposal for post-office in rome, italy to be adapted to a residential building for artists.'
    }
}

# Theme constants
THEMES = {
    'light': {
        'background': '#ffffff',  # White background
        'text': '#000000',        # Black text
        'accent': '#ff0000',      # Red accent
        'border': '#000000',      # Black border
        'hover': '#f5f5f5',       # Light grey for hover
        'card': '#ffffff',        # White card background
        'button': '#ff0000',      # Red button
        'button_hover': '#ff0000' # Same red for button hover
    },
    'dark': {
        'background': '#000000',  # Black background
        'text': '#ffffff',        # White text
        'accent': '#ff0000',      # Red accent
        'border': '#ffffff',      # White border
        'hover': '#1a1a1a',       # Dark grey for hover
        'card': '#000000',        # Black card background
        'button': '#ff0000',      # Red button
        'button_hover': '#ff0000' # Same red for button hover
    }
}

# Default theme
THEME = THEMES['light']

def get_tool_description(tool_name: str) -> str:
    """Get the description from the tool's readme file."""
    readme_path = TOOLBOX_DIR / f"{tool_name}_readme.txt"
    if readme_path.exists():
        with open(readme_path, 'r') as f:
            content = f.read().strip().split('\n')
            # Return the last non-empty line as the description
            for line in reversed(content):
                if line.strip():
                    # Convert uppercase to lowercase in the description
                    return line.strip().lower()
    return "a powerful toolkit that transforms complex operations into simple workflows."

def convert_pdf_to_preview(pdf_path: Path) -> List[Path]:
    """Check for existing previews in the preview directory."""
    preview_dir = pdf_path.parent / 'previews'
    if preview_dir.exists():
        existing_previews = sorted(preview_dir.glob(f'{pdf_path.stem}_*.png'))
        if existing_previews:
            logger.info(f"Using existing previews for {pdf_path}")
            return existing_previews
    return []

def get_first_image(folder_path: Path) -> Optional[Path]:
    """Get the first image (jpg, gif, or png) from a folder."""
    for ext in ['.jpg', '.jpeg', '.gif', '.png']:
        for file in folder_path.glob(f'*{ext}'):
            return file
    # If no image found, look for PDF and convert
    for pdf in folder_path.glob('*.pdf'):
        return convert_pdf_to_preview(pdf)[0]
    return None

def create_placeholder_readme(folder_path: Path) -> str:
    """Create a placeholder readme.txt if it doesn't exist."""
    readme_path = folder_path / 'readme.txt'
    if not readme_path.exists():
        description = random.choice(TOOL_DESCRIPTIONS)
        with open(readme_path, 'w') as f:
            f.write(description)
        return description
    with open(readme_path, 'r') as f:
        return f.read().strip()

def read_ghx_file(ghx_path: Path) -> str:
    """Read and format GHX file content."""
    try:
        if not ghx_path.exists():
            return "File not found"
        with open(ghx_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        logger.error(f"Error reading GHX file: {e}")
        return f"Error reading file: {str(e)}"

def get_navigation(current_page: str) -> str:
    """Generate the navigation buttons and theme toggle."""
    pages = {
        'home': 'index.html',
        'archive': 'archive.html',
        'toolbox': 'toolbox.html'
    }
    
    nav_items = []
    for name, link in pages.items():
        is_active = name == current_page
        active_class = ' active' if is_active else ''
        nav_items.append(f'<a href="{link}" class="nav-button{active_class}">{name}</a>')
    
    return f'''
    <style>
        .theme-toggle {{
            display: flex;
            align-items: center;
            border: 1px solid var(--border);
            border-radius: 4px;
            height: 3rem;
            padding: 0;
            position: relative;
            overflow: hidden;
            min-width: 110px;
        }}
        
        .theme-option {{
            padding: 0.5rem 0;
            font-size: 1.25rem;
            cursor: pointer;
            z-index: 1;
            position: relative;
            flex: 1;
            text-align: center;
            transition: color 0.3s ease;
            width: 55px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .theme-option.active {{
            color: var(--background);
        }}
        
        .theme-slider {{
            position: absolute;
            top: 4px;
            left: 4px;
            height: calc(100% - 8px);
            width: 50px;
            background-color: var(--accent);
            border-radius: 2px;
            transition: transform 0.3s ease;
        }}
        
        .theme-slider.dark {{
            transform: translateX(52px);
        }}
    </style>
    <div class="nav-container">
        <div class="nav-buttons">
            {"".join(nav_items)}
        </div>
        <div class="nav-right">
            <div class="theme-toggle">
                <div class="theme-option light active" onclick="toggleTheme('light')">☀</div>
                <div class="theme-option dark" onclick="toggleTheme('dark')">☾</div>
                <div class="theme-slider"></div>
            </div>
            <div id="clock" class="clock"></div>
        </div>
    </div>'''

def get_all_images(folder_path: Path) -> List[Path]:
    """Get all images (jpg, gif, png) from a folder."""
    images = []
    
    # First check if there's a previews directory
    previews_dir = folder_path / 'previews'
    if previews_dir.exists():
        # If previews directory exists, use those files
        for ext in ['.jpg', '.jpeg', '.gif', '.png', '.JPG', '.JPEG', '.GIF', '.PNG']:
            images.extend(previews_dir.glob(f'*{ext}'))
    else:
        # If no previews directory, use files from main directory
        for ext in ['.jpg', '.jpeg', '.gif', '.png', '.JPG', '.JPEG', '.GIF', '.PNG']:
            images.extend([
                f for f in folder_path.glob(f'*{ext}')
                if f.name != 'preview.png'  # Exclude old preview files
                and not f.stem.endswith('_presentation')  # Exclude presentation exports
            ])
    
    # Sort images naturally (so 1.jpg comes before 10.jpg)
    def natural_sort_key(path):
        import re
        # Split the filename (without extension) into text and number parts
        parts = re.split('([0-9]+)', path.stem)
        # Convert number parts to integers for proper sorting
        return [int(part) if part.isdigit() else part.lower() for part in parts]
    
    sorted_images = sorted(images, key=natural_sort_key)
    logger.info(f"Found {len(sorted_images)} images in {folder_path}:")
    for img in sorted_images:
        logger.info(f"  {img}")
    
    return sorted_images

def get_shared_search_js():
    """Generate the shared JavaScript code for search functionality."""
    return '''
    function performSearch() {
        const query = document.getElementById('searchInput').value.toLowerCase().trim();
        const resultsContainer = document.getElementById('searchResults');
        
        // Clear previous results
        resultsContainer.innerHTML = '';
        
        // If query is empty, hide results
        if (!query) {
            resultsContainer.classList.remove('active');
            return;
        }
        
        // Track results by type to avoid duplicates
        const projectResults = new Map();
        const toolResults = new Map();
        
        // Search in all projects - only keep the first match for each project name
        for (const [projectName, projectData] of Object.entries(projects)) {
            const searchText = (projectName + ' ' + 
                projectData.description + ' ' + 
                projectData.tags.join(' ')).toLowerCase();
            
            if (searchText.includes(query) && !projectResults.has(projectName)) {
                projectResults.set(projectName, {
                    title: projectName,
                    type: 'project',
                    url: 'archive.html?search=' + encodeURIComponent(query) + '#' + projectName
                });
            }
        }
        
        // Search in tools - only keep the first match for each tool name
        for (const [toolName, toolData] of Object.entries(tools)) {
            const searchText = (toolName + ' ' + 
                toolData.description + ' ' + 
                toolData.tags.join(' ')).toLowerCase();
            
            if (searchText.includes(query) && !toolResults.has(toolName)) {
                toolResults.set(toolName, {
                    title: toolName,
                    type: 'tool',
                    url: 'toolbox.html?search=' + encodeURIComponent(query) + '#' + toolName
                });
            }
        }
        
        // Combine results
        const results = [...projectResults.values(), ...toolResults.values()];
        
        // Display results
        if (results.length > 0) {
            results.forEach(result => {
                const resultItem = document.createElement('div');
                resultItem.className = 'search-result-item';
                resultItem.innerHTML = 
                    '<div class="search-result-title">' + result.title + '</div>' +
                    '<div class="search-result-tags">' + result.type + '</div>';
                resultItem.addEventListener('click', () => {
                    window.location.href = result.url;
                });
                resultsContainer.appendChild(resultItem);
            });
            resultsContainer.classList.add('active');
        } else {
            resultsContainer.classList.remove('active');
        }
    }
    
    // Add search input handler with debounce
    let searchTimeout;
    document.getElementById('searchInput').addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(performSearch, 300);
    });
    
    // Add search input handler for Enter key
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });'''

# Tools data
tools_dict = {}
for tool_dir in TOOLBOX_DIR.iterdir():
    if tool_dir.is_dir():
        gh_file = next(tool_dir.glob('*.gh'), None)
        ghx_file = next(tool_dir.glob('*.ghx'), None)
        if ghx_file:
            description = get_tool_description(tool_dir.name)
            tools_dict[tool_dir.name] = {
                'description': description,
                'tags': ['grasshopper']  # Default tag
            }
    elif tool_dir.suffix == '.ghx':
        description = get_tool_description(tool_dir.stem)
        tools_dict[tool_dir.stem] = {
            'description': description,
            'tags': ['grasshopper']  # Default tag
        }

# Add specific tags to tools
if 'illinois_institute_of_technology_truss_system' in tools_dict:
    tools_dict['illinois_institute_of_technology_truss_system']['tags'].append('kangaroo')
if 'lego_bridge_aggregation' in tools_dict:
    tools_dict['lego_bridge_aggregation']['tags'].append('wasp')

def generate_index_html():
    """Generate the landing page."""
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';">
    <title>santiago martínez-oropeza</title>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <style>
        :root {{
            /* Light theme (default) */
            --background: {THEMES['light']['background']};
            --text: {THEMES['light']['text']};
            --accent: {THEMES['light']['accent']};
            --border: {THEMES['light']['border']};
            --hover: {THEMES['light']['hover']};
            --card: {THEMES['light']['card']};
        }}
        
        /* Dark theme */
        [data-theme="dark"] {{
            --background: {THEMES['dark']['background']};
            --text: {THEMES['dark']['text']};
            --accent: {THEMES['dark']['accent']};
            --border: {THEMES['dark']['border']};
            --hover: {THEMES['dark']['hover']};
            --card: {THEMES['dark']['card']};
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: "SF Mono", Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            background-color: var(--background);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            width: 100%;
        }}
        
        .nav-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1rem;
        }}
        
        .nav-buttons {{
            display: flex;
            gap: 1rem;
        }}
        
        .nav-right {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .nav-button {{
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            color: var(--text);
            background-color: transparent;
            border: 1px solid var(--border);
            border-radius: 4px;
            text-decoration: none;
            transition: all 0.2s ease;
            height: 3rem;
            display: flex;
            align-items: center;
        }}
        
        .nav-button:hover {{
            color: var(--accent);
            border-color: var(--accent);
        }}
        
        .nav-button.active {{
            color: var(--accent);
            border-color: var(--accent);
        }}
        
        .clock {{
            font-size: 1rem;
            color: var(--text);
            padding: 0.75rem 1.5rem;
            border: 1px solid var(--border);
            border-radius: 4px;
            height: 3rem;
            display: flex;
            align-items: center;
        }}
        
        h1 {{
            font-size: 4rem;
            font-weight: 600;
            margin-bottom: 2rem;
            letter-spacing: -0.02em;
            color: var(--text);
        }}
        
        .revealing-text {{
            font-size: 1.2rem;
            line-height: 1.6;
            color: var(--text);
            margin-bottom: 2rem;
        }}
        
        .loading-dots {{
            display: inline-block;
            width: 1.2em;
            text-align: left;
        }}
        
        .loading-dots::after {{
            content: '';
            animation: loading 1.5s infinite;
        }}
        
        @keyframes loading {{
            0% {{ content: ''; }}
            33% {{ content: '.'; }}
            66% {{ content: '..'; }}
            100% {{ content: '...'; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {get_navigation('home')}
        <h1>santiago</h1>
        <div class="revealing-text">
            born in caracas, venezuela in 1999<br>
            bs.finance in 2021<br>
            m.arch loading<span class="loading-dots"></span>
        </div>
    </div>
    <script>
        const projects = {projects};  // Make projects data available
        const tools = {tools_dict};  // Make tools data available
        
        {get_theme_toggle_js()}
        
        function updateClock() {{
            const now = new Date();
            const options = {{ 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit',
                timeZoneName: 'short',
                hour12: false
            }};
            const timeString = new Intl.DateTimeFormat(undefined, options).format(now);
            document.getElementById('clock').textContent = timeString.toLowerCase();
        }}
        updateClock();
        setInterval(updateClock, 1000);
    </script>
</body>
</html>'''
    
    with open(OUTPUT_DIR / "index.html", "w") as f:
        f.write(html)

def get_highlight_styles():
    """Generate the CSS styles for highlighting search results."""
    return f'''
        .highlight {{
            background-color: {THEME['accent']};
            color: {THEME['background']};
            padding: 0.2em 0.4em;
            border-radius: 2px;
        }}
    '''

def get_highlighting_js():
    """Generate the JavaScript code for highlighting search results."""
    return '''
        // Safely escape special regex characters in a string
        function escapeRegExp(string) {
            return string.replace(/[.*+?^${}()|[\\\\/]/g, '\\\\$&');
        }
        
        function highlightSearchResults() {
            // Get search query from URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const searchQuery = urlParams.get('search');
            
            if (searchQuery) {
                const query = searchQuery.toLowerCase();
                const hash = window.location.hash.substring(1); // Remove the # from the hash
                
                console.log('Search query:', searchQuery);
                console.log('Hash:', hash);
                
                // Find the project or tool content
                const projectContent = document.querySelector(`#content-${hash}`);
                console.log('Found content:', projectContent);
                
                if (projectContent) {
                    // Expand the content
                    projectContent.style.display = 'block';
                    const button = projectContent.previousElementSibling.querySelector('.toggle-button');
                    if (button) {
                        button.style.transform = 'rotate(45deg)';
                    }
                    
                    // Get the description element
                    const description = projectContent.querySelector('.project-description, .tool-description');
                    if (description) {
                        // Create a temporary container to highlight text while preserving HTML
                        const container = document.createElement('div');
                        container.innerHTML = description.innerHTML;
                        
                        // Find and highlight text nodes only (preserve HTML)
                        const safeQuery = escapeRegExp(query);
                        const regex = new RegExp(safeQuery, 'gi');
                        
                        function highlightTextNodes(node) {
                            if (node.nodeType === Node.TEXT_NODE) {
                                // Only process text nodes
                                if (node.textContent.toLowerCase().includes(query)) {
                                    const span = document.createElement('span');
                                    span.innerHTML = node.textContent.replace(
                                        regex, 
                                        match => `<span class="highlight">${match}</span>`
                                    );
                                    node.parentNode.replaceChild(span, node);
                                }
                            } else if (node.nodeType === Node.ELEMENT_NODE) {
                                // Recursively process child nodes
                                Array.from(node.childNodes).forEach(highlightTextNodes);
                            }
                        }
                        
                        // Highlight inside the temporary container
                        Array.from(container.childNodes).forEach(highlightTextNodes);
                        
                        // Only update if we found matches
                        if (container.innerHTML.includes('highlight')) {
                            description.innerHTML = container.innerHTML;
                        }
                    }
                    
                    // Scroll to the content
                    projectContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
                } else {
                    console.log('No content found for hash:', hash);
                }
            }
        }
        
        // Call this function when the page loads and when the hash changes
        document.addEventListener('DOMContentLoaded', highlightSearchResults);
        window.addEventListener('hashchange', highlightSearchResults);
    '''

def generate_archive_html():
    """Generate the archive page."""
    # Define custom image orders for projects
    project_image_orders = {
        'ad_barnes_nature_reserve': [
            'site_plan.jpg',
            'floor_plan.jpg',
            'structural_plan.jpg',
            'exploded_iso_diagram.jpg',
            'render.jpg'
        ],
        'cannabis_farm': [
            'cover.jpg',
            'site_plan.jpg',
            'program_diagram.jpg',
            'harvesting_plan.jpg',
            'flowering_plan.jpg',
            'extraction_plan.jpg',
            'public_plan.jpg',
            'pavilion.jpg',
            'typical_structure.jpg',
            'flexbrick_composition_diagram.jpg'
        ],
        'chil_bookshelf': [
            'render.jpg',
            'con_doc.jpg',
            'diagram.jpg',
            'view_2.jpg',
            'built.JPG',
            'view_1.jpeg',
            'compositions.GIF'
        ]
    }

    # Get all unique tags
    all_tags = set()
    for project_data in projects.values():
        all_tags.update(project_data['tags'])
    all_tags = sorted(all_tags)
    
    project_items = []
    for project_name, project_data in projects.items():
        project_dir = ARCHIVE_DIR / project_name
        if project_dir.is_dir():
            images = get_all_images(project_dir)
            project_images = [str(img.relative_to(SITE_ROOT)) for img in images]
            
            # Debug logging for chil_bookshelf
            if project_name == 'chil_bookshelf':
                logger.info(f"Processing images for chil_bookshelf:")
                logger.info(f"Found images: {project_images}")
            
            # Get thumbnail image - use specific images for certain projects
            if project_name == 'chil_bookshelf':
                # Set thumbnail to render.jpg
                thumbnail = next((img for img in project_images if 'render.jpg' in img), project_images[0] if project_images else None)
                
                # Explicitly order images for chil_bookshelf
                ordered_images = []
                for img_name in ['con_doc.jpg', 'render.jpg', 'diagram.jpg', 'view_2.jpg', 'built.JPG', 'view_1.jpeg', 'compositions.GIF']:
                    matching_img = next((img for img in project_images if img.endswith(img_name)), None)
                    if matching_img:
                        ordered_images.append(matching_img)
                
                # Add any remaining images that weren't in our explicit order
                remaining_images = [img for img in project_images if img not in ordered_images]
                project_images = ordered_images + remaining_images
                
                # Add cache-busting for con_doc.jpg and view_1.jpeg
                project_images = [f"{img}?t={int(datetime.now().timestamp())}" if 'con_doc.jpg' in img or 'view_1.jpeg' in img else img for img in project_images]
                
                logger.info(f"Final ordered images for chil_bookshelf: {project_images}")
            elif project_name == 'icosahedron_explosion':
                # For icosahedron_explosion, use only the first image as both thumbnail and content
                thumbnail = project_images[0] if project_images else None
                project_images = [thumbnail] if thumbnail else []
            elif project_name == 'illinois_institute_of_technology_dorms':
                # Get all PNGs from the preview directory
                preview_dir = project_dir / 'previews'
                if preview_dir.exists():
                    preview_images = sorted(preview_dir.glob('*.png'))
                    if preview_images:
                        # Use the first image as thumbnail
                        thumbnail = str(preview_images[0].relative_to(SITE_ROOT))
                        # Use all preview images in order
                        project_images = [str(img.relative_to(SITE_ROOT)) for img in preview_images]
                        logger.info(f"Using {len(project_images)} preview images for illinois_institute_of_technology_dorms")
                    else:
                        logger.warning(f"No preview images found in {preview_dir}")
                        thumbnail = project_images[0] if project_images else None
                else:
                    logger.warning(f"Preview directory not found for illinois_institute_of_technology_dorms")
                    thumbnail = project_images[0] if project_images else None
            elif project_name == 'janus_house':
                # Keep the current thumbnail
                thumbnail = project_images[0] if project_images else None
                
                # Explicitly order images for janus_house
                ordered_images = []
                for img_name in ['cover.jpeg', 'dogtrot_diagram.jpg', 'form_diagram.jpeg', 'unrolled_diagram.jpg', 'floor_plan.jpg', 'section.jpg']:
                    matching_img = next((img for img in project_images if img.endswith(img_name)), None)
                    if matching_img:
                        ordered_images.append(matching_img)
                
                # Add any remaining images that weren't in our explicit order
                remaining_images = [img for img in project_images if img not in ordered_images]
                project_images = ordered_images + remaining_images
                
                # Add cache-busting for unrolled_diagram.jpg to ensure latest version
                project_images = [f"{img}?t={int(datetime.now().timestamp())}" if 'unrolled_diagram.jpg' in img else img for img in project_images]
                
                logger.info(f"Final ordered images for janus_house: {project_images}")
            elif project_name == 'lego_bridge':
                # Get all PNGs from the preview directory
                preview_dir = project_dir / 'previews'
                if preview_dir.exists():
                    preview_images = sorted(preview_dir.glob('*.png'))
                    if preview_images:
                        # Use the first image as thumbnail
                        thumbnail = str(preview_images[0].relative_to(SITE_ROOT))
                        # Use all preview images in order
                        project_images = [str(img.relative_to(SITE_ROOT)) for img in preview_images]
                        logger.info(f"Using {len(project_images)} preview images for lego_bridge")
                    else:
                        logger.warning(f"No preview images found in {preview_dir}")
                        thumbnail = project_images[0] if project_images else None
                else:
                    logger.warning(f"Preview directory not found for lego_bridge")
                    thumbnail = project_images[0] if project_images else None
            elif project_name == 'moca_playhouse':
                # Get all images from the main directory
                main_images = []
                for ext in ['.jpg', '.jpeg', '.gif', '.png', '.JPG', '.JPEG', '.GIF', '.PNG']:
                    main_images.extend([
                        f for f in project_dir.glob(f'*{ext}')
                        if f.name != 'preview.png'  # Exclude old preview files
                        and not f.stem.endswith('_presentation')  # Exclude presentation exports
                    ])
                
                # Get all images from the previews directory
                preview_dir = project_dir / 'previews'
                preview_images = []
                if preview_dir.exists():
                    for ext in ['.jpg', '.jpeg', '.gif', '.png', '.JPG', '.JPEG', '.GIF', '.PNG']:
                        preview_images.extend(preview_dir.glob(f'*{ext}'))
                
                # Combine and sort all images
                all_images = sorted(main_images + preview_images, key=lambda x: x.name)
                
                # Set thumbnail to view_2.JPG
                thumbnail = next((img for img in all_images if img.name == 'view_2.JPG'), None)
                if thumbnail:
                    thumbnail = str(thumbnail.relative_to(SITE_ROOT))
                else:
                    thumbnail = str(all_images[0].relative_to(SITE_ROOT)) if all_images else None
                
                # Only include the specified images in the exact order
                project_images = []
                for img_name in ['Floor Plan_001.png', 'tech_drawings_001.png', 'tech_drawings_002.png', 
                               'tech_drawings_010.png', 'tech_drawings_012.png', 'tech_drawings_014.png', 
                               'view_4.jpg', 'view_2.JPG', 'view_3.JPG']:
                    matching_img = next((img for img in all_images if img.name == img_name), None)
                    if matching_img:
                        project_images.append(str(matching_img.relative_to(SITE_ROOT)))
                
                logger.info(f"Final ordered images for moca_playhouse: {project_images}")
            elif project_name == 'nervi_dome':
                # For Schwennicke, use only the first image as both thumbnail and content
                thumbnail = project_images[0] if project_images else None
                project_images = [thumbnail] if thumbnail else []
            elif project_name == 'parametric_cup':
                # For parametric_cup, use only the first image as both thumbnail and content
                thumbnail = project_images[0] if project_images else None
                project_images = [thumbnail] if thumbnail else []
            elif project_name == 'parametric_stop':
                # Set thumbnail to cover.jpeg
                thumbnail = next((img for img in images if img.name == 'cover.jpeg'), None)
                if thumbnail:
                    thumbnail = str(thumbnail.relative_to(SITE_ROOT))
                else:
                    thumbnail = project_images[0] if project_images else None
                
                # Only include the specified images in the exact order, excluding cover and back_cover
                project_images = []
                for img_name in ['index_diagram.jpeg', 'site_plan.jpeg', 'floor_plan.jpeg', 
                               'section.jpeg', 'perspective.jpeg']:
                    matching_img = next((img for img in images if img.name == img_name), None)
                    if matching_img:
                        project_images.append(str(matching_img.relative_to(SITE_ROOT)))
                
                logger.info(f"Final ordered images for parametric_stop: {project_images}")
            elif project_name == 'ad_barnes_nature_reserve':
                thumbnail = next((img for img in project_images if 'render.jpg' in img), project_images[0] if project_images else None)
            elif project_name == 'rome_artist_residence':
                # Get all PNGs from the preview directory
                preview_dir = project_dir / 'preview'
                if preview_dir.exists():
                    preview_images = sorted(preview_dir.glob('*.png'))
                    if preview_images:
                        # Use the first image as thumbnail
                        thumbnail = str(preview_images[0].relative_to(SITE_ROOT))
                        # Use all preview images in order
                        project_images = [str(img.relative_to(SITE_ROOT)) for img in preview_images]
                        logger.info(f"Using {len(project_images)} preview images for rome_artist_residence")
                    else:
                        logger.warning(f"No preview images found in {preview_dir}")
                        thumbnail = project_images[0] if project_images else None
                else:
                    logger.warning(f"Preview directory not found for rome_artist_residence")
                    thumbnail = project_images[0] if project_images else None
            elif project_name == 'renault_center':
                # Get all PNGs from the preview directory
                preview_dir = project_dir / 'previews'
                if preview_dir.exists():
                    preview_images = sorted(preview_dir.glob('*.png'))
                    if preview_images:
                        # Use the first image as thumbnail
                        thumbnail = str(preview_images[0].relative_to(SITE_ROOT))
                        # Use all preview images in order
                        project_images = [str(img.relative_to(SITE_ROOT)) for img in preview_images]
                        logger.info(f"Using {len(project_images)} preview images for renault_center")
                    else:
                        logger.warning(f"No preview images found in {preview_dir}")
                        thumbnail = project_images[0] if project_images else None
                else:
                    logger.warning(f"Preview directory not found for renault_center")
                    thumbnail = project_images[0] if project_images else None
            elif project_name == 'remote_research_center':
                # Get all PNGs from the preview directory
                preview_dir = project_dir / 'previews'
                if preview_dir.exists():
                    preview_images = sorted(preview_dir.glob('*.png'))
                    if preview_images:
                        # Use the first image as thumbnail
                        thumbnail = str(preview_images[0].relative_to(SITE_ROOT))
                        # Use all preview images in order
                        project_images = [str(img.relative_to(SITE_ROOT)) for img in preview_images]
                        logger.info(f"Using {len(project_images)} preview images for remote_research_center")
                    else:
                        logger.warning(f"No preview images found in {preview_dir}")
                        thumbnail = project_images[0] if project_images else None
                else:
                    logger.warning(f"Preview directory not found for remote_research_center")
                    thumbnail = project_images[0] if project_images else None
            else:
                thumbnail = project_images[0] if project_images else None
            
            if thumbnail is None:
                continue  # Skip projects with no images
            
            # Sort images according to custom order if defined (for all projects except chil_bookshelf)
            if project_name in project_image_orders and project_name != 'chil_bookshelf':
                order = project_image_orders[project_name]
                # Create a dictionary to store the order of each image
                order_dict = {img: i for i, img in enumerate(order)}
                # Sort images, putting ordered ones first and others at the end
                project_images.sort(key=lambda x: order_dict.get(x.split('/')[-1], float('inf')))
                
                # Debug logging for project after sorting
                logger.info(f"Sorted images for {project_name}: {project_images}")
            
            # Create tag elements
            tag_elements = []
            for tag in project_data['tags']:
                if 'grasshopper' in tag.lower() and 'link' in project_data:
                    tag_elements.append(f'<span class="tag" data-tag="{tag}">{tag}</span>')
                else:
                    tag_elements.append(f'<span class="tag" data-tag="{tag}">{tag}</span>')
            
            item = f'''
                <div class="project-item" data-project="{project_name}">
                    <div class="project-header" onclick="toggleProject('{project_name}')">
                        <div class="project-title-container">
                            <h2 class="project-title">{project_name}</h2>
                            <div class="project-tags">
                                {''.join(tag_elements)}
                            </div>
                        </div>
                        <div class="project-thumbnail">
                            <img src="{thumbnail}" alt="{project_name} thumbnail">
                        </div>
                        <button class="toggle-button">
                            <svg width="24" height="24" viewBox="0 0 16 16">
                                <path fill="currentColor" d="M8 4.5a.5.5 0 01.5.5v6a.5.5 0 01-1 0V5a.5.5 0 01.5-.5zM4.5 8a.5.5 0 01.5-.5h6a.5.5 0 010 1H5a.5.5 0 01-.5-.5z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="project-content" id="content-{project_name}">
                        <div class="project-description">
                            {project_data['description']}
                        </div>
                        <div class="project-images">
                            {''.join(f'<img src="{img}" alt="{project_name} image" class="project-image" loading="lazy">' for img in project_images)}
                        </div>
                </div>
            </div>'''
            project_items.append(item)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';">
    <title>archive - santiago martínez-oropeza</title>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <style>
        :root {{
            /* Light theme (default) */
            --background: {THEMES['light']['background']};
            --text: {THEMES['light']['text']};
            --accent: {THEMES['light']['accent']};
            --border: {THEMES['light']['border']};
            --hover: {THEMES['light']['hover']};
            --card: {THEMES['light']['card']};
        }}
        
        /* Dark theme */
        [data-theme="dark"] {{
            --background: {THEMES['dark']['background']};
            --text: {THEMES['dark']['text']};
            --accent: {THEMES['dark']['accent']};
            --border: {THEMES['dark']['border']};
            --hover: {THEMES['dark']['hover']};
            --card: {THEMES['dark']['card']};
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: "SF Mono", Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            background-color: var(--background);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            width: 100%;
        }}
        
        .nav-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1rem;
        }}
        
        .nav-buttons {{
            display: flex;
            gap: 1rem;
        }}
        
        .nav-right {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .search-container {{
            display: flex;
            align-items: center;
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 0.75rem 1.5rem;
            height: 100%;
            min-height: 3rem;
            position: relative;
        }}
        
        .search-input {{
            border: none;
            background: transparent;
            color: var(--text);
            font-family: inherit;
            font-size: 1rem;
            padding: 0;
            outline: none;
            width: 200px;
            height: 100%;
        }}
        
        .search-button {{
            background: none;
            border: none;
            color: var(--text);
            cursor: pointer;
            padding: 0;
            font-size: 1rem;
            height: 100%;
            display: flex;
            align-items: center;
        }}
        
        .search-button:hover {{
            color: var(--accent);
        }}
        
        .nav-button {{
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            color: var(--text);
            background-color: transparent;
            border: 1px solid var(--border);
            border-radius: 4px;
            text-decoration: none;
            transition: all 0.2s ease;
            height: 3rem;
            display: flex;
            align-items: center;
        }}
        
        .nav-button:hover {{
            color: var(--accent);
            border-color: var(--accent);
        }}
        
        .nav-button.active {{
            color: var(--accent);
            border-color: var(--accent);
        }}
        
        .clock {{
            font-size: 1rem;
            color: var(--text);
            padding: 0.75rem 1.5rem;
            border: 1px solid var(--border);
            border-radius: 4px;
            height: 3rem;
            display: flex;
            align-items: center;
        }}
        
        h1 {{
            font-size: 4rem;
            font-weight: 600;
            margin-bottom: 2rem;
            letter-spacing: -0.02em;
            color: var(--text);
        }}
        
        .active-filters {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}
        
        .active-filter {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.25rem 0.5rem;
            font-size: 0.8rem;
            color: var(--background);
            background-color: var(--accent);
            border: 1px solid var(--accent);
            border-radius: 4px;
        }}
        
        .active-filter button {{
            background: none;
            border: none;
            color: var(--background);
            cursor: pointer;
            padding: 0;
            font-size: 1rem;
            line-height: 1;
        }}
        
        .project-item {{
            border-bottom: 1px solid var(--border);
            padding: 1rem;
            transition: all 0.2s ease;
            margin: 0 -1rem;
            position: relative;
        }}
        
        .project-item:hover {{
            box-shadow: none;
            background: none;
            border-bottom: 1px solid var(--border);
        }}

        .project-item:hover .project-title::after {{
            content: '';
            display: inline-block;
            width: 8px;
            height: 8px;
            background-color: var(--accent);
            border-radius: 50%;
            margin-left: 8px;
            vertical-align: middle;
        }}
        
        .project-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            padding: 0.5rem 0;
            gap: 1rem;
        }}
        
        .project-title-container {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            flex: 1;
        }}
        
        .project-thumbnail {{
            width: 120px;
            height: 80px;
            flex-shrink: 0;
            border: 1px solid var(--text);
            border-radius: 4px;
            overflow: hidden;
            transition: all 0.2s;
        }}
        
        .project-thumbnail:hover {{
            border-color: var(--accent);
        }}
        
        .project-thumbnail img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .project-title {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text);
            margin: 0;
        }}
        
        .project-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        
        .tag {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            font-size: 0.8rem;
            color: var(--accent);
            border: 1px solid var(--accent);
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .tag:hover {{
            background-color: var(--accent);
            color: var(--background);
        }}
        
        .toggle-button {{
            background: none;
            border: none;
            color: var(--text);
            cursor: pointer;
            padding: 0.5rem;
            transition: transform 0.2s;
        }}
        
        .toggle-button:hover {{
            color: var(--accent);
        }}
        
        .project-content {{
            display: none;
            padding: 1rem 0;
        }}
        
        .project-content.active {{
            display: block;
        }}
        
        .project-description {{
            margin-bottom: 1rem;
            line-height: 1.6;
        }}
        
        .project-images {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
        }}
        
        .project-image {{
            width: 100%;
            height: auto;
            object-fit: cover;
            border: 1px solid var(--border);
            transition: transform 0.2s ease;
        }}
        
        .project-image:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .project-link {{
            color: var(--accent);
            text-decoration: underline;
            transition: color 0.2s;
        }}
        
        .project-link:hover {{
            color: var(--text);
        }}
        
        /* Modal styles */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}
        
        .modal.active {{
            display: flex;
        }}
        
        .modal-content {{
            max-width: 90%;
            max-height: 90%;
            object-fit: contain;
        }}
        
        .modal-nav {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            color: white;
            font-size: 2rem;
            cursor: pointer;
            background: none;
            border: none;
            padding: 1rem;
            transition: color 0.2s;
            font-family: inherit;
        }}
        
        .modal-nav:hover {{
            color: var(--accent);
        }}
        
        .modal-prev {{
            left: 2rem;
        }}
        
        .modal-next {{
            right: 2rem;
        }}
        
        .modal-close {{
            position: absolute;
            top: 2rem;
            right: 2rem;
            color: white;
            font-size: 2rem;
            cursor: pointer;
            background: none;
            border: none;
            padding: 1rem;
            transition: color 0.2s;
            font-family: inherit;
        }}
        
        .modal-close:hover {{
            color: var(--accent);
        }}
        
        @media (max-width: 768px) {{
            .project-images {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .search-results {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--background);
            border: 1px solid var(--border);
            border-radius: 4px;
            margin-top: 4px;
            max-height: 300px;
            overflow-y: auto;
            overflow-x: hidden;
            display: none;
            z-index: 1000;
        }}

        .search-results.active {{
            display: block;
        }}

        .search-result-item {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .search-result-item:last-child {{
            border-bottom: none;
        }}

        .search-result-item:hover {{
            background: var(--hover);
        }}

        .search-result-title {{
            font-weight: 600;
            margin-bottom: 0.25rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .search-result-tags {{
            font-size: 0.8rem;
            color: var(--accent);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        {get_highlight_styles()}
    </style>
</head>
<body>
    <div class="container">
        {get_navigation('archive')}
        <h1>archive</h1>
        <div class="active-filters" id="activeFilters"></div>
        <div class="project-list">
            {''.join(project_items)}
        </div>
    </div>
    
    <!-- Modal for expanded images -->
    <div class="modal" id="imageModal">
        <button class="modal-close" id="modalClose">×</button>
        <button class="modal-nav modal-prev" id="modalPrev"><</button>
        <img class="modal-content" id="modalImage">
        <button class="modal-nav modal-next" id="modalNext">></button>
    </div>
    
    <script>
        const projects = {projects};  // Make projects data available
        const tools = {tools_dict};  // Make tools data available
        
        // Initialize the set for active tags
        const activeTags = new Set();
        
        {get_theme_toggle_js()}
        
        function toggleProject(projectName) {{
            const content = document.getElementById(`content-${{projectName}}`);
            const button = content.previousElementSibling.querySelector('.toggle-button');
            
            if (content.style.display === 'block') {{
                content.style.display = 'none';
                button.style.transform = 'rotate(0deg)';
            }} else {{
                content.style.display = 'block';
                button.style.transform = 'rotate(45deg)';
            }}
        }}
        
        function toggleTag(tag) {{
            if (activeTags.has(tag)) {{
                activeTags.delete(tag);
            }} else {{
                activeTags.add(tag);
            }}
            updateActiveFilters();
            filterProjects();
        }}
        
        function updateActiveFilters() {{
            const activeFiltersContainer = document.getElementById('activeFilters');
            activeFiltersContainer.innerHTML = '';
            
            if (activeTags.size > 0) {{
                activeTags.forEach(tag => {{
                    const filterElement = document.createElement('div');
                    filterElement.className = 'active-filter';
                    const removeButton = document.createElement('button');
                    removeButton.textContent = '×';
                    removeButton.onclick = (e) => {{
                        e.stopPropagation();
                        removeFilter(tag);
                    }};
                    filterElement.appendChild(document.createTextNode(tag));
                    filterElement.appendChild(removeButton);
                    activeFiltersContainer.appendChild(filterElement);
                }});
            }}
        }}
        
        function removeFilter(tag) {{
            activeTags.delete(tag);
            updateActiveFilters();
            filterProjects();
        }}
        
        function filterProjects() {{
            const projectItems = document.querySelectorAll('.project-item');
            projectItems.forEach(item => {{
                const projectName = item.dataset.project;
                const projectData = projects[projectName];
                if (projectData) {{
                    const projectTags = new Set(projectData.tags);
                    const hasActiveTags = activeTags.size === 0 || 
                        Array.from(activeTags).every(tag => projectTags.has(tag));
                    item.style.display = hasActiveTags ? 'block' : 'none';
                }}
            }});
        }}
        
        function updateClock() {{
            const now = new Date();
            const options = {{ 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit',
                timeZoneName: 'short',
                hour12: false
            }};
            const timeString = new Intl.DateTimeFormat(undefined, options).format(now);
            document.getElementById('clock').textContent = timeString.toLowerCase();
        }}
        updateClock();
        setInterval(updateClock, 1000);
        
        // Add image modal functionality
        const modal = document.getElementById('imageModal');
        const modalImg = document.getElementById('modalImage');
        const modalClose = document.getElementById('modalClose');
        const modalPrev = document.getElementById('modalPrev');
        const modalNext = document.getElementById('modalNext');
        let currentProjectImages = [];
        let currentImageIndex = 0;
        
        // Add click handlers to all project images
        document.querySelectorAll('.project-image').forEach(img => {{
            img.addEventListener('click', () => {{
                // Get all images in the current project
                const projectItem = img.closest('.project-item');
                currentProjectImages = Array.from(projectItem.querySelectorAll('.project-image'));
                currentImageIndex = currentProjectImages.indexOf(img);
                
                modalImg.src = img.src;
                modal.classList.add('active');
                document.body.style.overflow = 'hidden';
            }});
        }});
        
        function showImage(index) {{
            if (index >= 0 && index < currentProjectImages.length) {{
                currentImageIndex = index;
                modalImg.src = currentProjectImages[index].src;
            }}
        }}
        
        // Navigation handlers
        modalPrev.addEventListener('click', () => {{
            showImage(currentImageIndex - 1);
        }});
        
        modalNext.addEventListener('click', () => {{
            showImage(currentImageIndex + 1);
        }});
        
        // Close modal when clicking the close button
        modalClose.addEventListener('click', () => {{
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }});
        
        // Close modal when clicking outside the image
        modal.addEventListener('click', (e) => {{
            if (e.target === modal) {{
                modal.classList.remove('active');
                document.body.style.overflow = '';
            }}
        }});
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => {{
            if (modal.classList.contains('active')) {{
                if (e.key === 'Escape') {{
                    modal.classList.remove('active');
                    document.body.style.overflow = '';
                }} else if (e.key === 'ArrowLeft') {{
                    showImage(currentImageIndex - 1);
                }} else if (e.key === 'ArrowRight') {{
                    showImage(currentImageIndex + 1);
                }}
            }}
        }});
        
        // Function to expand toolbox project
        function expandToolboxProject(event, projectName) {{
            event.preventDefault();
            const url = new URL(event.target.href);
            const hash = url.hash.substring(1);  // Remove the # from the hash
            window.location.href = url.pathname + '?expand=true' + '#' + hash;
        }}
        
        {get_highlighting_js()}
        
        // Add event delegation for tag clicks
        document.querySelector('.project-list').addEventListener('click', function(event) {{
            if (event.target.classList.contains('tag')) {{
                event.stopPropagation(); // Prevent toggling the project when clicking tags
                const tag = event.target.getAttribute('data-tag');
                if (tag) {{
                    toggleTag(tag);
                }}
            }}
        }});
    </script>
</body>
</html>'''
    
    with open(OUTPUT_DIR / "archive.html", "w") as f:
        f.write(html)

def generate_toolbox_html():
    """Generate the toolbox page."""
    tools = []
    for tool_dir in TOOLBOX_DIR.iterdir():
        if tool_dir.is_dir():
            gh_file = next(tool_dir.glob('*.gh'), None)
            ghx_file = next(tool_dir.glob('*.ghx'), None)
            if ghx_file:
                description = get_tool_description(tool_dir.name)
                tools.append({
                    'name': tool_dir.name,
                    'description': description,
                    'gh_file': gh_file,
                    'ghx_file': ghx_file,
                    'tags': tools_dict[tool_dir.name]['tags']  # Use tags from global dict
                })
        elif tool_dir.suffix == '.ghx':
            description = get_tool_description(tool_dir.stem)
            tools.append({
                'name': tool_dir.stem,
                'description': description,
                'gh_file': None,
                'ghx_file': tool_dir,
                'tags': tools_dict[tool_dir.stem]['tags']  # Use tags from global dict
            })
    
    # Sort tools by name
    tools.sort(key=lambda x: x['name'])

    # Create a directory for the GHX content files if it doesn't exist
    ghx_content_dir = OUTPUT_DIR / 'ghx_content'
    ghx_content_dir.mkdir(exist_ok=True)

    # Save GHX contents to separate files
    for tool in tools:
        ghx_content = read_ghx_file(tool['ghx_file'])
        content_file = ghx_content_dir / f"{tool['name']}.ghx"
        with open(content_file, 'w', encoding='utf-8') as f:
            f.write(ghx_content)

    tool_items = []
    for tool in tools:
        gh_download = f'''
            <a href="{tool['gh_file'].relative_to(SITE_ROOT)}" class="tool-button" download>
                <svg width="16" height="16" viewBox="0 0 16 16">
                    <path fill="currentColor" d="M7.47 10.78a.75.75 0 001.06 0l3.75-3.75a.75.75 0 00-1.06-1.06L8.75 8.44V1.75a.75.75 0 00-1.5 0v6.69L4.78 5.97a.75.75 0 00-1.06 1.06l3.75 3.75zM3.75 13a.75.75 0 000 1.5h8.5a.75.75 0 000-1.5h-8.5z"/>
                </svg>
                download .gh
            </a>''' if tool['gh_file'] else ''

        # Create tag elements
        tag_elements = []
        for tag in tool['tags']:
            tag_elements.append(f'<span class="tag" data-tag="{tag}">{tag}</span>')

        item = f'''
            <div class="tool-item" data-tool="{tool['name']}">
                <div class="tool-header" onclick="toggleTool('{tool['name']}')">
                    <div class="tool-title-container">
                    <h2 class="tool-name">{tool['name']}</h2>
                        <div class="tool-tags">
                            {''.join(tag_elements)}
                </div>
                </div>
                    <button class="toggle-button">
                        <svg width="24" height="24" viewBox="0 0 16 16">
                            <path fill="currentColor" d="M8 4.5a.5.5 0 01.5.5v6a.5.5 0 01-1 0V5a.5.5 0 01.5-.5zM4.5 8a.5.5 0 01.5-.5h6a.5.5 0 010 1H5a.5.5 0 01-.5-.5z"/>
                        </svg>
                    </button>
                </div>
                <div class="tool-content" id="content-{tool['name']}">
                    <div class="tool-description">{tool['description'] + ('.' if not tool['description'].endswith('.') else '')}</div>
                <div class="tool-actions">
                        <button class="tool-button" onclick="toggleCode('{tool['name']}')">
                        <svg width="16" height="16" viewBox="0 0 16 16">
                            <path fill="currentColor" d="M4.72 3.22a.75.75 0 001.06 1.06L2.06 8l3.72 3.72a.75.75 0 10-1.06 1.06L.47 8.53a.75.75 0 000-1.06l4.25-4.25zm6.56 0a.75.75 0 10-1.06 1.06L13.94 8l-3.72 3.72a.75.75 0 101.06 1.06l4.25-4.25a.75.75 0 000-1.06l-4.25-4.25z"/>
                        </svg>
                            view code
                    </button>
                    {gh_download}
                    <a href="{tool['ghx_file'].relative_to(SITE_ROOT)}" class="tool-button" download>
                        <svg width="16" height="16" viewBox="0 0 16 16">
                            <path fill="currentColor" d="M7.47 10.78a.75.75 0 001.06 0l3.75-3.75a.75.75 0 00-1.06-1.06L8.75 8.44V1.75a.75.75 0 00-1.5 0v6.69L4.78 5.97a.75.75 0 00-1.06 1.06l3.75 3.75zM3.75 13a.75.75 0 000 1.5h8.5a.75.75 0 000-1.5h-8.5z"/>
                        </svg>
                            download .ghx
                    </a>
                </div>
                    <pre id="code-{tool['name']}" class="code-preview"></pre>
                    <div id="loading-{tool['name']}" class="loading" style="display: none;">Loading...</div>
                </div>
            </div>'''
        tool_items.append(item)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';">
    <title>toolbox - santiago martínez-oropeza</title>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <style>
        :root {{
            /* Light theme (default) */
            --background: {THEMES['light']['background']};
            --text: {THEMES['light']['text']};
            --accent: {THEMES['light']['accent']};
            --border: {THEMES['light']['border']};
            --hover: {THEMES['light']['hover']};
            --card: {THEMES['light']['card']};
        }}
        
        /* Dark theme */
        [data-theme="dark"] {{
            --background: {THEMES['dark']['background']};
            --text: {THEMES['dark']['text']};
            --accent: {THEMES['dark']['accent']};
            --border: {THEMES['dark']['border']};
            --hover: {THEMES['dark']['hover']};
            --card: {THEMES['dark']['card']};
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: "SF Mono", Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            background-color: var(--background);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            width: 100%;
        }}
        
        .nav-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1rem;
        }}
        
        .nav-buttons {{
            display: flex;
            gap: 1rem;
        }}
        
        .nav-right {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .search-container {{
            display: flex;
            align-items: center;
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 0.75rem 1.5rem;
            height: 100%;
            min-height: 3rem;
            position: relative;
        }}
        
        .search-input {{
            border: none;
            background: transparent;
            color: var(--text);
            font-family: inherit;
            font-size: 1rem;
            padding: 0;
            outline: none;
            width: 200px;
            height: 100%;
        }}
        
        .search-button {{
            background: none;
            border: none;
            color: var(--text);
            cursor: pointer;
            padding: 0;
            font-size: 1rem;
            height: 100%;
            display: flex;
            align-items: center;
        }}
        
        .search-button:hover {{
            color: var(--accent);
        }}
        
        .nav-button {{
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            color: var(--text);
            background-color: transparent;
            border: 1px solid var(--border);
            border-radius: 4px;
            text-decoration: none;
            transition: all 0.2s ease;
            height: 3rem;
            display: flex;
            align-items: center;
        }}
        
        .nav-button:hover {{
            color: var(--accent);
            border-color: var(--accent);
        }}
        
        .nav-button.active {{
            color: var(--accent);
            border-color: var(--accent);
        }}
        
        .clock {{
            font-size: 1rem;
            color: var(--text);
            padding: 0.75rem 1.5rem;
            border: 1px solid var(--border);
            border-radius: 4px;
            height: 3rem;
            display: flex;
            align-items: center;
        }}
        
        h1 {{
            font-size: 4rem;
            font-weight: 600;
            margin-bottom: 2rem;
            letter-spacing: -0.02em;
            color: var(--text);
        }}
        
        .active-filters {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}
        
        .active-filter {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.25rem 0.5rem;
            font-size: 0.8rem;
            color: var(--background);
            background-color: var(--accent);
            border: 1px solid var(--accent);
            border-radius: 4px;
        }}
        
        .active-filter button {{
            background: none;
            border: none;
            color: var(--background);
            cursor: pointer;
            padding: 0;
            font-size: 1rem;
            line-height: 1;
        }}
        
        .tool-item {{
            border-bottom: 1px solid var(--border);
            padding: 1rem;
            transition: all 0.2s ease;
            margin: 0 -1rem;
            position: relative;
        }}
        
        .tool-item:hover {{
            box-shadow: none;
            background: none;
            border-bottom: 1px solid var(--border);
        }}

        .tool-item:hover .tool-name::after {{
            content: '';
            display: inline-block;
            width: 8px;
            height: 8px;
            background-color: var(--accent);
            border-radius: 50%;
            margin-left: 8px;
            vertical-align: middle;
        }}
        
        .tool-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            padding: 0.5rem 0;
        }}
        
        .tool-title-container {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        
        .tool-name {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text);
            margin: 0;
        }}
        
        .tool-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        
        .tag {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            font-size: 0.8rem;
            color: var(--accent);
            border: 1px solid var(--accent);
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .tag:hover, .tag.active {{
            background-color: var(--accent);
            color: var(--background);
        }}
        
        .toggle-button {{
            background: none;
            border: none;
            color: var(--text);
            cursor: pointer;
            padding: 0.5rem;
            transition: transform 0.2s;
        }}
        
        .toggle-button:hover {{
            color: var(--accent);
        }}
        
        .tool-content {{
            display: none;
            padding: 1rem 0;
        }}
        
        .tool-content.active {{
            display: block;
        }}
        
        .tool-description {{
            margin-bottom: 1rem;
            line-height: 1.6;
        }}
        
        .tool-actions {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        
        .tool-button {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
            color: var(--text);
            background: transparent;
            border: 1px solid var(--border);
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s;
        }}
        
        .tool-button:hover {{
            color: var(--accent);
            border-color: var(--accent);
        }}
        
        .code-preview {{
            display: none;
            margin-top: 1rem;
            padding: 1rem;
            background: var(--background);
            border: 1px solid var(--border);
            border-radius: 4px;
            font-family: inherit;
            font-size: 0.9rem;
            white-space: pre;
            overflow-x: auto;
            max-height: 400px;
        }}
        
        .loading {{
            margin-top: 1rem;
            color: var(--accent);
            font-size: 0.9rem;
        }}
        
        @media (max-width: 768px) {{
            .tool-actions {{
                flex-direction: column;
            }}
        }}
        
        .search-results {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--background);
            border: 1px solid var(--border);
            border-radius: 4px;
            margin-top: 4px;
            max-height: 300px;
            overflow-y: auto;
            overflow-x: hidden;
            display: none;
            z-index: 1000;
        }}

        .search-results.active {{
            display: block;
        }}

        .search-result-item {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .search-result-item:last-child {{
            border-bottom: none;
        }}

        .search-result-item:hover {{
            background: var(--hover);
        }}

        .search-result-title {{
            font-weight: 600;
            margin-bottom: 0.25rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .search-result-tags {{
            font-size: 0.8rem;
            color: var(--accent);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        {get_highlight_styles()}
    </style>
</head>
<body>
    <div class="container">
        {get_navigation('toolbox')}
        <h1>toolbox</h1>
        <div class="active-filters" id="activeFilters"></div>
        <div class="tool-list">
            {''.join(tool_items)}
        </div>
    </div>
    
    <script>
        const projects = {projects};  // Make projects data available
        const tools = {tools_dict};  // Make tools data available
        
        // Initialize the set for active tags
        const activeTags = new Set();
        
        {get_theme_toggle_js()}
        
        function toggleTag(tag) {{
            if (activeTags.has(tag)) {{
                activeTags.delete(tag);
            }} else {{
                activeTags.add(tag);
            }}
            updateActiveFilters();
            filterTools();
        }}
        
        function updateActiveFilters() {{
            const activeFiltersContainer = document.getElementById('activeFilters');
            if (activeFiltersContainer) {{
                activeFiltersContainer.innerHTML = '';
                
                if (activeTags.size > 0) {{
                    activeTags.forEach(tag => {{
                        const filterElement = document.createElement('div');
                        filterElement.className = 'active-filter';
                        const removeButton = document.createElement('button');
                        removeButton.textContent = '×';
                        removeButton.onclick = (e) => {{
                            e.stopPropagation();
                            removeFilter(tag);
                        }};
                        filterElement.appendChild(document.createTextNode(tag));
                        filterElement.appendChild(removeButton);
                        activeFiltersContainer.appendChild(filterElement);
                    }});
                }}
            }}
        }}
        
        function removeFilter(tag) {{
            activeTags.delete(tag);
            updateActiveFilters();
            filterTools();
        }}
        
        function filterTools() {{
            const toolItems = document.querySelectorAll('.tool-item');
            toolItems.forEach(item => {{
                const toolName = item.dataset.tool;
                const toolData = tools[toolName];
                if (toolData) {{
                    const toolTags = new Set(toolData.tags);
                    const hasActiveTags = activeTags.size === 0 || 
                        Array.from(activeTags).every(tag => toolTags.has(tag));
                    item.style.display = hasActiveTags ? 'block' : 'none';
                }}
            }});
        }}
        
        async function toggleTool(toolName) {{
            const content = document.getElementById(`content-${{toolName}}`);
            const button = content.previousElementSibling.querySelector('.toggle-button');
            
            if (content.style.display === 'block') {{
                content.style.display = 'none';
                button.style.transform = 'rotate(0deg)';
            }} else {{
                content.style.display = 'block';
                button.style.transform = 'rotate(45deg)';
            }}
        }}
        
        async function toggleCode(toolName) {{
            const codePreview = document.getElementById(`code-${{toolName}}`);
            const loadingElement = document.getElementById(`loading-${{toolName}}`);
            const viewCodeButton = document.querySelector(`#content-${{toolName}} .tool-button[onclick="toggleCode('${{toolName}}')"]`);
            const isVisible = codePreview.style.display === 'block';
            
            if (isVisible) {{
                codePreview.style.display = 'none';
                viewCodeButton.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 16 16">
                        <path fill="currentColor" d="M4.72 3.22a.75.75 0 011.06 1.06L2.06 8l3.72 3.72a.75.75 0 11-1.06 1.06L.47 8.53a.75.75 0 010-1.06l4.25-4.25zm6.56 0a.75.75 0 10-1.06 1.06L13.94 8l-3.72 3.72a.75.75 0 101.06 1.06l4.25-4.25a.75.75 0 000-1.06l-4.25-4.25z"/>
                    </svg>
                    view code
                `;
                return;
            }}
            
            viewCodeButton.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 16 16">
                    <path fill="currentColor" d="M4.72 3.22a.75.75 0 011.06 1.06L2.06 8l3.72 3.72a.75.75 0 11-1.06 1.06L.47 8.53a.75.75 0 010-1.06l4.25-4.25zm6.56 0a.75.75 0 10-1.06 1.06L13.94 8l-3.72 3.72a.75.75 0 101.06 1.06l4.25-4.25a.75.75 0 000-1.06l-4.25-4.25z"/>
                </svg>
                close
            `;
            
            try {{
                loadingElement.style.display = 'block';
                const response = await fetch(`ghx_content/${{toolName}}.ghx`);
                if (!response.ok) throw new Error(`HTTP error! status: ${{response.status}}`);
                const content = await response.text();
                codePreview.textContent = content;
                codePreview.style.display = 'block';
            }} catch (error) {{
                console.error('Error loading code:', error);
                codePreview.textContent = 'Error loading code content.';
                codePreview.style.display = 'block';
            }} finally {{
                loadingElement.style.display = 'none';
            }}
        }}
        
        function updateClock() {{
            const now = new Date();
            const options = {{ 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit',
                timeZoneName: 'short',
                hour12: false
            }};
            const timeString = new Intl.DateTimeFormat(undefined, options).format(now);
            document.getElementById('clock').textContent = timeString.toLowerCase();
        }}
        updateClock();
        setInterval(updateClock, 1000);
        
        {get_highlighting_js()}
        
        // Function to expand a tool when the page loads with a hash or expand parameter
        function expandToolOnLoad() {{
            // Get hash from URL (without the #)
            const hash = window.location.hash.substring(1);
            // Check if we have a tool to expand
            if (hash) {{
                const toolContent = document.getElementById(`content-${{hash}}`);
                if (toolContent) {{
                    // Expand the content
                    toolContent.style.display = 'block';
                    const button = toolContent.previousElementSibling.querySelector('.toggle-button');
                    if (button) {{
                        button.style.transform = 'rotate(45deg)';
                    }}
                    // Scroll to the tool
                    toolContent.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }}
        }}
        
        // Call this function when the page loads
        document.addEventListener('DOMContentLoaded', expandToolOnLoad);
        
        // Add event delegation for tag clicks
        document.querySelector('.tool-list').addEventListener('click', function(event) {{
            if (event.target.classList.contains('tag')) {{
                event.stopPropagation(); // Prevent toggling the project when clicking tags
                const tag = event.target.getAttribute('data-tag');
                if (tag) {{
                    toggleTag(tag);
                }}
            }}
        }});
    </script>
</body>
</html>'''
    
    with open(OUTPUT_DIR / "toolbox.html", "w") as f:
        f.write(html)

def get_theme_toggle_js():
    """Generate the JavaScript code for the theme toggle functionality."""
    return '''
    // Check if user has a preferred theme stored
    let currentTheme = localStorage.getItem('theme') || 'light';
    
    // Apply the theme on page load
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // Update the toggle to match the current theme
    updateThemeToggle(currentTheme);
    
    function toggleTheme(theme) {
        // Update theme
        currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update the toggle UI
        updateThemeToggle(theme);
    }
    
    function updateThemeToggle(theme) {
        // Update toggle buttons
        document.querySelector('.theme-option.light').classList.toggle('active', theme === 'light');
        document.querySelector('.theme-option.dark').classList.toggle('active', theme === 'dark');
        
        // Update slider position
        document.querySelector('.theme-slider').classList.toggle('dark', theme === 'dark');
    }
    '''

def main():
    """Main function to generate the site."""
    try:
        # Generate all pages
        generate_index_html()
        logger.info("Generated index.html")
        
        generate_archive_html()
        logger.info("Generated archive.html")
        
        generate_toolbox_html()
        logger.info("Generated toolbox.html")
        
        # Start HTTP server
        import http.server
        import socketserver
        import socket

        class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            def end_headers(self):
                # Add CSP header
                self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';")
                super().end_headers()

        def find_available_port(start_port=8000, max_attempts=10):
            for port in range(start_port, start_port + max_attempts):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('', port))
                        return port
                except OSError:
                    logger.info(f"Port {port} is in use, trying next port...")
            raise OSError(f"Could not find an available port after {max_attempts} attempts")

        port = find_available_port()
        handler = CustomHTTPRequestHandler
        
        with socketserver.TCPServer(("", port), handler) as httpd:
            logger.info(f"Serving at http://localhost:{port}")
            httpd.serve_forever()
            
    except Exception as e:
        logger.error(f"Error generating site: {e}")
        raise

if __name__ == "__main__":
    main() 