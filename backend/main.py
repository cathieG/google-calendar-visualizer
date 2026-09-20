import base64
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

from visual_planner import ConceptRequest, plan_concept_image

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


# Folder where generated images will be stored
generated_dir = Path("generated")
generated_dir.mkdir(exist_ok=True)

# Make files in generated/ accessible through /generated/...
app.mount(
    "/generated",
    StaticFiles(directory=generated_dir),
    name="generated"
)


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/concept/plan")
def plan_concept(request: ConceptRequest):
    scene_plan = plan_concept_image(request)

    return {
        "scene_plan": scene_plan.model_dump()
    }

@app.post("/concept/generate")
def generate_concept(request: ConceptRequest):

    scene_plan = plan_concept_image(request)

    print("Generated scene plan:")
    print(scene_plan.model_dump_json(indent=2))

    prompt = f"""
    Create an illustration based on the following visual plan.

    Subject:
    {scene_plan.subject}

    Representation:
    {scene_plan.representation}

    Setting:
    {scene_plan.setting or "No specific setting"}

    Action:
    {scene_plan.action or "No specific action"}

    Important objects:
    {", ".join(scene_plan.important_objects)}

    Create this as a very wide horizontal banner for a Google Calendar event.
    Keep the important subjects fully visible within the frame.

    Keep the illustration simple, geometric, flat, and minimal in detail.
    Avoid depth and photorealism.

    Avoid text unless it is genuinely necessary to represent the concept.
    """.strip()

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
    }