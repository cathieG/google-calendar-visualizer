# Google Calendar Visualizer

Google Calendar Visualizer is a Chrome extension that adds custom illustrations to Google Calendar events.

Users can create reusable concepts such as people, activities, and places, associate generated images with those concepts, and display the selected image inside matching Google Calendar events.

The project currently includes the browser extension, a concept-management interface, and the first stages of an AI pipeline for interpreting concepts and preparing them for image generation.

---

## Current Features

### Google Calendar Integration

The Chrome extension runs directly inside Google Calendar using a Manifest V3 content script.

It currently:

- observes changes to the Google Calendar DOM
- detects event views as they are opened or updated
- reads event titles
- matches event titles against saved concepts
- retrieves concept information from Chrome Storage
- inserts the selected concept image into the Google Calendar event interface

Because Google Calendar updates dynamically without full page reloads, the extension uses `MutationObserver` to detect interface changes.

---

## Concept Management

The extension includes an options page for creating and managing concepts.

Each concept represents something that may appear repeatedly in calendar events.

Examples include:

- Gym
- Church
- Lunch
- Badminton
- Church band rehearsal
- a person
- a restaurant
- another frequently visited place

Concepts are grouped into three types:

- **Person**
- **Activity**
- **Place**

The options page currently supports:

- creating concepts
- editing concepts
- deleting concepts
- filtering concepts by type
- storing concept data in Chrome Storage
- viewing generated images associated with a concept
- selecting which image should be the active image for that concept

---

## Image History

A concept can have multiple generated images.

Instead of replacing an older image every time a new one is generated, the extension keeps previous generations associated with the concept.

Users can review those images and select the one they want to use.

The selected image is then used when the corresponding event is displayed in Google Calendar.

---

## Concept Interpretation Pipeline

The project also contains a Python-based concept interpretation pipeline.

The purpose of this stage is to convert a short concept name into structured information that can later be used by image-generation and visual-planning components.

For example, a concept such as:

```text
Church band rehearsal
```

can be converted into structured information describing:

- the visual idea
- the type of representation
- the main subject
- the setting
- the main action
- important objects
- optional accent details
- constraints on what should or should not appear

An example output may look conceptually like:

```json
{
  "visual_idea": "A small worship team rehearsing music together",
  "representation": "social_interaction_scene",
  "subject": "A group of singers and musicians",
  "setting": "A church rehearsal space",
  "action": "Practicing music together",
  "important_objects": [
    "Microphones",
    "Music stands",
    "Keyboard"
  ],
  "content_constraints": [
    "Show rehearsal rather than a worship service",
    "Avoid implying specific identities or roles",
    "Do not add a congregation or clergy"
  ]
}
```

This structured output is defined using schemas so later pipeline stages receive predictable fields rather than free-form model responses.

---

## Current Pipeline

The current project flow is approximately:

```text
Google Calendar Event
        ↓
Event Title Detection
        ↓
Concept Matching
        ↓
Saved Concept
        ↓
Selected Concept Image
        ↓
Google Calendar Event UI
```

For new image generation, the backend work is moving toward:

```text
Concept Name
     ↓
Concept Interpreter
     ↓
Structured Concept Data
     ↓
Reference Support
     ↓
Visual Planning
     ↓
Image Generation
     ↓
Saved Image History
     ↓
User Selects Active Image
```

The concept interpreter and schema definitions are currently implemented.

Reference support is the next major pipeline component.

---

## Reference Support

The planned reference system will provide relevant visual examples to later planning stages.

The goal is not to copy a reference image directly. Instead, references can provide information about how similar concepts are visually represented.

The interpreter can identify which reference dimensions may be useful for a specific concept.

Examples include:

- `representation_strategy`
- `recognition_structure`
- scene organization
- important visual cues
- subject relationships

A later reference-retrieval component can use those fields to find relevant visual precedents before the final image prompt is constructed.

---

## Planned Visual Planning Stage

After reference retrieval, a separate visual-planning stage will combine:

- the interpreted concept
- selected references
- representation requirements
- content constraints

The planner will determine the concrete composition that should be sent to the image-generation model.

For example, it may decide:

- whether to use a full scene or a simpler object-based composition
- how many people should appear
- which objects need to be prominent
- which details are unnecessary
- which visual cues distinguish the activity from similar activities
- how the scene should fit the wide calendar illustration format

This stage has not yet been fully integrated.

---

## Planned Style Integration

Style is intentionally handled separately from concept interpretation.

Future style integration may control shared properties such as:

- illustration style
- background treatment
- level of detail
- color palette
- line treatment
- character rendering
- composition density
- use of accent colors

This will allow different concepts to remain visually consistent even when they contain very different subject matter.

---

## Image Format

Concept illustrations are designed for a wide rectangular area inside Google Calendar.

The current target image size is approximately:

```text
1472 × 512
```

The composition therefore needs to work well in a wide aspect ratio rather than a square image.

---

## Technology Stack

### Chrome Extension

- JavaScript
- HTML
- CSS
- Chrome Extension Manifest V3
- Chrome Storage API
- DOM APIs
- `MutationObserver`

### Backend / AI Pipeline

- Python
- OpenAI API
- structured prompting
- schema-based model outputs

### Development

- Git
- GitHub
- VS Code

---

## Repository Components

The repository currently contains code for several related parts of the system.

### Browser Extension

Responsible for:

- interacting with Google Calendar
- detecting events
- matching events to concepts
- loading concept data
- displaying selected images

### Options Page

Responsible for:

- concept creation
- concept editing
- concept deletion
- concept type filtering
- image-history display
- active-image selection

### Concept Interpreter

Responsible for:

- analyzing a concept
- producing structured visual information
- identifying important content constraints
- identifying useful reference dimensions

### Schemas

Responsible for defining the structure of data passed between AI pipeline stages.

This ensures that components such as the interpreter, reference system, and future visual planner use a consistent interface.

---

## Current Development Status

### Implemented

- Chrome extension using Manifest V3
- Google Calendar DOM integration
- dynamic event detection using `MutationObserver`
- event-title extraction
- concept matching
- Chrome Storage integration
- concept creation, editing, and deletion
- Person / Activity / Place categories
- concept filtering
- concept image history
- active-image selection
- concept interpreter
- structured interpreter output
- schema definitions for the interpretation pipeline

### In Progress

- reference-support pipeline
- selecting relevant reference dimensions
- connecting interpreted concepts to visual references

### Planned

- reference retrieval
- visual / creative planning stage
- style configuration
- automated prompt construction
- image-generation integration
- storing generated outputs automatically in concept history
- improved matching between calendar event titles and saved concepts
- more robust handling of Google Calendar DOM changes
- end-to-end generation from a newly created concept

---

## Expected Future End-to-End Flow

Once the remaining components are integrated, creating a new concept could work like this:

```text
1. User creates a concept
          ↓
2. Concept is sent to the interpreter
          ↓
3. Interpreter generates structured concept data
          ↓
4. Reference system retrieves relevant examples
          ↓
5. Visual planner creates a scene specification
          ↓
6. Style settings are applied
          ↓
7. Image prompt is generated
          ↓
8. Image-generation model creates the illustration
          ↓
9. Image is added to the concept's history
          ↓
10. User selects the preferred image
          ↓
11. Matching Google Calendar events display that image
```

The current work is focused on building these stages separately before connecting them into a single automatic pipeline.

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd <repository-name>
```

Open Chrome and navigate to:

```text
chrome://extensions
```

Then:

1. Enable **Developer mode**
2. Click **Load unpacked**
3. Select the Chrome extension directory
4. Open the extension's options page to manage concepts

Additional setup will be required for backend AI functionality once the generation pipeline is fully integrated.

---

## Status

This project is actively under development.

The browser-side concept management and calendar integration are functional. Current backend development is focused on completing the structured pipeline between concept interpretation, reference support, visual planning, and image generation.
