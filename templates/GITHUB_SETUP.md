# {{ chatbot_name }} Chatbot - GitHub Repository Setup Guide

This guide will help you set up a GitHub repository for your newly generated chatbot.

## 1. Create a New GitHub Repository

1. Go to [GitHub](https://github.com) and sign in to your account
2. Click on the "+" icon in the top-right corner and select "New repository"
3. Enter "{{ repository_name }}" as the repository name
4. Add a description: "A custom chatbot powered by {{ model_name }} with topic-specific knowledge"
5. Choose whether the repository should be public or private
6. Select "Add a README file"
7. Click "Create repository"

## 2. Upload Your Chatbot Files

### Option 1: Using GitHub Web Interface

For a small number of files, you can upload directly through the GitHub web interface:

1. Navigate to your new repository
2. Click "Add file" > "Upload files"
3. Drag and drop all the files and folders from the generated chatbot directory
4. Add a commit message like "Initial commit of {{ chatbot_name }} chatbot"
5. Click "Commit changes"

### Option 2: Using Git Command Line (Recommended)

For the complete project with all files:

```bash
# Navigate to your chatbot directory
cd {{ chatbot_name }}

# Initialize a git repository
git init

# Add all files
git add .

# Commit the files
git commit -m "Initial commit of {{ chatbot_name }} chatbot"

# Add the remote repository
git remote add origin https://github.com/{{ github_username }}/{{ repository_name }}.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 3. Update Repository Information

1. Go to your repository settings and add topics like:
   - chatbot
   - ollama
   - llm
   - {{ model_name.split(':')[0] }}
   - flask

2. Edit the README.md file to include:
   - A description of your chatbot
   - The specific knowledge domain it covers
   - How to deploy and use it (link to DEPLOYMENT.md)

## 4. Share Your Chatbot

Once your repository is set up, you can share it with others by providing the link:

```
https://github.com/{{ github_username }}/{{ repository_name }}
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
