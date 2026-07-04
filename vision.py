from pathlib import Path
import fitz
from config import UPLOAD_FOLDER

UPLOAD_FOLDER = Path(UPLOAD_FOLDER)
IMAGE_FOLDER = Path("images")

IMAGE_FOLDER.mkdir(exist_ok=True)


def get_uploaded_pdfs():
    """
    Returns all uploaded PDFs.
    """
    return list(UPLOAD_FOLDER.glob("*.pdf"))


def extract_images():
    """
    Extract all images from every uploaded PDF.
    """

    image_paths = []

    for pdf in get_uploaded_pdfs():

        document = fitz.open(pdf)

        for page_no in range(len(document)):

            page = document.load_page(page_no)

            images = page.get_images(full=True)

            for index, image in enumerate(images):

                xref = image[0]

                base_image = document.extract_image(xref)

                image_bytes = base_image["image"]

                extension = base_image["ext"]

                image_path = IMAGE_FOLDER / (
                    f"{pdf.stem}_page{page_no+1}_{index}.{extension}"
                )

                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                image_paths.append(image_path)

    return image_paths