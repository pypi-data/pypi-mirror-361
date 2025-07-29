from dataclasses import dataclass, field
import os
import datetime

@dataclass
class ToolState:
    type: str = "ToolState"
    flow_run_id: str = field(default_factory=lambda: os.environ.get("PREFECT__FLOW_RUN_ID", ""))
    tool_name: str = ""
    step_name: str = ""
    message: str = ""
    total_files: int = 0
    processed_files: int = 0
    current_file_name: str  = ""         
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
