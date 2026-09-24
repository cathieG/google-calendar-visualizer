import base64
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

from visual_planner import (
    ConceptRequest,
    ContentPlan,
    plan_concept_image,
)


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI()


# ---------------------------------------------------------
# Generated image storage
# ---------------------------------------------------------

BACKEND_DIR = Path(__file__).parent

generated_dir = BACKEND_DIR / "generated"
generated_dir.mkdir(exist_ok=True)

app.mount(
    "/generated",
    StaticFiles(directory=generated_dir),
    name="generated",
)


# ---------------------------------------------------------
# Generic renderer prompt
# ---------------------------------------------------------

def build_renderer_prompt(content_plan: ContentPlan) -> str:
    """
    Convert a style-independent ContentPlan into instructions
    for the image model.

    The Content Planner has already decided WHAT the illustration
    should communicate.

    No style-specific art direction has been applied yet.

    For the generic baseline, the renderer may make reasonable
    default visual decisions while preserving the semantic content
    and hard content constraints.
    """

    candidate_objects = "\n".join(
        f"- {item}"
        for item in content_plan.candidate_objects
    )

    if not candidate_objects:
        candidate_objects = "- None specifically suggested."

    content_constraints = "\n".join(
        f"- {item}"
        for item in content_plan.content_constraints
    )

    if not content_constraints:
        content_constraints = "- No additional content constraints."

    if content_plan.accent_detail:
        accent_detail = content_plan.accent_detail
    else:
        accent_detail = "None."

    prompt = f"""
Create a wide horizontal calendar illustration based on the approved
content plan below.

The content planner has already decided WHAT the image should
communicate.

No specific predefined art style or art direction has been selected.

Use reasonable default visual decisions for HOW to compose and render
the image while preserving the approved semantic idea.

Do not reinterpret the event into a different concept.

--------------------------------------------------
APPROVED CONTENT IDEA
--------------------------------------------------

Visual idea:
{content_plan.visual_idea}

Suggested representation strategy:
{content_plan.representation}

Primary semantic subject:
{content_plan.subject}

Setting:
{content_plan.setting or "No particular setting is required."}

Action:
{content_plan.action or "No particular action is required."}

--------------------------------------------------
CANDIDATE OBJECTS
--------------------------------------------------

The content planner identified these objects as potentially useful
semantic resources:

{candidate_objects}

These objects are OPTIONS, not a checklist.

You may use all, some, or none of them depending on what best supports
the approved visual idea.

Do not add unrelated objects merely because they are commonly associated
with the event.

Minor incidental elements may be added when necessary for visual
coherence, but they must not introduce new semantic claims or a new
storyline.

--------------------------------------------------
OPTIONAL ACCENT DETAIL
--------------------------------------------------

{accent_detail}

If an accent detail is provided, you may include it when it improves
the illustration.

It is optional and should remain secondary to the core idea.

If no accent detail is provided, do not invent a significant new
secondary storyline.

--------------------------------------------------
CONTENT CONSTRAINTS
--------------------------------------------------

These are HARD semantic boundaries:

{content_constraints}

Do not violate these constraints through composition, staging, character
depiction, or rendering choices.

--------------------------------------------------
PEOPLE AND IDENTITY
--------------------------------------------------

Distinguish between IDENTIFIED PEOPLE and ANONYMOUS PEOPLE.

IDENTIFIED PEOPLE

An identified person is someone the ContentPlan associates with a
specific real person, such as a named participant.

When depicting an identified person, preserve any personal
characteristics explicitly provided by the ContentPlan.

Do not invent unsupported identity-specific characteristics for that
person, including:
- race or ethnicity,
- skin tone,
- age,
- gender,
- facial appearance,
- hair color or hairstyle,
- body type,
- distinctive clothing or personal style.

If these characteristics are unknown, do not visually present an
invented set of characteristics as though they describe that specific
person.

ANONYMOUS PEOPLE

When the scene naturally involves people but no particular person's
identity is being represented, depict ordinary, natural-looking human
figures.

Anonymous people MAY have normal visual characteristics such as:
- different skin tones,
- different hair colors,
- different hair textures and hairstyles,
- varied gender presentation,
- varied ordinary clothing,
- ordinary facial features and body variation.


In scenes containing multiple anonymous people, natural visual variety
is optional.

Do not use appearance to imply unsupported roles, relationships,
personalities, occupations, or stereotypes.

The goal for anonymous people is natural human variety.

The goal for identified people is fidelity to known information and
avoidance of unsupported identity claims.

--------------------------------------------------
TEXT
--------------------------------------------------

Do not include readable written words unless the approved content
specifically requires them.

Do not invent:
- names,
- captions,
- event titles,
- banners,
- labels,
- slogans,
- signs,
- greeting messages,
- song lyrics.

Numerals or simple symbols may appear only when they are semantically
necessary to communicate the approved idea.

--------------------------------------------------
GENERIC VISUAL TREATMENT
--------------------------------------------------

No predefined visual style has been selected.

Use your natural/default illustration behavior.

You may make reasonable visual choices about:
- composition,
- visual hierarchy,
- scale,
- framing,
- cropping,
- perspective,
- negative space,
- color,
- lighting,
- shape treatment,
- rendering technique.

These choices should make the approved content clear and visually
coherent.

They must not change the semantic meaning of the ContentPlan.

The final image should work as a wide horizontal calendar illustration
and should communicate the core idea clearly at relatively small size.
""".strip()

    return prompt


# ---------------------------------------------------------
# Image generation helper
# ---------------------------------------------------------

def render_content_plan(content_plan: ContentPlan) -> dict:
    """
    Render an existing ContentPlan without rerunning the
    concept interpreter or content planner.

    This is useful for repeatedly testing the renderer with
    exactly the same semantic plan.
    """

    print("Rendering content plan:")
    print(content_plan.model_dump_json(indent=2))

    prompt = build_renderer_prompt(content_plan)

    print("Renderer prompt:")
    print(prompt)

    result = client.images.generate(
        model="gpt-image-2",
        prompt=prompt,
        size="1472x512",
        quality="medium",
    )

    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"concept_{timestamp}.png"

    output_path = generated_dir / filename

    with output_path.open("wb") as image_file:
        image_file.write(image_bytes)

    image_url = f"http://127.0.0.1:8000/generated/{filename}"

    return {
        "message": "Image generated successfully",
        "filename": filename,
        "file": str(output_path),
        "image_url": image_url,
        "content_plan": content_plan.model_dump(),
    }


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.post("/concept/plan")
def plan_concept(request: ConceptRequest):
    content_plan = plan_concept_image(request)

    return {
        "content_plan": content_plan.model_dump()
    }


@app.post("/concept/render")
def render_existing_content_plan(
    content_plan: ContentPlan,
):
    return render_content_plan(content_plan)


@app.post("/concept/generate")
def generate_concept(request: ConceptRequest):

    # Stage 1:
    # Interpret the event and decide WHAT the illustration
    # should communicate.
    content_plan = plan_concept_image(request)

    print("Generated content plan:")
    print(content_plan.model_dump_json(indent=2))

    # Stage 2:
    # For now, render the ContentPlan using the model's
    # generic/default visual behavior.
    #
    # A style-specific Art Director will be inserted between
    # these two stages later.
    return render_content_plan(content_plan)