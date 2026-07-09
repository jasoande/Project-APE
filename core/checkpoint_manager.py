"""Pipeline checkpoint and resume capability for client workflows."""

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PipelineCheckpoint:
    """Tracks pipeline execution state for checkpoint/resume."""

    PHASE_ORDER: List[str] = field(default=None, init=False, repr=False)

    client_id: str
    run_id: str
    mode: str
    phase: str
    phase_number: int
    completed_phases: List[str] = field(default_factory=list)
    notebook_id: Optional[str] = None
    consolidated_pdf_path: Optional[str] = None
    industry: Optional[str] = None
    subsegments: Optional[str] = None
    quality_score: Optional[float] = None
    last_update: float = 0.0
    status: str = "in_progress"

    def __post_init__(self):
        self.PHASE_ORDER = [
            "setup_folder",
            "determine_industry",
            "check_auth",
            "create_notebook",
            "consolidate_pdf",
            "run_research",
            "run_chat",
            "generate_mindmap",
        ]


# Module-level constant for external access
PHASE_ORDER = [
    "setup_folder",
    "determine_industry",
    "check_auth",
    "create_notebook",
    "consolidate_pdf",
    "run_research",
    "run_chat",
    "generate_mindmap",
]


class CheckpointManager:
    """Manages saving and loading pipeline checkpoints."""

    def __init__(self, logs_dir: Path, client_id: str, run_id: str):
        self.client_id = client_id
        self.run_id = run_id
        self.checkpoint_dir = logs_dir / ".checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = self.checkpoint_dir / f"{client_id}.json"

    def save(self, checkpoint: PipelineCheckpoint) -> None:
        """Save checkpoint to disk."""
        checkpoint.last_update = time.time()
        data = asdict(checkpoint)
        data.pop("PHASE_ORDER", None)
        try:
            with open(self.checkpoint_file, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"[{self.client_id}] Checkpoint saved: phase={checkpoint.phase}")
        except OSError as e:
            logger.error(f"[{self.client_id}] Failed to save checkpoint: {e}")

    def load(self) -> Optional[PipelineCheckpoint]:
        """Load checkpoint from disk. Returns None if not found."""
        if not self.checkpoint_file.exists():
            return None
        try:
            with open(self.checkpoint_file, "r") as f:
                data = json.load(f)
            return PipelineCheckpoint(**data)
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            logger.warning(f"[{self.client_id}] Failed to load checkpoint: {e}")
            return None
        except OSError as e:
            logger.warning(f"[{self.client_id}] Failed to read checkpoint file: {e}")
            return None

    def should_skip_phase(self, phase_name: str, checkpoint: PipelineCheckpoint) -> bool:
        """Check if a phase has already been completed."""
        return phase_name in checkpoint.completed_phases

    def clear(self) -> None:
        """Delete the checkpoint file."""
        try:
            if self.checkpoint_file.exists():
                self.checkpoint_file.unlink()
                logger.debug(f"[{self.client_id}] Checkpoint cleared")
        except OSError as e:
            logger.warning(f"[{self.client_id}] Failed to clear checkpoint: {e}")
