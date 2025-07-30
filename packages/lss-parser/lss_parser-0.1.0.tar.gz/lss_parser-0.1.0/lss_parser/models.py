"""
Data models for LiveSplit LSS files.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Time(BaseModel):
    """Represents a time entry with optional RealTime, GameTime, and PauseTime."""
    real_time: Optional[str] = None
    game_time: Optional[str] = None
    pause_time: Optional[str] = None
    
    @field_validator('real_time', 'game_time', 'pause_time', mode='before')
    def ensure_string_or_none(cls, v):
        """Ensure times are strings or None."""
        if v is not None and not isinstance(v, str):
            return str(v)
        return v


class SplitTime(BaseModel):
    """Represents a split time with name and time data."""
    name: str
    time: Time = Field(default_factory=Time)


class SegmentTime(BaseModel):
    """Represents a time entry in segment history with ID and time data."""
    id: str
    time: Time = Field(default_factory=Time)


class Segment(BaseModel):
    """Represents a segment (split) in the run."""
    name: str
    icon: str = ""
    split_times: List[SplitTime] = Field(default_factory=list)
    best_segment_time: Time = Field(default_factory=Time)
    segment_history: List[SegmentTime] = Field(default_factory=list)


class Attempt(BaseModel):
    """Represents an attempt in the run history."""
    id: str
    started: Optional[str] = None
    is_started_synced: bool = True
    ended: Optional[str] = None
    is_ended_synced: bool = True
    time: Time = Field(default_factory=Time)


class Metadata(BaseModel):
    """Represents metadata about the run."""
    run_id: str = ""
    platform: str = ""
    platform_uses_emulator: bool = False
    region: str = ""
    variables: Dict[str, str] = Field(default_factory=dict)
    custom_variables: Dict[str, str] = Field(default_factory=dict)


class AutoSplitterSettings(BaseModel):
    """Represents auto splitter settings."""
    auto_reset: bool = True
    set_high_priority: bool = True
    set_game_time: bool = True
    file_time_offset: bool = False
    splits: List[str] = Field(default_factory=list)


class Run(BaseModel):
    """Represents a complete LiveSplit run."""
    version: str = "1.7.0"
    game_name: str = ""
    category_name: str = ""
    layout_path: str = ""
    game_icon: str = ""
    metadata: Metadata = Field(default_factory=Metadata)
    offset: str = "00:00:00"
    attempt_count: int = 0
    attempt_history: List[Attempt] = Field(default_factory=list)
    segments: List[Segment] = Field(default_factory=list)
    auto_splitter_settings: AutoSplitterSettings = Field(default_factory=AutoSplitterSettings)

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True
    )