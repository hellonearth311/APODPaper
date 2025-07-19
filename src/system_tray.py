"""
System tray integration for APODPaper
"""
import os
import pystray
from PIL import Image, ImageDraw


class SystemTray:
    def __init__(self, app_controller):
        self.app = app_controller
        self.icon = None
    
    def create_icon_image(self, width=64, height=64, color1="blue", color2="white"):
        """Create a simple icon for the system tray"""
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle([width // 4, height // 4, width * 3 // 4, height * 3 // 4], fill=color2)
        return image
    
    def get_icon_image(self):
        """Get the icon image from file or create a default one"""
        if os.path.exists("assets/icon.png"):
            image = Image.open("assets/icon.png")
            image = image.resize((256, 256), Image.Resampling.LANCZOS)
            return image
        else:
            return self.create_icon_image(256, 256)
    
    def create_menu(self):
        """Create the system tray context menu"""
        return pystray.Menu(
            pystray.MenuItem("Update Wallpaper", self.app.manual_update),
            pystray.MenuItem("Toggle Auto-Update", self.app.toggle_auto_update),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings", self.app.show_settings),
            pystray.MenuItem("About", self.app.show_about),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.quit_app)
        )
    
    def quit_app(self, icon=None, item=None):
        """Quit the application"""
        if self.icon:
            self.icon.stop()
    
    def setup(self):
        """Set up and return the system tray icon"""
        image = self.get_icon_image()
        menu = self.create_menu()
        
        self.icon = pystray.Icon(
            "APOD Wallpaper", 
            image, 
            "APOD Wallpaper - NASA Astronomy Picture of the Day",
            menu
        )
        
        return self.icon
    
    def run(self):
        """Run the system tray icon"""
        if self.icon:
            self.icon.run()
