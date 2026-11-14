import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlparse

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE_PATH = INSTANCE_DIR / "portfolio.db"
PROJECTS_PATH = DATA_DIR / "projects.json"
UPDATES_PATH = DATA_DIR / "updates.json"
UPLOADS_DIR = BASE_DIR / "static" / "uploads"
MAX_IMAGE_SIZE = 8 * 1024 * 1024
MAX_SCREENSHOTS = 8
app.config["MAX_CONTENT_LENGTH"] = 80 * 1024 * 1024

INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


@contextmanager
def connect_db():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


SEED_PROJECTS = [
    {
        "id": 1,
        "name": "Personal Portfolio",
        "description": "A polished site for my software engineering work, personal projects, and professional growth.",
        "github_link": "https://github.com/hpenaran",
        "status": "In Progress",
        "future_plans": "Refine the portfolio, add more projects, and prepare a stronger professional narrative.",
        "created_at": "2026-11-10T15:00:00Z",
        "updated_at": "2026-11-10T15:00:00Z",
    },
    {
        "id": 2,
        "name": "Study Planner",
        "description": "A personal study dashboard designed to track assignments, habits, and learning milestones.",
        "github_link": "https://github.com/hpenaran",
        "status": "Planning",
        "future_plans": "Map out weekly learning goals, automate reminders, and test the dashboard with real study data.",
        "created_at": "2026-11-10T15:05:00Z",
        "updated_at": "2026-11-10T15:05:00Z",
    },
]

SEED_UPDATES = [
    {
        "id": 1,
        "project_id": 1,
        "rough_update": "I refined the hero section and organized the project cards for a cleaner portfolio layout.",
        "polished_update": "I refined the hero section and organized the project cards to create a cleaner, more focused portfolio experience.",
        "created_at": "2026-11-10T15:10:00Z",
    },
    {
        "id": 2,
        "project_id": 2,
        "rough_update": "I mapped the project roadmap and started planning the daily learning workflow.",
        "polished_update": "I mapped the project roadmap and started planning a daily learning workflow to keep progress structured and measurable.",
        "created_at": "2026-11-10T15:12:00Z",
    },
]

def add_project_defaults(project):
    defaults = {
        "main_image": "",
        "screenshots": [],
        "technologies": [],
        "category": "Personal Project",
        "featured": False,
    }
    changed = False
    for key, value in defaults.items():
        if key not in project:
            project[key] = value
            changed = True
    if not isinstance(project["screenshots"], list):
        project["screenshots"] = []
        changed = True
    if not isinstance(project["technologies"], list):
        project["technologies"] = []
        changed = True
    if not isinstance(project["main_image"], str):
        project["main_image"] = ""
        changed = True
    screenshots = [path for path in project["screenshots"] if isinstance(path, str)]
    technologies = [
        technology for technology in project["technologies"] if isinstance(technology, str)
    ]
    if screenshots != project["screenshots"]:
        project["screenshots"] = screenshots
        changed = True
    if technologies != project["technologies"]:
        project["technologies"] = technologies
        changed = True
    if not isinstance(project["featured"], bool):
        project["featured"] = False
        changed = True
    return changed


def read_legacy_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file_obj:
        loaded = json.load(file_obj)
    if not isinstance(loaded, type(default)):
        raise ValueError(f"Legacy data in {path.name} must be a {type(default).__name__}.")
    return loaded


def insert_project(connection, project):
    add_project_defaults(project)
    connection.execute(
        """
        INSERT INTO projects (
            id, name, description, github_link, status, future_plans,
            created_at, updated_at, main_image, category, featured
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project["id"], project.get("name", ""), project.get("description", ""),
            project.get("github_link", ""), project.get("status", "Planning"),
            project.get("future_plans", ""), project.get("created_at", now_iso()),
            project.get("updated_at", now_iso()), project["main_image"],
            project["category"], int(project["featured"]),
        ),
    )
    connection.executemany(
        "INSERT INTO project_screenshots (project_id, path) VALUES (?, ?)",
        [(project["id"], path) for path in project["screenshots"]],
    )
    connection.executemany(
        "INSERT INTO project_technologies (project_id, technology) VALUES (?, ?)",
        [(project["id"], technology) for technology in project["technologies"]],
    )


def initialize_database():
    with connect_db() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                github_link TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL,
                future_plans TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                main_image TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL DEFAULT 'Personal Project',
                featured INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS project_screenshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                path TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS project_technologies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                technology TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                rough_update TEXT NOT NULL,
                polished_update TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        if connection.execute("SELECT COUNT(*) FROM projects").fetchone()[0]:
            return

        projects = read_legacy_json(PROJECTS_PATH, [])
        if not projects:
            projects = [dict(project) for project in SEED_PROJECTS]
        for project in projects:
            insert_project(connection, project)

        updates = read_legacy_json(UPDATES_PATH, [])
        if not updates and not PROJECTS_PATH.exists():
            updates = [dict(update) for update in SEED_UPDATES]
        valid_project_ids = {
            row["id"] for row in connection.execute("SELECT id FROM projects")
        }
        connection.executemany(
            """
            INSERT INTO updates (id, project_id, rough_update, polished_update, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    update["id"], update["project_id"], update.get("rough_update", ""),
                    update.get("polished_update", ""), update.get("created_at", now_iso()),
                )
                for update in updates
                if update.get("project_id") in valid_project_ids
            ],
        )


initialize_database()


def project_by_id(project_id):
    with connect_db() as connection:
        row = connection.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        if row is None:
            return None
        project = dict(row)
        project["featured"] = bool(project["featured"])
        project["screenshots"] = [
            item["path"] for item in connection.execute(
                "SELECT path FROM project_screenshots WHERE project_id = ? ORDER BY id",
                (project_id,),
            )
        ]
        project["technologies"] = [
            item["technology"] for item in connection.execute(
                "SELECT technology FROM project_technologies WHERE project_id = ? ORDER BY id",
                (project_id,),
            )
        ]
        return project


def all_projects():
    with connect_db() as connection:
        project_ids = [
            row["id"] for row in connection.execute("SELECT id FROM projects ORDER BY id")
        ]
    return [project_by_id(project_id) for project_id in project_ids]


def updates_for_project(project_id):
    with connect_db() as connection:
        rows = connection.execute(
            "SELECT * FROM updates WHERE project_id = ? ORDER BY created_at DESC, id DESC",
            (project_id,),
        )
        return [dict(row) for row in rows]


def persist_project(project, creating=False):
    with connect_db() as connection:
        if project["featured"]:
            connection.execute("UPDATE projects SET featured = 0")

        if creating:
            cursor = connection.execute(
                """
                INSERT INTO projects (
                    name, description, github_link, status, future_plans,
                    created_at, updated_at, main_image, category, featured
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project["name"], project["description"], project["github_link"],
                    project["status"], project["future_plans"], project["created_at"],
                    project["updated_at"], project["main_image"], project["category"],
                    int(project["featured"]),
                ),
            )
            project["id"] = cursor.lastrowid
        else:
            connection.execute(
                """
                UPDATE projects SET
                    name = ?, description = ?, github_link = ?, status = ?,
                    future_plans = ?, updated_at = ?, main_image = ?, category = ?,
                    featured = ?
                WHERE id = ?
                """,
                (
                    project["name"], project["description"], project["github_link"],
                    project["status"], project["future_plans"], project["updated_at"],
                    project["main_image"], project["category"], int(project["featured"]),
                    project["id"],
                ),
            )
            connection.execute(
                "DELETE FROM project_screenshots WHERE project_id = ?", (project["id"],)
            )
            connection.execute(
                "DELETE FROM project_technologies WHERE project_id = ?", (project["id"],)
            )

        connection.executemany(
            "INSERT INTO project_screenshots (project_id, path) VALUES (?, ?)",
            [(project["id"], path) for path in project["screenshots"]],
        )
        connection.executemany(
            "INSERT INTO project_technologies (project_id, technology) VALUES (?, ?)",
            [(project["id"], technology) for technology in project["technologies"]],
        )

    return project


def update_by_id(update_id):
    with connect_db() as connection:
        row = connection.execute(
            "SELECT * FROM updates WHERE id = ?", (update_id,)
        ).fetchone()
        return dict(row) if row is not None else None


def create_update_record(project_id, rough_update, polished_update):
    update = {
        "project_id": project_id,
        "rough_update": rough_update,
        "polished_update": polished_update,
        "created_at": now_iso(),
    }
    with connect_db() as connection:
        cursor = connection.execute(
            """
            INSERT INTO updates (project_id, rough_update, polished_update, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                update["project_id"], update["rough_update"],
                update["polished_update"], update["created_at"],
            ),
        )
        update["id"] = cursor.lastrowid
    return update


def clean_required_string(value, field_name):
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")

    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required.")

    return cleaned


def form_or_json_payload():
    if request.is_json:
        return request.get_json(silent=True)
    return request.form.to_dict()


def parse_bool(value, field_name):
    if isinstance(value, bool):
        return value
    if value in (None, "", "false", "0", "off"):
        return False
    if value in ("true", "1", "on"):
        return True
    raise ValueError(f"{field_name} must be true or false.")


def validate_project_payload(payload, existing=None):
    if not isinstance(payload, dict):
        raise ValueError("Project data must be a JSON object.")

    name = clean_required_string(payload.get("name"), "Project name")
    description = clean_required_string(payload.get("description"), "Description")
    github_value = payload.get("github_link", (existing or {}).get("github_link", ""))
    if github_value is None:
        github_value = ""
    if not isinstance(github_value, str):
        raise ValueError("GitHub link must be text.")
    github_link = github_value.strip()
    status = clean_required_string(
        payload.get("status", (existing or {}).get("status", "Planning")),
        "Current status",
    )
    allowed_statuses = {"Planning", "In Progress", "Completed"}
    if status not in allowed_statuses:
        raise ValueError("Current status must be Planning, In Progress, or Completed.")
    future_plans = clean_required_string(payload.get("future_plans"), "Future plans")

    if github_link:
        parsed = urlparse(github_link)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("GitHub link must be a valid URL when provided.")
        if len(github_link) > 300:
            raise ValueError("GitHub link must be 300 characters or fewer.")

    category = clean_required_string(
        payload.get("category", (existing or {}).get("category", "Personal Project")),
        "Project category",
    )
    categories = {
        "Web Application",
        "Mobile App",
        "Desktop Application",
        "Personal Project",
    }
    if category not in categories:
        raise ValueError("Choose a supported project category.")

    technologies_value = payload.get(
        "technologies", (existing or {}).get("technologies", [])
    )
    if isinstance(technologies_value, str):
        technologies = [item.strip() for item in technologies_value.split(",")]
    elif isinstance(technologies_value, list) and all(
        isinstance(item, str) for item in technologies_value
    ):
        technologies = [item.strip() for item in technologies_value]
    else:
        raise ValueError("Technologies must be a list or comma-separated text.")
    technologies = list(dict.fromkeys(item for item in technologies if item))
    if len(technologies) > 20 or any(len(item) > 40 for item in technologies):
        raise ValueError("Use up to 20 technologies, each 40 characters or fewer.")

    featured = parse_bool(
        payload.get("featured", (existing or {}).get("featured", False)),
        "Featured",
    )

    return {
        "name": name,
        "description": description,
        "github_link": github_link,
        "status": status,
        "future_plans": future_plans,
        "technologies": technologies,
        "category": category,
        "featured": featured,
    }


def validate_image_upload(upload):
    if upload is None or not upload.filename:
        return None

    filename = secure_filename(upload.filename)
    extension = Path(filename).suffix.lower()
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    if extension not in allowed_extensions:
        raise ValueError("Images must be JPG, PNG, GIF, or WEBP files.")

    contents = upload.stream.read(MAX_IMAGE_SIZE + 1)
    upload.stream.seek(0)
    if len(contents) > MAX_IMAGE_SIZE:
        raise ValueError("Each image must be 8 MB or smaller.")

    signatures = {
        ".jpg": contents.startswith(b"\xff\xd8\xff"),
        ".jpeg": contents.startswith(b"\xff\xd8\xff"),
        ".png": contents.startswith(b"\x89PNG\r\n\x1a\n"),
        ".gif": contents.startswith((b"GIF87a", b"GIF89a")),
        ".webp": contents.startswith(b"RIFF") and contents[8:12] == b"WEBP",
    }
    if not signatures[extension]:
        raise ValueError("The uploaded file does not match its image type.")
    return contents, extension


def save_image_upload(upload, validated_upload):
    if validated_upload is None:
        return ""
    contents, extension = validated_upload
    filename = f"{uuid4().hex}{extension}"
    target = UPLOADS_DIR / filename
    with target.open("wb") as file_obj:
        file_obj.write(contents)
    return f"uploads/{filename}"


def remove_uploaded_file(relative_path):
    if not isinstance(relative_path, str) or not relative_path:
        return
    target = (BASE_DIR / "static" / relative_path).resolve()
    uploads_root = UPLOADS_DIR.resolve()
    if uploads_root not in target.parents:
        return
    target.unlink(missing_ok=True)


def apply_project_images(project, payload, existing=None):
    main_upload = request.files.get("main_image")
    screenshot_uploads = [
        upload for upload in request.files.getlist("screenshots") if upload.filename
    ]
    if len(screenshot_uploads) > MAX_SCREENSHOTS:
        raise ValueError(f"Upload no more than {MAX_SCREENSHOTS} screenshots at once.")

    validated_main = validate_image_upload(main_upload)
    validated_screenshots = [
        (upload, validate_image_upload(upload)) for upload in screenshot_uploads
    ]

    clear_main = parse_bool(
        request.form.get(
            "remove_main_image",
            payload.get("remove_main_image", False),
        ),
        "Remove main image",
    )
    clear_screenshots = parse_bool(
        request.form.get(
            "clear_screenshots",
            payload.get("clear_screenshots", False),
        ),
        "Clear screenshots",
    )
    removed_screenshots = request.form.getlist("remove_screenshots")
    if not request.form and isinstance(payload.get("remove_screenshots"), list):
        removed_screenshots = payload["remove_screenshots"]
    previous_main = (existing or {}).get("main_image", "")
    previous_screenshots = list((existing or {}).get("screenshots", []))
    if any(path not in previous_screenshots for path in removed_screenshots):
        raise ValueError("A screenshot selected for removal does not belong to this project.")

    saved_files = []
    try:
        if validated_main is not None:
            project["main_image"] = save_image_upload(main_upload, validated_main)
            saved_files.append(project["main_image"])
        elif clear_main:
            project["main_image"] = ""

        remaining_screenshots = (
            [] if clear_screenshots else [
                path for path in previous_screenshots if path not in removed_screenshots
            ]
        )
        for upload, validated in validated_screenshots:
            path = save_image_upload(upload, validated)
            saved_files.append(path)
            remaining_screenshots.append(path)
        if len(remaining_screenshots) > MAX_SCREENSHOTS:
            raise ValueError(f"A project can have no more than {MAX_SCREENSHOTS} screenshots.")
        project["screenshots"] = remaining_screenshots
    except Exception:
        for path in saved_files:
            remove_uploaded_file(path)
        raise

    old_files = []
    if previous_main and previous_main != project.get("main_image"):
        old_files.append(previous_main)
    old_files.extend(
        path for path in previous_screenshots if path not in project["screenshots"]
    )
    return old_files, saved_files


def validate_update_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Update data must be a JSON object.")

    rough_update = clean_required_string(payload.get("rough_update"), "Rough update")
    polished_update = payload.get("polished_update")
    if polished_update is not None:
        if not isinstance(polished_update, str):
            raise ValueError("Polished update must be text when provided.")
        polished_update = polished_update.strip()
        if not polished_update:
            raise ValueError("Polished update cannot be empty.")

    return {
        "rough_update": rough_update,
        "polished_update": polished_update,
    }


def polish_update_text(rough_update):
    cleaned = " ".join(rough_update.split())
    if not cleaned:
        raise ValueError("Rough update is required.")

    sentence = cleaned[0].upper() + cleaned[1:]
    if not sentence.endswith("."):
        sentence += "."

    return (
        f"{sentence} I am now tightening the details, validating the experience, and preparing the next step for the project."
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/projects")
def get_projects():
    return jsonify(all_projects()), 200


@app.get("/api/projects/<int:project_id>")
def get_project(project_id):
    project = project_by_id(project_id)
    if project is None:
        return jsonify({"error": "Project not found."}), 404
    return jsonify(project), 200


@app.post("/api/projects")
def create_project():
    payload = form_or_json_payload()
    try:
        validated = validate_project_payload(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    project = {
        "name": validated["name"],
        "description": validated["description"],
        "github_link": validated["github_link"],
        "status": validated["status"],
        "future_plans": validated["future_plans"],
        "technologies": validated["technologies"],
        "category": validated["category"],
        "featured": validated["featured"],
        "main_image": "",
        "screenshots": [],
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    try:
        _, saved_files = apply_project_images(project, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        persist_project(project, creating=True)
    except (OSError, sqlite3.Error):
        for path in saved_files:
            remove_uploaded_file(path)
        raise
    return jsonify(project), 201


@app.put("/api/projects/<int:project_id>")
def update_project(project_id):
    project = project_by_id(project_id)
    if project is None:
        return jsonify({"error": "Project not found."}), 404

    payload = form_or_json_payload()
    try:
        validated = validate_project_payload(payload, project)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    old_values = dict(project)
    project["name"] = validated["name"]
    project["description"] = validated["description"]
    project["github_link"] = validated["github_link"]
    project["status"] = validated["status"]
    project["future_plans"] = validated["future_plans"]
    project["technologies"] = validated["technologies"]
    project["category"] = validated["category"]
    project["featured"] = validated["featured"]
    project["updated_at"] = now_iso()
    try:
        old_files, saved_files = apply_project_images(project, payload, old_values)
    except ValueError as exc:
        project.update(old_values)
        return jsonify({"error": str(exc)}), 400

    try:
        persist_project(project)
    except (OSError, sqlite3.Error):
        for path in saved_files:
            remove_uploaded_file(path)
        raise
    for path in old_files:
        remove_uploaded_file(path)
    return jsonify(project), 200


@app.delete("/api/projects/<int:project_id>")
def delete_project(project_id):
    project = project_by_id(project_id)
    if project is None:
        return jsonify({"error": "Project not found."}), 404

    removed_files = [project.get("main_image", "")]
    removed_files.extend(project.get("screenshots", []))
    with connect_db() as connection:
        connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    for path in removed_files:
        remove_uploaded_file(path)
    return "", 204


@app.get("/api/projects/<int:project_id>/updates")
def get_updates(project_id):
    if project_by_id(project_id) is None:
        return jsonify({"error": "Project not found."}), 404
    return jsonify(updates_for_project(project_id)), 200


@app.get("/api/activity")
def get_activity():
    counts = {}
    with connect_db() as connection:
        updates = connection.execute("SELECT created_at FROM updates")
        for update in updates:
            created_at = update["created_at"]
            try:
                day = datetime.fromisoformat(created_at.replace("Z", "+00:00")).date().isoformat()
            except (TypeError, ValueError):
                continue
            counts[day] = counts.get(day, 0) + 1
    return jsonify(
        [{"date": day, "count": count} for day, count in sorted(counts.items())]
    ), 200


@app.post("/api/projects/<int:project_id>/updates")
def create_update(project_id):
    if project_by_id(project_id) is None:
        return jsonify({"error": "Project not found."}), 404

    payload = form_or_json_payload()
    try:
        validated = validate_update_payload(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    update = create_update_record(
        project_id,
        validated["rough_update"],
        validated["polished_update"] or polish_update_text(validated["rough_update"]),
    )
    return jsonify(update), 201


@app.put("/api/projects/<int:project_id>/updates/<int:update_id>")
def edit_update(project_id, update_id):
    if project_by_id(project_id) is None:
        return jsonify({"error": "Project not found."}), 404

    update = update_by_id(update_id)
    if update is None or update.get("project_id") != project_id:
        return jsonify({"error": "Update not found."}), 404

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Update data must be a JSON object."}), 400

    try:
        rough_update = clean_required_string(payload.get("rough_update"), "Rough update")
        polished_update = payload.get("polished_update", update.get("polished_update"))
        if not isinstance(polished_update, str) or not polished_update.strip():
            raise ValueError("Polished update is required.")
        polished_update = polished_update.strip()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    update["rough_update"] = rough_update
    update["polished_update"] = polished_update
    with connect_db() as connection:
        connection.execute(
            "UPDATE updates SET rough_update = ?, polished_update = ? WHERE id = ?",
            (rough_update, polished_update, update_id),
        )
    return jsonify(update), 200


@app.delete("/api/projects/<int:project_id>/updates/<int:update_id>")
def delete_update(project_id, update_id):
    if project_by_id(project_id) is None:
        return jsonify({"error": "Project not found."}), 404

    update = update_by_id(update_id)
    if update is None or update.get("project_id") != project_id:
        return jsonify({"error": "Update not found."}), 404

    with connect_db() as connection:
        connection.execute("DELETE FROM updates WHERE id = ?", (update_id,))
    return "", 204


@app.post("/api/projects/<int:project_id>/updates/polish")
def polish_update(project_id):
    if project_by_id(project_id) is None:
        return jsonify({"error": "Project not found."}), 404

    payload = form_or_json_payload()
    if not isinstance(payload, dict):
        return jsonify({"error": "Rough update is required."}), 400

    try:
        rough_update = clean_required_string(payload.get("rough_update"), "Rough update")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    polished = polish_update_text(rough_update)
    return jsonify({"polished_update": polished}), 200


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"error": "Resource not found."}), 404


@app.errorhandler(500)
def handle_server_error(error):
    return jsonify({"error": "Internal server error."}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
