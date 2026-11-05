import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    projects = db.relationship("Project", backref="author")


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False, default="")
    likes = db.Column(db.Integer, nullable=False, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "likes": self.likes,
            "author_id": self.author_id,
            "author_name": self.author.name,
        }


def init_seed_data():
    if db.session.query(Project.id).first() is not None:
        return

    seed_file = Path(__file__).resolve().parent / "projects_seed.json"
    with seed_file.open("r", encoding="utf-8") as projects_file:
        seed_projects = json.load(projects_file)

    author = Author(name="Henry Penaranda")
    db.session.add(author)
    for project in seed_projects:
        db.session.add(
            Project(
                id=project["id"],
                title=project["title"],
                description=project["description"],
                likes=project["likes"],
                author=author,
            )
        )
    db.session.commit()


@app.route("/")
def index():
    projects = Project.query.all()
    return render_template("index.html", projects=projects)


@app.get("/api/projects")
def get_projects():
    projects = Project.query.all()
    return jsonify([project.to_dict() for project in projects])


@app.post("/api/projects")
def create_project():
    data = request.get_json(silent=True)
    title = data.get("title") if isinstance(data, dict) else None
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "A non-empty title is required"}), 400

    title = title.strip()
    if len(title) > 120:
        return jsonify({"error": "The title must be 120 characters or fewer"}), 400

    author = Author.query.filter_by(name="Henry Penaranda").first()
    if author is None:
        return jsonify({"error": "Project author is not available"}), 500

    project = Project(title=title, description="", likes=0, author=author)
    db.session.add(project)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Could not create project; the title must be unique"}), 400

    return jsonify(project.to_dict()), 201


@app.post("/api/projects/<int:project_id>/upvote")
def upvote_project(project_id):
    project = db.session.get(Project, project_id)
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    project.likes += 1
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Could not update project"}), 400

    return jsonify({"project_id": project_id, "likes": project.likes})


Path(app.instance_path).mkdir(parents=True, exist_ok=True)
with app.app_context():
    db.create_all()
    init_seed_data()


if __name__ == "__main__":
    app.run(debug=True)
