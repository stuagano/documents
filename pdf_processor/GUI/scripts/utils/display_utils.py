# display_utils.py

from PIL import Image, ImageDraw

def display_image_with_boxes(image, boxes, title="Image with Bounding Boxes"):
    """
    Displays the image with bounding boxes.

    Args:
        image (PIL.Image.Image): The image to display.
        boxes (list of tuples): List of bounding boxes (x, y, width, height).
        title (str): Title of the image window.
    """
    draw = ImageDraw.Draw(image)
    for box in boxes:
        x, y, width, height = box
        draw.rectangle([(x, y), (x + width, y + height)], outline="red", width=2)
    image.show(title=title)