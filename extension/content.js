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
  },
  {
    name: "Canaan",
    type: "person",
    aliases: ["Canaan","friend"],
    image: null
  }

];

const fallbackImages = {
  activity: "assets/fallback-activity.png",
  person: "assets/fallback-person.png",
  place: "assets/fallback-place.png"
};


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

function resolveImageUrl(imagePath) {
  if (!imagePath) return null;

  if (
    imagePath.startsWith("http://") ||
    imagePath.startsWith("https://")
  ) {
    return imagePath;
  }

  return chrome.runtime.getURL(imagePath);
}

function findMatchingConcepts(title) {
  if (!title) return [];

  const normalizedTitle = normalizeText(title);

  const matches = concepts
    .map((concept) => {
      const matchingAliases = concept.aliases.filter((alias) =>
        normalizedTitle.includes(normalizeText(alias))
      );

      if (matchingAliases.length === 0) {
        return null;
      }

      const longestMatchingAlias = matchingAliases.reduce(
        (longest, alias) =>
          normalizeText(alias).length > normalizeText(longest).length
            ? alias
            : longest
      );

      const normalizedAlias = normalizeText(longestMatchingAlias);

      const score =
        normalizedAlias === normalizedTitle
          ? 10000 + normalizedAlias.length
          : normalizedAlias.length;

      return {
        concept,
        score
      };
    })
    .filter((match) => match !== null);

  matches.sort((a, b) => b.score - a.score);

  return matches.map((match) => match.concept);
}

function getConceptWithImage(matchedConcepts) {
  return matchedConcepts.find((concept) => concept.image) || null;
}

function getImageForMatchedConcepts(matchedConcepts) {
  const conceptWithImage = getConceptWithImage(matchedConcepts);

  if (conceptWithImage) {
    return conceptWithImage.image;
  }

  const firstMatchedConcept = matchedConcepts[0];

  return fallbackImages[firstMatchedConcept.type] || null;
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

  const imagePath = getImageForMatchedConcepts(matchedConcepts);
  console.log("Selected image path:", imagePath);

  if (!imagePath) {
    return;
  }

  const imageUrl = resolveImageUrl(imagePath);

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

  console.log("Loaded concepts:", concepts);

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