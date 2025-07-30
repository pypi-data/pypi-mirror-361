"""
Data models for syft-awake network awakeness monitoring.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AwakeStatus(str, Enum):
    """Status of a network member."""
    AWAKE = "awake"
    SLEEPING = "sleeping"
    BUSY = "busy"
    UNKNOWN = "unknown"


class AwakeRequest(BaseModel):
    """Request to check if a user is awake and ready for interaction."""
    
    requester: str = Field(description="Email of the user making the request")
    message: str = Field(default="ping", description="Optional message with the ping")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the request was made"
    )
    priority: str = Field(default="normal", description="Priority level: low, normal, high")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AwakeResponse(BaseModel):
    """Response indicating awakeness status and availability."""
    
    responder: str = Field(description="Email of the user responding")
    status: AwakeStatus = Field(description="Current awakeness status")
    message: str = Field(default="I'm awake!", description="Custom response message")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the response was generated"
    )
    
    # Optional metadata about availability
    available_until: Optional[datetime] = Field(
        default=None,
        description="When the user expects to become unavailable (optional)"
    )
    response_time_ms: Optional[float] = Field(
        default=None,
        description="How long it took to generate this response"
    )
    workload: str = Field(
        default="light",
        description="Current workload: light, moderate, heavy"
    )
    capabilities: Dict[str, Any] = Field(
        default_factory=dict,
        description="What the user can help with right now"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NetworkAwakenessSummary(BaseModel):
    """Summary of network awakeness after pinging multiple users."""
    
    total_pinged: int = Field(description="Total number of users pinged")
    awake_count: int = Field(description="Number of users who responded as awake")
    response_count: int = Field(description="Number of users who responded at all")
    awake_users: list[str] = Field(description="List of awake user emails")
    sleeping_users: list[str] = Field(description="List of sleeping user emails")
    non_responsive: list[str] = Field(description="List of users who didn't respond")
    
    scan_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this network scan was performed"
    )
    scan_duration_ms: float = Field(description="How long the scan took")
    
    @property
    def awakeness_ratio(self) -> float:
        """Ratio of awake users to total pinged users."""
        if self.total_pinged == 0:
            return 0.0
        return self.awake_count / self.total_pinged
    
    @property
    def response_ratio(self) -> float:
        """Ratio of responsive users to total pinged users.""" 
        if self.total_pinged == 0:
            return 0.0
        return self.response_count / self.total_pinged
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }