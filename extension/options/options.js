let editingConceptName = null;

async function loadConcepts() {
  const concepts = await ConceptStorage.getConcepts();

  const conceptList = document.getElementById("concept-list");

  // Remove previously displayed concepts before rendering again.
  const oldConcepts = conceptList.querySelectorAll(".concept-item");
  oldConcepts.forEach((element) => element.remove());

  concepts.forEach((concept) => {
    const conceptElement = document.createElement("div");
    conceptElement.className = "concept-item";

    const nameElement = document.createElement("h3");
    nameElement.textContent = concept.name;

    const typeElement = document.createElement("p");
    typeElement.textContent = `Type: ${concept.type}`;

    const aliasesElement = document.createElement("p");
    aliasesElement.textContent = `Aliases: ${concept.aliases.join(", ")}`;

    const editButton = document.createElement("button");
    editButton.textContent = "Edit";
    editButton.dataset.conceptName = concept.name;
    editButton.addEventListener("click", () => {
      editConcept(concept);
    });

    const deleteButton = document.createElement("button");
    deleteButton.textContent = "Delete";
    deleteButton.dataset.conceptName = concept.name;
    deleteButton.addEventListener("click", () => {
      deleteConceptByName(concept.name);
    });

    conceptElement.appendChild(nameElement);
    conceptElement.appendChild(typeElement);
    conceptElement.appendChild(aliasesElement);
    conceptElement.appendChild(editButton);
    conceptElement.appendChild(deleteButton);

    conceptList.appendChild(conceptElement);
  });
}

async function deleteConceptByName(name) {
  const concepts = await ConceptStorage.getConcepts();

  const updatedConcepts = concepts.filter(
    (concept) => concept.name !== name
  );

  await ConceptStorage.saveConcepts(updatedConcepts);

  await loadConcepts();
}

function editConcept(concept) {
  editingConceptName = concept.name;

  const nameInput = document.getElementById("concept-name");
  const typeInput = document.getElementById("concept-type");
  const aliasesInput = document.getElementById("concept-aliases");
  const saveButton = document.getElementById("save-concept-button");

  nameInput.value = concept.name;
  typeInput.value = concept.type;

  aliasesInput.value = concept.aliases
    .filter((alias) => alias.toLowerCase() !== concept.name.toLowerCase())
    .join(", ");

  saveButton.textContent = "Save Changes";  
}

async function handleFormSubmit(event) {
  event.preventDefault();

  const nameInput = document.getElementById("concept-name");
  const typeInput = document.getElementById("concept-type");
  const aliasesInput = document.getElementById("concept-aliases");

  const name = nameInput.value.trim();
  const type = typeInput.value;

  const typedAliases = aliasesInput.value
    .split(",")
    .map((alias) => alias.trim())
    .filter((alias) => alias.length > 0);

  const aliases = [name, ...typedAliases];

  const newConcept = {
    name: name,
    type: type,
    aliases: aliases,
    image: null
  };

  const concepts = await ConceptStorage.getConcepts();

  if (editingConceptName) {
    const conceptIndex = concepts.findIndex(
      (concept) => concept.name === editingConceptName
    );

    if (conceptIndex !== -1) {
      // Keep the existing image when editing.
      newConcept.image = concepts[conceptIndex].image;

      // Replace the old concept with the edited version.
      concepts[conceptIndex] = newConcept;
    }
  } else {
    // We are not editing, so create a brand-new concept.
    concepts.push(newConcept);
  }

  await ConceptStorage.saveConcepts(concepts);

  editingConceptName = null;

  document.getElementById("save-concept-button").textContent = "Save Concept";

  document.getElementById("concept-form").reset();

  await loadConcepts();
}

const conceptForm = document.getElementById("concept-form");

conceptForm.addEventListener("submit", handleFormSubmit);

loadConcepts();