from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.String(20), nullable=True)
    is_completed = db.Column(db.Boolean, default=False)

    places = db.relationship(
        "Place",
        backref="project",
        cascade="all, delete-orphan",
        lazy=True
    )


class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)

    external_id = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    visited = db.Column(db.Boolean, default=False)
