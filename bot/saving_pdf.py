import logging
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def create_pdf_from_text(text: str):
    """Создает PDF-файл из переданного текста."""
    try:
        buffer = BytesIO()
        pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))

        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        c.setFont('DejaVu', 12)

        x = 72
        y = height - 72
        line_height = 14

        lines = text.split('\n')
        for line in lines:
            c.drawString(x, y, line)
            y -= line_height  # Смещаемся вниз для следующей строки
            # Простое добавление новой страницы, если текст не помещается
            if y < 40:
                c.showPage()
                c.setFont('DejaVu', 12)
                y = height - 72

        c.save()
        logging.info("PDF файл успешно создан.")
        buffer.seek(0)
        return buffer
    except Exception as e:
        logging.error(f"Ошибка при создании PDF: {e}")
        return False
