console.log("Google Calendar Visualizer loaded");

function highlightEvents() {
  const events = document.querySelectorAll(
    'div[role="button"][data-eventid]'
  );

  events.forEach((event) => {
    event.style.outline = "3px solid red";
  });
}

highlightEvents();

const observer = new MutationObserver(() => {
  highlightEvents();
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});