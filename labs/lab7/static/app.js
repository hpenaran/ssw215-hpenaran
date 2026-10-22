const filterInput = document.querySelector('#filter-input');
const projectCount = document.querySelector('#project-count');
const projectList = document.querySelector('.project-list');
const newTitleInput = document.querySelector('#new-title');
const addProjectButton = document.querySelector('#add-project-btn');
const createProjectForm = document.querySelector('#project-create-form');
const createProjectStatus = document.querySelector('#create-project-status');

function updateProjectList() {
  const query = filterInput.value.trim().toLowerCase();
  const cards = Array.from(document.querySelectorAll('.card'));
  let visibleCount = 0;
  const visibleTitles = [];

  cards.forEach((card) => {
    const text = card.textContent.toLowerCase();
    const matches = text.includes(query);

    card.classList.toggle('hidden', !matches);

    if (matches) {
      visibleCount += 1;
      const title = card.querySelector('.card-title');
      if (title) {
        visibleTitles.push(title.textContent.trim());
      }
    }
  });

  projectCount.textContent = `Showing ${visibleCount} of ${cards.length} projects`;
  console.log(visibleTitles);
}

function createProjectCard(project) {
  const card = document.createElement('article');
  card.className = 'card';
  card.dataset.projectId = project.id;

  const title = document.createElement('h3');
  title.className = 'card-title';
  title.textContent = project.title;

  const description = document.createElement('p');
  description.textContent = project.description;

  const likes = document.createElement('p');
  likes.append('Likes: ');

  const likeCount = document.createElement('span');
  likeCount.className = 'like-count';
  likeCount.textContent = project.likes;
  likes.append(likeCount);

  const upvoteButton = document.createElement('button');
  upvoteButton.className = 'upvote-btn';
  upvoteButton.type = 'button';
  upvoteButton.textContent = 'Upvote';

  card.append(title, description);
  if (project.likes > 10) {
    const badge = document.createElement('span');
    badge.className = 'badge';
    badge.textContent = 'Trending';
    card.append(badge);
  }
  card.append(likes, upvoteButton);
  return card;
}

if (filterInput && projectCount && projectList) {
  filterInput.addEventListener('input', updateProjectList);
  updateProjectList();
}

document.addEventListener('click', async (event) => {
  const button = event.target.closest('.upvote-btn');
  if (!button) {
    return;
  }

  const card = button.closest('.card');
  const likeCount = card?.querySelector('.like-count');
  const projectId = card?.dataset.projectId;

  if (!likeCount || !projectId) {
    console.error('Unable to upvote: project card is missing its ID or like count.');
    return;
  }

  button.disabled = true;
  try {
    const response = await fetch(`/api/projects/${projectId}/upvote`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Upvote request failed with status ${response.status}.`);
    }

    const result = await response.json();
    likeCount.textContent = result.likes;
  } catch (error) {
    console.error('Unable to upvote project:', error);
  } finally {
    button.disabled = false;
  }
});

if (createProjectForm && addProjectButton && newTitleInput && projectList) {
  createProjectForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    addProjectButton.disabled = true;
    createProjectStatus.textContent = '';

    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitleInput.value }),
      });
      if (response.status !== 201 || !response.ok) {
        createProjectStatus.textContent = `Could not add project (HTTP ${response.status}).`;
        return;
      }

      const project = await response.json();
      projectList.append(createProjectCard(project));
      newTitleInput.value = '';
      createProjectStatus.textContent = 'Project added.';
      updateProjectList();
    } catch (error) {
      console.error('Unable to create project:', error);
      createProjectStatus.textContent = 'Could not add project. Please try again.';
    } finally {
      addProjectButton.disabled = false;
    }
  });
}
