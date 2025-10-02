from __future__ import annotations
from abc import ABC, abstractmethod

class AIModelBase(ABC):
    """Abstract base class for AI model implementations using the Template Method pattern."""
    
    def __init__(self, model_id: str, task: str) -> None:
        """Initialize the AI model with identifier and task type."""
        # Store model identifier (e.g., "bert-base-uncased")
        self._model_id = model_id
        # Store task type (e.g., "text-classification", "summarization")
        self._task = task
        # Private pipeline object, initialized as None (lazy loading pattern)
        self.__pipeline = None
    
    @property
    def model_id(self) -> str: 
        """Get the model identifier."""
        return self._model_id
    
    @property
    def task(self) -> str: 
        """Get the task type."""
        return self._task
    
    def _set_pipeline(self, pipe) -> None: 
        """Set the pipeline object (protected method for subclasses)."""
        self.__pipeline = pipe
    
    def _get_pipeline(self):
        """Get the pipeline object, raises error if not initialized yet."""
        # Check if pipeline has been initialized
        if self.__pipeline is None: 
            raise RuntimeError("Pipeline not initialised.")
        return self.__pipeline
    
    @abstractmethod
    def run(self, input_data): 
        #Abstract method - subclasses must implement the model execution logic.
        ...
    
    def info(self) -> str: 
        #Return a formatted string with model information.
        return f"Model: {self._model_id} | Task: {self._task}"