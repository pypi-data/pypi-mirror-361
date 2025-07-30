"""|StoryPart| and related objects."""

from __future__ import annotations

from typing import IO, TYPE_CHECKING, Tuple, cast

from pptx.parts.chart import ChartPart

from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.opc.part import XmlPart
from docx.oxml.shape import CT_Inline
from docx.shared import Length, lazyproperty

from ..oxml.shape import CT_InlineChart

if TYPE_CHECKING:
    from pptx.chart.chart import Chart
    from pptx.chart.data import ChartData
    from pptx.enum.chart import XL_CHART_TYPE

    from docx.enum.style import WD_STYLE_TYPE
    from docx.image.image import Image
    from docx.parts.document import DocumentPart
    from docx.styles.style import BaseStyle


class StoryPart(XmlPart):
    """Base class for story parts.

    A story part is one that can contain textual content, such as the document-part and
    header or footer parts. These all share content behaviors like `.paragraphs`,
    `.add_paragraph()`, `.add_table()` etc.
    """

    def get_or_add_image(self, image_descriptor: str | IO[bytes]) -> Tuple[str, Image]:
        """Return (rId, image) pair for image identified by `image_descriptor`.

        `rId` is the str key (often like "rId7") for the relationship between this story
        part and the image part, reused if already present, newly created if not.
        `image` is an |Image| instance providing access to the properties of the image,
        such as dimensions and image type.
        """
        package = self._package
        assert package is not None
        image_part = package.get_or_add_image_part(image_descriptor)
        rId = self.relate_to(image_part, RT.IMAGE)
        return rId, image_part.image

    def get_style(self, style_id: str | None, style_type: WD_STYLE_TYPE) -> BaseStyle:
        """Return the style in this document matching `style_id`.

        Returns the default style for `style_type` if `style_id` is |None| or does not
        match a defined style of `style_type`.
        """
        return self._document_part.get_style(style_id, style_type)

    def get_style_id(
        self, style_or_name: BaseStyle | str | None, style_type: WD_STYLE_TYPE
    ) -> str | None:
        """Return str style_id for `style_or_name` of `style_type`.

        Returns |None| if the style resolves to the default style for `style_type` or if
        `style_or_name` is itself |None|. Raises if `style_or_name` is a style of the
        wrong type or names a style not present in the document.
        """
        return self._document_part.get_style_id(style_or_name, style_type)

    def new_pic_inline(
        self,
        image_descriptor: str | IO[bytes],
        width: int | Length | None = None,
        height: int | Length | None = None,
    ) -> CT_Inline:
        """Return a newly-created `w:inline` element.

        The element contains the image specified by `image_descriptor` and is scaled
        based on the values of `width` and `height`.
        """
        rId, image = self.get_or_add_image(image_descriptor)
        cx, cy = image.scaled_dimensions(width, height)
        shape_id, filename = self.next_id, image.filename
        return CT_Inline.new_pic_inline(shape_id, rId, filename, cx, cy)

    def _get_or_add_chart(
        self, chart_type: XL_CHART_TYPE, chart_data: ChartData
    ) -> Tuple[str, Chart]:
        """
        Return an (rId, chart) 2-tuple for the chart.
        Access the chart properties like description in python-pptx documents.
        """
        chart_part = ChartPart.new(chart_type, chart_data, self.package)  # type: ignore
        rId = self.relate_to(chart_part, RT.CHART)  # type: ignore
        return rId, chart_part.chart

    def new_chart_inline(
        self, chart_type: XL_CHART_TYPE, cx: Length, cy: Length, chart_data: ChartData
    ) -> tuple[CT_InlineChart, Chart]:
        """
        Return a newly-created `w:inline` element containing the chart
        with width *cx* and height *y*
        """
        rId, chart = self._get_or_add_chart(chart_type, chart_data)
        return CT_InlineChart.new_inline_chart(rId, cx, cy), chart

    @property
    def next_id(self) -> int:
        """Next available positive integer id value in this story XML document.

        The value is determined by incrementing the maximum existing id value. Gaps in
        the existing id sequence are not filled. The id attribute value is unique in the
        document, without regard to the element type it appears on.
        """
        id_str_lst = self._element.xpath("//@id")
        used_ids = [int(id_str) for id_str in id_str_lst if id_str.isdigit()]
        if not used_ids:
            return 1
        return max(used_ids) + 1

    @lazyproperty
    def _document_part(self) -> DocumentPart:
        """|DocumentPart| object for this package."""
        package = self.package
        assert package is not None
        return cast("DocumentPart", package.main_document_part)
