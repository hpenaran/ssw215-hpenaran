# SPRINT 2 REPORT

## PROJECT RECAP & API SURFACE

This project is a single-user portfolio website for a software engineering student to manage personal projects and showcase their progress, project history, and future plans to visitors such as potential employers. The core workflow is to create a project, save its information, enter a rough project update, use the "Polish Update" feature to generate a more organized version, and review the result before saving it to the project's history.

The backend uses Flask to handle API requests and SQLite to store project information, screenshots, technologies, and updates.

## API CONTRACT

GET /  
Returns the main portfolio website page.

GET /api/projects  
Returns all saved projects.  
Status Code: 200

GET /api/projects/<project_id>  
Returns information for one specific project.  
Status Codes: 200 if successful, 404 if the project does not exist.

POST /api/projects  
Creates a new project. The request includes the project name, description, GitHub link, status, future plans, category, technologies, featured status, and optional image uploads.  
Status Codes: 201 if created successfully, 400 if the request contains invalid information.

PUT /api/projects/<project_id>  
Updates an existing project's information.  
Status Codes: 200 if updated successfully, 400 if the request contains invalid information, 404 if the project does not exist.

DELETE /api/projects/<project_id>  
Deletes a project and its related records and uploaded images.  
Status Codes: 204 if deleted successfully, 404 if the project does not exist.

GET /api/projects/<project_id>/updates  
Returns all updates associated with a specific project.  
Status Codes: 200 if successful, 404 if the project does not exist.

GET /api/activity  
Returns the daily activity counts used to display the GitHub-style activity calendar.  
Status Code: 200

POST /api/projects/<project_id>/updates  
Creates a new project update. The request includes a rough update and can optionally include a polished update.  
Status Codes: 201 if created successfully, 400 if the request contains invalid information, 404 if the project does not exist.

PUT /api/projects/<project_id>/updates/<update_id>  
Edits an existing project update.  
Status Codes: 200 if updated successfully, 400 if the request contains invalid information, 404 if the project or update does not exist.

DELETE /api/projects/<project_id>/updates/<update_id>  
Deletes a specific update from a project.  
Status Codes: 204 if deleted successfully, 404 if the project or update does not exist.

POST /api/projects/<project_id>/updates/polish  
Receives a rough project update and returns a more organized version without immediately saving it.  
Status Codes: 200 if successful, 400 if the request contains invalid information, 404 if the project does not exist.

## DATABASE SCHEMA

The application uses SQLite with four relational tables.

projects

- id: INTEGER, primary key, automatically increments.
- name: TEXT, required.
- description: TEXT, required.
- github_link: TEXT, defaults to an empty string.
- status: TEXT, required.
- future_plans: TEXT, required.
- created_at: TEXT, required.
- updated_at: TEXT, required.
- main_image: TEXT, defaults to an empty string.
- category: TEXT, defaults to "Personal Project".
- featured: INTEGER, defaults to 0. Used to determine whether a project is featured.

project_screenshots

- id: INTEGER, primary key, automatically increments.
- project_id: INTEGER, foreign key referencing projects.id.
- path: TEXT, stores the screenshot file path.

project_technologies

- id: INTEGER, primary key, automatically increments.
- project_id: INTEGER, foreign key referencing projects.id.
- technology: TEXT, stores the name of a technology associated with the project.

updates

- id: INTEGER, primary key, automatically increments.
- project_id: INTEGER, foreign key referencing projects.id.
- rough_update: TEXT, stores the original update written by the user.
- polished_update: TEXT, stores the organized version of the update.
- created_at: TEXT, stores when the update was created.

The project_screenshots, project_technologies, and updates tables use project_id to connect their records to the projects table. Foreign key constraints with ON DELETE CASCADE ensure that related records are automatically deleted when their project is deleted.

## HOW TO RUN & TEST

1. Clone the repository.

   git clone <your-github-repository-url>

2. Navigate into the project folder and install the dependencies.

   cd <your-project-folder>
   pip install -r requirements.txt

3. Start the Flask backend.

   python app.py

4. Open http://127.0.0.1:5000 in your browser. Create a project, add technologies and images, edit its information, create an update, use the Polish Update feature, and check that the information remains saved after restarting the application. You can also test deleting a project to confirm its related records are removed.

## AI USAGE LOG & REFLECTION

I used AI to help transition the backend from JSON file storage to an SQLite database. I also used it to understand how to organize the database tables, connect Flask routes to database operations, and handle relationships between projects, screenshots, technologies, and updates. AI helped me review the API structure, request methods, and expected HTTP status codes.

I tested the backend by creating, editing, retrieving, and deleting projects and updates. I also checked that project information remained saved after restarting the application and that deleting a project removed its related records. This helped me understand the importance of testing database relationships and making sure API responses match what the frontend expects.

## PERSISTENCE REFLECTION

Using SQLite instead of JSON files makes the application easier to organize as it grows. With JSON, I would have to manually manage IDs and rewrite entire files whenever information changed. SQLite allows me to use primary keys, foreign keys, and SQL queries to manage related information more reliably. It also provides better support for handling multiple database operations without having to manually manage the entire data file.