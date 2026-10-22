# SPEC: Developer Portfolio Welcome Page
## 1. Purpose & Scope
- A personal portfolio welcome page for Henry Penaranda, a second-year software
engineering student.
- Non-Goals: no multi-page routing; no backend; no contact forms.
## 2. Invariants & Negative Constraints
- All styling MUST reside in `./style.css` (no inline style="..." attributes).
- The page MUST NOT load external CSS frameworks or CDNs (no Bootstrap, no Tailwind).
- The avatar image MUST use the relative path `./assets/avatar.jpg`.
- The layout MUST collapse into a single vertical column on screens narrower than 768px.
- style.css MUST begin with the universal reset: `*, *::before, *::after { box-sizing:
border-box; }`.
- Spacing and font sizes MUST use rem. px MAY be used only for borders.
- Styling MUST use class selectors. ID selectors MUST NOT be used for styling.
- All JavaScript MUST live in ./app.js. index.html MUST NOT contain inline onclick
attributes or any <script> block with code inside it.
- app.js MUST be loaded from <head> with <script src="./app.js" defer></script>.
- Showing and hiding MUST be done by adding and removing a CSS class. app.js MUST NOT set
styles directly through .style.
- All project data MUST live in a Python list of dictionaries named projects_db in
app.py. templates/index.html MUST NOT contain a hardcoded project card.
- templates/index.html MUST render one card per project with a {% for %} loop.
- style.css and app.js MUST be linked with url_for('static', filename=...), never with a
plain relative path.
- No Jinja syntax ({{ }} or {% %}) may appear in static/app.js. External script files are
never processed by Flask.
- app.py MUST create the application with app = Flask(__name__), and MUST end with a
block that runs it with debug=True when the file is executed directly.
- The upvote route MUST accept POST only, and MUST declare its id parameter as
<int:project_id>.
- The upvote route MUST return jsonify(...), never render_template.
- app.js MUST check response.ok before reading the response body.
- projects.json MUST be the only source of project data. app.py MUST NOT contain a
hardcoded list of projects.
- The path to projects.json MUST be built from the location of app.py, not from a bare
relative path.
- Every route that changes a project MUST write the whole list back to projects.json
before it returns a response.
- projects.json MUST be written with json.dump(..., indent=2) so it stays readable in a
diff.
- The create-project route MUST accept POST only, at the path /api/projects.
- The route MUST append the new project to projects.json before it returns.
- The new project's id MUST be one higher than the largest id already in the file.
- A create request whose title is missing, or is empty once surrounding spaces are
removed, MUST be rejected by the server with status code 400, and the rejection MUST
happen before projects.json is opened.
## 3. UI Content & Interface Contract
- Hero header: my full name "Henry Penaranda", the subtitle "2/4 Software Engineer", and
this bio: "I am dedicated to learning and becoming an expert in my field. I love turning big ideas into reality".
- Action link: a button labelled "See my projects" that links to `#projects`.
- Projects section with id="projects": lists these items: I would like to make a professional website for myself for people to look at if they are curious about who I am.
- Social link: GitHub (https://github.com/hpenaran) MUST open in a new tab
(target="_blank").
-The page background MUST be some type of dark blue while the GitHub link at the bottom MUST be white
- The page MUST use semantic landmarks: one <header>, one <nav>, one <main>, one
<footer>, and each content group inside its own <section> with a heading.
- There MUST be exactly one <h1>, and heading levels MUST NOT skip (h1 then h2 then h3).
- <nav> MUST contain a link to the projects section and a link to my GitHub profile.
- Each project MUST be an <article class="card"> inside a container that uses display:
flex, flex-wrap: wrap and gap.
- The "See my projects" button MUST have four visually distinct states: :hover, :focus-
visible, :active, and :disabled.
- A second button labelled "Contact me (coming soon)" MUST be present with the HTML
disabled attribute, and MUST NOT look clickable.
- All four state rules MUST live in style.css.
- Above the projects there MUST be a text input with id="filter-input", and a <label>
bound to it reading "Filter projects".
- There MUST be an element with id="project-count" that reads "Showing X of Y projects".
- As the user types, cards whose text does not contain what was typed MUST be hidden by
adding the class "hidden", and the count MUST update immediately — no button, no page
reload.
- Emptying the box MUST bring every card back.
- style.css MUST define .hidden { display: none; }.
- Each time the filter runs, app.js MUST print the titles of the projects that are still
visible to the console with console.log.
- Each project in projects_db MUST have the keys: id (an integer), title, description,
and likes (an integer).
- Each rendered card MUST carry the attribute data-project-id holding that project's id.
- Visiting http://127.0.0.1:5000/ MUST serve the page, with one card per entry in
projects_db.
- The rendered cards MUST keep the same classes they had in Lab 5, so that the existing
filter in app.js keeps working with no changes to app.js.
- Each card MUST contain a button with class "upvote-btn" reading "Upvote", and an
element with class "like-count" showing that project's likes.
- Clicking Upvote MUST send a POST to /api/projects/<id>/upvote and update only the
number on that card, with no page reload.
- A project with more than 10 likes MUST show a "Trending" badge on its card.
- app.py MUST read projects.json and pass the resulting list to the template, so the page
shows whatever the file currently contains.
- After a successful upvote, the new like count MUST be present in projects.json on disk.
- Above the project list there MUST be a text input with id="new-title" and a button
reading "Add project".
- The input and the button MUST sit in their own block, outside the element that lays the
project cards out, so the existing card layout is unchanged.
- Clicking Add project MUST POST {"title": ...} to /api/projects, and the new card MUST
appear without a page reload.
- A successful create MUST return the new project as JSON with status code 201.

## 4. Acceptance Checklist
- [ x] The page still loads at http://127.0.0.1:5000/ and shows every project in
projects.json.
- [ x] app.py contains no hardcoded project list.
- [ x] Upvoting a project changes the number inside projects.json.
- [ x] Stopping the server with Ctrl+C, restarting it, and reloading the page keeps the
new count.
- [ x] Editing a title directly in projects.json and reloading the page changes what I
see.
- [ x] The DevTools Console shows no red errors.
- [ ] Typing a title and clicking Add project adds a card without reloading the page.
- [ ] The project cards still lay out the way they did in Lab 6.
- [ ] The new project is in projects.json, and it is still there after a restart.
- [ ] The Network tab shows the create request returning 201.
- [ ] Submitting an empty title leaves projects.json unchanged, and the server answers
400.

## 5. Audit Protocol
- Inspect the generated code line by line with `git diff --staged` before committing.