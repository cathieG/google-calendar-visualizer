# Architecture

## Core Principles

1. Google Calendar DOM logic stays isolated in a dedicated calendar adapter.
2. API secrets never live inside the Chrome extension.
3. People, places, and activities use one common concept model.
4. Deterministic keyword and alias matching happens before any LLM fallback.
5. Generated images are cached and reused whenever possible.
6. The extension should fail gracefully and never make Google Calendar unusable.
7. Mobile support is out of scope for the MVP.
8. Google Calendar API integration is a stretch goal, not a dependency.

## Initial Project Structure

calendar-visualizer/
├── extension/
│   ├── manifest.json
│   ├── content/
│   ├── options/
│   ├── storage/
│   └── assets/
├── backend/
├── shared/
├── tests/
├── PROJECT.md
├── ARCHITECTURE.md
├── TASKS.md
└── README.md

## MVP Data Model

A reusable concept can represent:

- Person
- Place
- Activity
- Other

Each concept may contain:

- id
- name
- type
- aliases
- text description
- important details to preserve
- reference images
- canonical generated image

## Event Processing Flow

Google Calendar event
→ extract title/location
→ match known concepts
→ semantic fallback if needed
→ retrieve concept assets
→ check cache
→ generate image if missing
→ render custom background in Calendar