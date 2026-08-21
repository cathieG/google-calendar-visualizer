console.log("Google Calendar Visualizer loaded");

const defaultConcepts = [
  {
    name: "Gym",
    type: "activity",
    aliases: ["gym", "workout"],
    image: "assets/test-background.png"
  },
  {
    name: "Church",
    type: "place",
    aliases: ["church", "church service"],
    image: "assets/church.png"
  },
  {
    name: "Lunch",
    type: "activity",
    aliases: ["lunch", "brunch"],
    image: "assets/lunch.png"
  },
  {
    name: "Sarah",
    type: "person",
    aliases: ["sarah"],
    image: null
  },
  {
    name: "Green Cafe",
    type: "place",
    aliases: ["green cafe", "green café"],
    image: null
  },
  {
    name: "Jim",
    type: "person",
    aliases: ["jim"],
    image: null
  },
  {
    name: "Carol",
    type: "person",
    aliases: ["carol"],
    image: null
  }
];

let concepts = [];
let lastLoggedMatchKey = null;

function normalizeText(text) {
  return (text || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim();
}

function isExtensionContextValid() {
  return (
    typeof chrome !== "undefined" &&
    chrome.runtime &&
    chrome.runtime.id
  );
}

function findMatchingConcepts(title) {
  if (!title) return [];

  const normalizedTitle = normalizeText(title);

  return concepts.filter((concept) =>
    concept.aliases.some((alias) =>
      normalizedTitle.includes(normalizeText(alias))
    )
  );
}

function getConceptWithImage(matchedConcepts) {
  return matchedConcepts.find((concept) => concept.image) || null;
}

function applyCustomIllustration() {
  if (!isExtensionContextValid()) return;

  const dialog = CalendarAdapter.getOpenDialog();
  if (!dialog) return;

  const title = CalendarAdapter.getEventTitle(dialog);
  if (!title) return;

  const matchedConcepts = findMatchingConcepts(title);
  if (matchedConcepts.length === 0) return;

  const matchKey = `${title}|${matchedConcepts
    .map((concept) => concept.name)
    .join(",")}`;

  if (lastLoggedMatchKey !== matchKey) {
    console.log(
      "Matched concepts:",
      matchedConcepts.map((concept) => ({
        name: concept.name,
        type: concept.type
      }))
    );

    lastLoggedMatchKey = matchKey;
  }

  const conceptWithImage = getConceptWithImage(matchedConcepts);

  if (!conceptWithImage) {
    return;
  }

  const imageUrl = chrome.runtime.getURL(conceptWithImage.image);

  const result = CalendarAdapter.applyIllustration(
    dialog,
    imageUrl
  );

  if (result === "created" || result === "replaced") {
    console.log(
      `Applied custom illustration (${result}):`,
      title
    );
  }
}

const observer = new MutationObserver(() => {
  if (!isExtensionContextValid()) {
    observer.disconnect();
    return;
  }

  applyCustomIllustration();
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

async function initialize() {
  concepts = await ConceptStorage.initializeConcepts(defaultConcepts);

  applyCustomIllustration();
}

chrome.storage.onChanged.addListener((changes, areaName) => {
  if (areaName !== "local") return;

  if (changes.concepts) {
    concepts = changes.concepts.newValue || [];

    console.log("Concepts updated from storage");

    applyCustomIllustration();
  }
});


initialize();