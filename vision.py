import fitz
from config import PROJECT_ROOT, UPLOAD_FOLDER

IMAGE_FOLDER = PROJECT_ROOT / "images"

IMAGE_FOLDER.mkdir(parents=True, exist_ok=True)


def get_uploaded_pdfs():
    """
    Returns all uploaded PDFs.
    """
    if not UPLOAD_FOLDER.is_dir():
        return []

    return [
        path
        for path in UPLOAD_FOLDER.iterdir()
        if path.is_file() and path.suffix.lower() == ".pdf"
    ]


def extract_images():
    """
    Extract all images from every uploaded PDF.
    """

    image_paths = []

    for pdf in get_uploaded_pdfs():

        with fitz.open(pdf) as document:
            for page_no in range(len(document)):
                page = document.load_page(page_no)
                for index, image in enumerate(page.get_images(full=True)):
                    xref = image[0]
                    base_image = document.extract_image(xref)
                    extension = base_image["ext"]
                    image_path = IMAGE_FOLDER / (
                        f"{pdf.stem}_page{page_no + 1}_{index}.{extension}"
                    )

                    with open(image_path, "wb") as image_file:
                        image_file.write(base_image["image"])

                    image_paths.append(image_path)

    return image_paths