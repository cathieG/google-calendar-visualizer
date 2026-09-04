import base64
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel


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


class ConceptRequest(BaseModel):
    prompt: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/concept/generate")
def generate_concept(request: ConceptRequest):
    result = client.images.generate(
        model="gpt-image-2",
        prompt=request.prompt,
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