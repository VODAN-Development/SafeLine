# Installation Guide

## Quick Start

### Option 1: Local Development

1. Install Python 3.8+
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Start Fuseki:
   ```
   docker-compose up -d
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open http://localhost:5000 in your browser

### Option 2: Docker Deployment

1. Build and run everything with Docker Compose:
   ```
   docker-compose up -d
   ```

2. The Flask app needs to be containerized separately. Create a Dockerfile for the Flask app in the project root.

### Option 3: Cloud Deployment (Render)

See DEPLOYMENT.md for detailed instructions.

## Configuration

Create a .env file in the project root:

```
FUSEKI_BASE=http://localhost:3030
FUSEKI_ADMIN_USER=admin
FUSEKI_ADMIN_PASSWORD=admin123
FLASK_SECRET_KEY=your-secret-key-here
```

## Testing

Login credentials for testing:

Reporter:
- Username: reporter
- Password: report123

Reviewer:
- Username: reviewer
- Password: review123

Note: Change these credentials in production by modifying the auth section in app.py.

## Troubleshooting

**Port already in use:**
If port 3030 is in use, modify docker-compose.yml to use a different port.

**Fuseki connection error:**
Ensure Fuseki is running: `docker ps`

**Forms not submitting:**
Check browser console for errors. Verify Fuseki is accessible at the configured URL.

## Next Steps

1. Review DEPLOYMENT.md for production setup
2. Check DEVELOPMENT.md for contributing guidelines
3. Read the main README.md for architecture overview
