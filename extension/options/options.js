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

    conceptElement.appendChild(nameElement);
    conceptElement.appendChild(typeElement);
    conceptElement.appendChild(aliasesElement);

    conceptList.appendChild(conceptElement);
  });
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

  concepts.push(newConcept);

  await ConceptStorage.saveConcepts(concepts);

  document.getElementById("concept-form").reset();

  await loadConcepts();
}

const conceptForm = document.getElementById("concept-form");

conceptForm.addEventListener("submit", handleFormSubmit);

loadConcepts();