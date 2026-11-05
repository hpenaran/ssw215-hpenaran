import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

PROJECTS_FILE = Path(__file__).resolve().parent / "projects.json"


def load_projects():
    with PROJECTS_FILE.open("r", encoding="utf-8") as projects_file:
        return json.load(projects_file)


@app.route("/")
def index():
    projects_db = load_projects()
    return render_template("index.html", projects=projects_db)


@app.post("/api/projects")
def create_project():
    data = request.get_json()
    title = data.get("title") if isinstance(data, dict) else None
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "A non-empty title is required"}), 400

    title = title.strip()
    projects_db = load_projects()
    project = {
        "id": max((item["id"] for item in projects_db), default=0) + 1,
        "title": title,
        "description": "",
        "likes": 0,
    }
    projects_db.append(project)

    with PROJECTS_FILE.open("w", encoding="utf-8") as projects_file:
        json.dump(projects_db, projects_file, indent=2)

    return jsonify(project), 201


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
