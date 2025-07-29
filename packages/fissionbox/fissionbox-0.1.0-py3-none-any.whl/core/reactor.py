from pydantic import BaseModel, Field
from typing import List, Optional, Union
from enum import Enum


class DetectionTaskType(str, Enum):
    """
    Enum representing the type of detection task.
    """

    OBJECT_DETECTION = "object_detection"
    # IMAGE_CLASSIFICATION = "image_classification"
    # INSTANCE_SEGMENTATION = "instance_segmentation"
    # KEYPOINT_DETECTION = "keypoint_detection"


class DetectionTaskGoal(BaseModel):
    """
    Represents a goal for a detection task
    the reason for the task, and the prompt to guide the detection process.
    Attributes:
        reason (str): The reason for the detection task, providing context or motivation.
        prompt (str): The prompt that guides the detection process, specifying what to look for in the image.
        type (DetectionTaskType): The type of detection task, defaulting to OBJECT_DETECTION.

    Example:
    ```python
    goal = DetectionTaskGoal(
        reason="Identify red bottle objects in the image for inventory management.",
        prompt="Find all items that are red and square-shaped."
        type=DetectionTaskType.OBJECT_DETECTION
        label="red_bottle"
    )
    ```
    """

    reason: str
    prompt: str
    type: DetectionTaskType = DetectionTaskType.OBJECT_DETECTION
    label: str

    class Config:  
        use_enum_values = True 


class Reactor(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="The unique identifier for the reactor.",
    )
    name: str = Field(
        ...,
        description="The name of the reactor to be created.",
        pattern=r"^[a-zA-Z0-9_\-]{1,100}$",
    )
    description: Optional[str] = Field(
        default=None,
        description="A brief description of the reactor.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="A list of tags associated.",
    )
    goals: list[DetectionTaskGoal] = Field(
        default_factory=list,
        description="A list of goals for the reactor, defining the tasks it should perform.",
        min_length=1,
        max_length=10,
        example=[
            {
                "reason": "Identify objects in the image for inventory management.",
                "prompt": "Find all items that are red and square-shaped.",
                "type": "object_detection",
                "label": "red_bottle"
            }
        ],
    )

    @classmethod
    def bootstrap(cls, data: dict) -> "Reactor":
        """
        Bootstrap a Reactor instance from a dictionary.
        
        Args:
            data (dict): The data to bootstrap the Reactor instance from.
        
        Returns:
            Reactor: A Reactor instance populated with the provided data.
        """
        goals = [
            DetectionTaskGoal(**goal) for goal in data.get("attributes", {}).get("goals", [])
        ]
        del data["attributes"]["goals"]
        return Reactor(
            id=data.get("id"),
            goals=goals,
            **data["attributes"],  # type: ignore[call-arg]  # noqa: E501
        )
