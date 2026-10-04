from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# =========================================================
# Input
# =========================================================


class ConceptRequest(BaseModel):
    """
    User-provided concept to visualize.
    """

    name: str
    type: str
    description: str | None = None


# =========================================================
# Shared canonical visual vocabulary
# =========================================================


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


class ReferenceDimension(str, Enum):
    representation_strategy = "representation_strategy"
    recognition_structure = "recognition_structure"
    human_presence = "human_presence"
    environment_strategy = "environment_strategy"
    temporal_focus = "temporal_focus"
    view_angle = "view_angle"
    scale_source = "scale_source"

# =========================================================
# 1. Concept interpretation
# =========================================================


class ConceptBrief(BaseModel):
    """
    Semantic grounding for the event.

    This object describes what the concept means and what is known,
    plausible, open, or protected from invention.

    It must not decide composition, viewpoint, depth, layers, color,
    cropping, or rendering style.
    """

    core_concept: str

    known_details: list[str] = Field(default_factory=list)
    general_associations: list[str] = Field(default_factory=list)
    open_choices: list[str] = Field(default_factory=list)
    protected_unknowns: list[str] = Field(default_factory=list)

    semantic_scope: SemanticScope = SemanticScope.matched_scope

    representation_optionality: RepresentationOptionality = (
        RepresentationOptionality.moderate
    )

    promising_semantic_cues: list[str] = Field(default_factory=list)

    # Annotation dimensions on which reference examples may help the
    # next planning stage.
    reference_dimensions: list[ReferenceDimension] = Field(default_factory=list)


# =========================================================
# 2. Creative candidate planning
# =========================================================


class SceneElement(BaseModel):
    """
    One visible element considered during shallow simulation of a
    candidate scene.
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
    A concrete mental sketch used to test one candidate before full
    art direction.

    It checks recognizability, viewpoint readability, redundancy,
    rough spatial organization, deliberate omissions, and risks.

    Formal scene layers are not planned here.
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

    # Candidate identity that later stages should protect.
    must_preserve: list[str] = Field(default_factory=list)
    may_adjust: list[str] = Field(default_factory=list)


class CandidateScene(BaseModel):
    id: str

    representation_strategy: RepresentationStrategy
    visual_thesis: str
    scene_description: str

    subject: str
    setting: str
    action: str
    human_presence: str

    recognition_structure: RecognitionStructure
    environment_strategy: EnvironmentStrategy


class CandidateScenePool(BaseModel):
    essence_visual_thesis: str
    representation_optionality: RepresentationOptionality
    candidates: list[CandidateScene]
    generation_priority: list[str]


# =========================================================
# 3. Candidate viability + diversity curation
# =========================================================


class ViabilityStatus(str, Enum):
    pass_ = "pass"
    pass_with_manageable_risk = "pass_with_manageable_risk"
    fail = "fail"


class ViabilityGate(BaseModel):
    status: ViabilityStatus
    notes: str = ""


class CandidateAssessment(BaseModel):
    """
    Viability assessment for one candidate scene.
    """

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

    Multiple valid but substantially different candidates may coexist.
    This stage should not impose an overall best-to-worst ranking.
    """

    assessments: list[CandidateAssessment]

    retained_candidate_ids: list[str]
    removed_as_redundant: list[str] = Field(default_factory=list)

    diversity_notes: list[str] = Field(default_factory=list)


# =========================================================
# 4. Reference support
# =========================================================


class ReferenceMode(str, Enum):
    exploratory = "exploratory"
    precedent = "precedent"
    contrast = "contrast"


class ReferenceAnnotationSource(str, Enum):
    runtime = "runtime"
    legacy = "legacy"
    runtime_then_legacy = "runtime_then_legacy"


class ReferenceRecord(BaseModel):
    """
    One image available to the reference system.

    Catalog metadata may exist without study annotations. Rich study
    records and compact runtime annotations are separate sources.
    """

    reference_id: str
    concept: str

    rendered_path: str
    raw_path: str | None = None
    annotation_path: str | None = None

    # Rich research record from study/<reference_id>.json.
    annotation: dict[str, Any] | None = None

    # Compact, human-reviewed runtime annotation using the canonical
    # visual codebook.
    runtime_annotation: dict[str, Any] | None = None


class ReferenceFocus(BaseModel):
    """
    One reference-retrieval question.

    stage records where the query came from.
    mode describes the retrieval objective.
    annotation_source determines which annotation representation may
    be used.

    The reference system supports a creative decision; it does not make
    that decision itself.
    """

    stage: str
    mode: ReferenceMode

    focus_fields: list[str]
    purpose: str

    # Optional annotation values already proposed by the planning stage.
    # Example:
    # {"view_angle": "overhead", "human_presence": "none"}
    target_values: dict[str, Any] = Field(default_factory=dict)

    max_references: int = 3

    annotation_source: ReferenceAnnotationSource = (
        ReferenceAnnotationSource.runtime_then_legacy
    )


class ReferenceMatch(BaseModel):
    """
    One selected reference plus the annotation evidence used during
    retrieval.

    matched_fields is retained for compatibility. It may contain both
    matching target fields and useful non-target evidence fields.
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
    Small, focused packet of visual evidence for one planning question.

    The packet normally contains only a few references rather than the
    full corpus.
    """

    focus: ReferenceFocus
    references: list[ReferenceMatch]
    teaching_notes: list[str] = Field(default_factory=list)


# =========================================================
# 5. Scene structure + layer-aware refinement
# =========================================================


class SceneLayer(BaseModel):
    """
    One meaningful plane in the already-designed scene's spatial or
    recognition structure.

    A layer groups content that functions together at a meaningful
    spatial/semantic level. It is not synonymous with an object, color
    region, or renderer group.

    Several objects may belong to one layer. Conversely, a plain base
    background or support region should not become a layer merely
    because it is visually distinct.

    When two groups occupy effectively the same spatial plane and one
    mainly supports the other, prefer merging them unless separating
    them materially improves the description of depth or recognition.

    Layers are descriptive first. They must not create new content or
    force a preferred layer count.
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
    Spatial organization inferred only after a coherent candidate scene
    already exists.

    layers should be the minimum meaningful decomposition needed to
    describe the scene's depth and recognition structure.

    depth_layer_count is a summary of that decomposition; it must equal
    len(layers). A plain graphic field is not automatically a scene
    layer, and shallow recesses do not automatically require separate
    layers unless they function as meaningfully distinct planes.
    """

    depth_strategy: str
    depth_layer_count: int
    depth_span: str

    perspective_strategy: str
    spatial_coherence: str

    layers: list[SceneLayer]


class LayerTreatment(BaseModel):
    """
    Visual treatment for one already-identified SceneLayer.

    There should be exactly one treatment per SceneLayer. Treatment
    controls attention and specificity; it must not create additional
    scene layers.
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
# Renderer reference evidence
# =========================================================

class FinalScenePlan(BaseModel):
    """
    Complete renderer-independent visual plan produced after candidate
    selection, scene-structure analysis, layer-aware refinement, and
    style-specific art direction.

    It should be specific enough for deterministic prompt compilation
    without requiring another creative planning step.
    """

    # Candidate/style identity.
    candidate_id: str
    style_id: str

    visual_thesis: str
    representation_strategy: RepresentationStrategy
    recognition_structure: RecognitionStructure

    # Scene content.
    subject: str
    setting: str
    action: str

    selected_objects: list[str] = Field(default_factory=list)
    accent_detail: str | None = None

    # View and composition.
    view_angle: str
    framing_scale: str

    composition_structure: str
    visual_weight_distribution: str
    salience_structure: str
    negative_space_strategy: str
    directional_flow: str

    # Scale and frame interaction.
    scale_source: str
    cropping_strength: str
    edge_continuation: str

    # Post-hoc scene structure and layer-specific treatment.
    scene_structure: SceneStructure
    layer_treatments: list[LayerTreatment]

    # Style translation.
    human_direction: str
    color_direction: str
    shape_direction: str
    detail_direction: str
    nonliteral_direction: str

# Preserved candidate constraints.
    content_constraints: list[str] = Field(default_factory=list)
    must_preserve: list[str] = Field(default_factory=list)
    may_adjust: list[str] = Field(default_factory=list)


# =========================================================
# 7. Rendering + critique
# =========================================================


class RenderPrompt(BaseModel):
    """
    Renderer-ready prompt compiled deterministically from a
    FinalScenePlan.
    """

    prompt: str
    reference_image_paths: list[str] = Field(default_factory=list)


class HumanVisualObservation(BaseModel):
    """
    Structured observation of one visible human figure.

    These fields describe what the rendered image actually shows.
    They do not decide by themselves whether the treatment is good
    or bad.
    """

    person_label: str

    face_treatment: Literal[
        "clearly_drawn",
        "simplified",
        "omitted",
        "unclear",
    ]

    body_coverage: Literal[
        "fully_clothed",
        "partially_exposed",
        "substantially_exposed",
        "unclear",
    ]

    exposure_appropriateness: Literal[
        "not_concerning",
        "potentially_awkward",
        "context_needed",
    ]

    anatomy_coherence: Literal[
        "clear",
        "stylized_but_coherent",
        "ambiguous",
        "broken",
    ]

    notes: str = ""


class VisualInspection(BaseModel):
    """
    Style-aware but plan-blind inspection of a rendered image.

    Rendered evidence is recorded before intended scene information
    is revealed.
    """

    overall_impression: str

    visible_strengths: list[str] = Field(
        default_factory=list
    )

    visible_concerns: list[str] = Field(
        default_factory=list
    )

    uncertainties: list[str] = Field(
        default_factory=list
    )

    google_calendar_language_observations: list[str] = Field(
        default_factory=list
    )

    human_observations: list[HumanVisualObservation] = Field(
        default_factory=list
    )


class CritiqueIssue(BaseModel):
    """
    One contextual critique issue.

    origin identifies the earliest pipeline level that probably
    needs to change.
    """

    category: Literal[
        "visual_coherence",
        "real_world_logic",
        "semantic_communication",
        "composition",
        "artistic_interest",
        "google_calendar_style",
        "rendering_language",
        "unintended_implication",
        "complexity",
    ]

    severity: Literal[
        "major",
        "moderate",
        "minor",
    ]

    origin: Literal[
        "render_execution",
        "art_direction",
        "scene_concept",
    ]

    observation: str
    why_it_matters: str
    recommendation: str

    change_type: Literal[
        "required_correction",
        "clarity_improvement",
        "style_improvement",
        "optional_enrichment",
    ]


class PreliminaryCritique(BaseModel):
    """
    Context-aware diagnosis before critique references are retrieved.
    """

    overall_read: str

    strengths: list[str] = Field(
        default_factory=list
    )

    issues: list[CritiqueIssue] = Field(
        default_factory=list
    )

    preserve: list[str] = Field(
        default_factory=list
    )

    visual_hook: str | None = None

    artistic_question: str | None = None

    reference_focus: list[str] = Field(
        default_factory=list
    )


class CritiqueResult(BaseModel):
    """
    Final critique after optional contrastive reference support.
    """

    action: Literal[
        "pass",
        "revise_render",
        "revise_art_direction",
        "reconsider_scene",
    ]

    overall_read: str

    strengths: list[str] = Field(
        default_factory=list
    )

    issues: list[CritiqueIssue] = Field(
        default_factory=list
    )

    preserve: list[str] = Field(
        default_factory=list
    )

    visual_hook: str | None = None

    reference_ids: list[str] = Field(
        default_factory=list
    )

