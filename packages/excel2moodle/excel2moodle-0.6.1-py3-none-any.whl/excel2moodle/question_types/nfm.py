"""Numerical question multi implementation."""

from types import UnionType
from typing import ClassVar

import lxml.etree as ET

from excel2moodle.core.globals import (
    Tags,
    XMLTags,
)
from excel2moodle.core.parser import QuestionParser
from excel2moodle.core.question import ParametricQuestion, Parametrics


class NFMQuestion(ParametricQuestion):
    nfmMand: ClassVar[dict[Tags, type | UnionType]] = {
        Tags.RESULT: str,
        Tags.BPOINTS: str,
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.answerElement: ET.Element

    def getUpdatedElement(self, variant: int = 1) -> ET.Element:
        """Update and get the Question Elements to reflect the version.

        `NFMQuestion` updates the answer Elements.
        `ParametricQuestion` updates the bullet points.
        `Question` returns the Element.
        """
        result = self.parametrics.getResult(variant)
        tolerance = round(self.rawData.get(Tags.TOLERANCE) * result, 3)
        self.answerElement.find(XMLTags.TEXT).text = str(result)
        self.answerElement.find(XMLTags.TOLERANCE).text = str(tolerance)
        return super().getUpdatedElement(variant)


class NFMQuestionParser(QuestionParser):
    def __init__(self) -> None:
        super().__init__()
        self.genFeedbacks = [XMLTags.GENFEEDB]
        self.question: NFMQuestion

    def setup(self, question: NFMQuestion) -> None:
        self.question: NFMQuestion = question
        super().setup(question)
        module = self.settings.get(Tags.IMPORTMODULE)
        if module and Parametrics.astEval.symtable.get(module, None) is None:
            Parametrics.astEval(f"import {module}")
            imported = Parametrics.astEval.symtable.get(module)
            self.logger.warning("Imported '%s' to Asteval symtable.", module)

    def _parseAnswers(self) -> list[ET.Element]:
        variables = self.question.bulletList.getVariablesDict(self.question)
        self.question.parametrics = Parametrics(
            self.rawInput.get(Tags.EQUATION),
            self.rawInput.get(Tags.FIRSTRESULT),
            self.question.id,
        )
        self.question.parametrics.variables = variables
        self.question.answerElement = self.getNumericAnsElement()
        return [self.question.answerElement]

    # TODO: @jbosse3: Implement a new _setVariants() method, to show in treewidget
    # def _setVariants(self, number: int) -> None:
    #     self.question.variants = number
    #     mvar = self.question.category.maxVariants
    #     if mvar is None:
    #         self.question.category.maxVariants = number
    #     else:
    #         self.question.category.maxVariants = min(number, mvar)
