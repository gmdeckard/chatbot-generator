# {{ chatbot_name }} Chatbot

This is the main configuration file for the {{ chatbot_name }} chatbot, which specializes in {{ chatbot_description }}.

## Main Configuration

- **Model**: {{ model_name }}
- **Created**: {{ date_created }}
- **Repository**: https://github.com/{{ github_username }}/{{ repository_name }}

## Features

- **Specialized Knowledge Base**: Custom information about {{ chatbot_description }}
- **Document Analysis**: Upload files for the chatbot to analyze
- **Customizable Behavior**: Tailored system prompt and LLM parameters
- **Docker Deployment**: Easy setup with Docker Compose

## Customization

### LLM Parameters
The chatbot's response behavior can be customized by editing `src/config/llm_config.json`, which contains:
- **System Prompt**: Defines the chatbot's personality and behavior
- **Parameters**: Controls temperature, token limits, and other generation settings

You can use the included utility script to update the configuration:
```bash
# Update system prompt
./update_config.py --prompt "Your new system prompt"

# Update parameters
./update_config.py --param temperature=0.8 --param max_tokens=2048

# Update system prompt from a file
./update_config.py --prompt-file my_prompt.txt
```

## How to Use

See the [Deployment Guide](./docs/DEPLOYMENT.md) for detailed instructions on how to deploy and use this chatbot.
