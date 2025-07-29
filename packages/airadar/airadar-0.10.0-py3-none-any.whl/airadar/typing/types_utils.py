import airadar.typing as radar_types

from typing import Any


def has_annotation_metadata(typ: Any) -> bool:
    if not hasattr(typ, "__metadata__"):
        return False

    return True


def is_input_artifact(typ: Any) -> bool:
    if not has_annotation_metadata(typ):
        return False

    return bool(typ.__metadata__[0] == radar_types.InputAnnotation)


def is_output_artifact(typ: Any) -> bool:
    if not has_annotation_metadata(typ):
        return False

    return bool(typ.__metadata__[0] == radar_types.OutputAnnotation)


def is_dataset_artifact(typ: Any) -> bool:
    if not has_annotation_metadata(typ):
        return False

    return bool(typ.__metadata__[0] == radar_types.DatasetType)


def is_model_artifact(typ: Any) -> bool:
    if not has_annotation_metadata(typ):
        return False

    return bool(typ.__metadata__[0] == radar_types.ModelType)


def is_artifact(typ: Any) -> bool:
    if not has_annotation_metadata(typ):
        return False

    return bool(typ.__metadata__[0] == radar_types.ArtifactType)


def is_radar_type(typ: Any) -> bool:
    if not has_annotation_metadata(typ):
        return False

    all_radar_types = [
        radar_types.InputAnnotation,
        radar_types.OutputAnnotation,
        radar_types.DatasetType,
        radar_types.ModelType,
        radar_types.ArtifactType,
    ]

    return bool(typ.__metadata__[0] in all_radar_types)
