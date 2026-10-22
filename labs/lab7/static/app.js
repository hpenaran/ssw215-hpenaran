const filterInput = document.querySelector('#filter-input');
const projectCount = document.querySelector('#project-count');
const cards = Array.from(document.querySelectorAll('.card'));

function updateProjectList() {
  const query = filterInput.value.trim().toLowerCase();
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

if (filterInput) {
  filterInput.addEventListener('input', updateProjectList);
  updateProjectList();
}

document.querySelectorAll('.upvote-btn').forEach((button) => {
  button.addEventListener('click', async () => {
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
});
