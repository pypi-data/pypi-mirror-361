import os
from mlflow.tracking.context.abstract_context import RunContextProvider

import airadar
from airadar.tracking.mlflow import start_mlflow_tracking
from typing import Dict, Any


class AIRadarRunContextProvider(RunContextProvider):  # type: ignore
    """Provide AIRadar context through plugin system"""

    def __init__(self) -> None:
        self._activated = False

    def in_context(self) -> bool:
        # MLFlow can trigger this plugin multiple times as part of one run
        # To avoid duplicate artifact logging we make sure our plugin only runs once
        if not self._activated:
            start_mlflow_tracking()
            self._activated = True
        return True

    def tags(self) -> Dict[Any, Any]:
        airadar_pipeline_id = os.environ.get("AIRADAR_PIPELINE_ID", "")
        airadar_console_url = os.environ.get(
            "AIRADAR_CONSOLE_URL", "https://dbx-demo.radar.protectai.com/pipelines"
        )
        return {
            "airadar.pipeline_uri": f"{airadar_console_url}/{airadar_pipeline_id}",
            "airadar.version": f"{airadar.__version__}",
        }
