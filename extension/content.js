console.log("Google Calendar Visualizer loaded");

const backgroundRules = {
  gym: "assets/test-background.png",
  church: "assets/church.png",
  lunch: "assets/lunch.png"
};

function getOpenDialog() {
  return document.querySelector('[role="dialog"][aria-labelledby]');
}

function getEventTitle(dialog) {
  if (!dialog) return null;

  const titleId = dialog.getAttribute("aria-labelledby");
  if (!titleId) return null;

  const titleElement = document.getElementById(titleId);
  return titleElement?.textContent?.trim() || null;
}

function findMatchingRule(title) {
  if (!title) return null;

  const lowerTitle = title.toLowerCase();

  return Object.entries(backgroundRules).find(
    ([keyword]) => lowerTitle.includes(keyword)
  ) || null;
}

function replaceExistingIllustration(header, imageUrl) {
  const popupImage = header.querySelector(".YrCd2b img");

  if (!popupImage) return false;

  if (popupImage.src !== imageUrl) {
    popupImage.src = imageUrl;
  }

  return true;
}

function createIllustration(header, imageUrl) {
  header.classList.add("fEQAz");

  const artWrapper = document.createElement("div");
  artWrapper.className = "YrCd2b";

  const popupImage = document.createElement("img");
  popupImage.className = "AuSgpc";
  popupImage.src = imageUrl;

  artWrapper.appendChild(popupImage);
  header.prepend(artWrapper);
}

function applyCustomIllustration() {
  const dialog = getOpenDialog();
  if (!dialog) return;

  const title = getEventTitle(dialog);
  if (!title) return;

  const matchedRule = findMatchingRule(title);
  if (!matchedRule) return;

  const [, imagePath] = matchedRule;
  const imageUrl = chrome.runtime.getURL(imagePath);

  const header = dialog.querySelector(".Tnsqdc");
  if (!header) return;

  const replaced = replaceExistingIllustration(header, imageUrl);

  if (!replaced) {
    createIllustration(header, imageUrl);
  }

  console.log("Applied custom illustration:", title);
}

const observer = new MutationObserver(() => {
  applyCustomIllustration();
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

applyCustomIllustration();