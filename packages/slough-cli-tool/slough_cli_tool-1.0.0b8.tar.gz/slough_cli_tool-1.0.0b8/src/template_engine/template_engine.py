"""Module with the TemplateEngine class for rendering templates."""

from typing import Any

from jinja2 import Template


class TemplateEngine:
    """Class for rendering templates with variables."""

    def __init__(self, context: dict[str, Any]) -> None:
        """Initialize the TemplateEngine with a template string."""
        self._context = context

    def render(self, template_string: str) -> str:
        """Render the template string with the context variables.

        Args:
            template_string: The template string to render.

        Returns:
            str: The rendered template.
        """
        template = Template(template_string)
        return template.render(self._context)
