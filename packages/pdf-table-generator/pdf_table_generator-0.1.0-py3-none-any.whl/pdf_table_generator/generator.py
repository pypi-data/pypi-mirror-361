from fpdf import FPDF
from typing import List


class TablePDF(FPDF):
    def __init__(
        self,
        title: str = "My PDF Report",
        font_family: str = "Arial",
        header_font_size: int = 14,
        section_font_size: int = 12,
        body_font_size: int = 9,
        orientation='P',
        unit='mm',
        format_type='A4'
    ):
        super().__init__(orientation, unit, format_type)
        self.title = title
        self.font_family = font_family
        self.header_font_size = header_font_size
        self.section_font_size = section_font_size
        self.body_font_size = body_font_size

        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(10, 10, 10)
        self.add_page()

    def header(self):
        self.set_font(self.font_family, "B", self.header_font_size)
        self.cell(0, 10, self.title, ln=True, align="C")
        self.ln(5)

    def section_title(self, title: str):
        self.set_font(self.font_family, "B", self.section_font_size)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def draw_table(self, headers: List[str], data: List[List[str]], col_widths: List[int]):
        assert len(headers) == len(col_widths), "Headers and column widths must match"
        line_height = 6

        self.set_font(self.font_family, "B", self.body_font_size + 1)
        x_start = self.get_x()
        y_start = self.get_y()

        for i, header in enumerate(headers):
            self.set_xy(x_start + sum(col_widths[:i]), y_start)
            self.multi_cell(col_widths[i], line_height, header, border=1, align='C')
        self.ln(line_height)

        self.set_font(self.font_family, "", self.body_font_size)
        for row in data:
            x_start = self.get_x()
            y_start = self.get_y()
            max_height = 0
            for i, cell in enumerate(row):
                num_lines = self.get_string_width(cell) / (col_widths[i] - 1)
                height = (int(num_lines) + 1) * line_height
                max_height = max(max_height, height)

            for i, cell in enumerate(row):
                self.set_xy(x_start + sum(col_widths[:i]), y_start)
                self.multi_cell(col_widths[i], line_height, cell, border=1)

            self.set_y(y_start + max_height)
        self.ln(5)

    def save_pdf(self, filename: str):
        self.output(filename)
        print(f"PDF saved as: {filename}")
