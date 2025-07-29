from dataclasses import dataclass

from wowool.portal.client.portal import Portal


@dataclass
class Component:
    name: str
    type: str
    description: str


class Components:
    """
    :class:`Components` is a
    """

    def __init__(self, type: str = "", language: str = "", portal: Portal | None = None):
        self._portal = portal or Portal()
        self.type = type
        self.language = language
        self._components = self.get(type=type, language=language)

    def get(self, type: str = "", language: str = "", **kwargs):
        components_raw: list[dict[str, str]] = self._portal._service.get(
            url="components/",
            json={
                "type": type,
                "language": language,
            },
            **kwargs,
        ).json()
        return [Component(**c) for c in components_raw]

    def __iter__(self):
        return iter(self._components)

    def __len__(self):
        return len(self._components)
