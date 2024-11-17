# Patent Infringement Analyzer

A web application that analyzes potential patent infringements by comparing company products against patent claims using AI.

## Quick Demo

![Demo](demo.gif)

## Quick Start Guide

1. Unzip the project folder:
   `unzip patent-infringement-analyzer.zip`

2. Create a .env file in the root directory:

   ```bash
   # Create .env file and add your OpenAI API key
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

3. Start the application:
   `docker-compose up -d`

4. Wait approximately 30 seconds for services to initialize

5. Access the application:

- Open your browser and visit: http://localhost:4000

## Using the Application

1. Search and select a patent using the patent search bar
2. Search and select a company using the company search bar
3. Click "Analyze Patent Infringement" to run the analysis
4. View results in Pretty or JSON format
5. Save important analyses for future reference
6. View saved reports in the "Saved Reports" tab
   Notes: Saved Reports tab will default show all saved reports for all companies, filter saved report with company dropdown.

## Troubleshooting

If you encounter any issues:

1. Ensure Docker container is running.
2. Check if ports 4000 and 8000 are available
3. Try restarting the services:
   `docker-compose down;
docker-compose up -d`

### Compactible docker version

docker version  
Client:
Cloud integration: v1.0.29
Version: 20.10.21
API version: 1.41
Go version: go1.18.7
Git commit: baeda1f
Built: Tue Oct 25 18:01:18 2022
OS/Arch: darwin/arm64
Context: default
Experimental: true

Server: Docker Desktop 4.15.0 (93002)
Engine:
Version: 20.10.21
API version: 1.41 (minimum version 1.12)
Go version: go1.18.7
Git commit: 3056208
Built: Tue Oct 25 17:59:41 2022
OS/Arch: linux/arm64
Experimental: false
containerd:
Version: 1.6.10
GitCommit: 770bd0108c32f3fb5c73ae1264f7e503fe7b2661
runc:
Version: 1.1.4
GitCommit: v1.1.4-0-g5fd4c4d
docker-init:
Version: 0.19.0
