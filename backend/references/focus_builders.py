from __future__ import annotations

from planning.schemas import (
    CandidateScene,
    ReferenceAnnotationSource,
    ReferenceFocus,
    ReferenceMode,
)


def build_art_direction_focus(
    candidate: CandidateScene,
    max_references: int = 6,
) -> ReferenceFocus:
    """
    Build the Stage-B precedent query for an already-curated candidate.

    Candidate identity supplies the precedent targets. Depth and
    cropping are requested as evidence only because the Art Director has
    not decided them yet.
    """

    representation = candidate.representation_strategy.value
    recognition = candidate.recognition_structure.value
    environment = candidate.environment_strategy.value

    return ReferenceFocus(
        stage="art_direction",
        mode=ReferenceMode.precedent,
        annotation_source=ReferenceAnnotationSource.runtime,
        focus_fields=[
            "representation_strategy",
            "recognition_structure",
            "environment_strategy",
            "depth",
            "cropping",
        ],
        purpose=(
            "Find structural precedents for art-directing an existing "
            f"{representation} candidate with {recognition} recognition "
            f"and {environment} environmental context. Inspect how "
            "similar scenes handle depth and cropping without copying "
            "their exact composition."
        ),
        target_values={
            "representation_strategy": representation,
            "recognition_structure": recognition,
            "environment_strategy": environment,
        },
        max_references=max_references,
    )