"""
Helper functions for template handling.
Templates are stored in the database as JSON with {{placeholder}} syntax for field substitution.
Images are resolved by the backend before returning to the frontend.
"""
import base64
from pathlib import Path

# ─── Load images as base64 ─────────────────────────────────────────────────
def load_images():
    """Load header and footer images from backend/template_data/ as base64."""
    images = {}
    template_data_dir = Path(__file__).parent.parent.parent / "backend" / "template_data"
    
    # Load header image
    header_path = template_data_dir / "header.png"
    if header_path.exists():
        with open(header_path, "rb") as f:
            images["header"] = "data:image/png;base64," + base64.b64encode(f.read()).decode()
    
    # Load footer image
    footer_path = template_data_dir / "footer.png"
    if footer_path.exists():
        with open(footer_path, "rb") as f:
            images["footer"] = "data:image/png;base64," + base64.b64encode(f.read()).decode()
    
    return images

_IMAGES = load_images()


def get_image_uri(image_key: str) -> str:
    """Get the base64 URI for an image."""
    if image_key == "headerImage":
        return _IMAGES.get("header", "")
    elif image_key == "footerImage":
        return _IMAGES.get("footer", "")
    return ""

