"""
Wallpaper management for Windows
"""
import ctypes


class WallpaperManager:
    def __init__(self):
        self.SPI_SETDESKWALLPAPER = 20
    
    def set_wallpaper(self, image_path):
        """Set desktop wallpaper to the specified image"""
        try:
            ctypes.windll.user32.SystemParametersInfoW(
                self.SPI_SETDESKWALLPAPER, 
                0, 
                image_path, 
                0
            )
            return True
        except Exception as e:
            print(f"Failed to set wallpaper: {e}")
            return False
    
    def is_supported(self):
        """Check if wallpaper setting is supported on this system"""
        try:
            # Test if we can access the Windows API
            return hasattr(ctypes.windll, 'user32')
        except:
            return False
