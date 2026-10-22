import json
from pathlib import Path

from flask import Flask, jsonify, render_template

app = Flask(__name__)

PROJECTS_FILE = Path(__file__).resolve().parent / "projects.json"


def load_projects():
    with PROJECTS_FILE.open(encoding="utf-8") as projects_file:
        return json.load(projects_file)


@app.route("/")
def index():
    projects_db = load_projects()
    return render_template("index.html", projects=projects_db)


@app.post("/api/projects/<int:project_id>/upvote")
def upvote_project(project_id):
    projects_db = load_projects()
    project = next(
        (project for project in projects_db if project["id"] == project_id),
        None,
    )
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    project["likes"] += 1
    with PROJECTS_FILE.open("w", encoding="utf-8") as projects_file:
        json.dump(projects_db, projects_file, indent=2)

    return jsonify({"project_id": project_id, "likes": project["likes"]})


if __name__ == "__main__":
    app.run(debug=True)
