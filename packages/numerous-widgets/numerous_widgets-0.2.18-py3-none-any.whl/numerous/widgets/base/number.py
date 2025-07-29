"""Module providing a numeric input widget for the numerous library."""

from typing import Any

import anywidget
import traitlets

from .config import get_widget_paths


# Get environment-appropriate paths
ESM, CSS = get_widget_paths("NumberInputWidget")


class Number(anywidget.AnyWidget):  # type: ignore[misc]
    """
    A widget for selecting a numeric value.

    The selected value can be accessed via the `selected_value` property.

    Args:
        label: The label of the number input.
        tooltip: The tooltip of the number input.
        default: The default value of the number input.
        start: The minimum value allowed.
        stop: The maximum value allowed.
        step: The step size for increments/decrements.
        fit_to_content: Whether to fit the width to the content.
        label_inline: Whether to show the label inline.
        unit: Optional unit label to display after the value.
        strict_validation: Whether to coerce values to limits when focus is lost.

    """

    # Define traitlets for the widget properties
    ui_label = traitlets.Unicode().tag(sync=True)
    ui_tooltip = traitlets.Unicode().tag(sync=True)
    value = traitlets.Float().tag(sync=True)
    start = traitlets.Float().tag(sync=True)
    stop = traitlets.Float().tag(sync=True)
    step = traitlets.Float().tag(sync=True)
    valid = traitlets.Bool().tag(sync=True)
    fit_to_content = traitlets.Bool(default_value=False).tag(sync=True)
    label_inline = traitlets.Bool(default_value=True).tag(sync=True)
    unit = traitlets.Unicode(default_value="").tag(sync=True)  # New traitlet for unit
    strict_validation = traitlets.Bool(default_value=True).tag(
        sync=True
    )  # New traitlet

    # Load the JavaScript and CSS from external files
    _esm = ESM
    _css = CSS

    def __init__(
        self,
        label: str,
        tooltip: str | None = None,
        default: float = 0.0,
        start: float = 0.0,
        stop: float = 100.0,
        step: float = 1.0,
        fit_to_content: bool = False,
        label_inline: bool = True,
        unit: str | None = None,  # New parameter
        strict_validation: bool = True,  # New parameter
    ) -> None:
        # Initialize with keyword arguments
        super().__init__(
            ui_label=label,
            ui_tooltip=tooltip if tooltip is not None else "",
            value=default,
            start=start,
            stop=stop,
            step=step,
            fit_to_content=fit_to_content,
            label_inline=label_inline,
            unit=unit if unit is not None else "",  # Initialize unit
            strict_validation=strict_validation,
        )

    @property
    def selected_value(self) -> float:
        """
        Return the currently selected numeric value.

        Returns:
            float: The currently selected numeric value.

        """
        return float(self.value)

    @property
    def val(self) -> float:
        """
        Return the currently selected numeric value.

        Returns:
            float: The currently selected numeric value.

        """
        return float(self.value)

    @val.setter
    def val(self, value: float) -> None:
        """
        Set the currently selected numeric value.

        Args:
            value: The new value to set.

        """
        self.value = value

    @traitlets.observe("value")  # type: ignore[misc]
    def _validate_value(self, change: dict[str, Any]) -> None:
        self.valid = self.start <= change["new"] <= self.stop
