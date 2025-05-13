#!/usr/bin/env python3
"""
Chatbot Generator
----------------
This script helps you create a custom chatbot with domain-specific knowledge.
It generates a self-contained Docker container with Ollama and a web UI.
"""
import os
import sys
import shutil
import subprocess
import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging
import json
import datetime
import textwrap
from collections import OrderedDict

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('chatbot_generator')

# Constants
TEMPLATE_DIR = Path(__file__).parent / "templates"
OLLAMA_MODELS = [
    "llama3.2:1b", 
    "llama3:8b", 
    "llama3:70b", 
    "mistral:7b", 
    "phi3:mini", 
    "tinyllama:1.1b"
]
DEFAULT_MODEL = "llama3.2:1b"

# Default system prompt and LLM parameters
DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant specialized in {{chatbot_description}}. 
You provide accurate, concise information based on your knowledge and the documents in your knowledge base.
If you don't know something or if the information isn't in your knowledge base, admit it clearly.
Always maintain a helpful and professional tone."""

DEFAULT_LLM_PARAMS = {
    "temperature": 0.7,
    "top_k": 40,
    "top_p": 0.9,
    "max_tokens": 1024,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.0
}

# UI Customization Options
THEME_COLORS = OrderedDict([
    ("sky", {"primary": "#0EA5E9", "bg": "#F0F9FF", "text": "#0C4A6E"}),
    ("forest", {"primary": "#22C55E", "bg": "#F0FDF4", "text": "#14532D"}),
    ("lavender", {"primary": "#8B5CF6", "bg": "#F5F3FF", "text": "#4C1D95"}),
    ("sunset", {"primary": "#F59E0B", "bg": "#FFFBEB", "text": "#78350F"}),
    ("ocean", {"primary": "#0891B2", "bg": "#ECFEFF", "text": "#155E75"})
])

FONT_STYLES = [
    {"name": "Modern", "font_family": "Inter, system-ui, sans-serif", "style": "clean"},
    {"name": "Classic", "font_family": "Georgia, serif", "style": "traditional"},
    {"name": "Minimal", "font_family": "Roboto, Arial, sans-serif", "style": "minimal"},
    {"name": "Technical", "font_family": "JetBrains Mono, monospace", "style": "code"},
    {"name": "Friendly", "font_family": "Quicksand, sans-serif", "style": "rounded"}
]

def validate_chatbot_name(name: str) -> bool:
    """Check if the chatbot name is valid."""
    return bool(re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$', name)) and len(name) <= 50

def get_theme_choice() -> Tuple[str, Dict[str, str]]:
    """
    Prompt user to select a color theme.
    
    Returns:
        tuple: (theme_name, theme_colors_dict)
    """
    print("\nSelect a color theme for your chatbot UI:")
    for i, (theme_name, colors) in enumerate(THEME_COLORS.items()):
        print(f"{i+1}. {theme_name.title()} - Primary: {colors['primary']}, Background: {colors['bg']}")
    
    while True:
        try:
            choice = input(f"\nChoose a theme (1-{len(THEME_COLORS)}) [default: 1 - Sky]: ").strip()
            if not choice:
                choice = "1"
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(THEME_COLORS):
                theme_name = list(THEME_COLORS.keys())[choice_idx]
                return theme_name, THEME_COLORS[theme_name]
            else:
                print(f"Please enter a number between 1 and {len(THEME_COLORS)}")
        except ValueError:
            print("Please enter a valid number")
    
def get_font_choice() -> Dict[str, str]:
    """
    Prompt user to select a font style.
    
    Returns:
        dict: Selected font style information
    """
    print("\nSelect a font style for your chatbot UI:")
    for i, font in enumerate(FONT_STYLES):
        print(f"{i+1}. {font['name']} - {font['font_family'].split(',')[0]}")
    
    while True:
        try:
            choice = input(f"\nChoose a font style (1-{len(FONT_STYLES)}) [default: 1 - Modern]: ").strip()
            if not choice:
                choice = "1"
                
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(FONT_STYLES):
                return FONT_STYLES[choice_idx]
            else:
                print(f"Please enter a number between 1 and {len(FONT_STYLES)}")
        except ValueError:
            print("Please enter a valid number")


def get_system_prompt(chatbot_description: str) -> str:
    """
    Get custom system prompt from file or use default.
    
    Args:
        chatbot_description: Description of the chatbot's specialty
        
    Returns:
        str: The system prompt to use
    """
    # Create a copy of the template file for the user to edit
    template_file = TEMPLATE_DIR / "system_prompt.md"
    temp_file = Path("system_prompt.md")
    
    if not template_file.exists():
        logger.warning("System prompt template not found, using default")
        return DEFAULT_SYSTEM_PROMPT.replace('{{chatbot_description}}', chatbot_description)
    
    # Copy the template file to the current directory for editing
    shutil.copy2(template_file, temp_file)
    
    print("\n" + "="*80)
    print("CUSTOM SYSTEM PROMPT")
    print("="*80)
    print(f"\nA file named '{temp_file}' has been created.")
    print("Please open this file in your text editor, replace the content with your custom")
    print(f"system prompt for a chatbot specializing in {chatbot_description}, and save it.")
    print("\nFor example, you can use another AI like ChatGPT to help create a good system prompt.")
    print("\nPress Enter when you've finished editing the file...")
    input()
    
    # Read the edited file
    try:
        with open(temp_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        # Check if this is still the template content or if it's been customized
        if "Delete everything above this line" in content:
            # User left the template intact or didn't edit
            # Extract only the default prompt
            if "## Default Prompt" in content and "## Tips" in content:
                default_section = content.split("## Default Prompt")[1].split("## Tips")[0].strip()
                return default_section.replace('{{chatbot_description}}', chatbot_description)
            else:
                return DEFAULT_SYSTEM_PROMPT.replace('{{chatbot_description}}', chatbot_description)
        
        return content
    except Exception as e:
        logger.error(f"Error reading system prompt file: {str(e)}")
        print(f"Error reading the system prompt file: {str(e)}")
        print("Using default system prompt instead.")
        return DEFAULT_SYSTEM_PROMPT.replace('{{chatbot_description}}', chatbot_description)
    finally:
        # Clean up the temporary file
        if temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass


def get_llm_parameters() -> Dict[str, Any]:
    """
    Get custom LLM parameters from file or use default.
    
    Returns:
        dict: Dictionary of LLM parameters
    """
    # Create a copy of the template file for the user to edit
    template_file = TEMPLATE_DIR / "llm_parameters.json"
    temp_file = Path("llm_parameters.json")
    
    if not template_file.exists():
        logger.warning("LLM parameters template not found, using default")
        return DEFAULT_LLM_PARAMS
    
    # Copy the template file to the current directory for editing
    shutil.copy2(template_file, temp_file)
    
    print("\n" + "="*80)
    print("CUSTOM LLM PARAMETERS")
    print("="*80)
    print(f"\nA file named '{temp_file}' has been created.")
    print("Please open this file in your text editor, adjust the parameters as needed,")
    print("and save it. The file contains documentation and examples for different use cases.")
    print("\nPress Enter when you've finished editing the file...")
    input()
    
    # Read the edited file
    try:
        with open(temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract JSON from the file (it might contain comments and examples)
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        
        if json_match:
            # Found JSON in code block format
            json_str = json_match.group(1)
            custom_params = json.loads(json_str)
        else:
            # Try to parse the whole file as JSON
            custom_params = json.loads(content)
            
        # Validate keys and set defaults for missing ones
        for key, default_value in DEFAULT_LLM_PARAMS.items():
            if key not in custom_params:
                custom_params[key] = default_value
                
        return custom_params
    except Exception as e:
        logger.error(f"Error reading LLM parameters file: {str(e)}")
        print(f"Error reading the LLM parameters file: {str(e)}")
        print("Using default LLM parameters instead.")
        return DEFAULT_LLM_PARAMS
    finally:
        # Clean up the temporary file
        if temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass

def create_directory_structure(base_path: Path, chatbot_name: str) -> Path:
    """Create the directory structure for the chatbot."""
    logger.info(f"Creating directory structure for {chatbot_name}")
    chatbot_dir = base_path / chatbot_name
    
    if chatbot_dir.exists():
        logger.warning(f"Directory {chatbot_dir} already exists")
        response = input("Directory already exists. Overwrite? [y/N]: ").lower()
        if response != 'y':
            logger.info("Aborting...")
            sys.exit(0)
        shutil.rmtree(chatbot_dir)
    
    # Create main directories
    directories = [
        "",
        "src",
        "src/static/css",
        "src/static/js",
        "src/templates",
        "src/models",
        "src/knowledge_base",
        "src/utils",
        "knowledge/documents",
        "docs",
    ]
    
    for directory in directories:
        (chatbot_dir / directory).mkdir(parents=True, exist_ok=True)
        
    return chatbot_dir

def copy_and_update_template_files(template_dir: Path, target_dir: Path, config: Dict[str, Any]) -> None:
    """Copy and update template files."""
    logger.info("Copying and updating template files")
    
    # Get all template files
    for template_path in template_dir.glob("**/*"):
        if template_path.is_file():
            # Get relative path from template directory
            relative_path = template_path.relative_to(template_dir)
            target_path = target_dir / relative_path
            
            # Make sure the parent directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Read the template, replace placeholders, and write to target
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Replace placeholders
            for key, value in config.items():
                placeholder = f"{{{{{{ {key} }}}}}}"
                content = content.replace(placeholder, str(value))
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)

def setup_knowledge_base(target_dir: Path) -> None:
    """Set up the knowledge base directory with example documents."""
    kb_dir = target_dir / "knowledge" / "documents"
    
    # Create a sample document
    sample_doc = kb_dir / "sample.md"
    with open(sample_doc, 'w', encoding='utf-8') as f:
        f.write("""# Sample Document

This is a sample document for your chatbot knowledge base. You can add more documents
in various formats:

- Text files (.txt)
- Markdown files (.md)
- Code files (.py, .js, .html, etc.)
- CSV files (.csv)
- JSON files (.json)

The chatbot will use this knowledge to answer questions related to your specific domain.
""")

def generate_dockerfile(target_dir: Path, config: Dict[str, Any]) -> None:
    """Generate a Dockerfile."""
    logger.info("Generating Dockerfile")
    
    dockerfile_content = f"""# Dockerfile for {config['chatbot_name']} Chatbot
FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV MODEL_NAME="{config['model_name']}"
ENV OLLAMA_BASE_URL="http://ollama:11434"

# Create directories for data
RUN mkdir -p /app/knowledge/documents /app/logs

# Install system dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
        curl \\
        build-essential \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \\
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY knowledge/ ./knowledge/

# Create a non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/api/health || exit 1

# Set the entrypoint
CMD ["python", "src/app.py"]
"""
    
    with open(target_dir / "Dockerfile", 'w', encoding='utf-8') as f:
        f.write(dockerfile_content)

def generate_docker_compose(target_dir: Path, config: Dict[str, Any]) -> None:
    """Generate a docker-compose.yml file."""
    logger.info("Generating docker-compose.yml")
    
    compose_data = {
        'version': '3.8',
        'services': {
            'webapp': {
                'build': {
                    'context': '.',
                    'dockerfile': 'Dockerfile'
                },
                'ports': ['5000:5000'],
                'volumes': [
                    './knowledge:/app/knowledge',
                    './logs:/app/logs'
                ],
                'environment': [
                    'FLASK_DEBUG=false',
                    f'MODEL_NAME={config["model_name"]}',
                    'OLLAMA_BASE_URL=http://ollama:11434',
                    'KNOWLEDGE_BASE_PATH=/app/knowledge/documents',
                    'LOG_INTERACTIONS=true',
                    'LOG_DIR=/app/logs'
                ],
                'depends_on': ['ollama'],
                'restart': 'unless-stopped',
                'healthcheck': {
                    'test': ['CMD', 'curl', '-f', 'http://localhost:5000/api/health'],
                    'interval': '30s',
                    'timeout': '10s',
                    'retries': 3,
                    'start_period': '10s'
                }
            },
            'ollama': {
                'image': 'ollama/ollama:latest',
                'volumes': ['ollama_data:/root/.ollama'],
                'ports': ['11434:11434'],
                'command': f'sh -c "ollama serve & sleep 10 && ollama pull {config["model_name"]} && wait"',
                'restart': 'unless-stopped',
                # GPU section is commented out by default
                # 'deploy': {
                #     'resources': {
                #         'reservations': {
                #             'devices': [{
                #                 'driver': 'nvidia',
                #                 'count': 1,
                #                 'capabilities': ['gpu']
                #             }]
                #         }
                #     }
                # }
            }
        },
        'volumes': {'ollama_data': {}}
    }
    
    with open(target_dir / "docker-compose.yml", 'w', encoding='utf-8') as f:
        yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)

def generate_requirements(target_dir: Path, config: Dict[str, Any]) -> None:
    """Generate requirements.txt file."""
    logger.info("Generating requirements.txt")
    
    requirements = """# Web framework
Flask==2.3.3
flask-cors==4.0.0
gunicorn==21.2.0
Werkzeug==2.3.7

# HTTP client for communicating with Ollama
requests==2.31.0

# Utilities
python-dotenv==1.0.0
pyyaml==6.0.1
Markdown==3.5.1
python-dateutil==2.8.2
json-schema-validator==0.1.0

# Logging and monitoring
structlog==23.2.0
"""
    
    with open(target_dir / "requirements.txt", 'w', encoding='utf-8') as f:
        f.write(requirements)

def generate_deployment_guide(target_dir: Path, config: Dict[str, Any]) -> None:
    """Generate deployment guide."""
    logger.info("Generating deployment guide")
    
    deployment_guide = f"""# Deployment Guide for {config['chatbot_name']}

This guide will help you deploy the {config['chatbot_name']} chatbot on your system.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 19.03.0+)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 1.27.0+)
- At least 4GB of RAM available for Docker

## Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/{config['github_username']}/{config['repository_name']}.git
cd {config['repository_name']}
```

### 2. Start the Chatbot

```bash
docker-compose up -d
```

This command will:
1. Download the Ollama image
2. Pull the {config['model_name']} model (this may take a few minutes on first run)
3. Build and start the web application

### 3. Access the Chatbot

Open your web browser and go to:
```
http://localhost:5000
```

You should now see the {config['chatbot_name']} interface, ready to answer your questions!

## Usage Tips

- **First-time startup**: The first time you run the chatbot, it may take a few minutes to download the LLM model.
- **Add more documents**: To add more knowledge to your chatbot, place documents in the `knowledge/documents` directory and restart the container.
- **GPU acceleration**: If you have an NVIDIA GPU, you can uncomment the GPU section in `docker-compose.yml` to enable acceleration.

## Troubleshooting

- **Container fails to start**: Ensure you have at least 4GB of memory allocated to Docker
- **Slow responses**: The {config['model_name']} model requires adequate CPU resources. Consider enabling GPU support or using a smaller model.
- **Connection issues**: Make sure ports 5000 and 11434 are not in use by other applications.

## Customization

You can customize the appearance and behavior of the chatbot:

### UI Customization
Modify the CSS files in the `src/static/css` directory.

### LLM Behavior
To adjust how the AI responds:
1. Edit the system prompt in `src/config/llm_config.json`
2. Modify LLM parameters in the same file to control response style

#### Using the Configuration Utility

For easier updates, use the included utility script:

```bash
# Update the system prompt
./update_config.py --prompt "Your new system prompt"

# Update specific LLM parameters
./update_config.py --param temperature=0.8 --param max_tokens=2048

# Load a system prompt from a file
./update_config.py --prompt-file custom_prompt.txt
```

After making changes, rebuild and restart the containers:

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## License

This project is licensed under the MIT License.
"""
    
    with open(target_dir / "docs" / "DEPLOYMENT.md", 'w', encoding='utf-8') as f:
        f.write(deployment_guide)

def generate_chatbot_guide(target_dir: Path, config: Dict[str, Any]) -> None:
    """Generate chatbot generation guide."""
    logger.info("Generating chatbot guide")
    
    chatbot_guide = f"""# {config['chatbot_name']} Chatbot - GitHub Repository Setup Guide

This guide will help you set up a GitHub repository for your newly generated chatbot.

## 1. Create a New GitHub Repository

1. Go to [GitHub](https://github.com) and sign in to your account
2. Click on the "+" icon in the top-right corner and select "New repository"
3. Enter "{config['repository_name']}" as the repository name
4. Add a description: "A custom chatbot powered by {config['model_name']} with topic-specific knowledge"
5. Choose whether the repository should be public or private
6. Select "Add a README file"
7. Click "Create repository"

## 2. Upload Your Chatbot Files

### Option 1: Using GitHub Web Interface

For a small number of files, you can upload directly through the GitHub web interface:

1. Navigate to your new repository
2. Click "Add file" > "Upload files"
3. Drag and drop all the files and folders from the generated chatbot directory
4. Add a commit message like "Initial commit of {config['chatbot_name']} chatbot"
5. Click "Commit changes"

### Option 2: Using Git Command Line (Recommended)

For the complete project with all files:

```bash
# Navigate to your chatbot directory
cd {config['chatbot_name']}

# Initialize a git repository
git init

# Add all files
git add .

# Commit the files
git commit -m "Initial commit of {config['chatbot_name']} chatbot"

# Add the remote repository
git remote add origin https://github.com/{config['github_username']}/{config['repository_name']}.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 3. Update Repository Information

1. Go to your repository settings and add topics like:
   - chatbot
   - ollama
   - llm
   - {config['model_name'].split(':')[0]}
   - flask

2. Edit the README.md file to include:
   - A description of your chatbot
   - The specific knowledge domain it covers
   - How to deploy and use it (link to DEPLOYMENT.md)

## 4. Share Your Chatbot

Once your repository is set up, you can share it with others by providing the link:

```
https://github.com/{config['github_username']}/{config['repository_name']}
```

Users can follow the instructions in DEPLOYMENT.md to deploy your chatbot on their own systems.

## 5. Making Updates

If you want to update your chatbot in the future:

1. Add new documents to the knowledge base
2. Make any code modifications needed
3. Rebuild your Docker container to test locally
4. Commit and push your changes to GitHub

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Ollama Documentation](https://ollama.com/docs)
- [GitHub Guides](https://guides.github.com/)
"""
    
    with open(target_dir / "docs" / "GITHUB_SETUP.md", 'w', encoding='utf-8') as f:
        f.write(chatbot_guide)

def generate_readme(target_dir: Path, config: Dict[str, Any]) -> None:
    """Generate README.md file."""
    logger.info("Generating README.md")
    
    readme_content = f"""# {config['chatbot_name']} - Topic-Specific Chatbot

A custom chatbot powered by the {config['model_name']} language model via Ollama. This chatbot specializes in {config['chatbot_description']} and provides a simple web interface for interactions.

## Features

- **Specialized Knowledge**: Pre-loaded with domain-specific information on {config['chatbot_description']}
- **Document Analysis**: Upload documents or code snippets for instant analysis
- **Web Interface**: User-friendly interface for chatting with the bot
- **Self-contained**: Runs in Docker with no external API dependencies
- **Portable**: Deploy anywhere Docker is available

## Quick Start

See the [Deployment Guide](./docs/DEPLOYMENT.md) for detailed instructions on how to get the chatbot running.

## Knowledge Base

This chatbot comes pre-loaded with specific knowledge about {config['chatbot_description']}. You can extend its knowledge by adding more documents to the `knowledge/documents` directory.

## Technical Details

- **LLM**: {config['model_name']}
- **Backend**: Flask Python web server
- **Inference**: Ollama local inference engine
- **Deployment**: Docker and Docker Compose
- **Date Created**: {datetime.datetime.now().strftime('%Y-%m-%d')}

## License

This project is licensed under the MIT License.
"""
    
    with open(target_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)

def generate_custom_css(target_dir: Path, theme_colors: Dict[str, str], font_style: Dict[str, str]) -> None:
    """
    Generate a custom CSS file with the selected theme colors and font style.
    
    Args:
        target_dir: Target directory path
        theme_colors: Dictionary with color values
        font_style: Dictionary with font style information
    """
    logger.info(f"Generating custom CSS with {list(theme_colors.keys())} theme and {font_style['name']} font")
    
    css_dir = target_dir / "src" / "static" / "css"
    css_dir.mkdir(parents=True, exist_ok=True)
    
    # Read the base CSS template
    base_css_path = target_dir.parent / "src" / "static" / "css" / "style.css"
    
    if base_css_path.exists():
        with open(base_css_path, 'r', encoding='utf-8') as f:
            base_css = f.read()
    else:
        logger.warning(f"Base CSS file not found at {base_css_path}")
        base_css = "/* Default styles */\n"
    
    # Create custom CSS with theme variables
    custom_css = f"""/* 
 * Custom CSS for {target_dir.name} chatbot
 * Theme: {theme_colors.get('name', 'Custom')}
 * Font: {font_style['name']}
 */

:root {{
    --primary-color: {theme_colors['primary']};
    --background-color: {theme_colors['bg']};
    --text-color: {theme_colors['text']};
    --font-family: {font_style['font_family']};
}}

body {{
    font-family: var(--font-family);
    background-color: var(--background-color);
    color: var(--text-color);
}}

.header {{
    background-color: var(--primary-color);
}}

.primary-button, button[type="submit"] {{
    background-color: var(--primary-color);
}}

.bot-message {{
    border-left: 3px solid var(--primary-color);
}}

.bot-info {{
    margin-top: 10px;
    color: #586e75;
    font-style: italic;
}}

.customization-tip {{
    background-color: rgba(var(--primary-color-rgb, 14, 165, 233), 0.1);
    border-radius: 6px;
    padding: 12px 16px;
    margin: 20px 0;
    font-size: 0.9rem;
}}

.customization-tip code {{
    background-color: rgba(0,0,0,0.05);
    padding: 2px 4px;
    border-radius: 3px;
}}

/* Base styles */
{base_css}

/* Custom {font_style['style']} style adjustments */
"""

    # Add font-specific styles
    if font_style['style'] == 'clean':
        custom_css += """
.message {
    border-radius: 4px;
}
.input-container {
    border-radius: 4px;
}
"""
    elif font_style['style'] == 'traditional':
        custom_css += """
.message {
    border-radius: 0;
    border-bottom: 1px solid rgba(0,0,0,0.1);
}
h1, h2, h3 {
    font-weight: normal;
    letter-spacing: -0.5px;
}
"""
    elif font_style['style'] == 'minimal':
        custom_css += """
* {
    transition: all 0.2s ease;
}
.message {
    border: none;
    border-bottom: 1px solid rgba(0,0,0,0.05);
    margin-bottom: 8px;
}
button {
    border-radius: 3px;
}
"""
    elif font_style['style'] == 'code':
        custom_css += """
pre, code {
    font-family: var(--font-family);
}
.message {
    border-radius: 0;
    border-left: 2px solid var(--primary-color);
}
.user-message {
    border-left: 2px solid #606060;
}
"""
    elif font_style['style'] == 'rounded':
        custom_css += """
.message {
    border-radius: 18px;
}
button {
    border-radius: 24px;
}
.chat-form input {
    border-radius: 24px;
}
"""

    # Write custom CSS file
    with open(css_dir / "style.css", 'w', encoding='utf-8') as f:
        f.write(custom_css)

def copy_source_files(source_dir: Path, target_dir: Path) -> None:
    """Copy source code files from the main chatbot app to the generated chatbot."""
    logger.info("Copying source code files")
    
    # Define files to copy
    files_to_copy = [
        ("src/app.py", "src/app.py"),
        ("src/models/llm.py", "src/models/llm.py"),
        ("src/knowledge_base/loader.py", "src/knowledge_base/loader.py"),
        ("src/knowledge_base/processor.py", "src/knowledge_base/processor.py"),
        ("src/utils/helpers.py", "src/utils/helpers.py"),
        # We'll create a custom CSS file instead of copying the original
        # ("src/static/css/style.css", "src/static/css/style.css"),
        ("src/static/js/main.js", "src/static/js/main.js"),
        ("src/templates/index.html", "src/templates/index.html"),
        ("src/templates/chat.html", "src/templates/chat.html"),
    ]
    
    # Copy template files
    template_files_to_copy = [
        ("templates/update_config.py", "update_config.py"),
    ]
    
    # Create directories if they don't exist
    for _, target_file_path in files_to_copy:
        target_path = target_dir / target_file_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    for source_file_path, target_file_path in files_to_copy:
        source_path = source_dir.parent / source_file_path
        target_path = target_dir / target_file_path
        
        if source_path.exists():
            shutil.copy2(source_path, target_path)
        else:
            logger.warning(f"Source file {source_path} does not exist")
            
    # Copy template files
    for source_file_path, target_file_path in template_files_to_copy:
        source_path = source_dir / source_file_path
        target_path = target_dir / target_file_path
        
        if source_path.exists():
            shutil.copy2(source_path, target_path)
            # Make script executable
            if target_path.suffix == '.py':
                target_path.chmod(target_path.stat().st_mode | 0o111)  # Add executable bit
        else:
            logger.warning(f"Template file {source_path} does not exist")

def generate_llm_config(target_dir: Path, system_prompt: str, llm_params: Dict[str, Any]) -> None:
    """
    Generate configuration file for the LLM parameters.
    
    Args:
        target_dir: Target directory path
        system_prompt: System prompt for the LLM
        llm_params: Dictionary of LLM parameters
    """
    logger.info("Generating LLM configuration")
    
    config_dir = target_dir / "src" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the LLM config file with metadata
    config = {
        "system_prompt": system_prompt,
        "parameters": llm_params,
        "metadata": {
            "created_at": datetime.datetime.now().isoformat(),
            "description": "Configuration for chatbot LLM behavior and response generation",
            "version": "1.0"
        }
    }
    
    with open(config_dir / "llm_config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    # Create README with instructions for customization
    readme_content = """# LLM Configuration

This directory contains configuration files that control the behavior and response style of your chatbot.

## Files

- `llm_config.json`: Main configuration file with system prompt and parameters
- `__init__.py`: Python module that provides easy access to the configuration

## How to Customize

### System Prompt

The system prompt defines the personality, knowledge, and behavior of your chatbot. To modify it:

1. Open `llm_config.json`
2. Find the "system_prompt" field
3. Replace its value with your custom prompt
4. Save the file and rebuild the Docker container

### LLM Parameters

Parameters control how the language model generates responses:

- `temperature`: Controls randomness (0.0-1.0, higher = more creative)
- `top_k`: Limits token selection to top k most likely tokens 
- `top_p`: Nucleus sampling threshold for controlled randomness
- `max_tokens`: Maximum length of generated responses
- `presence_penalty`: Reduces repetition of tokens already present
- `frequency_penalty`: Reduces repetition based on frequency

To modify these parameters, edit their values in the "parameters" section of `llm_config.json`.

After making changes, rebuild and restart the Docker container:

```bash
docker-compose down
docker-compose build
docker-compose up -d
```
"""
    
    with open(config_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Create a Python module to access the config
    py_content = """# Generated LLM configuration module
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_llm_config() -> Dict[str, Any]:
    \"\"\"
    Load LLM configuration from config file
    
    Returns:
        dict: Configuration including system prompt and parameters
    \"\"\"
    config_path = Path(__file__).parent / "llm_config.json"
    
    if not config_path.exists():
        logger.warning("LLM config file not found, using default configuration")
        return {
            "system_prompt": "You are a helpful assistant.",
            "parameters": {
                "temperature": 0.7,
                "top_k": 40,
                "top_p": 0.9,
                "max_tokens": 1024,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0
            }
        }
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load LLM config: {str(e)}")
        logger.info("Using default configuration")
        return {
            "system_prompt": "You are a helpful assistant.",
            "parameters": {
                "temperature": 0.7,
                "top_k": 40,
                "top_p": 0.9,
                "max_tokens": 1024
            }
        }
        
def update_llm_config(new_config: Dict[str, Any]) -> bool:
    \"\"\"
    Update LLM configuration
    
    Args:
        new_config: New configuration to save
        
    Returns:
        bool: True if update was successful, False otherwise
    \"\"\"
    config_path = Path(__file__).parent / "llm_config.json"
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to update LLM config: {str(e)}")
        return False
"""
    
    with open(config_dir / "__init__.py", 'w', encoding='utf-8') as f:
        f.write(py_content)


def generate_gitignore(target_dir: Path) -> None:
    """Generate .gitignore file."""
    logger.info("Generating .gitignore")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# Logs
logs/
*.log
npm-debug.log*

# Docker
.docker/

# IDE specific files
.idea/
.vscode/
*.swp
*.swo
.DS_Store
"""
    
    with open(target_dir / ".gitignore", 'w', encoding='utf-8') as f:
        f.write(gitignore_content)

def main():
    logger.info("Starting Chatbot Generator")
    
    # Welcome message
    print("\n" + "="*80)
    print("                    CUSTOM CHATBOT GENERATOR")
    print("="*80 + "\n")
    print("This tool helps you create a specialized chatbot with your own knowledge base.")
    print("The chatbot will run as a self-contained Docker container with a web UI.\n")
    
    # Get chatbot name
    while True:
        chatbot_name = input("Enter a name for your chatbot: ").strip()
        if validate_chatbot_name(chatbot_name):
            break
        print("Invalid name. Use only letters, numbers, underscores, and hyphens.")
    
    # Get chatbot description
    chatbot_description = input("\nDescribe what this chatbot specializes in: ").strip() or "general knowledge"
    
    # Get GitHub username for deployment guide
    github_username = input("\nEnter your GitHub username (for documentation): ").strip() or "yourusername"
    
    # Generate repository name (kebab case)
    repository_name = chatbot_name.lower().replace(' ', '-') + "-chatbot"
    print(f"\nRepository name will be: {repository_name}")
    
    # Display available models and choose one
    print("\nAvailable LLM models:")
    for i, model in enumerate(OLLAMA_MODELS):
        print(f"{i+1}. {model}")
    
    model_choice = input(f"\nChoose a model (1-{len(OLLAMA_MODELS)}) [default: 1 - llama3.2:1b]: ").strip()
    
    try:
        model_index = int(model_choice) - 1
        if 0 <= model_index < len(OLLAMA_MODELS):
            model_name = OLLAMA_MODELS[model_index]
        else:
            model_name = DEFAULT_MODEL
    except (ValueError, IndexError):
        model_name = DEFAULT_MODEL
    
    print(f"\nUsing model: {model_name}")
    
    # Knowledge base instructions 
    print("\nYou'll need to add documents to the knowledge base directory.")
    print("Supported formats: .txt, .md, .py, .js, .html, .csv, .json")
    
    # Select UI theme
    theme_name, theme_colors = get_theme_choice()
    
    # Select font style
    font_style = get_font_choice()
    
    # Get custom system prompt and LLM parameters
    # We're showing these instructions before to prepare the user
    print("\nNext, you'll be prompted to customize:")
    print("1. The system prompt (defining your chatbot's personality and behavior)")
    print("2. The LLM parameters (controlling response style and generation)")
    print("\nFor each, you'll edit a file in your text editor. Instructions will be provided.")
    print("What text editor would you like to use to modify these files?")
    print("For example: 'nano', 'vim', 'code', 'gedit', etc.")
    editor = input("Editor [default: system default]: ").strip() or "editor"
    
    # Set the EDITOR environment variable for this session
    os.environ['EDITOR'] = editor
    
    # Get custom system prompt from file
    system_prompt = get_system_prompt(chatbot_description)
    
    # Get LLM parameters from file
    llm_params = get_llm_parameters()
    
    # Config
    config = {
        "chatbot_name": chatbot_name,
        "chatbot_description": chatbot_description,
        "model_name": model_name,
        "github_username": github_username,
        "repository_name": repository_name,
        "date_created": datetime.datetime.now().strftime("%Y-%m-%d"),
        "theme_name": theme_name,
        "primary_color": theme_colors["primary"],
        "background_color": theme_colors["bg"],
        "text_color": theme_colors["text"],
        "font_family": font_style["font_family"],
        "font_style": font_style["style"],
        "font_name": font_style["name"]
    }
    
    # Confirm and proceed
    print("\nReady to generate your chatbot with the following settings:")
    print(f"- Name: {chatbot_name}")
    print(f"- Description: {chatbot_description}")
    print(f"- LLM Model: {model_name}")
    print(f"- GitHub Repository: {github_username}/{repository_name}")
    print(f"- UI Theme: {theme_name.title()} (Primary color: {theme_colors['primary']})")
    print(f"- Font Style: {font_style['name']} ({font_style['font_family'].split(',')[0]})")
    print(f"- Custom System Prompt: {'Yes' if system_prompt != DEFAULT_SYSTEM_PROMPT.replace('{{chatbot_description}}', chatbot_description) else 'Default'}")
    print(f"- Custom LLM Parameters: {'Yes' if llm_params != DEFAULT_LLM_PARAMS else 'Default'}")
    
    proceed = input("\nGenerate chatbot? [Y/n]: ").lower() != 'n'
    
    if not proceed:
        print("\nChatbot generation cancelled.")
        return        # Create the chatbot
    try:
        # Create directory structure
        chatbot_dir = create_directory_structure(Path.cwd(), chatbot_name)
        
        # Copy source files from main app
        copy_source_files(Path(__file__).parent, chatbot_dir)
        
        # Generate custom CSS with selected theme and font
        generate_custom_css(chatbot_dir, theme_colors, font_style)
        
        # Generate LLM configuration with custom system prompt and parameters
        generate_llm_config(chatbot_dir, system_prompt, llm_params)
        
        # Generate configuration and deployment files
        generate_dockerfile(chatbot_dir, config)
        generate_docker_compose(chatbot_dir, config)
        generate_requirements(chatbot_dir, config)
        generate_readme(chatbot_dir, config)
        generate_deployment_guide(chatbot_dir, config)
        generate_chatbot_guide(chatbot_dir, config)
        generate_gitignore(chatbot_dir)
        
        # Set up knowledge base
        setup_knowledge_base(chatbot_dir)
        
        print(f"\n✅ Chatbot generated successfully in: {chatbot_dir}")
        print("\nNext steps:")
        print(f"1. Add domain-specific documents to {chatbot_dir}/knowledge/documents/")
        print(f"2. Follow the guide in {chatbot_dir}/docs/GITHUB_SETUP.md to create a GitHub repository")
        print(f"3. Share your chatbot with others using the deployment guide")
        
    except Exception as e:
        logger.error(f"Error generating chatbot: {str(e)}", exc_info=True)
        print(f"\n❌ Error generating chatbot: {str(e)}")

if __name__ == "__main__":
    main()
