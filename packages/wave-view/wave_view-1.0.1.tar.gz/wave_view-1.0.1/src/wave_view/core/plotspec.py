"""
Pydantic-based plot specification models.

This module provides PlotSpec and YAxisSpec classes that replace PlotConfig
with structured validation and type safety.
"""

from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import yaml
import numpy as np
from pydantic import BaseModel, Field, ConfigDict
import plotly.graph_objects as go


class XAxisSpec(BaseModel):
    """X-axis configuration specification."""
    signal: str = Field(..., description="X-axis signal key")
    label: Optional[str] = Field(None, description="X-axis label")
    log_scale: bool = Field(False, description="Use logarithmic scale")
    unit: Optional[str] = Field(None, description="Unit for display")
    range: Optional[List[float]] = Field(None, description="[min, max] range")


class YAxisSpec(BaseModel):
    """Y-axis configuration specification."""
    label: str = Field(..., description="Y-axis label")
    signals: Dict[str, str] = Field(..., description="Legend name -> signal key mapping")
    log_scale: bool = Field(False, description="Use logarithmic scale")
    unit: Optional[str] = Field(None, description="Unit for display")
    range: Optional[List[float]] = Field(None, description="[min, max] range")
    color: Optional[str] = Field(None, description="Axis color")


class PlotSpec(BaseModel):
    """
    Pydantic-based plot specification with fluent API.
    
    Replaces PlotConfig with structured validation and composable workflow.
    """
    # Core configuration
    # Accept both lowercase (preferred) and uppercase aliases for backward compatibility
    x: XAxisSpec = Field(..., description="X-axis configuration", alias="X")
    y: List[YAxisSpec] = Field(..., description="Y-axis specifications", alias="Y")
    title: Optional[str] = Field(None, description="Plot title")
    
    # Styling options
    width: Optional[int] = Field(None, description="Plot width in pixels")
    height: Optional[int] = Field(None, description="Plot height in pixels")
    theme: Optional[str] = Field("plotly", description="Plot theme")
    
    # Title positioning
    title_x: float = Field(0.5, description="Title x position (0=left, 0.5=center, 1=right)")
    title_xanchor: str = Field("center", description="Title anchor: left, center, right")
    
    # Advanced options
    show_legend: bool = Field(True, description="Show legend")
    grid: bool = Field(True, description="Show grid")
    zoom_buttons: bool = Field(True, description="Show zoom control buttons")
    zoom_buttons_x: float = Field(0.05, description="Zoom buttons X position (0=left, 1=right)")
    zoom_buttons_y: float = Field(1.05, description="Zoom buttons Y position (1=top of plot)")
    show_rangeslider: bool = Field(True, description="Show range slider below X-axis")
    
    # Pydantic model configuration
    model_config = ConfigDict(populate_by_name=True, extra="allow")
    
    # Factory methods
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'PlotSpec':
        """Create PlotSpec from YAML string."""
        try:
            config_dict = yaml.safe_load(yaml_str)
            if isinstance(config_dict, list):
                raise ValueError("Multi-figure configurations not supported")
            return cls.model_validate(config_dict)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'PlotSpec':
        """
        Create PlotSpec from YAML file.
        
        Args:
            file_path: Path to YAML configuration file
            
        Returns:
            PlotSpec instance
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If YAML is invalid or unsupported
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            yaml_content = file_path.read_text(encoding='utf-8')
            return cls.from_yaml(yaml_content)
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {file_path}: {e}")
    
    # Configuration export methods
    def to_dict(self) -> Dict[str, Any]:
        """
        Export clean configuration dictionary for v1.0.0 plotting functions.
        
        Returns:
            Dict containing clean configuration suitable for standalone plotting functions
        """
        return {
            "title": self.title,
            "x": {
                "signal": self.x.signal,
                "label": self.x.label,
                "log_scale": self.x.log_scale,
                "unit": self.x.unit,
                "range": self.x.range
            },
            "y": [
                {
                    "label": y_spec.label,
                    "signals": y_spec.signals,
                    "log_scale": y_spec.log_scale,
                    "unit": y_spec.unit,
                    "range": y_spec.range,
                    "color": y_spec.color
                }
                for y_spec in self.y
            ],
            "width": self.width,
            "height": self.height,
            "theme": self.theme,
            "title_x": self.title_x,
            "title_xanchor": self.title_xanchor,
            "show_legend": self.show_legend,
            "grid": self.grid,
            "zoom_buttons": self.zoom_buttons,
            "zoom_buttons_x": self.zoom_buttons_x,
            "zoom_buttons_y": self.zoom_buttons_y,
            "show_rangeslider": self.show_rangeslider
        } 