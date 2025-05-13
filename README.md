# Chatbot Generator

A tool for creating specialized, self-contained chatbots with custom knowledge bases. This generator allows you to quickly build a Docker container with an Ollama LLM server and a web UI for interacting with domain-specific knowledge.

## Features

- **Easy Setup**: Simple command-line interface to configure your chatbot
- **Custom Knowledge**: Add your own documents to create a specialized knowledge base
- **LLM Options**: Choose from various Llama, Mistral, and other open-source models
- **UI Customization**: 
  - 5 professionally designed color themes (Sky, Forest, Lavender, Sunset, Ocean)
  - 5 font style options (Modern, Classic, Minimal, Technical, Friendly)
- **AI Behavior Control**:
  - Custom system prompt to define chatbot personality and expertise
  - Fine-tuned LLM parameters (temperature, top_k, top_p, etc.)
  - Guided process to get optimal prompts from other AI systems
- **Deployment Ready**: Generates a complete, ready-to-deploy Docker application
- **GitHub Integration**: Includes guides for creating and sharing your chatbot via GitHub

## Prerequisites

- Python 3.7+
- Docker and Docker Compose (for running the generated chatbot)
- Basic knowledge of terminal/command line

## Quick Start

```bash
# Clone this repository
git clone https://github.com/yourusername/chatbot-generator.git
cd chatbot-generator

# Make the script executable
chmod +x generate_chatbot.py

# Run the generator
python generate_chatbot.py
```

Follow the prompts to configure your chatbot with:
- A custom name
- Description of its specialty/knowledge domain
- Choice of LLM model
- UI theme colors (5 attractive options)
- Font style and typography (5 modern options)
- Custom system prompt and LLM parameters (get assistance from another LLM)
- GitHub username (for documentation)

## Generated Chatbot Structure

The generator creates a complete project with the following structure:

```
your-chatbot-name/
├── docs/
│   ├── DEPLOYMENT.md        # Guide for deploying the chatbot
│   └── GITHUB_SETUP.md      # Guide for creating a GitHub repository
├── knowledge/
│   └── documents/           # Directory for knowledge base documents
├── src/
│   ├── config/              # Configuration files for LLM behavior
│   │   └── llm_config.json  # Custom system prompt and parameters
│   └── ...                  # Application source code
├── .gitignore
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker container definition
├── README.md                # Project documentation
└── requirements.txt         # Python dependencies
```

## Adding Knowledge

After generating your chatbot, add domain-specific documents to the `knowledge/documents/` directory before building the Docker container.

## AI Customization

The generator helps you create a specialized AI assistant with two key customization options:

### System Prompt

The system prompt defines your chatbot's personality, expertise level, and response behavior. The generator provides:
- A helpful default prompt that you can use out-of-the-box
- Guidance on creating an optimal custom prompt using another AI system
- Easy way to paste in a custom prompt created elsewhere

### LLM Parameters

Fine-tune how the language model generates responses with customizable parameters:
- **Temperature**: Controls randomness (0.0-1.0, higher = more creative)
- **Top_k**: Limits token selection to top k most likely tokens
- **Top_p**: Uses nucleus sampling for controlled randomness
- **Max Tokens**: Sets maximum response length
- **Presence/Frequency Penalty**: Reduces repetition in responses

You can input these as a JSON object during the chatbot generation process.

### Examples

#### Example System Prompt for a Coding Assistant

```
You are CodingGuru, a specialized programming assistant for JavaScript and React development.
When answering coding questions:
1. First explain the core concept in simple terms
2. Provide a code example that demonstrates best practices
3. Point out common pitfalls and how to avoid them
4. Add comments to explain complex parts of your code
5. Offer resources for further learning when appropriate

If you're asked about technologies outside your expertise (JavaScript/React), acknowledge your limitations but try to provide general guidance where possible.
```

#### Example LLM Parameters for Different Use Cases

**Creative Writing Bot:**
```json
{
  "temperature": 0.8,
  "top_p": 0.9,
  "max_tokens": 2048,
  "frequency_penalty": 0.5
}
```

**Technical Documentation Bot:**
```json
{
  "temperature": 0.3,
  "top_p": 0.85,
  "max_tokens": 1024,
  "frequency_penalty": 0.2
}
```

## Deployment

The generated chatbot includes a comprehensive deployment guide in `docs/DEPLOYMENT.md` with instructions for:

1. Cloning the repository
2. Starting the Docker containers
3. Accessing the web interface
4. Troubleshooting common issues

## Advanced Usage

### Testing Your Custom Configurations

After generating your chatbot, you can test your custom system prompt and LLM parameters:

```bash
# Navigate to your chatbot directory
cd your-chatbot-name

# Start the chatbot
docker-compose up -d

# Open the web interface
xdg-open http://localhost:5000
```

### Modifying Configurations After Deployment

To change the system prompt or LLM parameters after deployment:

1. Edit the configuration file:
   ```bash
   nano src/config/llm_config.json
   ```

2. Rebuild and restart the Docker containers:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

### Sharing Your Custom Chatbot

After customizing your chatbot:

1. Push to GitHub following the instructions in `docs/GITHUB_SETUP.md`
2. Share the repository link with others
3. They can deploy their own instance following the deployment guide

## License

This project is licensed under the MIT License - see the LICENSE file for details.
