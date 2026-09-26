from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# =========================================================
# Input and concept interpretation
# =========================================================

class ConceptRequest(BaseModel):
    name: str
    type: str
    description: str | None = None


class RepresentationOptionality(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"


class RepresentationStrategy(str, Enum):
    human_action_scene = "human_action_scene"
    human_object_interaction = "human_object_interaction"
    multi_person_interaction = "multi_person_interaction"
    occupational_figure = "occupational_figure"
    object_centered_scene = "object_centered_scene"
    symbolic_object_composition = "symbolic_object_composition"
    iconic_object_collage = "iconic_object_collage"
    prepared_environment = "prepared_environment"
    environment_led_scene = "environment_led_scene"
    decorative_atmosphere_scene = "decorative_atmosphere_scene"


class RecognitionStructure(str, Enum):
    concentrated = "concentrated"
    dominant_anchor_with_support = "dominant_anchor_with_support"
    distributed_symbolic = "distributed_symbolic"
    distributed_functional = "distributed_functional"
    distributed_iconic = "distributed_iconic"
    distributed_narrative = "distributed_narrative"
    relational = "relational"
    contextual = "contextual"
    mixed = "mixed"


class SemanticScope(str, Enum):
    matched_scope = "matched_scope"
    narrowed_instance = "narrowed_instance"
    broader_neighboring_domain = "broader_neighboring_domain"
    mixed_breadth = "mixed_breadth"
    uncertain = "uncertain"


class EnvironmentStrategy(str, Enum):
    omitted = "omitted"
    abstract = "abstract"
    partial_context = "partial_context"
    semantic_environment = "semantic_environment"
    simplified_literal = "simplified_literal"
    narrative_environment = "narrative_environment"


class ConceptBrief(BaseModel):
    """
    Semantic grounding for the event.

    This stage must not decide composition, viewpoint, depth,
    layers, color, cropping, or rendering style.
    """

    core_concept: str

    known_details: list[str] = Field(default_factory=list)
    general_associations: list[str] = Field(default_factory=list)
    open_choices: list[str] = Field(default_factory=list)
    protected_unknowns: list[str] = Field(default_factory=list)

    semantic_scope: SemanticScope = SemanticScope.matched_scope
    recognition_specificity: str = "moderate"

    representation_optionality: RepresentationOptionality = (
        RepresentationOptionality.moderate
    )

    promising_semantic_cues: list[str] = Field(default_factory=list)

    # Annotation dimensions for which examples may help
    # the next planning stage.
    reference_dimensions: list[str] = Field(default_factory=list)


# =========================================================
# Creative candidate + shallow scene simulation
# =========================================================

class SceneElement(BaseModel):
    """
    One visible element considered while mentally simulating
    a candidate scene.
    """

    name: str
    semantic_role: str

    viewpoint_readability: Literal[
        "high",
        "moderate",
        "low",
        "uncertain",
    ]

    semantic_redundancy: Literal[
        "low",
        "moderate",
        "high",
        "unknown",
    ] = "unknown"

    keep: bool = True
    notes: str = ""


class SceneSimulation(BaseModel):
    """
    A concrete mental sketch of the candidate before
    full art direction.

    The planner tests:
    - recognizability,
    - viewpoint readability,
    - semantic redundancy,
    - rough spatial organization,
    - deliberate omissions.

    Layers are NOT planned here.
    """

    visual_thesis: str
    view_angle: str

    primary_recognition_anchor: str
    supporting_recognition_cues: list[str] = Field(default_factory=list)

    scene_elements: list[SceneElement] = Field(default_factory=list)

    rough_layout: str
    deliberate_omissions: list[str] = Field(default_factory=list)

    design_risks: list[str] = Field(default_factory=list)
    renderer_risks: list[str] = Field(default_factory=list)

    # Protect the identity of this candidate during later refinement.
    must_preserve: list[str] = Field(default_factory=list)
    may_adjust: list[str] = Field(default_factory=list)


class CandidateScene(BaseModel):
    """
    One coherent visual direction.

    The scene should be imagined first; annotation fields
    formalize that idea rather than generate it mechanically.
    """

    id: str
    visual_thesis: str

    representation_strategy: RepresentationStrategy
    recognition_structure: RecognitionStructure

    subject: str
    setting: str
    action: str

    human_presence: str
    environment_strategy: EnvironmentStrategy
    semantic_scope: SemanticScope

    accent_detail: str | None = None
    content_constraints: list[str] = Field(default_factory=list)

    simulation: SceneSimulation


# =========================================================
# Candidate viability + diversity curation
# =========================================================

class ViabilityStatus(str, Enum):
    pass_ = "pass"
    pass_with_manageable_risk = "pass_with_manageable_risk"
    fail = "fail"


class ViabilityGate(BaseModel):
    status: ViabilityStatus
    notes: str = ""


class CandidateAssessment(BaseModel):
    candidate_id: str

    semantic_legitimacy: ViabilityGate
    recognition_sufficiency: ViabilityGate
    scene_coherence: ViabilityGate
    calendar_format_feasibility: ViabilityGate
    style_grammar_compatibility: ViabilityGate
    independence_from_explanation: ViabilityGate

    overall_status: ViabilityStatus

    refinement_requests: list[str] = Field(default_factory=list)
    failure_reasons: list[str] = Field(default_factory=list)


class CandidateCuration(BaseModel):
    """
    Result of viability filtering followed by diversity curation.

    Valid but substantially different candidates may coexist.
    This stage should not force an overall best-to-worst ranking.
    """

    assessments: list[CandidateAssessment]

    retained_candidate_ids: list[str]
    removed_as_redundant: list[str] = Field(default_factory=list)

    diversity_notes: list[str] = Field(default_factory=list)


# =========================================================
# Reference support
# =========================================================

class ReferenceMode(str, Enum):
    exploratory = "exploratory"
    precedent = "precedent"
    contrast = "contrast"


class ReferenceFocus(BaseModel):
    """
    Describes the visual-design question for which references
    should be retrieved.

    The reference system supports the planning framework;
    it does not make the creative decision itself.
    """

    stage: str
    mode: ReferenceMode

    focus_fields: list[str]
    purpose: str

    # Optional annotation values already proposed by the planner.
    # Example:
    # {"view_angle": "overhead", "human_presence": "none"}
    target_values: dict[str, Any] = Field(default_factory=dict)

    max_references: int = 3


class ReferenceMatch(BaseModel):
    """
    One selected precedent from the annotated reference corpus.
    """

    reference_id: str
    concept: str

    image_path: str

    matched_fields: dict[str, Any] = Field(default_factory=dict)

    teaching_focus: str = ""
    contrast_note: str | None = None

    score: float = 0.0


class ReferencePacket(BaseModel):
    """
    Small, focused set of visual examples for one planning decision.

    Normally contains 2-4 references, rather than the whole corpus.
    """

    focus: ReferenceFocus

    references: list[ReferenceMatch]

    teaching_notes: list[str] = Field(default_factory=list)


# =========================================================
# Scene structure + layer-aware refinement
# =========================================================

class SceneLayer(BaseModel):
    """
    One meaningful visual plane discovered from an already-designed
    candidate scene.

    Layers are descriptive first: do not invent content merely
    to satisfy a desired layer count.
    """

    index: int
    role: str
    contents: list[str] = Field(default_factory=list)

    semantic_priority: Literal[
        "primary",
        "supporting",
        "tertiary",
    ]

    notes: str = ""


class SceneStructure(BaseModel):
    """
    Spatial organization inferred after the candidate scene exists.
    """

    depth_strategy: str
    depth_layer_count: int
    depth_span: str

    perspective_strategy: str
    spatial_coherence: str

    layers: list[SceneLayer]


class LayerTreatment(BaseModel):
    """
    Visual treatment applied after layer analysis.
    """

    layer_index: int

    detail_priority: Literal[
        "highest",
        "high",
        "moderate",
        "reduced",
        "minimal",
    ]

    contrast_priority: Literal[
        "strong",
        "moderate",
        "quiet",
    ]

    color_role: str
    shape_specificity: str

    notes: str = ""


# =========================================================
# Final art-direction plan
# =========================================================

class FinalScenePlan(BaseModel):
    """
    Complete structured visual plan produced after:
    - candidate selection,
    - scene-structure analysis,
    - layer-aware refinement,
    - full style-specific art direction.
    """

    candidate_id: str
    style_id: str

    visual_thesis: str

    representation_strategy: RepresentationStrategy
    recognition_structure: RecognitionStructure

    subject: str
    setting: str
    action: str

    selected_objects: list[str] = Field(default_factory=list)
    accent_detail: str | None = None

    view_angle: str
    framing_scale: str

    composition_structure: str
    visual_weight_distribution: str
    salience_structure: str
    negative_space_strategy: str
    directional_flow: str

    scale_source: str
    cropping_strength: str
    edge_continuation: str

    scene_structure: SceneStructure
    layer_treatments: list[LayerTreatment]

    human_direction: str
    color_direction: str
    shape_direction: str
    detail_direction: str
    nonliteral_direction: str

    content_constraints: list[str] = Field(default_factory=list)

    must_preserve: list[str] = Field(default_factory=list)
    may_adjust: list[str] = Field(default_factory=list)


# =========================================================
# Rendering + critique
# =========================================================

class RenderPrompt(BaseModel):
    """
    Renderer-ready prompt compiled deterministically from FinalScenePlan.
    """

    prompt: str
    reference_image_paths: list[str] = Field(default_factory=list)


class CritiqueResult(BaseModel):
    decision: Literal["pass", "revise"]

    fix: list[str] = Field(default_factory=list)
    preserve: list[str] = Field(default_factory=list)


class ReferenceRecord(BaseModel):
    """
    One image available to the reference system.

    Every catalog image can exist without a detailed study annotation.
    Rich annotation data is attached when available.
    """

    reference_id: str
    concept: str

    rendered_path: str
    raw_path: str | None = None
    annotation_path: str | None = None

    annotation: dict[str, Any] | None = None


class CandidateScenePool(BaseModel):
    """
    Divergent set of independently viable visual directions produced
    before candidate curation.

    These candidates are alternatives, not a best-to-worst ranking.
    """

    candidates: list[CandidateScene]
