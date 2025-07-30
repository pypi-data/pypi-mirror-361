"""Spec for defining data from a http connector request."""

import re
from typing import Any

from engineai.sdk.dashboard.dependencies import HttpConnectorDependency
from engineai.sdk.dashboard.dependencies.connectors.http.http_connector_header import (
    HttpConnectorHeader,
)
from engineai.sdk.dashboard.interface import HttpConnectorInterface
from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from ...exceptions import DataInvalidSlugError


class HttpGet(AbstractFactoryLinkItemsHandler, HttpConnectorInterface):
    """Spec for defining data from a http connector request."""

    def __init__(
        self,
        *,
        path: TemplatedStringItem,
        slug: str,
        headers: dict[str, str] | None = None,
        as_dict: bool = False,
    ) -> None:
        """Constructor for HttpGet class.

        Args:
            path: path to the data.
            headers: headers for the request.
            slug: slug of data connector.
            as_dict: flag to return data as dictionary.
        """
        super().__init__()
        self.__path = path
        self.__slug = self.__set_slug(slug)
        self.__dependency = HttpConnectorDependency(
            path=self.__path,
            slug=self.__slug,
            headers=(
                [
                    HttpConnectorHeader(key=key, value=value)
                    for key, value in headers.items()
                ]
                if headers is not None
                else None
            ),
        )
        self.as_dict = as_dict

    @property
    def dependency(self) -> HttpConnectorDependency:
        """Property to get the dependency object."""
        return self.__dependency

    @property
    def slug(self) -> str:
        """Return the slug."""
        return self.__slug

    @staticmethod
    def __set_slug(slug: str) -> str:
        """Set a connector slug."""
        pattern = re.compile("^[a-z0-9-_]+$")

        if (
            pattern.search(slug) is None
            or slug[-1] == "_"
            or not (3 <= len(slug) <= 36)
        ):
            raise DataInvalidSlugError(slug=slug)

        return slug

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return self.__dependency.build()
