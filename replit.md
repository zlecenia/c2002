# 02 Project

## Overview
This is a simple Node.js web application that was imported from GitHub (https://github.com/zlecenia/02). The original repository contained only a README file, so a complete web application structure was created to make it functional in the Replit environment.

## Recent Changes
- **September 29, 2025**: Complete project setup from minimal GitHub import
  - Added Node.js/Express.js server configuration
  - Created frontend interface with HTML, CSS, and JavaScript
  - Configured Replit workflow for port 5000
  - Set up deployment configuration for autoscale

## Project Architecture
- **Backend**: Express.js server running on port 5000 (0.0.0.0 for Replit compatibility)
- **Frontend**: Static HTML/CSS/JS served from /public directory
- **API**: Basic REST endpoint at /api/hello
- **Deployment**: Configured for autoscale deployment target

## Key Features
- Express.js web server
- Static file serving
- Basic API endpoint
- Responsive frontend interface
- Replit-optimized configuration

## Structure
```
/
├── server.js          # Main Express server
├── package.json       # Node.js dependencies and scripts
├── public/            # Static frontend files
│   ├── index.html     # Main webpage
│   ├── style.css      # Styling
│   └── script.js      # Frontend JavaScript
└── replit.md          # This documentation
```

## Current State
The application is fully functional and running. The web server is configured to run on port 5000 with proper host binding for Replit's proxy environment. The deployment is configured for production use with autoscale target.