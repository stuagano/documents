from PIL import Image, ImageDraw
from PyQt5.QtGui import QImage, QPixmap


def display_image_with_boxes(image, boxes, labels=None):
    """
    Draws bounding boxes on the image for visualization.

    Args:
        image (PIL.Image.Image): The image to draw boxes on.
        boxes (list of tuples): List of bounding boxes (x, y, width, height).
        labels (list of str, optional): Labels for each bounding box.
    """
    draw = ImageDraw.Draw(image)
    for i, box in enumerate(boxes):
        x, y, width, height = box
        draw.rectangle([x, y, x + width, y + height], outline="red", width=2)
        if labels and i < len(labels):
            draw.text((x, y - 10), labels[i], fill="red")
    return image    

def pil_to_pixmap(pil_image):
    """Convert PIL Image to QPixmap."""
    if pil_image.mode == "RGBA":
        qim = QImage(pil_image.tobytes("raw", "RGBA"), pil_image.size[0],
                    pil_image.size[1], QImage.Format_RGBA8888)
    else:
        qim = QImage(pil_image.tobytes("raw", "RGB"), pil_image.size[0],
                    pil_image.size[1], QImage.Format_RGB888)
    return QPixmap.fromImage(qim)
