import base64
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()

client = OpenAI()


# ---------------------------------------------------------
# Data models
# ---------------------------------------------------------

class ConceptRequest(BaseModel):
    name: str
    type: str
    description: str | None = None


class ScenePlan(BaseModel):
    subject: str
    representation: str
    setting: str
    action: str
    important_objects: list[str]


class ReferenceSelection(BaseModel):
    concepts: list[str]


# ---------------------------------------------------------
# Google Calendar visual references
# ---------------------------------------------------------

REFERENCE_DIR = Path(__file__).parent / "references" / "rendered"

VISUAL_REFERENCES = [
    ("Art", "img_art.png"),
    ("Baby Shower", "img_babyshower.png"),
    ("Badminton", "img_badminton.png"),
    ("Chinese New Year", "img_chinesenewyear.png"),
    ("Delivery", "img_delivery.png"),
    ("Karate", "img_karate.png"),
    ("Learn Instrument", "img_learninstrument.png"),
    ("Tennis", "img_tennis.png"),
    ("Wedding", "img_wedding.png"),
]


# ---------------------------------------------------------
# Image helper
# ---------------------------------------------------------

def image_to_data_url(path: Path) -> str:
    """
    Convert a local PNG image into a base64 data URL
    that can be sent to the OpenAI API.
    """
    image_bytes = path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    return f"data:image/png;base64,{encoded}"


# ---------------------------------------------------------
# Reference selector
# ---------------------------------------------------------

def select_visual_references(
    request: ConceptRequest,
) -> list[tuple[str, str]]:
    """
    Choose a small subset of Google Calendar reference illustrations
    that will be useful for planning the new concept.
    """

    available_concepts = [
        concept_name
        for concept_name, _ in VISUAL_REFERENCES
    ]

    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": """
You select visual design references for a calendar illustration planner.

You will receive:
1. a new calendar concept,
2. a list of available reference concepts.

Choose exactly 3 references that would be most useful when deciding
how the new concept should be visually represented.

Do not simply choose the three concepts that are most semantically
similar.

Choose references that together help the visual planner compare
different possible representation strategies.

Prefer a useful combination of:
- semantic relevance,
- analogous activities or events,
- contrasting ways a concept might be represented.

Return only concepts from the supplied list.
""".strip(),
            },
            {
                "role": "user",
                "content": f"""
New concept: {request.name}
Concept type: {request.type}
Description: {request.description or "None provided"}

Available reference concepts:
{", ".join(available_concepts)}
""".strip(),
            },
        ],
        text_format=ReferenceSelection,
    )

    selected_names = response.output_parsed.concepts

    selected_references = [
        (concept_name, filename)
        for concept_name, filename in VISUAL_REFERENCES
        if concept_name in selected_names
    ]

    print(
        f"Selected visual references for {request.name}: "
        f"{[name for name, _ in selected_references]}"
    )

    return selected_references


# ---------------------------------------------------------
# Build multimodal reference message
# ---------------------------------------------------------

def build_visual_reference_content(
    references: list[tuple[str, str]],
):
    """
    Build a multimodal message containing the selected Google Calendar
    reference illustrations.

    Each image is labeled with its concept name, but we deliberately
    do not describe what appears inside it. The planner should infer
    Google's representation decisions from the image itself.
    """

    content = [
        {
            "type": "input_text",
            "text": (
                "Below are reference illustrations used by Google Calendar. "
                "Each image is labeled with the concept it represents. "
                "Study what Google chose to depict for each concept. "
                "Focus on representation decisions: which subjects, objects, "
                "people, actions, or environments were included. "
                "Do not copy the rendering style."
            ),
        }
    ]

    for concept_name, filename in references:
        image_path = REFERENCE_DIR / filename

        if not image_path.exists():
            raise FileNotFoundError(
                f"Visual reference image not found: {image_path}"
            )

        content.append(
            {
                "type": "input_text",
                "text": f"Reference concept: {concept_name}",
            }
        )

        content.append(
            {
                "type": "input_image",
                "image_url": image_to_data_url(image_path),
            }
        )

    return content


# ---------------------------------------------------------
# Visual planner
# ---------------------------------------------------------

def plan_concept_image(request: ConceptRequest) -> ScenePlan:
    """
    Select useful visual references and then create a scene plan
    for the requested calendar concept.
    """

    # Stage 1:
    # Select a small subset of useful Google Calendar references.
    selected_references = select_visual_references(request)

    # Stage 2:
    # Give those actual images to the visual planner.
    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": """
You are a visual planner for small calendar illustrations.

Your job is to decide WHAT should be depicted, not HOW it should be drawn.

Choose the clearest and simplest visual representation of the concept.

Possible representation strategies include:

- activity_scene:
  A person or people performing an action. Use this when human action
  itself is important for recognizing the concept.

- environment_scene:
  A recognizable place or environment. Use this when the setting
  communicates the concept without requiring a person.

- object_composition:
  A small arrangement of distinctive objects or symbols. Prefer this
  when a few recognizable objects communicate the concept more simply
  than a full scene.

- character_activity:
  A character performing a simple recognizable action, when showing
  the person adds useful meaning without requiring a complex scene.

- atmosphere_scene:
  Environmental or symbolic elements that communicate a celebration,
  holiday, season, or mood.

Before choosing a representation, consider multiple possible ways to
depict the concept.

Prefer the representation that:
1. communicates the concept immediately,
2. uses the fewest necessary visual elements,
3. works well in a small, wide calendar banner,
4. avoids unnecessary people, objects, and background detail.

People should only appear when human action, posture, interaction,
or identity is important for communicating the concept.

The reference images supplied by the user are examples of how
Google Calendar has visually represented different concepts.

Study the references for general representation principles:
- when objects alone are sufficient,
- when a setting is important,
- when human action is important,
- when a symbolic or atmospheric composition works better.

Do not simply copy the subject matter of a reference.

Do not assume a new concept should use the same representation
strategy as the most similar reference.

The important_objects field should usually contain 2-4 items.

For setting or action, use an empty string when that field is
not necessary.

The action field describes an action occurring within the scene.
Do not use the action field for composition or drawing instructions.

Focus only on WHAT should be depicted.

Do not make decisions about illustration style, colors, rendering,
lighting, or artistic technique.
""".strip(),
            },

            # Selected actual Google Calendar illustrations
            {
                "role": "user",
                "content": build_visual_reference_content(
                    selected_references
                ),
            },

            # New concept to plan
            {
                "role": "user",
                "content": f"""
Now plan a NEW calendar illustration.

Concept name: {request.name}
Concept type: {request.type}
Additional description: {request.description or "None provided"}

Choose the representation that communicates this particular concept
most clearly and simply.
""".strip(),
            },
        ],
        text_format=ScenePlan,
    )

    return response.output_parsed