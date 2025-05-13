# Deployment Guide for {{ chatbot_name }}

This guide will help you deploy the {{ chatbot_name }} chatbot on your system.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 19.03.0+)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 1.27.0+)
- At least 4GB of RAM available for Docker

## Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/{{ github_username }}/{{ repository_name }}.git
cd {{ repository_name }}
```

### 2. Start the Chatbot

```bash
docker-compose up -d
```

This command will:
1. Download the Ollama image
2. Pull the {{ model_name }} model (this may take a few minutes on first run)
3. Build and start the web application

### 3. Access the Chatbot

Open your web browser and go to:
```
http://localhost:5000
```

You should now see the {{ chatbot_name }} interface, ready to answer your questions!

## Usage Tips

- **First-time startup**: The first time you run the chatbot, it may take a few minutes to download the LLM model.
- **Add more documents**: To add more knowledge to your chatbot, place documents in the `knowledge/documents` directory and restart the container.
- **GPU acceleration**: If you have an NVIDIA GPU, you can uncomment the GPU section in `docker-compose.yml` to enable acceleration.

## Troubleshooting

- **Container fails to start**: Ensure you have at least 4GB of memory allocated to Docker
- **Slow responses**: The {{ model_name }} model requires adequate CPU resources. Consider enabling GPU support or using a smaller model.
- **Connection issues**: Make sure ports 5000 and 11434 are not in use by other applications.

## Customization

You can customize the appearance and behavior of the chatbot by modifying the files in the `src` directory. After making changes, rebuild and restart the containers:

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## License

This project is licensed under the MIT License.
