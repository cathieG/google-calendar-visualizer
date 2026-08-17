console.log("Google Calendar Visualizer loaded");

function updatePopupIllustration() {
  const popupImage = document.querySelector("img.AuSgpc");

  if (popupImage) {
    const customImageUrl = chrome.runtime.getURL(
      "assets/test-background.png"
    );

    popupImage.src = customImageUrl;
    popupImage.style.objectFit = "cover";
    popupImage.style.objectPosition = "center";

    console.log("Popup illustration replaced with local image");
  }
}

const observer = new MutationObserver(() => {
  updatePopupIllustration();
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

updatePopupIllustration();