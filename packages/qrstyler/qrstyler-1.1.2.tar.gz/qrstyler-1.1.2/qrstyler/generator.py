from PIL import Image, ImageDraw
import os
import qrcode
from typing import Optional
from .themes import ThemesEnum, THEMES_DICT, DEFAULT_COLOR
from dataclasses import dataclass


# from qrgenerator.process import ProcessQRCode

"""
QR Code Generator Module

This module provides the QRGenerator class for generating customizable QR codes with optional theming and logo embedding.

Classes:
    QRConfig: Dataclass for configuring QR code generation options (version, logo, theme, colors, etc).
    QRGenerator: Main class for generating QR codes using the provided configuration.

Usage Example:
    config = QRConfig(version=4, show_logo=True, logo_path="tests/python.webp", show_theme=True)
    generator = QRGenerator(config)
    generator.generate_qr_code("https://example.com", output_file="output.png")
"""

@dataclass
class QRConfig:
    """
    Configuration dataclass for QRGenerator.

    Attributes:
        version (int): QR code version (size/complexity).
        show_logo (bool): Whether to embed a logo in the QR code.
        logo_path (Optional[str]): Path to a custom logo image file.
        show_theme (bool): Whether to apply a color theme to the QR code.
        color_positiond_detection_corners (bool): Whether to color the finder patterns (corners).
        box_size (int): Size of each QR code box (pixel size).
        border (int): Border size (in boxes).
        theme (str): Theme name or enum value for color and logo.
        custom_finder_pattern_color (Optional[str]): Custom color for finder patterns.
        custom_theme_color (Optional[str]): Custom color for the QR code body.
    """
    version: int = 1
    show_logo: bool = False
    logo_path: Optional[str] = None
    show_theme: bool = False
    color_positiond_detection_corners: bool = False
    box_size: int = 10
    border: int = 1
    theme: str = ThemesEnum.DEFAULT
    custom_finder_pattern_color: Optional[str] = None
    custom_theme_color: Optional[str] = None

class QRGenerator:
    """
    Generates QR codes with optional theming and logo embedding.

    Use a QRConfig object to specify all options for QR code generation.
    """
    def __init__(self, config: QRConfig):
        """
        Initialize the QRGenerator with a configuration object.

        Args:
            config (QRConfig): Configuration for QR code generation.
        """
        self.config = config
        self.version = config.version
        self.error_correction = qrcode.ERROR_CORRECT_L
        self.box_size = config.box_size
        self.border = max(1, config.border)
        self.theme = THEMES_DICT.get(config.theme, THEMES_DICT[ThemesEnum.DEFAULT])
        self.show_logo = config.show_logo
        self.show_theme = config.show_theme
        self.color_positiond_detection_corners = config.color_positiond_detection_corners
        self.size = 0
        self.matrix = [[]]
        self.logo = config.logo_path if config.logo_path else self.theme.get("logo", None)
        self.custom_finder_pattern_color = config.custom_finder_pattern_color
        self.custom_theme_color = config.custom_theme_color

    def generate_qr_code(self, data, output_file = None):
        """
        Generate a QR code image from the provided data.

        Args:
            data (str): The data to encode in the QR code.
            output_file (Optional[str]): If provided, saves the QR code image to this file.

        Returns:
            PIL.Image.Image: The generated QR code image (if output_file is None).
        """
        basic_qr_code_image, basic_qr_code_draw = self.__get_base_qrcode(data = data)
        basic_qr_code_draw = self.__apply_theme(basic_qr_code_draw)
        qrcode_with_logo = self.__apply_logo(basic_qr_code_image)
        if output_file is not None:
            qrcode_with_logo.save(output_file)
        else:
            return qrcode_with_logo
    


    def __get_base_qrcode(self, data):
        """
        Create a basic QR code image and drawing context from the input data.

        Args:
            data (str): The data to encode in the QR code.

        Returns:
            Tuple[PIL.Image.Image, PIL.ImageDraw.ImageDraw]: The image and drawing context.
        """
        border_size = max(1, self.border)
        
        # Create QR code with minimal border
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=border_size,  # Reduced border
        )
        qr.add_data(data=data)
        qr.make(fit=True)
        
        # Get QR code matrix
        self.matrix = qr.get_matrix()
        self.size = len(self.matrix)
        
        # Create image
        img_size = self.size * 10  # box_size=10
        img = Image.new('RGB', (img_size, img_size), 'white')
        draw = ImageDraw.Draw(img)

        return img, draw
    

    def __apply_theme(self, qr_code_img):
        """
        Apply the selected theme and custom colors to the QR code image.

        Args:
            qr_code_img (PIL.ImageDraw.ImageDraw): The drawing context for the QR code image.

        Returns:
            PIL.ImageDraw.ImageDraw: The drawing context with theme applied.
        """
        finder_pattern_color = self.custom_finder_pattern_color if self.custom_finder_pattern_color is not None else self.theme.get("finder_pattern_color", DEFAULT_COLOR)
        for row in range(self.size):
            for col in range(self.size):
                if self.matrix[row][col]:
                    # Check if in any position detection pattern (full 7×7 squares)
                    in_corner = (
                        (row < (7+self.border) and col < (7 + self.border)) or        # Top-left
                        (row < (7 + self.border) and col > self.size - (8 + self.border)) or  # Top-right
                        (row > self.size - (8 + self.border) and col < (7 + self.border))     # Bottom-left
                    )
                    theme_color = self.custom_theme_color if self.custom_theme_color is not None else self.theme.get("theme_color", DEFAULT_COLOR)


                    # if it is in the corner and the theme is shown and color_positiond_detection_corners is true, then color the corner
                    if self.color_positiond_detection_corners and in_corner:
                            color = finder_pattern_color
                    elif self.show_theme and not in_corner:
                        color = theme_color
                    else:
                        color = DEFAULT_COLOR
                 
                    qr_code_img.rectangle(
                        [(col * 10, row * 10), ((col + 1) * 10, (row + 1) * 10)],
                        fill=color
                    )
        
        return qr_code_img
    

    def __apply_logo(self, qr_code_image):
        """
        Embed a logo image in the center of the QR code, with rounded corners and a border.

        Args:
            qr_code_image (PIL.Image.Image): The QR code image to modify.

        Returns:
            PIL.Image.Image: The QR code image with the logo embedded (if applicable).
        """
        logo_path = self.logo
        # If user supplied a logo_path
        if self.logo:
            if os.path.isabs(self.logo) and os.path.exists(self.logo):
                logo_path = self.logo
            elif os.path.exists(self.logo):  # relative to CWD
                logo_path = self.logo
            else:
                # Fallback to theme logo if user-supplied path doesn't exist
                theme_logo = self.theme.get("logo", None)
                if theme_logo:
                    package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    logo_path = os.path.join(package_root, "qrstyler", theme_logo)
                else:
                    logo_path = None
        else:
            # No user logo, use theme logo
            theme_logo = self.theme.get("logo", None)
            if theme_logo:
                package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                logo_path = os.path.join(package_root, "qrgenerator", theme_logo)
            else:
                logo_path = None

        if self.show_logo and logo_path and os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            logo_size = int(min(qr_code_image.size) * 0.11)  # 20% of QR size
            logo.thumbnail((logo_size, logo_size))

            # Create a rounded rectangle mask for the logo
            mask = Image.new('L', logo.size, 0)
            draw = ImageDraw.Draw(mask)
            radius = int(min(logo.size) * 0.15)  # 10% corner radius
            draw.rounded_rectangle(
                [(0, 0), logo.size],
                radius=radius,
                fill=255
            )

            # Apply the rounded mask to the logo (preserve transparency)
            logo_rounded = Image.new('RGBA', logo.size)
            logo_rounded.paste(logo, (0, 0), mask=mask)

            # Create a white border with rounded corners (fully opaque)
            border_size = 8  # Thickness of border (reduced from 12 to 6)
            border_img_size = (logo.size[0] + 2 * border_size, logo.size[1] + 2 * border_size)
            border_img = Image.new('RGBA', border_img_size, (255, 255, 255, 255))  # Opaque white
            border_draw = ImageDraw.Draw(border_img)
            border_draw.rounded_rectangle(
                [(0, 0), border_img_size],
                radius=radius + border_size,
                fill=(255, 255, 255, 255)
            )
            # Paste the rounded logo onto the border using the mask for roundness
            border_img.paste(logo_rounded, (border_size, border_size), mask=logo_rounded)

            # Calculate where to paste the border_img (centered)
            paste_x = (qr_code_image.size[0] - border_img.size[0]) // 2
            paste_y = (qr_code_image.size[1] - border_img.size[1]) // 2

            # Clear the area under the logo+border (fill with fully opaque white)
            qr_draw = ImageDraw.Draw(qr_code_image)
            qr_draw.rounded_rectangle(
                [(paste_x, paste_y), (paste_x + border_img.size[0], paste_y + border_img.size[1])],
                radius=radius + border_size,
                fill=(255, 255, 255, 255)
            )

            # Paste the bordered logo onto the QR code
            qr_code_image.paste(
                border_img,
                (paste_x, paste_y),
                mask=border_img
            )
        
        return qr_code_image
