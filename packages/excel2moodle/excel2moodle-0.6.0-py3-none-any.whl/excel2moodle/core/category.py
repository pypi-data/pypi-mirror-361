import logging
import re
from typing import TYPE_CHECKING

import lxml.etree as ET
import pandas as pd

from excel2moodle.core.settings import Tags

if TYPE_CHECKING:
    from excel2moodle.core.question import Question

loggerObj = logging.getLogger(__name__)


class Category:
    """Category stores a list of question. And holds shared information for all."""

    def __init__(
        self,
        name: str,
        description: str,
        dataframe: pd.DataFrame,
        settings: dict[str, float | str],
    ) -> None:
        """Instantiate a new Category object."""
        self.NAME = name
        match = re.search(r"\d+$", str(self.NAME))
        self.n: int = int(match.group(0)) if match else 99
        self.desc = str(description)
        self.dataframe: pd.DataFrame = dataframe
        self.settings: dict[str, float | str] = settings if settings else {}
        self.questions: dict[int, Question] = {}
        self.maxVariants: int | None = None
        loggerObj.info("initializing Category %s", self.NAME)

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def points(self) -> float:
        return self.settings.get(Tags.POINTS)

    @points.setter
    def points(self, points: float) -> None:
        self.settings[Tags.POINTS] = points

    @property
    def id(self) -> str:
        return f"{self.n:02d}"

    def __hash__(self) -> int:
        return hash(self.NAME)

    def __eq__(self, other: object, /) -> bool:
        if isinstance(other, Category):
            return self.NAME == other.NAME
        return False

    def getCategoryHeader(self) -> ET.Element:
        """Insert an <question type='category'> before all Questions of this Category."""
        header = ET.Element("question", type="category")
        cat = ET.SubElement(header, "category")
        info = ET.SubElement(header, "info", format="html")
        ET.SubElement(cat, "text").text = f"$module$/top/{self.NAME}"
        ET.SubElement(info, "text").text = str(self.desc)
        ET.SubElement(header, "idnumber").text = self.id
        ET.indent(header)
        return header
