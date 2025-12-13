# Development Guide

## Architecture Overview

SafeLine consists of three main components:

1. Web Interface (Flask)
   - User authentication
   - Multi-step form
   - Report submission

2. Data Processing
   - CSV storage
   - RDF conversion

3. Data Storage (Fuseki)
   - RDF triple store
   - SPARQL querying

## Project Structure

```
safeline-app/
├── app.py                      # Flask application and routes
├── csv_reports_to_rdf.py       # CSV to RDF conversion
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Fuseki container configuration
├── Dockerfile                  # Fuseki image configuration
├── docker-entrypoint.sh        # Fuseki startup script
├── .gitignore                  # Git ignore rules
├── templates/                  # HTML templates
│   ├── login.html
│   ├── form.html
│   └── reviewer.html
├── docs/                       # Documentation
│   ├── INSTALLATION.md
│   ├── DEPLOYMENT.md
│   ├── DEVELOPMENT.md
│   └── API.md
└── README.md                   # Main documentation
```

## Key Components

### Flask Application (app.py)

Main routes:

- GET / - Login page
- POST / - Authentication
- GET /report - Reporter form
- POST /submit - Form submission (auto-uploads to Fuseki)
- GET /reviewer - Reviewer dashboard
- POST /convert_and_upload - Manual RDF upload
- GET /logout - Session cleanup

Key functions:

- save_report_to_fuseki() - Converts form data to RDF and uploads
- ensure_fuseki_dataset() - Creates Fuseki dataset if missing
- current_role() - Gets user role from session

### RDF Conversion (csv_reports_to_rdf.py)

Converts CSV rows to RDF triples using SORD ontology:

- Parses CSV with DictReader
- Creates RDF graph with Turtle serialization
- Maps CSV fields to SORD properties
- Handles data type conversion (dates, integers)

### Data Flow

1. User submits form via Flask
2. Data saved to CSV file
3. save_report_to_fuseki() converts data to RDF
4. RDF posted to Fuseki /sord/data endpoint
5. Data persists in Fuseki triple store

## Development Workflow

### Setting Up Development Environment

1. Clone the repository
2. Create virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Start Fuseki:
   ```
   docker-compose up -d
   ```

5. Run Flask:
   ```
   python app.py
   ```

6. Access at http://localhost:5000

### Making Changes

To modify the application:

1. Update app.py or other Python files
2. Flask auto-reloads on changes (development mode)
3. Test with provided demo credentials
4. Commit changes with clear messages

### Adding New Fields

To add a new field to incident reports:

1. Add column to CSV header in app.py (line with writer.writerow)
2. Add form input to templates/form.html
3. Add JavaScript handling in form.html for new step if needed
4. Map field to SORD property in csv_reports_to_rdf.py
5. Add RDF triple generation in save_report_to_fuseki()
6. Update documentation

### Testing

1. Test reporter workflow:
   - Login as reporter
   - Fill form with test data
   - Submit and verify Fuseki data

2. Test reviewer workflow:
   - Login as reviewer
   - View submitted data
   - Test convert/upload button

3. Test error cases:
   - Submit with missing required fields
   - Test with invalid dates
   - Test with Fuseki offline

## Code Style

- Use clear variable names
- Add comments for complex logic
- Follow PEP 8 Python style guide
- Validate user input
- Handle exceptions gracefully

## Dependencies

Key libraries used:

- Flask 2.3.2 - Web framework
- rdflib 7.0.0 - RDF processing
- requests 2.31.0 - HTTP requests
- gunicorn 21.2.0 - Production server

See requirements.txt for exact versions.

## Deployment Process

1. Make changes locally
2. Test thoroughly
3. Commit to Git
4. Push to GitHub
5. Render auto-deploys on push

## Debugging

Enable Flask debug mode:
```
python app.py  # Runs in debug mode by default
```

Check Fuseki logs:
```
docker logs safeline-fuseki
```

Check application logs:
- Render: Dashboard > Logs
- Local: Console output

## Common Issues

**CSV file grows too large:**
Implement periodic archiving or database storage.

**Fuseki out of memory:**
Use persistent TDB2 storage instead of in-memory.

**Form submission timeout:**
Increase timeout in requests.post() calls.

**Character encoding issues:**
Ensure all files use UTF-8 encoding.

## Future Improvements

1. Database for user management
2. Better error handling and user feedback
3. Data export in multiple formats
4. Advanced SPARQL querying interface
5. User role management
6. Audit logging
7. Data validation rules engine
8. Multi-language interface

## Contact

For development questions, see the main repository CONTRIBUTING.md file.
