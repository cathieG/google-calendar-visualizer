console.log("Google Calendar Visualizer loaded");

const backgroundRules = {
  gym: "assets/test-background.png",
  church: "assets/church.png",
  lunch: "assets/lunch.png"
};

function updatePopupIllustration() {
  const dialog = document.querySelector(
    '[role="dialog"][aria-labelledby]'
  );

  if (!dialog) return;

  // Get the current event title
  const titleId = dialog.getAttribute("aria-labelledby");
  const titleElement = document.getElementById(titleId);
  const title = titleElement?.textContent?.trim();

  if (!title) return;

  const lowerTitle = title.toLowerCase();

  // Find the first matching keyword
  const matchedRule = Object.entries(backgroundRules).find(
    ([keyword]) => lowerTitle.includes(keyword)
  );

  if (!matchedRule) return;

  const [, imagePath] = matchedRule;
  const customImageUrl = chrome.runtime.getURL(imagePath);

  const header = dialog.querySelector(".Tnsqdc");

  if (!header) return;

  // Case 1:
  // Google already created an illustration area.
  let artWrapper = header.querySelector(".YrCd2b");
  let popupImage = artWrapper?.querySelector("img");

  if (popupImage) {
    if (popupImage.src !== customImageUrl) {
      popupImage.src = customImageUrl;
      console.log("Replaced existing illustration:", title);
    }

    return;
  }

  // Case 2:
  // Google did NOT create an illustration area.
  // Recreate Google's illustrated-event structure.
  header.classList.add("fEQAz");

  artWrapper = document.createElement("div");
  artWrapper.className = "YrCd2b";

  popupImage = document.createElement("img");
  popupImage.className = "AuSgpc";
  popupImage.src = customImageUrl;

  artWrapper.appendChild(popupImage);
  header.prepend(artWrapper);

  console.log("Created custom illustration:", title);
}

const observer = new MutationObserver(() => {
  updatePopupIllustration();
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

updatePopupIllustration();