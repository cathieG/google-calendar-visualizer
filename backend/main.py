from pathlib import Path
from pydantic import BaseModel

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from planning.interpreter import interpret_concept
from planning.creative_planner import plan_candidate_scenes

from planning.schemas import CandidateScene
from planning.schemas import RenderPrompt
from references.curator import curate_references
from references.focus_builders import build_art_direction_focus
from planning.art_director import art_direct_scene
from planning.schemas import (
    ConceptBrief,
    ConceptRequest,
    FinalScenePlan,
    ReferencePacket
)

from references.curator import curate_semantic_references
from references.render_selector import select_renderer_references
from references.render_selector import RendererReferencePacket
from rendering.image_renderer import render_image
from rendering.prompt_compiler import compile_render_prompt

from styles import get_style_profile

load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class ArtDirectDebugRequest(BaseModel):
    candidate: CandidateScene
    reference_packet: ReferencePacket | None = None
    style_id: str = "google_calendar"


class CompileDebugRequest(BaseModel):
    plan: FinalScenePlan
    reference_packet: RendererReferencePacket | None = None
    style_id: str = "google_calendar"


class FullPipelineDebugRequest(BaseModel):
    request: ConceptRequest
    style_id: str = "google_calendar"



# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }

@app.post("/debug/interpret")
def debug_interpret(
    request: ConceptRequest,
):
    return interpret_concept(request)


@app.post("/debug/stage-a")
def debug_stage_a(
    concept_brief: ConceptBrief,
):
    return curate_semantic_references(
        concept_brief
    )


@app.post("/debug/creative-plan")
def debug_creative_plan(
    request: ConceptRequest,
    concept_brief: ConceptBrief,
    reference_packet: ReferencePacket,
):
    return plan_candidate_scenes(
        request=request,
        concept_brief=concept_brief,
        reference_packet=reference_packet,
    )

@app.post("/concept/plan")
def plan_concept(request: ConceptRequest):
    concept_brief = interpret_concept(request)
    reference_packet = curate_semantic_references(
        concept_brief
    )
    candidate_pool = plan_candidate_scenes(
        request=request,
        concept_brief=concept_brief,
        reference_packet=reference_packet,
    )
    return {
        "concept_brief": concept_brief.model_dump(),
        "reference_packet": reference_packet.model_dump(),
        "candidate_pool": candidate_pool.model_dump(),
    }


@app.post("/debug/stage-b")
def debug_stage_b(
    candidate: CandidateScene,
):
    focus = build_art_direction_focus(
        candidate
    )

    reference_packet = curate_references(
        focus
    )

    return {
        "focus": focus.model_dump(),
        "reference_packet": reference_packet.model_dump(),
    }


@app.post("/debug/art-direct")
def debug_art_direct(
    debug_request: ArtDirectDebugRequest,
):
    style_profile = get_style_profile(
        debug_request.style_id
    )

    return art_direct_scene(
        candidate=debug_request.candidate,
        style_profile=style_profile,
        reference_packet=debug_request.reference_packet,
    )


@app.post("/debug/stage-c")
def debug_stage_c(
    plan: FinalScenePlan,
):
    return select_renderer_references(
        plan=plan,
        max_references=6,
    )


@app.post("/debug/compile")
def debug_compile(
    debug_request: CompileDebugRequest,
):
    style_profile = get_style_profile(
        debug_request.style_id
    )

    return compile_render_prompt(
        plan=debug_request.plan,
        style_profile=style_profile,
        reference_packet=debug_request.reference_packet,
    )


@app.post("/debug/render")
def debug_render(
    render_prompt: RenderPrompt,
):
    output_path = render_image(
        render_prompt
    )

    return {
        "message": "Image generated successfully",
        "filename": output_path.name,
        "file": str(output_path),
        "image_url": (
            f"http://127.0.0.1:8000/generated/"
            f"{output_path.name}"
        ),
    }

@app.post("/debug/full-pipeline")
def debug_full_pipeline(
    debug_request: FullPipelineDebugRequest,
):
    """
    Run the complete pipeline for every candidate produced
    by the Creative Planner.

    Shared stages:
    Concept Interpreter
    -> Stage A
    -> Creative Planner

    Then, for every candidate in generation_priority:
    Stage B
    -> Art Director
    -> Stage C
    -> Prompt Compiler
    -> Renderer
    """

    # -----------------------------------------------------
    # 1. Concept Interpreter
    # -----------------------------------------------------

    concept_brief = interpret_concept(
        debug_request.request
    )

    # -----------------------------------------------------
    # 2. Stage A
    # -----------------------------------------------------

    stage_a_packet = curate_semantic_references(
        concept_brief
    )

    # -----------------------------------------------------
    # 3. Creative Planner
    # -----------------------------------------------------

    candidate_pool = plan_candidate_scenes(
        request=debug_request.request,
        concept_brief=concept_brief,
        reference_packet=stage_a_packet,
    )

    # -----------------------------------------------------
    # 4. Load style once
    # -----------------------------------------------------

    style_profile = get_style_profile(
        debug_request.style_id
    )

    # -----------------------------------------------------
    # 5. Index candidates by ID
    # -----------------------------------------------------

    candidates_by_id = {
        candidate.id: candidate
        for candidate in candidate_pool.candidates
    }

    # -----------------------------------------------------
    # 6. Run every available candidate
    #    in generation-priority order
    # -----------------------------------------------------

    candidate_results = []

    for candidate_rank, candidate_id in enumerate(
        candidate_pool.generation_priority,
        start=1,
    ):
        candidate = candidates_by_id.get(
            candidate_id
        )

        if candidate is None:
            raise ValueError(
                f"Generation-priority candidate "
                f"'{candidate_id}' was not found in "
                "candidate_pool.candidates."
            )

        # -------------------------------------------------
        # Stage B
        # -------------------------------------------------

        stage_b_focus = build_art_direction_focus(
            candidate
        )

        stage_b_packet = curate_references(
            stage_b_focus
        )

        # -------------------------------------------------
        # Art Director
        # -------------------------------------------------

        final_scene_plan = art_direct_scene(
            candidate=candidate,
            style_profile=style_profile,
            reference_packet=stage_b_packet,
        )

        # -------------------------------------------------
        # Stage C
        # -------------------------------------------------

        stage_c_packet = select_renderer_references(
            plan=final_scene_plan,
            max_references=6,
        )

        # -------------------------------------------------
        # Prompt Compiler
        # -------------------------------------------------

        render_prompt = compile_render_prompt(
            plan=final_scene_plan,
            style_profile=style_profile,
            reference_packet=stage_c_packet,
        )

        # -------------------------------------------------
        # Renderer
        # -------------------------------------------------

        output_path = render_image(
            render_prompt
        )

        # -------------------------------------------------
        # Save this candidate's complete debug trail
        # -------------------------------------------------

        candidate_results.append(
            {
                "candidate_rank": candidate_rank,
                "candidate_id": candidate_id,
                "candidate": candidate.model_dump(),
                "stage_b_focus": (
                    stage_b_focus.model_dump()
                ),
                "stage_b_references": (
                    stage_b_packet.model_dump()
                ),
                "final_scene_plan": (
                    final_scene_plan.model_dump()
                ),
                "stage_c_references": (
                    stage_c_packet.model_dump()
                ),
                "render_prompt": (
                    render_prompt.model_dump()
                ),
                "image": {
                    "message": (
                        "Image generated successfully"
                    ),
                    "filename": output_path.name,
                    "file": str(output_path),
                    "image_url": (
                        "http://127.0.0.1:8000/"
                        f"generated/{output_path.name}"
                    ),
                },
            }
        )

    # -----------------------------------------------------
    # 7. Return shared planning output
    #    + every candidate branch
    # -----------------------------------------------------

    return {
        "request": (
            debug_request.request.model_dump()
        ),
        "style_id": debug_request.style_id,
        "concept_brief": (
            concept_brief.model_dump()
        ),
        "stage_a_references": (
            stage_a_packet.model_dump()
        ),
        "candidate_pool": (
            candidate_pool.model_dump()
        ),
        "candidate_count": len(
            candidate_pool.generation_priority
        ),
        "candidate_results": candidate_results,
    }