import os

def get_license_path():
    """Fetches Aspose license path from an environment variable or uses a default."""
    return os.getenv("ASPOSE_LICENSE_PATH", "Aspose.Total.lic")

def use_aspose_license():
    """Checks if Aspose license should be applied (True/False)."""
    return os.getenv("USE_ASPOSE_LICENSE", "true").lower() in ["1", "true", "yes"]