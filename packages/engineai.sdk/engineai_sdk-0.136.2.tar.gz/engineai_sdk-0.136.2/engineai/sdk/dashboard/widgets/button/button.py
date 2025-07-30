"""Spec for Cartesian widget."""

from typing import Any

import pandas as pd
from typing_extensions import override

from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.widgets.base import Widget

from .external import ExternalAction


class Button(Widget):
    """Spec for Button widget."""

    _DEPENDENCY_ID = "__BUTTON_DATA_DEPENDENCY__"
    _WIDGET_API_TYPE = "button"
    _FLUID_ROW_COMPATIBLE = True

    _DEFAULT_HEIGHT = 0.5
    _FORCE_HEIGHT = True

    def __init__(
        self,
        *,
        action: ExternalAction,
        widget_id: str | None = None,
        icon: TemplatedStringItem | None = None,
        label: TemplatedStringItem | None = None,
    ) -> None:
        """Construct spec for Button widget.

        Args:
            action: Type of action to be performed on the button.
            widget_id: unique widget id in a dashboard.
            icon: icon spec.
            label: label to be displayed in the button.
        """
        super().__init__(widget_id=widget_id)
        self.__icon = icon
        self.__label = label
        self.__action = action

    @override
    def _prepare(self, **_: object) -> None:
        if self.__label is None:
            self.__label = self.__action.event_type

    @override
    def validate(self, data: pd.DataFrame | dict[str, Any], **__: object) -> None:
        """Widget validations. Button has no data to validate."""
        return

    @override
    def _build_widget_input(self) -> dict[str, Any]:
        return {
            "icon": build_templated_strings(items=self.__icon) if self.__icon else None,
            "label": (
                build_templated_strings(items=self.__label) if self.__label else None
            ),
            "action": {"external": self.__action.build()},
        }
