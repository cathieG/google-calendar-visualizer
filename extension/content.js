console.log("Google Calendar Visualizer loaded");

const concepts = [
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

function ensureIllustration(header, imageUrl) {
  if (!header) return "no-header";

  const existingImage = header.querySelector(".YrCd2b img");

  // Case 1: Google already created an illustration area (or we created one earlier)
  if (existingImage) {
    if (existingImage.src === imageUrl) {
      return "unchanged";
    }

    existingImage.src = imageUrl;
    return "replaced";
  }

  // Case 2: No illustration exists yet — create one using Google's layout classes
  header.classList.add("fEQAz");

  const artWrapper = document.createElement("div");
  artWrapper.className = "YrCd2b";

  const popupImage = document.createElement("img");
  popupImage.className = "AuSgpc";
  popupImage.src = imageUrl;

  artWrapper.appendChild(popupImage);
  header.prepend(artWrapper);

  return "created";
}

function applyCustomIllustration() {
  if (!isExtensionContextValid()) return;

  const dialog = CalendarAdapter.getOpenDialog();
  if (!dialog) return;

  const title = CalendarAdapter.getEventTitle(dialog);
  if (!title) return;

  const matchedConcepts = findMatchingConcepts(title);
  if (matchedConcepts.length === 0) return;

  const conceptWithImage = getConceptWithImage(matchedConcepts);
  if (!conceptWithImage) return;

  const imageUrl = chrome.runtime.getURL(conceptWithImage.image);
  const result = CalendarAdapter.applyIllustration(dialog, imageUrl);

  // Only log when we actually changed something
  if (result === "created" || result === "replaced") {
    console.log(
      "Matched concepts:",
      matchedConcepts.map((concept) => ({
        name: concept.name,
        type: concept.type
      }))
    );

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

applyCustomIllustration();