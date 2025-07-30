"""Interface for dependency manager."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import TypeAlias

import pandas as pd

StaticDataType: TypeAlias = pd.DataFrame | dict[str, Any]


class DependencyManagerInterface(ABC):
    """Interface for dependency manager."""

    _DEPENDENCY_ID: str | None = None

    @property
    def query_parameter(self) -> str:
        """Query parameter."""
        return ""

    @property
    def dependency_id(self) -> str:
        """Dependency id."""
        if self._DEPENDENCY_ID is None:
            msg = f"Class {self.__class__.__name__}.DEPENDENCY_ID not defined."
            raise NotImplementedError(msg)
        return self._DEPENDENCY_ID

    @property
    @abstractmethod
    def data_id(self) -> str:
        """Returns data id.

        Returns:
            str: data id
        """

    @abstractmethod
    def validate(self, data: StaticDataType, **kwargs: object) -> None:
        """Page routing has no validations to do."""
