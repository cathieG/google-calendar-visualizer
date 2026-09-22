import base64
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

from visual_planner import ConceptRequest, ScenePlan, plan_concept_image


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

# Folder where generated images will be stored.
generated_dir = Path("generated")
generated_dir.mkdir(exist_ok=True)

# Make files in generated/ accessible through /generated/...
app.mount(
    "/generated",
    StaticFiles(directory=generated_dir),
    name="generated",
)


# ---------------------------------------------------------
# Renderer prompt
# ---------------------------------------------------------

def build_renderer_prompt(scene_plan: ScenePlan) -> str:
    """
    Convert the approved ScenePlan into instructions for the image model.

    The Visual Planner has already made the important creative decisions.

    The renderer's job is therefore to EXECUTE the plan faithfully,
    not reinterpret the concept or expand it into a more complex
    real-world scene.
    """

    important_objects = "\n".join(
        f"- {item}"
        for item in scene_plan.important_objects
    )

    avoid_items = "\n".join(
        f"- {item}"
        for item in scene_plan.avoid
    )

    if scene_plan.accent_detail:
        accent_detail = scene_plan.accent_detail
    else:
        accent_detail = "None. Do not invent one."

    prompt = f"""
Create a wide horizontal calendar illustration by faithfully following
the approved visual design below.

The creative planning has already been completed.

Do not reinterpret the underlying event.
Do not try to make the scene more complete or more representative.
Do not add content merely because it is commonly associated with the
subject.

--------------------------------------------------
APPROVED VISUAL IDEA
--------------------------------------------------

Visual idea:
{scene_plan.visual_idea}

Representation strategy:
{scene_plan.representation}

Primary subject:
{scene_plan.subject}

Setting:
{scene_plan.setting or "No specific setting is required."}

Action:
{scene_plan.action or "No specific action is required."}

--------------------------------------------------
APPROVED OBJECTS
--------------------------------------------------

The following objects are explicitly approved for this design:

{important_objects}

These are the important objects for THIS illustration.

Do not add extra objects simply because they are commonly associated
with the event.

--------------------------------------------------
OPTIONAL ACCENT DETAIL
--------------------------------------------------

{accent_detail}

If an accent detail is provided, keep it small and secondary.

If no accent detail is provided, do not invent one.

--------------------------------------------------
DESIGN-SPECIFIC RESTRICTIONS
--------------------------------------------------

The planner specifically asked you to avoid:

{avoid_items}

Treat these as important constraints.

--------------------------------------------------
GLOBAL RENDERING RULES
--------------------------------------------------

Follow the ScenePlan rather than using your own knowledge of what this
kind of event usually looks like.

Do not expand the approved idea into a more comprehensive scene.

Do not add extra people unless the ScenePlan clearly requires them.

Do not add additional narrative actions or interpersonal interactions.

Do not invent relationships between people.

Do not add decorative objects merely to fill empty space.

When depicting a scene or activity involving multiple participants, they may have
ordinary human features such as simple hair shapes.

Keep background content sparse.

Leave comfortable empty space when appropriate.

Do not include readable written words.

Do not include:
- names,
- captions,
- event titles,
- banners,
- signs,
- labels,
- slogans,
- greeting messages.

Numerals or simple symbols may appear only when they are explicitly
required by the ScenePlan itself.

--------------------------------------------------
VISUAL TREATMENT
--------------------------------------------------

Create the illustration as a very wide horizontal banner suitable for
a Google Calendar event.

Keep the main visual idea immediately readable at small size.

Keep important subjects fully inside the frame.

Use a simple, clean, geometric illustration.

Favor:
- clear silhouettes,
- simple shapes,
- restrained detail,
- sparse composition,
- minimal depth,
- limited perspective,
- clean separation between major forms.

Avoid:
- photorealism,
- cinematic rendering,
- complex lighting,
- excessive shading,
- dense backgrounds,
- unnecessary texture,
- dramatic perspective,
- visual clutter.

The final image should feel like one deliberately selected visual idea,
not a complete depiction of everything that could happen at the event.
""".strip()

    return prompt


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/concept/plan")
def plan_concept(request: ConceptRequest):
    scene_plan = plan_concept_image(request)

    return {
        "scene_plan": scene_plan.model_dump()
    }


@app.post("/concept/render")
def render_scene_plan(scene_plan: ScenePlan):

    print("Rendering existing scene plan:")
    print(scene_plan.model_dump_json(indent=2))

    prompt = build_renderer_prompt(scene_plan)

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

    with open(output_path, "wb") as image_file:
        image_file.write(image_bytes)

    image_url = f"http://127.0.0.1:8000/generated/{filename}"

    return {
        "message": "Image generated successfully",
        "filename": filename,
        "file": str(output_path),
        "image_url": image_url,
        "scene_plan": scene_plan.model_dump(),
    }


@app.post("/concept/generate")
def generate_concept(request: ConceptRequest):

    # First let the semantic / visual-planning pipeline decide
    # what the illustration should depict.
    scene_plan = plan_concept_image(request)

    print("Generated scene plan:")
    print(scene_plan.model_dump_json(indent=2))

    # The image model receives only the approved ScenePlan.
    # It should execute the plan rather than redesigning the event.
    prompt = build_renderer_prompt(scene_plan)

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

    with open(output_path, "wb") as image_file:
        image_file.write(image_bytes)

    image_url = f"http://127.0.0.1:8000/generated/{filename}"

    return {
        "message": "Image generated successfully",
        "filename": filename,
        "file": str(output_path),
        "image_url": image_url,
        "scene_plan": scene_plan.model_dump(),
    }