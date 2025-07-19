"""
Main application controller for APODPaper
"""
import platform
import tkinter as tk
import customtkinter as ctk
from .config import Config
from .apod_client import APODClient
from .wallpaper import WallpaperManager
from .gui import APIKeyDialog, NotificationWindow, UnsupportedOSWindow, WindowUtils
from .system_tray import SystemTray
from .scheduler import Scheduler
from PIL import Image, ImageTk
import io
import os


class APODPaperApp:
    def __init__(self, root):
        self.root = root
        self.config = Config()
        self.wallpaper_manager = WallpaperManager()
        self.apod_client = None
        self.system_tray = SystemTray(self)
        self.scheduler = Scheduler(self)
        self.api_key = None
    
    def initialize(self):
        """Initialize the application"""
        # Check if running on Windows
        if platform.system().lower() != "windows":
            UnsupportedOSWindow.show(self.root)
            return False
        
        # Get API key
        self.api_key = self.get_or_prompt_api_key()
        if not self.api_key or not self.config.is_valid_api_key(self.api_key):
            return False
        
        # Initialize APOD client
        self.apod_client = APODClient(self.api_key, self.config.apod_folder)
        
        return True
    
    def get_or_prompt_api_key(self):
        """Get API key from config or prompt user"""
        api_key = self.config.get_api_key()
        if not self.config.is_valid_api_key(api_key):
            dialog = APIKeyDialog(self.config, self.root)
            api_key = dialog.show()
        return api_key
    
    def check_and_update_wallpaper(self):
        """Check if wallpaper needs updating and update it"""
        config_data = self.config.get_config()
        
        if not config_data.get("auto_update", True):
            return
        
        from datetime import datetime
        last_update = config_data.get("last_update", "")
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Only update if we haven't updated today
        if last_update != today:
            result = self.apod_client.download_with_fallback(silent=True)
            if result:
                image_path, apod_data = result
                if self.wallpaper_manager.set_wallpaper(image_path):
                    self.config.update_last_update()
                    print(f"Wallpaper automatically updated at {datetime.now()}")
                    return True
        
        return False
    
    def manual_update(self, icon=None, item=None):
        """Manually update wallpaper"""
        try:
            result = self.apod_client.download_with_fallback()
            if result:
                image_path, apod_data = result
                if self.wallpaper_manager.set_wallpaper(image_path):
                    self.config.update_last_update()
                    title = apod_data.get('title', 'Unknown')
                    NotificationWindow.show("Success!", 
                                          f"Wallpaper updated successfully!\n\n{title}", 
                                          "success", parent=self.root)
                else:
                    NotificationWindow.show("Error", "Failed to set wallpaper", "error", parent=self.root)
            else:
                NotificationWindow.show("Error", "Could not download APOD image", "error", parent=self.root)
        except Exception as e:
            NotificationWindow.show("Error", f"Update failed: {str(e)}", "error", parent=self.root)
    
    def toggle_auto_update(self, icon=None, item=None):
        """Toggle automatic updates on/off"""
        auto_update_enabled = self.config.toggle_auto_update()
        status = "enabled" if auto_update_enabled else "disabled"
        NotificationWindow.show("Settings", f"Auto-update {status}", "settings", parent=self.root)
        
        # Restart scheduler with new settings
        if auto_update_enabled:
            self.scheduler.start()
        else:
            self.scheduler.stop()
    
    def show_settings(self, icon=None, item=None):
        """Show settings window"""
        from src.gui import WindowUtils, Theme
        settings_dialog = ctk.CTkToplevel(self.root)
        settings_dialog.title("Settings")
        settings_dialog.geometry("400x300")
        WindowUtils.set_window_icon(settings_dialog)

        # Apply dark theme
        settings_dialog.configure(fg_color=Theme.SPACE_BLACK)

        # Placeholder content
        label = ctk.CTkLabel(
            settings_dialog,
            text="Settings window coming soon!",
            font=ctk.CTkFont(size=14),
            text_color=Theme.TEXT
        )
        label.pack(pady=20)

    def show_about(self, icon=None, item=None):
        """Show about dialog"""
        from src.gui import WindowUtils, Theme
        about_dialog = ctk.CTkToplevel(self.root)
        about_dialog.title("About APODPaper")
        about_dialog.geometry("400x400")
        WindowUtils.set_window_icon(about_dialog)

        # Apply dark theme
        about_dialog.configure(fg_color=Theme.SPACE_BLACK)

        # Placeholder content
        label = ctk.CTkLabel(
            about_dialog,
            text="APODPaper v1.0.0\n\nNASA Astronomy Picture of the Day\nWallpaper Application",
            font=ctk.CTkFont(size=14),
            text_color=Theme.TEXT
        )
        label.pack(pady=20)

        # Add app icon
        if os.path.exists("assets/icon.png"):
            icon_image = Image.open("assets/icon.png")
            icon_image = icon_image.resize((400, 400), Image.Resampling.LANCZOS)
            bio = io.BytesIO()
            icon_image.save(bio, format='PNG')
            bio.seek(0)
            photo = tk.PhotoImage(data=bio.getvalue())
            icon_label = ctk.CTkLabel(
                about_dialog,
                image=photo,
                text=""
            )
            icon_label.image = photo  # Retain reference to prevent garbage collection
            icon_label.pack(pady=10)
    
    def run(self):
        """Main application entry point"""
        import threading
        if not self.initialize():
            return

        # Initial wallpaper check
        self.check_and_update_wallpaper()

        # Start scheduler
        self.scheduler.start()

        # Set up and run system tray in a background thread
        tray_icon = self.system_tray.setup()
        tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
        tray_thread.start()


def main(root):
    """Entry point for the application"""
    app = APODPaperApp(root)
    app.run()
    root.mainloop()


if __name__ == "__main__":
    main()
