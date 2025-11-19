"""Quote card image generation service."""
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap
from typing import Tuple


class QuoteImageGenerator:
    """Generates shareable quote card images."""

    def __init__(self):
        self.width = 1200
        self.height = 630  # Twitter/Facebook optimal size
        self.bg_color = '#fffbf0'  # Light cream background
        self.text_color = '#1a1a1a'
        self.accent_color = '#ff4444'
        self.border_color = '#666666'

    def _get_font(self, size: int, bold: bool = False):
        """Get font, falling back to default if custom fonts unavailable."""
        font_paths = [
            # Debian/Ubuntu paths
            ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
            # Alpine paths
            ("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSerif.ttf"),
            # Fallback to sans for both
            ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]

        for bold_path, regular_path in font_paths:
            try:
                path = bold_path if bold else regular_path
                return ImageFont.truetype(path, size)
            except (OSError, IOError):
                continue

        # Fall back to default font if nothing works
        try:
            return ImageFont.load_default()
        except:
            # Ultimate fallback - use basic PIL font
            return None

    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """Wrap text to fit within max width."""
        if font is None:
            # Simple word wrapping without font metrics
            words = text.split()
            lines = []
            current_line = []
            max_words_per_line = 8

            for word in words:
                current_line.append(word)
                if len(current_line) >= max_words_per_line:
                    lines.append(' '.join(current_line))
                    current_line = []

            if current_line:
                lines.append(' '.join(current_line))
            return lines

        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                bbox = font.getbbox(test_line)
                width = bbox[2] - bbox[0]
            except:
                # If font doesn't support getbbox, estimate
                width = len(test_line) * (font.size * 0.6 if hasattr(font, 'size') else 10)

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def generate_quote_image(
        self,
        quote_text: str,
        category: str,
        absurdity_score: int
    ) -> BytesIO:
        """
        Generate a shareable quote card image.

        Args:
            quote_text: The quote text
            category: Quote category
            absurdity_score: Absurdity score 1-10

        Returns:
            BytesIO object containing PNG image data
        """
        # Create image with background
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)

        # Add border
        border_width = 8
        draw.rectangle(
            [(border_width, border_width),
             (self.width - border_width, self.height - border_width)],
            outline=self.border_color,
            width=border_width
        )

        # Fonts
        quote_font = self._get_font(48, bold=False)
        meta_font = self._get_font(32, bold=True)
        brand_font = self._get_font(36, bold=True)

        # Wrap quote text
        padding = 100
        max_text_width = self.width - (padding * 2)
        wrapped_lines = self._wrap_text(quote_text, quote_font, max_text_width)

        # Calculate total text height
        line_spacing = 10
        text_height = len(wrapped_lines) * (quote_font.size + line_spacing)

        # Draw quote marks and text
        y_pos = (self.height - text_height) // 2 - 40

        # Opening quote mark
        quote_mark_font = self._get_font(120, bold=True)
        draw.text(
            (padding - 20, y_pos - 60),
            '"',
            fill=self.border_color + '40',  # Semi-transparent
            font=quote_mark_font
        )

        # Draw wrapped text
        for line in wrapped_lines:
            bbox = quote_font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x_pos = (self.width - text_width) // 2

            draw.text(
                (x_pos, y_pos),
                line,
                fill=self.text_color,
                font=quote_font
            )
            y_pos += quote_font.size + line_spacing

        # Closing quote mark
        draw.text(
            (self.width - padding - 20, y_pos - 20),
            '"',
            fill=self.border_color + '40',
            font=quote_mark_font
        )

        # Draw metadata badges at bottom
        badge_y = self.height - 100

        # Absurdity badge
        absurdity_text = f"ABSURDITY: {absurdity_score}/10"
        bbox = meta_font.getbbox(absurdity_text)
        badge_width = bbox[2] - bbox[0] + 40
        badge_height = bbox[3] - bbox[1] + 20
        badge_x = (self.width - badge_width - 300) // 2

        draw.rounded_rectangle(
            [(badge_x, badge_y - 10),
             (badge_x + badge_width, badge_y + badge_height + 10)],
            radius=20,
            fill=self.accent_color
        )

        draw.text(
            (badge_x + 20, badge_y),
            absurdity_text,
            fill='white',
            font=meta_font
        )

        # Category badge
        category_text = category.upper()
        bbox = meta_font.getbbox(category_text)
        cat_badge_width = bbox[2] - bbox[0] + 40
        cat_badge_x = badge_x + badge_width + 30

        draw.rounded_rectangle(
            [(cat_badge_x, badge_y - 10),
             (cat_badge_x + cat_badge_width, badge_y + badge_height + 10)],
            radius=20,
            fill='#e0e0e0'
        )

        draw.text(
            (cat_badge_x + 20, badge_y),
            category_text,
            fill=self.text_color,
            font=meta_font
        )

        # Add branding at top
        brand_text = "THE STORY - UnioNews"
        bbox = brand_font.getbbox(brand_text)
        brand_width = bbox[2] - bbox[0]
        brand_x = (self.width - brand_width) // 2

        draw.text(
            (brand_x, 50),
            brand_text,
            fill=self.text_color,
            font=brand_font
        )

        # Convert to bytes
        output = BytesIO()
        img.save(output, format='PNG', quality=95)
        output.seek(0)

        return output
