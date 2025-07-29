import logging
logger = logging.getLogger(__name__)

import io
import base64
from PIL import Image
from pydantic import BaseModel
import fitz

class PdfReaderArgs(BaseModel):
    file_path: str
    page_range: tuple[int, int] | None = None
    

class PdfReaderFunction():
    def __init__(self, dpi: int = 200):      
        self.dpi = dpi
    
    def __call__(self, **kwargs) -> dict:
        args = PdfReaderArgs(**kwargs)
        
        pdf_doc = fitz.open(args.file_path)
        
        # Check if page range is valid
        start_page, end_page = args.page_range
        if start_page and end_page:
            if start_page < 0 or end_page < 0:
                raise ValueError("Page range must be positive")
            if start_page > end_page:
                raise ValueError("Start page must be less than end page")
            if start_page > len(pdf_doc):
                raise ValueError("Start page is greater than the number of pages in the PDF")
            if end_page > len(pdf_doc):
                raise ValueError("End page is greater than the number of pages in the PDF")
        
            if end_page - start_page > 10:
                end_page = start_page + 10
        else:
            start_page = 0
            end_page = len(pdf_doc)
        
        base64_images = []
        zoom = self.dpi / 72  # 72 is the default DPI for PDFs
        mat = fitz.Matrix(zoom, zoom)
        
        for page_num in range(start_page, end_page):
            page = pdf_doc.load_page(page_num)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            base64_images.append(base64.b64encode(buffer.getvalue()).decode("utf-8"))
        
        return {"text": f"Read pages {start_page} to {end_page} of {len(pdf_doc)} pages in {args.file_path}", "base64_images": base64_images}