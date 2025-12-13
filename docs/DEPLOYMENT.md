# Deployment Guide

## Render Deployment

This guide covers deploying SafeLine to Render.com.

### Step 1: Prepare Your Repository

Ensure your GitHub repository has all required files:

- app.py
- csv_reports_to_rdf.py
- requirements.txt
- Dockerfile
- docker-entrypoint.sh
- docker-compose.yml (optional)
- templates/ folder with HTML files
- README.md

### Step 2: Deploy Fuseki Service

1. Go to https://render.com/dashboard
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure:
   - Name: safeline-fuseki
   - Region: Choose based on your location
   - Runtime: Docker
   - Build Command: (leave empty)
   - Start Command: (leave empty)

5. Add Environment Variables:
   - ADMIN_PASSWORD: (secure password)

6. Select Instance Type: Free (or Starter for production)
7. Click "Create Web Service"

Note the service URL (e.g., https://safeline-fuseki.onrender.com)

### Step 3: Deploy Flask Application

1. Create another Web Service
2. Configure:
   - Name: safeline-flask
   - Region: Same as Fuseki
   - Runtime: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn app:app --bind 0.0.0.0:$PORT

3. Add Environment Variables:
   - FUSEKI_BASE: https://safeline-fuseki.onrender.com
   - FUSEKI_ADMIN_USER: admin
   - FUSEKI_ADMIN_PASSWORD: (same as Fuseki service)
   - FLASK_SECRET_KEY: (generate a secure key)

4. Select Instance Type: Free
5. Click "Create Web Service"

### Step 4: Verification

1. Access the Flask app at the provided Render URL
2. Test reporter login with demo credentials
3. Submit a test report
4. Verify data appears in Fuseki at https://safeline-fuseki.onrender.com

### Step 5: Production Considerations

Before production:

1. Change default passwords in CONTRIBUTING.md or environment variables
2. Use a proper database for user credentials instead of hardcoded values
3. Enable HTTPS (Render does this automatically)
4. Set up database for user management
5. Configure persistent storage if using Render Disk
6. Set up monitoring and logging
7. Create backup strategy for data
8. Review and implement security best practices

## Local Docker Deployment

To run locally with Docker:

```bash
docker-compose up -d
python app.py
```

This starts:
- Fuseki on http://localhost:3030
- Flask app on http://localhost:5000

## Environment Variables Reference

| Variable | Purpose | Default |
|----------|---------|---------|
| FUSEKI_BASE | Fuseki server URL | http://localhost:3030 |
| FUSEKI_ADMIN_USER | Fuseki username | admin |
| FUSEKI_ADMIN_PASSWORD | Fuseki password | admin123 |
| FLASK_SECRET_KEY | Flask session key | change-this-in-production |

## Monitoring

For production deployments:

1. Monitor Render service logs
2. Set up alerts for service failures
3. Monitor disk space for CSV file growth
4. Monitor Fuseki triple store size
5. Check for authentication failures

## Scaling

For increased traffic:

1. Upgrade Flask service instance type on Render
2. Consider database for user management
3. Implement caching for reviewer queries
4. Consider separate Fuseki instance for read queries

## Backup and Recovery

1. Regularly download CSV files as backup
2. Export Fuseki data periodically
3. Test restore procedures
4. Keep database backups separate from code repository

## Support

For issues with Render deployment, see:
- Render Documentation: https://render.com/docs
- SafeLine GitHub Issues: (link to repository)
