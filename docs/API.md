# API Documentation

## Overview

SafeLine provides a web interface for form submission and data management. This document describes the API endpoints and data structures.

## Authentication

Authentication uses Flask sessions with hardcoded credentials:

- Reporter: username "reporter", password "report123"
- Reviewer: username "reviewer", password "review123"

## Endpoints

### Authentication

**POST /**
- Login endpoint
- Parameters:
  - role: "reporter" or "reviewer"
  - password: authentication password
- Response: Redirect to /report or /reviewer

**GET /logout**
- Logout endpoint
- Response: Redirect to login page

### Reporter

**GET /report**
- Display incident report form
- Requires: reporter role
- Response: HTML form

**POST /submit**
- Submit incident report
- Requires: reporter role, all required fields
- Parameters: Form fields for incident data
- Response: Redirect to /report with success flag

### Reviewer

**GET /reviewer**
- Display submitted reports
- Requires: reviewer role
- Response: HTML dashboard with report table

**POST /convert_and_upload**
- Convert CSV to RDF and upload to Fuseki
- Requires: reporter or reviewer role
- Response: JSON with success status

### Utility

**GET /?error=1**
- Login with error message
- Response: Login page with error

## Data Structures

### Form Submission

The form collects:

Organization:
- org_id: Organization identifier
- input_by: Person recording the data
- date_received: When report was received
- date_recorded: When data was recorded

Location:
- country: Country
- state: State or province
- town: Town or city
- village: Village
- camp: Refugee camp (if applicable)

Incident:
- incident_date: Date of incident
- violence_type: Type of violence
- short_desc: Brief description
- num_victims: Number of victims

Victim:
- victim_age: Age group
- victim_gender: Gender

Perpetrator:
- num_perpetrators: Number of perpetrators
- perp_affiliation: Perpetrator group

Publication:
- pub_type: Publication type
- pub_date: Publication date
- pub_link: Link to source

### RDF Output

Form data is converted to RDF Turtle format:

```turtle
@prefix sord: <http://fieldlab2.org/ontology/sord#> .
@prefix schema: <http://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://fieldlab2.org/data/CASE-20251213-abc123> 
    a sord:SexualViolenceIncident ;
    sord:recordId "CASE-20251213-abc123" ;
    sord:organisationId "ORG-001" ;
    sord:inputBy "John Doe" ;
    sord:hasLocation <http://fieldlab2.org/data/location_CASE-20251213-abc123> ;
    sord:hasVictim <http://fieldlab2.org/data/victim_CASE-20251213-abc123> .

<http://fieldlab2.org/data/location_CASE-20251213-abc123>
    a sord:Location ;
    sord:locationName "Nairobi, Kenya" .
```

### CSV Output

Data is also stored in CSV format:

| case_id | org_id | input_by | date_received | ... |
|---------|--------|----------|---------------|-----|
| CASE-... | ORG-1 | John Doe | 2025-12-13 | ... |

## Response Codes

**200 OK** - Successful request
**302 Found** - Redirect
**403 Forbidden** - Unauthorized access
**404 Not Found** - Resource not found
**500 Internal Error** - Server error
**502 Bad Gateway** - Fuseki unavailable

## Error Handling

Errors are returned as JSON:

```json
{
  "success": false,
  "message": "Error description"
}
```

## Rate Limiting

No rate limiting implemented. For production, add rate limiting middleware.

## Data Validation

The form validates:

- Required fields not empty
- Dates are valid and logical
- Numbers are positive
- Incident date not in future

Validation errors are shown to user with field highlighting.

## Fuseki Integration

Data is automatically uploaded to Fuseki at:

`POST {FUSEKI_BASE}/sord/data`

Headers:
- Content-Type: text/turtle

The application handles:
- Dataset creation if missing
- Data serialization to Turtle
- HTTP error responses from Fuseki

## Session Management

Session data:

```python
session["role"]  # "reporter" or "reviewer"
```

Sessions expire on browser close. For production, set session timeout.

## CORS

No CORS headers implemented. Add if frontend runs on different domain.

## Pagination

Reviewer dashboard shows all reports without pagination. For large datasets, implement pagination in /reviewer endpoint.

## Search and Filter

No search implemented. To add:

1. Add query parameter to /reviewer
2. Filter data in Python before rendering
3. Update HTML with search form

## Export

No export endpoint implemented. To add:

1. Implement /export endpoint
2. Return CSV with proper headers
3. Or return JSON representation

## Future API Enhancements

1. RESTful SPARQL interface
2. Bulk upload via API
3. Data export endpoints
4. User management API
5. Permission-based access control
6. API key authentication
