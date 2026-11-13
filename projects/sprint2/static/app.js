const projectForm = document.querySelector('[data-project-form]');
const projectFormTitle = document.querySelector('[data-project-form-title]');
const projectSubmit = document.querySelector('[data-project-submit]');
const editProjectId = document.querySelector('[data-edit-project-id]');
const cancelEditButton = document.querySelector('[data-cancel-edit]');
const projectStatus = document.querySelector('[data-project-status]');
const existingMedia = document.querySelector('[data-existing-media]');
const existingMediaList = document.querySelector('[data-existing-media-list]');
const updateForm = document.querySelector('[data-update-form]');
const projectSelect = document.querySelector('[data-project-select]');
const projectList = document.querySelector('[data-project-list]');
const featuredSpotlight = document.querySelector('[data-featured-spotlight]');
const polishedOutput = document.querySelector('[data-polished-output]');
const savePolishedButton = document.querySelector('[data-save-polished]');
const displayPolishedButton = document.querySelector('[data-display-polished]');
const updateStatus = document.querySelector('[data-update-status]');
const activityCalendar = document.querySelector('[data-activity-calendar]');
const activityDetail = document.querySelector('[data-activity-detail]');

let currentPolishedUpdate = '';
let projectsCache = [];
let updatesCache = new Map();

function statusClass(status) {
  const normalized = status.toLowerCase();
  if (normalized.includes('plan')) {
    return 'status-planning';
  }
  if (normalized.includes('hold')) {
    return 'status-on-hold';
  }
  if (normalized.includes('complete')) {
    return 'status-complete';
  }
  return 'status-active';
}

function formatDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value || 'Date unavailable';
  }
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    timeZone: 'UTC',
  });
}

function appendImage(parent, relativePath, className, altText) {
  if (!relativePath) {
    return;
  }
  const image = document.createElement('img');
  image.className = className;
  image.src = `/static/${relativePath}`;
  image.alt = altText;
  image.loading = 'lazy';
  image.addEventListener('error', () => {
    const wrapper = image.parentElement;
    image.remove();
    if (wrapper?.classList.contains('project-image-wrap') && !wrapper.childElementCount) {
      wrapper.remove();
    }
  }, { once: true });
  parent.appendChild(image);
}

function renderTechnologies(project) {
  const list = document.createElement('ul');
  list.className = 'technology-tags';
  (Array.isArray(project.technologies) ? project.technologies : []).forEach((technology) => {
    const tag = document.createElement('li');
    tag.className = 'technology-tag';
    tag.textContent = technology;
    list.appendChild(tag);
  });
  return list;
}

function renderUpdateHistory(projectId) {
  const details = document.createElement('details');
  details.className = 'project-details';
  const summary = document.createElement('summary');
  summary.textContent = 'Project details and updates';
  details.appendChild(summary);

  const screenshots = projectsCache.find((project) => project.id === projectId)?.screenshots || [];
  if (screenshots.length) {
    const screenshotHeading = document.createElement('h4');
    screenshotHeading.textContent = 'Screenshots';
    details.appendChild(screenshotHeading);
    const gallery = document.createElement('div');
    gallery.className = 'screenshot-gallery';
    screenshots.forEach((path, index) => {
      appendImage(gallery, path, 'screenshot-image', `Project screenshot ${index + 1}`);
    });
    details.appendChild(gallery);
  }

  const updateHeading = document.createElement('h4');
  updateHeading.textContent = 'Recent updates';
  details.appendChild(updateHeading);
  const list = document.createElement('ul');
  list.className = 'history-list';
  const updates = updatesCache.get(projectId) || [];
  if (!updates.length) {
    const item = document.createElement('li');
    item.textContent = 'No updates yet for this project.';
    list.appendChild(item);
  } else {
    updates.forEach((entry) => {
      const item = document.createElement('li');
      item.className = 'update-entry';
      item.dataset.updateId = String(entry.id);
      const date = document.createElement('time');
      date.dateTime = entry.created_at || '';
      date.textContent = formatDate(entry.created_at);
      const text = document.createElement('span');
      text.textContent = ` ${entry.polished_update || entry.rough_update}`;
      const content = document.createElement('div');
      content.className = 'update-entry-content';
      content.append(date, text);

      const actions = document.createElement('div');
      actions.className = 'update-actions';
      const editButton = document.createElement('button');
      editButton.className = 'button secondary-button compact-button';
      editButton.type = 'button';
      editButton.dataset.updateAction = 'edit';
      editButton.textContent = 'Edit';
      const deleteButton = document.createElement('button');
      deleteButton.className = 'button secondary-button compact-button';
      deleteButton.type = 'button';
      deleteButton.dataset.updateAction = 'delete';
      deleteButton.textContent = 'Remove';
      actions.append(editButton, deleteButton);
      item.append(content, actions);
      list.appendChild(item);
    });
  }
  details.appendChild(list);
  return details;
}

function createUpdateEditForm(update) {
  const form = document.createElement('form');
  form.className = 'update-edit-form';
  form.dataset.updateId = String(update.id);

  const roughLabel = document.createElement('label');
  roughLabel.className = 'update-edit-field';
  roughLabel.textContent = 'Rough update';
  const roughInput = document.createElement('textarea');
  roughInput.name = 'rough_update';
  roughInput.required = true;
  roughInput.value = update.rough_update || '';
  roughLabel.appendChild(roughInput);

  const polishedLabel = document.createElement('label');
  polishedLabel.className = 'update-edit-field';
  polishedLabel.textContent = 'Polished update';
  const polishedInput = document.createElement('textarea');
  polishedInput.name = 'polished_update';
  polishedInput.required = true;
  polishedInput.value = update.polished_update || '';
  polishedLabel.appendChild(polishedInput);

  const actions = document.createElement('div');
  actions.className = 'update-actions';
  const saveButton = document.createElement('button');
  saveButton.className = 'button primary-button compact-button';
  saveButton.type = 'submit';
  saveButton.textContent = 'Save Update';
  const cancelButton = document.createElement('button');
  cancelButton.className = 'button secondary-button compact-button';
  cancelButton.type = 'button';
  cancelButton.dataset.updateAction = 'cancel';
  cancelButton.textContent = 'Cancel';
  actions.append(saveButton, cancelButton);
  form.append(roughLabel, polishedLabel, actions);
  return form;
}

function createProjectCard(project, isSpotlight = false) {
  const article = document.createElement('article');
  article.className = isSpotlight ? 'card featured' : 'card';
  article.dataset.projectId = String(project.id);

  const image = document.createElement('div');
  image.className = 'project-image-wrap';
  appendImage(image, project.main_image, 'project-image', `${project.name} main image`);
  if (image.childElementCount) {
    article.appendChild(image);
  }

  const header = document.createElement('div');
  header.className = 'card-header';
  const title = document.createElement('h3');
  title.className = 'card-title';
  title.textContent = project.name;
  const badges = document.createElement('div');
  badges.className = 'card-badges';
  const category = document.createElement('span');
  category.className = 'category-tag';
  category.textContent = project.category || 'Personal Project';
  const statusTag = document.createElement('span');
  statusTag.className = `status-tag ${statusClass(project.status || '')}`;
  statusTag.textContent = project.status || 'Planning';
  badges.append(category, statusTag);
  header.append(title, badges);

  const description = document.createElement('p');
  description.className = 'card-description';
  description.textContent = project.description || '';

  const technologyTags = renderTechnologies(project);
  const futurePlans = document.createElement('p');
  futurePlans.className = 'card-description future-plans';
  futurePlans.textContent = `Future plans: ${project.future_plans || 'Not specified.'}`;

  const meta = document.createElement('div');
  meta.className = 'card-meta';
  if (project.github_link) {
    const gitLink = document.createElement('a');
    gitLink.className = 'mini-link';
    gitLink.href = project.github_link;
    gitLink.target = '_blank';
    gitLink.rel = 'noopener noreferrer';
    gitLink.textContent = 'GitHub';
    meta.appendChild(gitLink);
  }

  const actions = document.createElement('div');
  actions.className = 'project-actions';
  const editButton = document.createElement('button');
  editButton.className = 'button secondary-button compact-button';
  editButton.type = 'button';
  editButton.dataset.action = 'edit';
  editButton.textContent = 'Edit';
  const deleteButton = document.createElement('button');
  deleteButton.className = 'button secondary-button compact-button';
  deleteButton.type = 'button';
  deleteButton.dataset.action = 'delete';
  deleteButton.textContent = 'Delete';
  actions.append(editButton, deleteButton);

  article.append(header, description);
  if (technologyTags.childElementCount) {
    article.appendChild(technologyTags);
  }
  article.append(futurePlans, meta, renderUpdateHistory(project.id), actions);
  return article;
}

function renderProjectSelect(projects) {
  if (!projectSelect) {
    return;
  }
  const previousValue = projectSelect.value;
  projectSelect.replaceChildren();
  if (!projects.length) {
    const option = document.createElement('option');
    option.value = '';
    option.textContent = 'No projects yet';
    projectSelect.appendChild(option);
    return;
  }
  projects.forEach((project) => {
    const option = document.createElement('option');
    option.value = String(project.id);
    option.textContent = project.name;
    projectSelect.appendChild(option);
  });
  projectSelect.value = projects.some((project) => String(project.id) === previousValue)
    ? previousValue
    : String(projects[0].id);
}

function renderExistingMedia(project) {
  existingMediaList.replaceChildren();
  appendImage(existingMediaList, project.main_image, 'existing-main-image', 'Current main image');
  (project.screenshots || []).forEach((path, index) => {
    const row = document.createElement('label');
    row.className = 'existing-screenshot';
    appendImage(row, path, 'existing-screenshot-image', `Current screenshot ${index + 1}`);
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.name = 'remove_screenshots';
    checkbox.value = path;
    row.append(checkbox, document.createTextNode(' Remove'));
    existingMediaList.appendChild(row);
  });
  existingMedia.hidden = false;
}

function resetProjectForm() {
  projectForm.reset();
  editProjectId.value = '';
  projectFormTitle.textContent = 'Create a Project';
  projectSubmit.textContent = 'Save Project';
  cancelEditButton.hidden = true;
  existingMedia.hidden = true;
  existingMediaList.replaceChildren();
}

function startProjectEdit(project) {
  resetProjectForm();
  editProjectId.value = String(project.id);
  projectForm.elements.name.value = project.name;
  projectForm.elements.description.value = project.description;
  projectForm.elements.github_link.value = project.github_link;
  projectForm.elements.status.value = project.status || 'Planning';
  projectForm.elements.category.value = project.category || 'Personal Project';
  projectForm.elements.technologies.value = (project.technologies || []).join(', ');
  projectForm.elements.future_plans.value = project.future_plans || '';
  projectForm.elements.featured.checked = Boolean(project.featured);
  projectFormTitle.textContent = `Edit ${project.name}`;
  projectSubmit.textContent = 'Save Changes';
  cancelEditButton.hidden = false;
  renderExistingMedia(project);
  projectForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

async function loadProjects() {
  const response = await fetch('/api/projects');
  if (!response.ok) {
    throw new Error(`Unable to load projects (HTTP ${response.status}).`);
  }
  projectsCache = await response.json();
  const updateResults = await Promise.all(projectsCache.map(async (project) => {
    const updateResponse = await fetch(`/api/projects/${project.id}/updates`);
    if (!updateResponse.ok) {
      throw new Error(`Unable to load updates for ${project.name} (HTTP ${updateResponse.status}).`);
    }
    return [project.id, await updateResponse.json()];
  }));
  updatesCache = new Map(updateResults);
  renderProjectSelect(projectsCache);

  projectList.replaceChildren();
  featuredSpotlight.replaceChildren();
  const featuredProject = projectsCache.find((project) => project.featured);
  if (featuredProject) {
    featuredSpotlight.appendChild(createProjectCard(featuredProject, true));
    featuredSpotlight.hidden = false;
  } else {
    featuredSpotlight.hidden = true;
  }

  const regularProjects = projectsCache.filter((project) => !project.featured);
  if (!regularProjects.length && !featuredProject) {
    const emptyState = document.createElement('p');
    emptyState.className = 'empty-state';
    emptyState.textContent = 'No projects have been created yet.';
    projectList.appendChild(emptyState);
  } else {
    regularProjects.forEach((project) => projectList.appendChild(createProjectCard(project)));
  }
}

async function loadActivity() {
  const response = await fetch('/api/activity');
  if (!response.ok) {
    throw new Error(`Unable to load project activity (HTTP ${response.status}).`);
  }
  const activity = await response.json();
  const counts = new Map(activity.map((entry) => [entry.date, entry.count]));
  const today = new Date();
  const todayUtc = new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate()));
  activityCalendar.replaceChildren();
  const weekdays = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
  const firstMonth = new Date(Date.UTC(todayUtc.getUTCFullYear(), todayUtc.getUTCMonth() - 11, 1));

  for (let monthOffset = 0; monthOffset < 12; monthOffset += 1) {
    const monthDate = new Date(Date.UTC(
      firstMonth.getUTCFullYear(),
      firstMonth.getUTCMonth() + monthOffset,
      1
    ));
    const month = document.createElement('section');
    month.className = 'activity-month';
    const title = document.createElement('h4');
    title.className = 'activity-month-title';
    title.textContent = monthDate.toLocaleDateString(undefined, {
      month: 'long',
      year: 'numeric',
      timeZone: 'UTC',
    });
    const grid = document.createElement('div');
    grid.className = 'activity-month-grid';

    weekdays.forEach((weekday) => {
      const label = document.createElement('span');
      label.className = 'activity-weekday';
      label.textContent = weekday;
      grid.appendChild(label);
    });

    const firstWeekday = monthDate.getUTCDay();
    for (let blankDay = 0; blankDay < firstWeekday; blankDay += 1) {
      const spacer = document.createElement('span');
      spacer.className = 'activity-empty-day';
      grid.appendChild(spacer);
    }

    const daysInMonth = new Date(Date.UTC(
      monthDate.getUTCFullYear(),
      monthDate.getUTCMonth() + 1,
      0
    )).getUTCDate();
    for (let dayNumber = 1; dayNumber <= daysInMonth; dayNumber += 1) {
      const date = new Date(Date.UTC(
        monthDate.getUTCFullYear(),
        monthDate.getUTCMonth(),
        dayNumber
      ));
      const dateString = date.toISOString().slice(0, 10);
      if (date > todayUtc) {
        const futureDay = document.createElement('span');
        futureDay.className = 'activity-empty-day';
        grid.appendChild(futureDay);
        continue;
      }

      const count = counts.get(dateString) || 0;
      const cell = document.createElement('button');
      cell.type = 'button';
      cell.className = `activity-day activity-level-${count === 0 ? 0 : count === 1 ? 1 : count <= 3 ? 2 : count <= 6 ? 3 : 4}`;
      cell.textContent = String(dayNumber);
      cell.dataset.date = dateString;
      cell.dataset.count = String(count);
      cell.title = `${dateString}: ${count} ${count === 1 ? 'update' : 'updates'}`;
      cell.setAttribute('aria-label', cell.title);
      grid.appendChild(cell);
    }

    month.append(title, grid);
    activityCalendar.appendChild(month);
  }
}

function resizeImage(file, maxWidth = 1600, maxHeight = 1200) {
  return new Promise((resolve, reject) => {
    const imageUrl = URL.createObjectURL(file);
    const image = new Image();
    image.onload = () => {
      const scale = Math.min(1, maxWidth / image.naturalWidth, maxHeight / image.naturalHeight);
      const canvas = document.createElement('canvas');
      canvas.width = Math.max(1, Math.round(image.naturalWidth * scale));
      canvas.height = Math.max(1, Math.round(image.naturalHeight * scale));
      const context = canvas.getContext('2d');
      if (!context) {
        URL.revokeObjectURL(imageUrl);
        reject(new Error(`Unable to resize ${file.name}.`));
        return;
      }
      context.drawImage(image, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((blob) => {
        URL.revokeObjectURL(imageUrl);
        if (!blob) {
          reject(new Error(`Unable to resize ${file.name}.`));
          return;
        }
        const name = `${file.name.replace(/\.[^.]+$/, '')}.jpg`;
        resolve(new File([blob], name, { type: 'image/jpeg' }));
      }, 'image/jpeg', 0.82);
    };
    image.onerror = () => {
      URL.revokeObjectURL(imageUrl);
      reject(new Error(`${file.name} could not be opened as an image.`));
    };
    image.src = imageUrl;
  });
}

function reportError(error, statusElement, fallback) {
  console.error(error);
  if (statusElement) {
    statusElement.textContent = error.message || fallback;
  }
}

projectForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!projectForm.reportValidity()) {
    return;
  }

  const id = editProjectId.value;
  const body = new FormData(projectForm);
  body.delete('project_id');
  body.set('featured', projectForm.elements.featured.checked ? 'true' : 'false');
  const mainImageInput = projectForm.elements.main_image;
  const screenshotInput = projectForm.elements.screenshots;
  const selectedMainImage = mainImageInput.files[0];
  const selectedScreenshots = Array.from(screenshotInput.files);
  body.delete('main_image');
  body.delete('screenshots');
  const buttonText = projectSubmit.textContent;
  projectSubmit.disabled = true;
  projectStatus.textContent = selectedMainImage || selectedScreenshots.length
    ? 'Resizing images before upload...'
    : '';
  try {
    if (selectedMainImage) {
      body.append('main_image', await resizeImage(selectedMainImage));
    }
    for (const screenshot of selectedScreenshots) {
      body.append('screenshots', await resizeImage(screenshot));
    }
    const response = await fetch(id ? `/api/projects/${id}` : '/api/projects', {
      method: id ? 'PUT' : 'POST',
      body,
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || `Project could not be saved (HTTP ${response.status}).`);
    }
    resetProjectForm();
    projectStatus.textContent = id ? 'Project updated successfully.' : 'Project saved successfully.';
    await loadProjects();
  } catch (error) {
    reportError(error, projectStatus, 'Project could not be saved.');
  } finally {
    projectSubmit.disabled = false;
    if (!editProjectId.value) {
      projectSubmit.textContent = buttonText === 'Save Changes' ? 'Save Project' : buttonText;
    }
  }
});

cancelEditButton.addEventListener('click', resetProjectForm);

async function handleProjectCardAction(event) {
  const updateButton = event.target.closest('[data-update-action]');
  if (updateButton) {
    await handleUpdateAction(updateButton);
    return;
  }

  const button = event.target.closest('[data-action]');
  if (!button) {
    return;
  }
  const card = button.closest('[data-project-id]');
  const project = projectsCache.find((entry) => String(entry.id) === card?.dataset.projectId);
  if (!project) {
    return;
  }
  if (button.dataset.action === 'edit') {
    startProjectEdit(project);
    return;
  }
  if (button.dataset.action === 'delete') {
    if (!window.confirm(`Delete "${project.name}" and its update history?`)) {
      return;
    }
    button.disabled = true;
    try {
      const response = await fetch(`/api/projects/${project.id}`, { method: 'DELETE' });
      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.error || `Project could not be deleted (HTTP ${response.status}).`);
      }
      if (editProjectId.value === String(project.id)) {
        resetProjectForm();
      }
      projectStatus.textContent = 'Project deleted.';
      await Promise.all([loadProjects(), loadActivity()]);
    } catch (error) {
      reportError(error, projectStatus, 'Project could not be deleted.');
      button.disabled = false;
    }
  }
}

projectList.addEventListener('click', handleProjectCardAction);
featuredSpotlight.addEventListener('click', handleProjectCardAction);

async function handleUpdateAction(button) {
  const item = button.closest('[data-update-id]');
  const card = button.closest('[data-project-id]');
  const projectId = Number(card?.dataset.projectId);
  const updateId = Number(item?.dataset.updateId);
  const update = (updatesCache.get(projectId) || []).find((entry) => entry.id === updateId);
  if (!item || !projectId || !update) {
    return;
  }

  if (button.dataset.updateAction === 'cancel') {
    await loadProjects();
    return;
  }
  if (button.dataset.updateAction === 'edit') {
    item.replaceChildren(createUpdateEditForm(update));
    item.querySelector('textarea[name="rough_update"]').focus();
    return;
  }
  if (button.dataset.updateAction !== 'delete') {
    return;
  }
  if (!window.confirm('Remove this project update?')) {
    return;
  }

  button.disabled = true;
  try {
    const response = await fetch(`/api/projects/${projectId}/updates/${updateId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const result = await response.json();
      throw new Error(result.error || `Update could not be removed (HTTP ${response.status}).`);
    }
    updateStatus.textContent = 'Project update removed.';
    await Promise.all([loadProjects(), loadActivity()]);
  } catch (error) {
    reportError(error, updateStatus, 'Project update could not be removed.');
    button.disabled = false;
  }
}

async function saveUpdateEdit(event) {
  const form = event.target.closest('.update-edit-form');
  if (!form) {
    return;
  }
  event.preventDefault();
  if (!form.reportValidity()) {
    return;
  }

  const item = form.closest('[data-update-id]');
  const card = form.closest('[data-project-id]');
  const projectId = Number(card?.dataset.projectId);
  const updateId = Number(form.dataset.updateId);
  const submitButton = form.querySelector('button[type="submit"]');
  submitButton.disabled = true;

  try {
    const response = await fetch(`/api/projects/${projectId}/updates/${updateId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rough_update: form.elements.rough_update.value,
        polished_update: form.elements.polished_update.value,
      }),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || `Update could not be saved (HTTP ${response.status}).`);
    }
    updateStatus.textContent = 'Project update saved.';
    await loadProjects();
  } catch (error) {
    reportError(error, updateStatus, 'Project update could not be saved.');
    submitButton.disabled = false;
  }
}

projectList.addEventListener('submit', saveUpdateEdit);
featuredSpotlight.addEventListener('submit', saveUpdateEdit);

updateForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const projectId = Number(projectSelect.value);
  const roughUpdate = new FormData(updateForm).get('rough_update')?.toString().trim() || '';
  if (!projectId || !roughUpdate) {
    updateStatus.textContent = 'Select a project and enter a rough update.';
    return;
  }
  try {
    const response = await fetch(`/api/projects/${projectId}/updates/polish`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rough_update: roughUpdate }),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || `Unable to polish the update (HTTP ${response.status}).`);
    }
    currentPolishedUpdate = result.polished_update || '';
    polishedOutput.textContent = currentPolishedUpdate;
    updateStatus.textContent = 'Polished update ready to review.';
  } catch (error) {
    reportError(error, updateStatus, 'Unable to polish the update.');
  }
});

savePolishedButton.addEventListener('click', async () => {
  const projectId = Number(projectSelect.value);
  const roughUpdate = new FormData(updateForm).get('rough_update')?.toString().trim() || '';
  if (!projectId || !roughUpdate || !currentPolishedUpdate) {
    updateStatus.textContent = 'Polish an update before saving it.';
    return;
  }
  try {
    const response = await fetch(`/api/projects/${projectId}/updates`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rough_update: roughUpdate, polished_update: currentPolishedUpdate }),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || `Update could not be saved (HTTP ${response.status}).`);
    }
    updateForm.reset();
    currentPolishedUpdate = '';
    polishedOutput.textContent = 'Choose a project and add a rough update to begin.';
    updateStatus.textContent = 'Update saved successfully.';
    await Promise.all([loadProjects(), loadActivity()]);
  } catch (error) {
    reportError(error, updateStatus, 'Update could not be saved.');
  }
});

displayPolishedButton.addEventListener('click', () => {
  if (!currentPolishedUpdate) {
    updateStatus.textContent = 'There is no polished update to display yet.';
    return;
  }
  polishedOutput.textContent = currentPolishedUpdate;
  updateStatus.textContent = 'Polished update displayed.';
});

activityCalendar.addEventListener('click', (event) => {
  const day = event.target.closest('.activity-day');
  if (day) {
    const count = Number(day.dataset.count);
    activityCalendar.querySelector('.activity-day.selected')?.classList.remove('selected');
    day.classList.add('selected');
    activityDetail.textContent = `${day.dataset.date}: ${count} ${count === 1 ? 'update' : 'updates'}.`;
  }
});

loadProjects().catch((error) => {
  reportError(error, projectStatus, 'Unable to load project data right now.');
  projectList.textContent = 'Unable to load project data right now.';
});
loadActivity().catch((error) => {
  reportError(error, activityDetail, 'Unable to load project activity.');
});
