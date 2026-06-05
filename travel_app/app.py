from flask import Flask, request, jsonify
from models import db, Project, Place
import requests


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///travel.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return {"message": "Travel API is running"}

@app.route("/projects", methods=["POST"])
def create_project():
    data = request.get_json()

    if not data or not data.get("name"):
        return {"error": "Project name is required"}, 400

    places_data = data.get("places", [])

    if places_data and len(places_data) > 10:
        return {"error": "Project cannot contain more than 10 places"}, 400

    if len(places_data) == 0:
        return {"error": "Project must contain at least one place"}, 400

    external_ids = [str(place.get("external_id")) for place in places_data]

    if len(external_ids) != len(set(external_ids)):
        return {"error": "Duplicate places are not allowed in one project"}, 400

    project = Project(
        name=data["name"],
        description=data.get("description"),
        start_date=data.get("start_date")
    )

    db.session.add(project)
    db.session.flush()

    created_places = []

    for place_data in places_data:
        external_id = place_data.get("external_id")

        if not external_id:
            db.session.rollback()
            return {"error": "external_id is required for each place"}, 400

        artwork = get_artwork(external_id)

        if not artwork:
            db.session.rollback()
            return {"error": f"Artwork with external_id {external_id} not found"}, 404

        place = Place(
            project_id=project.id,
            external_id=str(external_id),
            title=artwork.get("title", "Unknown title"),
            notes=place_data.get("notes"),
            visited=False
        )

        db.session.add(place)
        created_places.append(place)

    db.session.commit()

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "start_date": project.start_date,
        "is_completed": project.is_completed,
        "places": [
            {
                "id": place.id,
                "project_id": place.project_id,
                "external_id": place.external_id,
                "title": place.title,
                "notes": place.notes,
                "visited": place.visited
            }
            for place in created_places
        ]
    }, 201

@app.route("/projects", methods=["GET"])
def get_projects():
    projects = Project.query.all()

    result = []

    for project in projects:
        result.append({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "start_date": project.start_date,
            "is_completed": project.is_completed
        })

    return jsonify(result)

@app.route("/projects/<int:project_id>", methods=["GET"])
def get_project(project_id):
    project = Project.query.get_or_404(project_id)

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "start_date": project.start_date,
        "is_completed": project.is_completed
    }

@app.route("/projects/<int:project_id>", methods=["PUT"])
def update_project(project_id):
    project = Project.query.get_or_404(project_id)

    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    if "name" in data:
        project.name = data["name"]

    if "description" in data:
        project.description = data["description"]

    if "start_date" in data:
        project.start_date = data["start_date"]

    db.session.commit()

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "start_date": project.start_date,
        "is_completed": project.is_completed
    }

@app.route("/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)

    has_visited_places = any(place.visited for place in project.places)

    if has_visited_places:
        return {
            "error": "Project cannot be deleted because it has visited places"
        }, 400

    db.session.delete(project)
    db.session.commit()

    return {"message": "Project deleted"}

def get_artwork(external_id):
    url = f"https://api.artic.edu/api/v1/artworks/{external_id}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    return response.json().get("data")

@app.route("/projects/<int:project_id>/places", methods=["POST"])
def add_place_to_project(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json()

    if not data or not data.get("external_id"):
        return {"error": "external_id is required"}, 400

    if len(project.places) >= 10:
        return {"error": "Project cannot contain more than 10 places"}, 400

    existing_place = Place.query.filter_by(
        project_id=project.id,
        external_id=str(data["external_id"])
    ).first()

    if existing_place:
        return {"error": "Place already exists in this project"}, 400

    artwork = get_artwork(data["external_id"])

    if not artwork:
        return {"error": "Artwork not found"}, 404

    place = Place(
        project_id=project.id,
        external_id=str(data["external_id"]),
        title=artwork.get("title", "Unknown title"),
        notes=data.get("notes"),
        visited=False
    )

    db.session.add(place)
    db.session.commit()

    return {
        "id": place.id,
        "project_id": place.project_id,
        "external_id": place.external_id,
        "title": place.title,
        "notes": place.notes,
        "visited": place.visited
    }, 201

@app.route("/projects/<int:project_id>/places", methods=["GET"])
def get_project_places(project_id):
    project = Project.query.get_or_404(project_id)

    result = []

    for place in project.places:
        result.append({
            "id": place.id,
            "project_id": place.project_id,
            "external_id": place.external_id,
            "title": place.title,
            "notes": place.notes,
            "visited": place.visited
        })

    return jsonify(result)

@app.route("/projects/<int:project_id>/places/<int:place_id>", methods=["GET"])
def get_project_place(project_id, place_id):
    place = Place.query.filter_by(id=place_id, project_id=project_id).first_or_404()

    return {
        "id": place.id,
        "project_id": place.project_id,
        "external_id": place.external_id,
        "title": place.title,
        "notes": place.notes,
        "visited": place.visited
    }

@app.route("/projects/<int:project_id>/places/<int:place_id>", methods=["PUT"])
def update_place(project_id, place_id):
    place = Place.query.filter_by(id=place_id, project_id=project_id).first_or_404()

    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    if "notes" in data:
        place.notes = data["notes"]

    if "visited" in data:
        place.visited = data["visited"]

    project = Project.query.get(project_id)

    if project.places and all(p.visited for p in project.places):
        project.is_completed = True
    else:
        project.is_completed = False

    db.session.commit()

    return {
        "id": place.id,
        "project_id": place.project_id,
        "external_id": place.external_id,
        "title": place.title,
        "notes": place.notes,
        "visited": place.visited
    }


if __name__ == "__main__":
    app.run(debug=True)
