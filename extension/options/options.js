let editingConceptName = null;
let generatedImageUrl = null;

let activeConceptType = "person";

// Generation history for the concept currently
// being created or edited.
let workingImageHistory = [];

// Concept currently open in the detail view.
let currentViewedConcept = null;


// =========================================================
// View helpers
// =========================================================

function showLibraryView() {
  document.getElementById("add-concept").hidden = false;
  document.getElementById("concept-list").hidden = false;
  document.getElementById("concept-detail").hidden = true;
}


function showDetailView() {
  document.getElementById("add-concept").hidden = true;
  document.getElementById("concept-list").hidden = true;
  document.getElementById("concept-detail").hidden = false;
}


// =========================================================
// Concept library
// =========================================================

async function loadConcepts() {
  const concepts = await ConceptStorage.getConcepts();

  const conceptGrid =
    document.getElementById("concept-grid");

  conceptGrid.innerHTML = "";

  // Highlight selected tab.
  const tabs =
    document.querySelectorAll(".concept-type-tab");

  tabs.forEach((tab) => {
    tab.classList.toggle(
      "active",
      tab.dataset.type === activeConceptType
    );
  });

  // Only show concepts belonging to selected category.
  const filteredConcepts = concepts.filter(
    (concept) =>
      concept.type === activeConceptType
  );

  if (filteredConcepts.length === 0) {
    const emptyMessage =
      document.createElement("p");

    emptyMessage.className =
      "empty-concept-message";

    emptyMessage.textContent =
      `No ${activeConceptType} concepts yet.`;

    conceptGrid.appendChild(emptyMessage);

    return;
  }

  filteredConcepts.forEach((concept) => {
    const conceptElement =
      document.createElement("div");

    conceptElement.className =
      "concept-item";

    conceptElement.tabIndex = 0;

    const nameElement =
      document.createElement("h3");

    nameElement.textContent =
      concept.name;

    const typeElement =
      document.createElement("p");

    typeElement.textContent =
      concept.type;

    conceptElement.appendChild(nameElement);
    conceptElement.appendChild(typeElement);

    // Current selected image becomes card thumbnail.
    if (concept.image) {
      const imageElement =
        document.createElement("img");

      imageElement.src =
        concept.image;

      imageElement.alt =
        `${concept.name} preview`;

      imageElement.className =
        "concept-card-image";

      conceptElement.appendChild(imageElement);
    }

    // Delete is now a small X in the top-right corner.
    const deleteButton =
      document.createElement("button");

    deleteButton.type = "button";

    deleteButton.className =
      "concept-delete-button";

    deleteButton.textContent =
      "×";

    deleteButton.setAttribute(
      "aria-label",
      `Delete ${concept.name}`
    );

    deleteButton.title =
      `Delete ${concept.name}`;

    deleteButton.addEventListener(
      "click",
      (event) => {
        event.stopPropagation();

        deleteConceptByName(
          concept.name
        );
      }
    );

    conceptElement.appendChild(
      deleteButton
    );

    const buttonContainer =
      document.createElement("div");

    buttonContainer.className =
      "concept-card-actions";

    const editButton =
      document.createElement("button");

    editButton.textContent =
      "Edit";

    editButton.addEventListener(
      "click",
      (event) => {
        event.stopPropagation();

        editConcept(concept);
      }
    );

    buttonContainer.appendChild(
      editButton
    );

    conceptElement.appendChild(
      buttonContainer
    );

    conceptElement.addEventListener(
      "click",
      () => {
        openConceptDetails(concept);
      }
    );

    conceptElement.addEventListener(
      "keydown",
      (event) => {
        if (
          event.key === "Enter" ||
          event.key === " "
        ) {
          event.preventDefault();

          openConceptDetails(concept);
        }
      }
    );

    conceptGrid.appendChild(
      conceptElement
    );
  });
}


// =========================================================
// Image selection
// =========================================================

async function setConceptImage(
  conceptName,
  imageUrl
) {
  const concepts =
    await ConceptStorage.getConcepts();

  const conceptIndex =
    concepts.findIndex(
      (concept) =>
        concept.name === conceptName
    );

  if (conceptIndex === -1) {
    return;
  }

  const concept =
    concepts[conceptIndex];

  const history = [
    ...(concept.imageHistory || [])
  ];

  // Preserve the previously selected image in history
  // if it was created before history tracking existed.
  if (
    concept.image &&
    !history.some(
      (item) =>
        item.url === concept.image
    )
  ) {
    history.push({
      url: concept.image,
      generatedAt: null
    });
  }

  // Make sure the selected image is also represented
  // in the history list.
  if (
    !history.some(
      (item) =>
        item.url === imageUrl
    )
  ) {
    history.push({
      url: imageUrl,
      generatedAt: null
    });
  }

  concept.image =
    imageUrl;

  concept.imageHistory =
    history;

  concepts[conceptIndex] =
    concept;

  await ConceptStorage.saveConcepts(
    concepts
  );

  currentViewedConcept =
    concept;

  // Update the library thumbnail and detail view.
  await loadConcepts();

  openConceptDetails(
    concept
  );
}


// =========================================================
// Concept detail view
// =========================================================

function openConceptDetails(concept) {
  currentViewedConcept =
    concept;

  document.getElementById(
    "detail-name"
  ).textContent =
    concept.name;

  document.getElementById(
    "detail-type"
  ).textContent =
    `Type: ${concept.type}`;

  document.getElementById(
    "detail-aliases"
  ).textContent =
    concept.aliases &&
    concept.aliases.length > 0
      ? concept.aliases.join(", ")
      : "None";

  document.getElementById(
    "detail-description"
  ).textContent =
    concept.description ||
    "No description.";

  // -----------------------------------------
  // Current image
  // -----------------------------------------

  const currentImage =
    document.getElementById(
      "detail-current-image"
    );

  const noCurrentImage =
    document.getElementById(
      "detail-no-current-image"
    );

  if (concept.image) {
    currentImage.src =
      concept.image;

    currentImage.hidden =
      false;

    noCurrentImage.hidden =
      true;
  } else {
    currentImage.src = "";

    currentImage.hidden =
      true;

    noCurrentImage.hidden =
      false;
  }

  // -----------------------------------------
  // Image history
  // -----------------------------------------

  const historyGrid =
    document.getElementById(
      "image-history-grid"
    );

  const noHistory =
    document.getElementById(
      "no-image-history"
    );

  historyGrid.innerHTML =
    "";

  const history = [
    ...(concept.imageHistory || [])
  ];

  // Older concepts may have a current image that predates
  // image-history tracking. Include it in the displayed list.
  if (
    concept.image &&
    !history.some(
      (item) =>
        item.url === concept.image
    )
  ) {
    history.push({
      url: concept.image,
      generatedAt: null
    });
  }

  if (history.length === 0) {
    noHistory.hidden =
      false;
  } else {
    noHistory.hidden =
      true;

    // Newest first for display.
    const newestFirst =
      [...history].reverse();

    newestFirst.forEach(
      (historyItem) => {
        const historyElement =
          document.createElement("div");

        historyElement.className =
          "history-item";

        const imageWrapper =
          document.createElement("div");

        imageWrapper.className =
          "history-image-wrapper";

        const imageElement =
          document.createElement("img");

        imageElement.src =
          historyItem.url;

        imageElement.alt =
          `${concept.name} historical generation`;

        const isCurrent =
          historyItem.url ===
          concept.image;

        if (isCurrent) {
          historyElement.classList.add(
            "current-history-item"
          );
        }

        const selectButton =
          document.createElement("button");

        selectButton.type =
          "button";

        selectButton.className =
          "history-select-button";

        if (isCurrent) {
          selectButton.textContent =
            "✓ Current";

          selectButton.disabled =
            true;

          selectButton.classList.add(
            "current"
          );
        } else {
          selectButton.textContent =
            "Use this image";

          selectButton.addEventListener(
            "click",
            async (event) => {
              event.stopPropagation();

              await setConceptImage(
                concept.name,
                historyItem.url
              );
            }
          );
        }

        imageWrapper.appendChild(
          imageElement
        );

        imageWrapper.appendChild(
          selectButton
        );

        historyElement.appendChild(
          imageWrapper
        );

        if (
          historyItem.generatedAt
        ) {
          const dateElement =
            document.createElement("p");

          const date =
            new Date(
              historyItem.generatedAt
            );

          dateElement.textContent =
            date.toLocaleString();

          historyElement.appendChild(
            dateElement
          );
        }

        historyGrid.appendChild(
          historyElement
        );
      }
    );
  }

  showDetailView();
}


// =========================================================
// Delete
// =========================================================

async function deleteConceptByName(name) {
  const concepts =
    await ConceptStorage.getConcepts();

  const updatedConcepts =
    concepts.filter(
      (concept) =>
        concept.name !== name
    );

  await ConceptStorage.saveConcepts(
    updatedConcepts
  );

  currentViewedConcept =
    null;

  showLibraryView();

  await loadConcepts();
}


// =========================================================
// Edit
// =========================================================

function editConcept(concept) {
  editingConceptName =
    concept.name;

  generatedImageUrl =
    null;

  workingImageHistory = [
    ...(concept.imageHistory || [])
  ];

  // Preserve a current image that was created before
  // image-history tracking existed.
  if (
    concept.image &&
    !workingImageHistory.some(
      (item) =>
        item.url === concept.image
    )
  ) {
    workingImageHistory.push({
      url: concept.image,
      generatedAt: null
    });
  }

  const nameInput =
    document.getElementById(
      "concept-name"
    );

  const typeInput =
    document.getElementById(
      "concept-type"
    );

  const aliasesInput =
    document.getElementById(
      "concept-aliases"
    );

  const descriptionInput =
    document.getElementById(
      "concept-description"
    );

  const saveButton =
    document.getElementById(
      "save-concept-button"
    );

  const currentImagePanel =
    document.getElementById(
      "current-image-panel"
    );

  const currentImageElement =
    document.getElementById(
      "current-concept-image"
    );

  const previewElement =
    document.getElementById(
      "concept-image-preview"
    );

  const keepCurrentImageButton =
    document.getElementById(
      "keep-current-image-button"
    );

  nameInput.value =
    concept.name;

  typeInput.value =
    concept.type;

  descriptionInput.value =
    concept.description || "";

  aliasesInput.value =
    (concept.aliases || [])
      .filter(
        (alias) =>
          alias.toLowerCase() !==
          concept.name.toLowerCase()
      )
      .join(", ");

  // -----------------------------------------
  // Current image
  // -----------------------------------------

  if (concept.image) {
    currentImageElement.src =
      concept.image;

    currentImagePanel.hidden =
      false;

    keepCurrentImageButton.hidden =
      false;
  } else {
    currentImageElement.src =
      "";

    currentImagePanel.hidden =
      true;

    keepCurrentImageButton.hidden =
      true;
  }

  // New generation starts empty.
  previewElement.src =
    "";

  previewElement.hidden =
    true;

  document.getElementById(
    "generation-status"
  ).textContent = "";

  saveButton.textContent =
    "Save Changes";

  showLibraryView();

  document
    .getElementById(
      "add-concept"
    )
    .scrollIntoView({
      behavior: "smooth"
    });
}


// =========================================================
// Generate image
// =========================================================

async function generateConceptImage() {
  const nameInput =
    document.getElementById(
      "concept-name"
    );

  const typeInput =
    document.getElementById(
      "concept-type"
    );

  const descriptionInput =
    document.getElementById(
      "concept-description"
    );

  const statusElement =
    document.getElementById(
      "generation-status"
    );

  const previewElement =
    document.getElementById(
      "concept-image-preview"
    );

  const name =
    nameInput.value.trim();

  const type =
    typeInput.value;

  const description =
    descriptionInput.value.trim();

  if (!name) {
    statusElement.textContent =
      "Please enter a concept name before generating an image.";

    return;
  }

  statusElement.textContent =
    "Generating image...";

  try {
    const response =
      await fetch(
        "http://127.0.0.1:8000/concept/generate",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body:
            JSON.stringify({
              name: name,
              type: type,
              description:
                description || null
            })
        }
      );

    if (!response.ok) {
      throw new Error(
        `Generation failed: ${response.status}`
      );
    }

    const data =
      await response.json();

    generatedImageUrl =
      data.image_url;

    // Every generated image enters history,
    // regardless of whether it becomes the
    // selected/current image.
    workingImageHistory.push({
      url:
        generatedImageUrl,

      generatedAt:
        new Date().toISOString()
    });

    previewElement.src =
      generatedImageUrl;

    previewElement.hidden =
      false;

    statusElement.textContent =
      "Image generated successfully.";

  } catch (error) {
    console.error(
      "Image generation error:",
      error
    );

    statusElement.textContent =
      "Could not generate the image. Make sure the backend is running.";
  }
}


// =========================================================
// Save
// =========================================================

async function handleFormSubmit(event) {
  event.preventDefault();

  const nameInput =
    document.getElementById(
      "concept-name"
    );

  const typeInput =
    document.getElementById(
      "concept-type"
    );

  const aliasesInput =
    document.getElementById(
      "concept-aliases"
    );

  const descriptionInput =
    document.getElementById(
      "concept-description"
    );

  const description =
    descriptionInput.value.trim();

  const name =
    nameInput.value.trim();

  const type =
    typeInput.value;

  const typedAliases =
    aliasesInput.value
      .split(",")
      .map(
        (alias) =>
          alias.trim()
      )
      .filter(
        (alias) =>
          alias.length > 0
      );

  const aliases = [
    name,
    ...typedAliases
  ];

  const newConcept = {
    name: name,
    type: type,
    aliases: aliases,
    description: description,

    // Newest selected image.
    image:
      generatedImageUrl,

    // All generations made after
    // adding history support.
    imageHistory:
      workingImageHistory
  };

  const concepts =
    await ConceptStorage.getConcepts();

  if (editingConceptName) {
    const conceptIndex =
      concepts.findIndex(
        (concept) =>
          concept.name ===
          editingConceptName
      );

    if (conceptIndex !== -1) {
      const oldConcept =
        concepts[conceptIndex];

      // No selected new image:
      // retain existing image.
      if (!generatedImageUrl) {
        newConcept.image =
          oldConcept.image;
      }

      concepts[conceptIndex] =
        newConcept;
    }

  } else {
    concepts.push(
      newConcept
    );
  }

  await ConceptStorage.saveConcepts(
    concepts
  );

  // Show the category containing
  // the concept that was just saved.
  activeConceptType =
    type;

  // -----------------------------------------
  // Reset state
  // -----------------------------------------

  editingConceptName =
    null;

  generatedImageUrl =
    null;

  workingImageHistory =
    [];

  currentViewedConcept =
    null;

  const previewElement =
    document.getElementById(
      "concept-image-preview"
    );

  const currentImagePanel =
    document.getElementById(
      "current-image-panel"
    );

  const currentImageElement =
    document.getElementById(
      "current-concept-image"
    );

  const keepCurrentImageButton =
    document.getElementById(
      "keep-current-image-button"
    );

  currentImagePanel.hidden =
    true;

  currentImageElement.src =
    "";

  keepCurrentImageButton.hidden =
    true;

  previewElement.src =
    "";

  previewElement.hidden =
    true;

  document.getElementById(
    "generation-status"
  ).textContent = "";

  document.getElementById(
    "save-concept-button"
  ).textContent =
    "Save Concept";

  document.getElementById(
    "concept-form"
  ).reset();

  await loadConcepts();

  showLibraryView();
}


// =========================================================
// Event listeners
// =========================================================

const conceptForm =
  document.getElementById(
    "concept-form"
  );

const generateImageButton =
  document.getElementById(
    "generate-image-button"
  );

const backToLibraryButton =
  document.getElementById(
    "back-to-library-button"
  );

const detailEditButton =
  document.getElementById(
    "detail-edit-button"
  );

const keepCurrentImageButton =
  document.getElementById(
    "keep-current-image-button"
  );

const conceptTypeTabs =
  document.querySelectorAll(
    ".concept-type-tab"
  );


conceptForm.addEventListener(
  "submit",
  handleFormSubmit
);


generateImageButton.addEventListener(
  "click",
  generateConceptImage
);


backToLibraryButton.addEventListener(
  "click",
  () => {
    currentViewedConcept =
      null;

    showLibraryView();
  }
);


detailEditButton.addEventListener(
  "click",
  () => {
    if (currentViewedConcept) {
      editConcept(
        currentViewedConcept
      );
    }
  }
);


// Keep the existing selected image,
// while preserving newly generated images
// in the history.
keepCurrentImageButton.addEventListener(
  "click",
  () => {
    generatedImageUrl =
      null;

    document.getElementById(
      "generation-status"
    ).textContent =
      "The current image will remain selected. The new generation will stay in image history.";
  }
);


// Person / Activity / Place tabs.
conceptTypeTabs.forEach(
  (tab) => {
    tab.addEventListener(
      "click",
      async () => {
        activeConceptType =
          tab.dataset.type;

        await loadConcepts();
      }
    );
  }
);


// =========================================================
// Initial load
// =========================================================

loadConcepts();