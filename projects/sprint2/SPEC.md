# SPEC: Personal Project Tracker and Developer Portfolio Website

## 1. Purpose & Scope

### 1.1 One-Sentence Pitch

A single-user project portfolio website where a software engineering student manages personal projects, tracks project updates and history, and displays current projects and future plans for visitors, including potential employers.

### 1.2 Target Persona

An individual software engineering student who wants to organize personal projects, document progress, and showcase completed work, current projects, and future plans to potential employers and other visitors.

### 1.3 Core Workflow

The primary workflow is:

1. Create a project.
2. Enter and save the project's information.
3. Add a rough project update.
4. Click **"Polish Update"** to generate a polished update using a single-turn LLM API call.
5. Review the generated update.
6. Choose to save and display the polished update in the project's history.

The interface must directly support this workflow. Additional portfolio features must not distract from or replace it.

### 1.4 IS / IS NOT Matrix

**The system IS:**
- A focused personal utility for one software engineering student to manage and showcase personal projects, progress, and future plans.
- A public-facing, view-only portfolio for visitors.
- A project tracker with project records, update history, current status, and upcoming plans.
- A website that uses AI to transform rough project updates into concise, polished reports.
- A responsive, interactive frontend built with HTML5, CSS, and vanilla JavaScript.

**The system IS NOT:**
- A multi-user portfolio platform, team collaboration tool, or enterprise project management system.
- A social media platform with comments, likes, follows, feeds, or user-to-user messaging.
- A system that allows visitors to edit projects or contribute updates.
- A GitHub-integrated application that automatically tracks commits.
- A system that uses autonomous AI agents or background workers.
- A multi-page website requiring routing or a complex application architecture.

### 1.5 Secondary Portfolio Welcome Page Requirements

The website may incorporate the following welcome-page features when they support the primary project tracker:

- A hero section introducing Henry Penaranda as a second-year software engineering student.
- The subtitle "2/4 Software Engineer".
- The biography: "I am dedicated to learning and becoming an expert in my field. I love turning big ideas into reality".
- A "See my projects" button that navigates to the projects section.
- A GitHub profile link to https://github.com/hpenaran.
- A dark blue background and white GitHub link near the bottom of the page.
- A "Contact me (coming soon)" button that is disabled and visibly unavailable.

The welcome section is secondary to the project tracker. The project management interface, update-polishing workflow, and project history must remain the primary focus. The contact button must remain disabled, and no contact form should be implemented.

## 2. Functional Requirements and Boundaries

### 2.1 What the System DOES

1. Allows the owner to create and manage project records containing:
   - Project name
   - Description
   - GitHub link
   - Current status
   - Future plans
   - Project update history

2. Displays a public, view-only portfolio featuring:
   - All saved projects
   - The main current project
   - Recent project updates
   - Upcoming plans
   - A rolling 12-month activity calendar that shows every day of each month, drops its oldest month, and adds each new month automatically.

3. Allows the owner to enter rough project updates and request a polished version using a single-turn LLM API call.

4. Allows the owner to review the polished output before saving or displaying it.

5. Maintains project update history, including the date, original rough update, and polished update.

6. Supports a report of what was accomplished today when requested or when relevant to the owner's workflow.

7. Uses interactive project cards, status tags, buttons, forms, and other visual indicators to make information easy to navigate.

8. Uses vanilla JavaScript and DOM event listeners to validate input, respond to user actions, and update the interface dynamically.

### 2.2 What the System DOES NOT

1. Support multiple user accounts, team workspaces, visitor editing, or collaborative project management.
2. Include public comments, likes, follows, feeds, or user-to-user messaging.
3. Automatically retrieve GitHub commits, issues, or other repository information through GitHub APIs.
4. Use autonomous AI agents, scheduled background workers, or continuous AI processing.
5. Require multi-page routing, a complex backend, or a contact form.
6. Expand into a general-purpose project management platform.

### 2.3 Rule of Ones

- **One target persona:** An individual software engineering student.
- **One core user journey:** Create a project, save its information, write a rough update, polish it, review it, and display the finalized update.
- **Two database entities:** Projects and Updates.
- **One AI capability:** A single-turn LLM call that transforms a rough project update into a concise, polished update. The same capability may generate a report of today's accomplishments when requested, without introducing a separate AI workflow.

## 3. Technical Requirements

### 3.1 Project Structure

The source code must be organized into the following files and directories:

app.py: Main Flask application, application configuration, and API routes.

templates/index.html: Main HTML page served by Flask.

static/style.css: All styling and responsive layout rules.

static/app.js: Vanilla JavaScript, event listeners, frontend validation, and API communication.

static/assets/avatar.jpg: Relative-path avatar image, if the welcome-page requirements are retained.

instance/portfolio.db: SQLite database for persistent project records and updates.

SPEC.md: Project requirements and technical specifications.

SPRINT1.md: Project recap, workflow demo instructions, and AI usage reflection.

requirements.txt: Python dependencies, including Flask.

The application must run locally through Flask at http://localhost:5000.

The Flask application must serve HTML from the templates directory and static assets from the static directory.

All backend functionality must reside in Python files. Frontend functionality must remain separated into HTML, CSS, and JavaScript.

### 3.2 HTML Structure and Interface

1. Use semantic HTML5 elements, including one `<header>`, one `<nav>`, one `<main>`, one `<footer>`, and appropriate `<section>` elements with headings.
2. Use exactly one `<h1>`, with heading levels that do not skip levels.
3. Include a primary project management interface that supports the core workflow.
4. Include a project creation form with fields for the project name, description, GitHub link, status, and future plans.
5. Include a project update form with a rough-update input and a "Polish Update" button.
6. Include a review area for the polished update and a way to save or display the accepted version.
7. Display projects as `<article class="card">` elements inside a flex container using `display: flex`, `flex-wrap: wrap`, and `gap`.
8. Include a navigation link to the projects section and a link to the owner's GitHub profile.
9. If the welcome-page design is included, use the relative avatar path `./assets/avatar.jpg`.
10. Embed initial component state in HTML using semantic elements and `data-*` attributes where appropriate so JavaScript can read and manipulate the interface state.

### 3.3 CSS and Responsive Design

1. `style.css` must begin with the following universal reset:

   `*, *::before, *::after { box-sizing: border-box; }`

2. Use Flexbox or CSS Grid to create a clean, responsive layout.
3. Use a dark blue background if incorporating the welcome-page visual design.
4. Make the GitHub link near the bottom of the page white.
5. Use `rem` for spacing and font sizes. Pixels may be used only for borders.
6. Ensure the layout collapses into a single vertical column on screens narrower than 768px.
7. Prevent horizontal scrolling at a viewport width of 375px.
8. Use clear visual hierarchy through project cards, buttons, status tags, containers, and progress indicators where appropriate.
9. Keep all styling in `style.css` and use class selectors rather than ID selectors.
10. Give the "See my projects" button four distinct states: `:hover`, `:focus-visible`, `:active`, and `:disabled`.
11. Ensure the "Contact me (coming soon)" button has the HTML `disabled` attribute and does not appear clickable.
12. Define all four primary-button state rules in `style.css`.

### 3.4 Vanilla JavaScript and Dynamic Interactivity

The prototype must be functionally interactive rather than a static mockup.

1. Use vanilla JavaScript and DOM event listeners to capture button clicks, form submissions, text input, and dropdown changes.
2. Implement at least two types of dynamic DOM updates:
   - **Content updates:** Change project descriptions, status labels, update text, or counters.
   - **Style or geometry updates:** Change progress-bar widths, status colors, or other visual indicators.
   - **Attribute or state updates:** Modify `data-*` attributes, disable buttons when appropriate, or update component states.
   - **Structural or lifecycle updates:** Add or remove project cards and update-history entries dynamically.

3. Validate required fields before allowing a project or update to be submitted.
4. Prevent invalid actions, such as polishing an empty update or saving a project without a required name.
5. Provide clear feedback when an action succeeds or when the user must correct an input.
6. Keep project information and update history synchronized within the prototype.
7. Ensure interactive elements respect their boundaries, including required fields, disabled buttons, and valid workflow states.

At least two of the dynamic update types must be demonstrated in the working prototype.

### 3.5 Data Model

The intended logical data model contains two entities.

**Projects**

| Field | Purpose |
|---|---|
| `id` | Unique project identifier |
| `name` | Project name |
| `description` | Project description |
| `github_link` | Link to the project's repository |
| `status` | Current project status |
| `future_plans` | Planned next steps |

**Updates**

| Field | Purpose |
|---|---|
| `id` | Unique update identifier |
| `project_id` | Associated project |
| `date` | Date of the update |
| `rough_update` | Original user-written update |
| `polished_update` | AI-generated polished version |

Each update must be associated with its corresponding project using `project_id`.

The backend must implement this data model in SQLite. Projects and Updates must be maintained as separate tables, with each update referencing its associated project through project_id and a foreign-key constraint.

The application must create and initialize instance/portfolio.db when it starts, load existing records from it, and save all project and update changes there. Existing data/projects.json and data/updates.json files may be imported once when initializing an empty database; after that, SQLite is the sole source of persistent records.

The frontend must retrieve and modify project information through Flask API endpoints rather than maintaining its own independent source of project records.

### 3.6 AI Capability and Responsible Use

1. Use a single-turn call to an LLM API to transform a rough project update into a concise, polished update suitable for display.
2. Allow the owner to review the generated text before saving it.
3. Support generating a summary of what was accomplished today when requested, using the available project update information.
4. Do not implement autonomous agents, background workers, or continuous AI processing.
5. Do not claim that the AI has performed work, accessed repositories, or verified accomplishments that were not provided to it.
6. Do not expose API keys or other secrets in frontend JavaScript. If an actual API key is required, a secure integration must be addressed separately; the frontend prototype should use a clearly labeled mock response if no secure API integration is available.
7. The developer must understand and be able to explain every line of code, including DOM queries, event listeners, callbacks, validation, and state changes.

## 3.7 Backend Architecture and Python Requirements

The application must use Python and Flask to provide a modular backend that manages project records, update history, input validation, and communication with the frontend.

1. Application Entry Point

Create an app.py file as the main application entry point.

Use Flask to initialize and configure the application.

Run the application locally at http://localhost:5000.

Organize backend functionality into clearly defined routes and helper functions.

Keep backend logic separate from HTML, CSS, and JavaScript.

The Flask application must serve the frontend and handle API requests.

2. Python Data Structures

Represent projects and updates using native Python data structures.

Represent project and update records as dictionaries when processing them in Python.

Each project and update must have a unique identifier.

Associate updates with projects through project_id.

Use appropriate Python data types:

Integers for identifiers.

Strings for names, descriptions, links, and update content.

Booleans for true/false flags.

Appropriate date/time representations for timestamps.

Use .get() with sensible defaults or guarded dictionary lookups when accessing potentially missing values.

Strip unnecessary whitespace from user-provided strings before storing them.

Avoid treating every input as an unvalidated string.

3. Data Management and Persistence

Maintain project and update records in Python data structures while the application is running.

Implement helper functions to create, retrieve, modify, and delete records.

Generate unique identifiers when creating projects and updates.

Ensure updates remain associated with the correct project.

Persist records between application restarts using instance/portfolio.db.

Load saved records when the Flask application starts.

Save changes to the database whenever records are created, modified, or deleted.

Use SQLite's projects and updates tables, with project_id as a foreign key from updates to projects. Store project technologies and screenshot paths in related tables.

4. Flask Routes and HTTP Methods

Implement REST-style API endpoints to manage projects and updates.

Projects:

GET /api/projects - Return all projects.

GET /api/projects/<project_id> - Return a specific project.

POST /api/projects - Validate and create a new project.

PUT /api/projects/<project_id> - Update an existing project.

DELETE /api/projects/<project_id> - Delete a project if removal is supported.

Updates:

GET /api/projects/<project_id>/updates - Return updates associated with a project.

POST /api/projects/<project_id>/updates - Create an update associated with a project.

AI:

POST /api/projects/<project_id>/updates/polish - Accept a rough update and return a polished version using the existing single-turn LLM capability.

All endpoints must return structured JSON responses.

5. Defensive Input Validation

Validate incoming request bodies before processing them.

Check that required fields exist and contain valid values.

Reject missing, empty, malformed, or incorrectly typed data.

Strip leading and trailing whitespace from strings.

Validate project identifiers before accessing records.

Confirm that referenced projects exist before creating or retrieving their updates.

Return an informative error message when validation fails.

Do not allow malformed requests to modify stored records.

6. HTTP Status Codes

Every API route must explicitly return an appropriate HTTP status code.

200 OK: Successful retrieval or modification of an existing resource.

201 Created: Successful creation of a new resource, including its generated ID and created record.

204 No Content: Successful deletion without a response body.

400 Bad Request: Missing, invalid, or malformed client input.

404 Not Found: Requested project or update does not exist.

500 Internal Server Error: Unexpected server-side error.

Error responses must contain a descriptive JSON message. Unexpected errors must be handled gracefully without exposing stack traces, internal paths, or sensitive information to the client.

7. Frontend and Backend Communication

Use JavaScript fetch() to communicate with Flask API endpoints.

Send and receive JSON data using appropriate HTTP methods.

Replace frontend-only project storage with backend-managed records.

Dynamically update the interface using the data returned by the backend.

Display informative messages when API requests succeed or fail.

Handle loading states and unsuccessful requests without breaking the interface.

Ensure the existing project creation, update polishing, review, and history workflow remains functional.

8. Code Quality and Organization

Keep route handlers focused on HTTP requests and responses.

Move reusable data operations and validation into helper functions.

Avoid unnecessary duplication of validation and storage logic.

Use descriptive variable and function names.

Include comments where they clarify non-obvious logic.

The developer must understand and be able to explain all implemented backend functionality.

## 4. Deliverables

### 4.1 Source Code

Submit the following through the repository or course submission portal:

- `index.html`
- `style.css`
- `app.js`
- `assets/avatar.jpg`, if the welcome-page requirements are included
- Any other required local assets

The project must open and function locally in modern browsers. The main workflow must be testable without requiring a reviewer to configure a backend or provide private credentials.

### 4.2 README / Sprint 1 Report

Submit a `SPRINT1.md` file containing the following sections.

**1. Project Recap**

Write two to three sentences summarizing the project, its target user, and its single core workflow.

**2. Workflow Demo Guide**

Provide a short, numbered list explaining how a reviewer can:
1. Open the website locally.
2. Create a project and enter its information.
3. Write a rough project update.
4. Click "Polish Update."
5. Review and save or display the polished update.
6. Confirm that the project and its update history appear correctly.

**3. AI Usage Log and Reflection**

Write one paragraph documenting:
- The AI tools and prompts used during development.
- Which generated code or suggestions were accepted.
- Any incorrect, unsuitable, or hallucinated AI output encountered.
- How the code was reviewed, tested, corrected, and understood.

## 5. Acceptance Checklist

### 5.1 Core Functionality

- [ ] The website supports the single-user project tracker workflow.
- [ ] A project can be created with the required information.
- [ ] A rough update can be entered and submitted for polishing.
- [ ] The polished update can be reviewed before being displayed.
- [ ] Projects and update history appear dynamically.
- [ ] Required fields are validated.
- [ ] At least two types of dynamic DOM updates work.
- [ ] The main current project, recent updates, and future plans are visible.

### 5.2 HTML and CSS

- [ ] `index.html`, `style.css`, and `app.js` are organized as separate files.
- [ ] `style.css` begins with the required universal reset.
- [ ] No inline `style` attributes or external CSS frameworks are used.
- [ ] No ID selectors are used for styling.
- [ ] The page contains exactly one `<h1>`, one `<header>`, one `<nav>`, one `<main>`, and one `<footer>`.
- [ ] Every project is an `<article class="card">` inside a flex container with `gap`.
- [ ] The layout collapses to one column below 768px.
- [ ] No horizontal scrollbar appears at a viewport width of 375px.
- [ ] The avatar uses `./assets/avatar.jpg` if included.
- [ ] The primary navigation links to the projects section and GitHub profile.
- [ ] The primary button has visually distinct hover, focus-visible, active, and disabled

## 5.3 Backend and API Functionality

Flask application starts successfully at localhost:5000.

app.py serves the frontend through Flask.

Projects and updates are stored in SQLite and converted to Python dictionaries for API responses.

Every project and update has a unique identifier.

Updates reference their associated projects through project_id.

Project and update records persist through instance/portfolio.db.

Existing records load when the application starts.

Project creation works through a POST request.

Project retrieval works through GET requests.

Existing project modification works through PUT requests.

Deletion works through DELETE requests if implemented.

Project updates can be created and retrieved through API endpoints.

Required fields and data types are validated on the backend.

Invalid requests return 400 Bad Request.

Missing resources return 404 Not Found.

Successful creation returns 201 Created and the newly generated ID.

Successful retrieval and modification return 200 OK.

Successful deletion returns 204 No Content when supported.

Unexpected server errors return 500 Internal Server Error.

API responses use structured JSON.

Error responses do not expose internal stack traces.

JavaScript communicates with Flask through fetch().

Existing frontend functionality remains operational.