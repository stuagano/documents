from PIL import Image, ImageDraw
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QLabel, QDialog, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem


def pil2pixmap(pil_image):
    """Converts a PIL Image to a QPixmap."""
    if pil_image.mode == "RGB":
        r, g, b = pil_image.split()
        image = Image.merge("RGB", (b, g, r))
    elif pil_image.mode == "RGBA":
        r, g, b, a = pil_image.split()
        image = Image.merge("RGBA", (b, g, r, a))
    elif pil_image.mode == "L":
        image = pil_image.convert("RGBA")
    image2 = image.convert("RGBA")
    data = image2.tobytes("raw", "RGBA")
    qim = QImage(data, image.size[0], image.size[1], QImage.Format.Format_RGBA8888)
    pixmap = QPixmap.fromImage(qim)
    return pixmap


def display_image_in_label(label, image_path):
    """Displays an image in a QLabel."""
    pixmap = QPixmap(image_path)
    label.setPixmap(pixmap.scaled(label.size()))
    label.show()


def display_image_with_boxes(image, boxes):
    """Displays an image with bounding boxes in a pop-out window."""
    draw = ImageDraw.Draw(image)

    for box_data in boxes.values():
        for box in box_data:
            draw.rectangle(box, outline="red", width=2)

    # Convert PIL Image to QPixmap
    qpixmap = pil2pixmap(image)

    # Create a dialog to display the image
    dialog = QDialog()
    dialog.setWindowTitle("Image with Bounding Boxes")

    # Create a QGraphicsView and scene
    graphics_view = QGraphicsView(dialog)
    scene = QGraphicsScene()
    graphics_view.setScene(scene)

    # Add the image to the scene
    pixmap_item = QGraphicsPixmapItem(qpixmap)
    scene.addItem(pixmap_item)

    # Set the layout
    layout = QVBoxLayout(dialog)
    layout.addWidget(graphics_view)

    # Show the dialog
    dialog.exec()