window.CalendarAdapter = {
  getOpenDialog() {
    return document.querySelector('[role="dialog"][aria-labelledby]');
  },

  getEventTitle(dialog) {
    if (!dialog) return null;

    const titleId = dialog.getAttribute("aria-labelledby");
    if (!titleId) return null;

    const titleElement = document.getElementById(titleId);
    return titleElement?.textContent?.trim() || null;
  },

  getHeader(dialog) {
    return dialog?.querySelector(".Tnsqdc") || null;
  },

  hasGoogleIllustration(dialog) {
    const header = this.getHeader(dialog);
    if (!header) return false;

    const image = header.querySelector(".YrCd2b img");

    if (!image) {
      return false;
    }

    return image.dataset.calendarVisualizer !== "true";
  },


  applyIllustration(dialog, imageUrl) {
    const header = this.getHeader(dialog);

    if (!header) {
      return "no-header";
    }

    const existingImage = header.querySelector(".YrCd2b img");

    // Google already has an illustration area
    if (existingImage) {
      existingImage.dataset.calendarVisualizer = "true";
      existingImage.style.transform = "scaleX(-1)";

      if (existingImage.src === imageUrl) return "unchanged";

      existingImage.src = imageUrl;
      return "replaced";
    }

    // Google has no illustration, so create one
    header.classList.add("fEQAz");

    const artWrapper = document.createElement("div");
    artWrapper.className = "YrCd2b";

    const popupImage = document.createElement("img");
    popupImage.className = "AuSgpc";
    popupImage.src = imageUrl;
    popupImage.dataset.calendarVisualizer = "true";
    popupImage.style.transform = "scaleX(-1)";

    artWrapper.appendChild(popupImage);
    header.prepend(artWrapper);

    return "created";
  }
};