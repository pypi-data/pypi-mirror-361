import functools
import inspect
import logging
import os

from typing import Optional, Any, Dict, Callable
from docstring_parser import parse
from airadar import radar_types
from airadar.radar import RadarPipeline
from airadar.typing.types_utils import (
    is_artifact,
    is_radar_type,
    is_dataset_artifact,
    is_model_artifact,
)


logger = logging.getLogger(__name__)


def pipeline(
    func: Optional[Callable[..., Any]] = None,
    pipeline_id: Optional[str] = os.environ.get("AIRADAR_PIPELINE_ID"),
    external_run_id: Optional[str] = None,
    external_run_uri: Optional[str] = None,
    editable: bool = False,
    return_var_name: Optional[str] = None,
    argument_type_dictionary: Optional[Dict[str, radar_types.BaseType]] = None,
) -> Callable[..., Any]:
    """
    Pipeline function decorator that allow Radar to use the arguments and return value of the function to capture artifact paths.

    Within a decorated function, Radar looks for variables annotated with [radar_types][airadar.typing], using the values
     of these variables as artifact paths. Alternatively to type hints, you can pass a dictionary mapping
     variables names to types. See the examples below.

    Arguments:
        func: Decorated function
        pipeline_id: The uuid of the pipeline obtained from Radar's web dashboard.
        external_run_id: ID for a pipeline run provided by a 3rd party tool (e.g. MLflow or Kubeflow).
        external_run_uri: URI identifying this pipeline run from the platform it ran on.
        editable: To keep pipeline open to log additional artifacts to it, set this to True.
        argument_type_dictionary: You can mark arguments to your decorated function using type dictionary.
        return_var_name: Name of the return variable is used by Radar to give a meaningful name to the artifact returned by decorated function.
    Returns:
        A function with the same signature as the decorated one, but is wrapped with Radar instrumentation

    Examples:

        ```python
        @pipeline
        def training(daily_sales_record: radar_types.Dataset[Path]):
            '''
            :param source: Daily sales record
            '''
            ...
        ```
        Radar use variable names as artifact names and use function docstring (if provided) to
        extract description of the variable. Type hints are used to mark a path as either dataset
        or model.


        In the above example, Radar will log the path to data as input dataset using
        `daily_sales_record` as its name and  `Daily sales record` from docstring as the
        description of this dataset.

        You can also tell Radar about the arguments to the function via an argument dictionary instead
        of using type hints

        ```python
        argument_dict = {
            'source': radar.Dataset,
            'return': radar.Dataset
        }

        @pipeline(argument_type_dictionary=argument_dict)
        def cleaning(source: Path) -> Path:
            # A function that returns a new data frame after performing a cleaning step.
            ....
        ```
    """

    if func is None:
        return functools.partial(
            pipeline,
            pipeline_id=pipeline_id,
            external_run_id=external_run_id,
            external_run_uri=external_run_uri,
            editable=editable,
            argument_type_dictionary=argument_type_dictionary,
            return_var_name=return_var_name,
        )

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if func is None:
            return None

        # TODO: Check if function has multiple decorations.
        all_args = dict(zip(inspect.getfullargspec(func).args, args))
        all_args = {**all_args, **kwargs}
        all_annotations = func.__annotations__
        if argument_type_dictionary:
            all_annotations = {**all_annotations, **argument_type_dictionary}

        func_docstring_params = {}
        try:
            func_docstring = parse(text=func.__doc__ or "")
            func_docstring_params = {
                param.arg_name: param.description for param in func_docstring.params
            }
        except:
            logger.warning(
                f"Failed to parse docstring for func {func.__name__}. Artifact description will be missing"
            )

        radar_obj = RadarPipeline(
            pipeline_id=pipeline_id,
            external_run_uri=external_run_uri,
            external_run_id=external_run_id,
            editable=editable,
        )
        radar_obj.start_run()

        for arg_name, arg_value in all_args.items():
            if arg_name in all_annotations:
                typ = all_annotations[arg_name]
                description = (
                    func_docstring_params[arg_name]
                    if arg_name in func_docstring_params
                    else ""
                )
                _log_artifact(
                    radar_obj,
                    artifact_name=arg_name,
                    typ=typ,
                    value=arg_value,
                    description=description or "",
                )

        value = func(*args, **kwargs)

        # Check the return data path
        if "return" in all_annotations:
            typ = all_annotations["return"]
            description = (
                func_docstring.returns.description
                if func_docstring and func_docstring.returns
                else ""
            )
            _log_artifact(
                radar_obj,
                artifact_name=return_var_name or func.__name__,
                typ=typ,
                value=value,
                description=description or "",
                is_return_value=True,
            )

        radar_obj.finish_run()

        return value

    return wrapper


def _log_artifact(
    radar_obj: RadarPipeline,
    artifact_name: str,
    typ: Any,
    value: Any,
    description: str,
    is_return_value: bool = False,
) -> None:
    if not is_radar_type(typ):
        return

    artifact_type = None
    if is_dataset_artifact(typ):
        artifact_type = radar_types.Dataset
    elif is_model_artifact(typ):
        artifact_type = radar_types.Model
    elif is_artifact(typ):
        artifact_type = radar_types.Artifact

    if artifact_type is None:
        return

    radar_obj.log_artifact(
        uri=value,
        artifact_type=artifact_type,
        name=artifact_name,
        description=description,
    )
