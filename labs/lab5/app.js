const filterInput = document.querySelector('#filter-input');
const projectCount = document.querySelector('#project-count');
const cards = Array.from(document.querySelectorAll('.card'));

function updateProjectList() {
  const query = filterInput.value.trim().toLowerCase();
  let visibleCount = 0;

  cards.forEach((card) => {
    const text = card.textContent.toLowerCase();
    const matches = text.includes(query);

    card.classList.toggle('hidden', !matches);

    if (matches) {
      visibleCount += 1;
    }
  });

  projectCount.textContent = `Showing ${visibleCount} of ${cards.length} projects`;
}

if (filterInput) {
  filterInput.addEventListener('input', updateProjectList);
  updateProjectList();
}
