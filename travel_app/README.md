# Travel Projects API

Flask CRUD API for managing travel projects and places imported from the Art Institute of Chicago API.

## Overview

This application allows users to create travel projects, add places from the Art Institute of Chicago API, manage notes, track visited places, and automatically complete projects when all places have been visited.

## Technologies

* Python 3
* Flask
* Flask-SQLAlchemy
* SQLite
* Requests

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd travel_app
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python app.py
```

The application will start on:

```text
http://127.0.0.1:5000
```

## Database

The application uses SQLite.

The database file is created automatically when the application starts:

```text
travel.db
```

## Third-Party API

Places are validated using the Art Institute of Chicago API:

```text
https://api.artic.edu/api/v1/artworks/{external_id}
```

## API Endpoints

### Projects

Create project:

```http
POST /projects
```

Get all projects:

```http
GET /projects
```

Get project by ID:

```http
GET /projects/<project_id>
```

Update project:

```http
PUT /projects/<project_id>
```

Delete project:

```http
DELETE /projects/<project_id>
```

### Places

Add place to project:

```http
POST /projects/<project_id>/places
```

Get all places in project:

```http
GET /projects/<project_id>/places
```

Get place by ID:

```http
GET /projects/<project_id>/places/<place_id>
```

Update place notes or visited status:

```http
PUT /projects/<project_id>/places/<place_id>
```

## Example Request

Create a project with places:

```json
{
  "name": "Chicago Trip",
  "description": "Art museum visit",
  "start_date": "2026-07-01",
  "places": [
    {
      "external_id": "129884",
      "notes": "Want to visit this artwork"
    }
  ]
}
```

## Business Rules

* A project must contain at least one place.
* A project can contain a maximum of 10 places.
* The same place cannot be added twice to the same project.
* Places are validated through the Art Institute of Chicago API before being stored.
* A project cannot be deleted if any of its places are marked as visited.
* When all places in a project are marked as visited, the project is automatically marked as completed.

## HTTP Status Codes

* 200 OK
* 201 Created
* 400 Bad Request
* 404 Not Found

## Author

Leonid Lishchynskyi
