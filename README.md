# SQL to NoSQL-Converter

## Introduction

This project was developed as a part of my bachelor thesis at Aalen University.
It converts standard SQL into Cypher Query Language. 
At the moment it supports only Cypher, but it can be further developed with other NoSQL languages.

The basis of the client application was taken from https://github.com/SimonRuttmann/ERModellingTool and extended appropriately.

The server application was newly created for this project.

## Guide

This is a guide how to install and run the application locally.

### Frontend

1. Navigate to: https://nodejs.org/en/download/
2. Download the executable or package depending on your operating system
3. Verify node is installed with the command "node-v" in the integrated terminal
4. Go to the frontend/reactapp folder
5. Type in command terminal: "npm install" (all dependencies will be installed)
6. Run the command in terminal: "npm start" and the development server should start, after some seconds 
    the browser should start and show the application (if not start a browser and navigate to localhost:3000)

### Backend

1. Download the zip from the Repository.

I am listing at least two possible ways to run the application.

With Console:
1. Install Python 3.10.8 directly : https://www.python.org/downloads/release/python-3108/
2. Go inside the unzipped project folder
3. Navigate to the backend folder
4. Run the command: "pip install -r requirements.txt" (should install missing packages)
5. Open the Console in this folder (for example: SHIFT+RIGHTCLICK => open powershell)
6. Run the command: "flask --app main/BackendFlask run" (should start the development flask server)

With PyCharm:
1. Install PyCharm: https://www.jetbrains.com/de-de/pycharm/
2. Open the unzipped project in PyCharm
3. Install Python version
4. Import missing packages
5. Open the Terminal in PyCharm
6. Navigate to the backend folder
7. Run the command: "flask --app main/BackendFlask run" (should start the development flask server)

To close the application just press "CONTROL + C" or close the console.
