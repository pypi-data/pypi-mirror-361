import os
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, model_validator
from typing import Optional
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor


class ExportMode(Enum):
    CONSOLE = "CONSOLE"
    HTTP = "HTTP"
    GRPC = "GRPC"
    
class InstrumentationParams(BaseModel):
    service_name: str
    export_server_url: Optional[str] = None
    export_server_token: Optional[str] = None
    export_mode: Optional[ExportMode] = ExportMode.HTTP
    extra_instrumentors: Optional[List[BaseInstrumentor]] = []
    enable_logging: Optional[bool] = False

    @model_validator(mode="before")
    def validate_export_mode(cls, values):
        export_server_url = values.get("export_server_url")
        if export_server_url is None:
            values["export_mode"] = ExportMode.CONSOLE
        return values

    # Allow arbitrary types for fields like BaseInstrumentor
    model_config = dict(arbitrary_types_allowed=True)

