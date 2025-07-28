"""
Main application controller for APODPaper
"""
import platform
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import io
import os

try:
    from .config import Config
    from .apod_client import APODClient
    from .wallpaper import WallpaperManager
    from .gui import APIKeyDialog, UnsupportedOSWindow, WindowUtils, show_info
    from .system_tray import SystemTray
    from .scheduler import Scheduler
except:
    from config import Config
    from apod_client import APODClient
    from wallpaper import WallpaperManager
    from gui import APIKeyDialog, UnsupportedOSWindow, WindowUtils, show_info
    from system_tray import SystemTray
    from scheduler import Scheduler


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
            hd_enabled = self.config.get_hd_preference()
            random_enabled = self.config.get_random_image_preference()
            
            result = self.apod_client.download_with_fallback(silent=True, hd=hd_enabled, random_date=random_enabled)
            if result:
                image_path, apod_data = result
                if self.wallpaper_manager.set_wallpaper(image_path):
                    self.config.update_last_update()
                    print(f"Wallpaper automatically updated at {datetime.now()}")
                    return True
        
        return False
    
    def manual_update(self, icon=None, item=None):
        """Manually update wallpaper"""
        def do_update():
            try:
                hd_enabled = self.config.get_hd_preference()
                random_enabled = self.config.get_random_image_preference()
                
                result = self.apod_client.download_with_fallback(hd=hd_enabled, random_date=random_enabled)
                if result:
                    image_path, apod_data = result
                    if self.wallpaper_manager.set_wallpaper(image_path):
                        self.config.update_last_update()
                        # Schedule dialog creation on main thread
                        self.root.after(0, lambda: self._show_success_dialog("Successfully updated wallpaper!"))
                    else:
                        self.root.after(0, lambda: self._show_error_dialog("Could not update", "Failed to update wallpaper :("))
                else:
                    self.root.after(0, lambda: self._show_warning_dialog("Could not download image", "Failed to download image. Perhaps your API key is wrong?"))
            except Exception as e:
                self.root.after(0, lambda: self._show_error_dialog("Unknown Error", f"We encountered an unknown error updating the APOD \n {e} \n Please create an issue on GitHub!"))
        
        # Run the update in a separate thread to avoid blocking the UI
        import threading
        threading.Thread(target=do_update, daemon=True).start()
    
    def toggle_auto_update(self, icon=None, item=None):
        """Toggle automatic updates on/off"""
        auto_update_enabled = self.config.toggle_auto_update()
        status = "enabled" if auto_update_enabled else "disabled"
        show_info(self.root, "Settings", f"Auto-update {status}", "gear")
        
        # Restart scheduler with new settings
        if auto_update_enabled:
            self.scheduler.start()
        else:
            self.scheduler.stop()
    
    def show_settings(self, icon=None, item=None):
        """Show settings window"""
        from src.gui import WindowUtils, Theme, APIKeyDialog
        settings_dialog = ctk.CTkToplevel(self.root)
        settings_dialog.title("Settings")
        settings_dialog.geometry("500x600")
        settings_dialog.resizable(False, False)
        WindowUtils.set_window_icon(settings_dialog)

        # Apply dark theme
        settings_dialog.configure(fg_color=Theme.SPACE_BLACK)

        # Configure grid
        settings_dialog.grid_columnconfigure(0, weight=1)
        settings_dialog.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(settings_dialog, height=80, fg_color=Theme.ACCENT, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=25)

        # Content frame
        content_frame = ctk.CTkFrame(settings_dialog, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
        content_frame.grid_columnconfigure(0, weight=1)

        # API Key Section
        api_section = ctk.CTkFrame(content_frame, fg_color=Theme.SECONDARY)
        api_section.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        api_section.grid_columnconfigure(1, weight=1)

        api_label = ctk.CTkLabel(
            api_section,
            text="NASA API Key:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=Theme.TEXT
        )
        api_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        current_key = self.config.get_api_key()
        masked_key = f"{current_key[:8]}...{current_key[-4:]}" if len(current_key) > 12 else "DEMO_KEY"
        api_display = ctk.CTkLabel(
            api_section,
            text=masked_key,
            font=ctk.CTkFont(size=12),
            text_color=Theme.ACCENT
        )
        api_display.grid(row=0, column=1, padx=20, pady=15, sticky="w")

        def update_api_key():
            dialog = APIKeyDialog(self.config, settings_dialog)
            new_key = dialog.show()
            if new_key:
                masked_key = f"{new_key[:8]}...{new_key[-4:]}" if len(new_key) > 12 else "DEMO_KEY"
                api_display.configure(text=masked_key)
                # Reinitialize APOD client with new key
                self.api_key = new_key
                self.apod_client = APODClient(self.api_key, self.config.apod_folder)

        api_button = ctk.CTkButton(
            api_section,
            text="Update",
            command=update_api_key,
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            width=80
        )
        api_button.grid(row=0, column=2, padx=20, pady=15)

        # Auto-update Section
        auto_section = ctk.CTkFrame(content_frame, fg_color=Theme.SECONDARY)
        auto_section.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        auto_section.grid_columnconfigure(0, weight=1)

        auto_label = ctk.CTkLabel(
            auto_section,
            text="Automatic Updates:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=Theme.TEXT
        )
        auto_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        auto_switch = ctk.CTkSwitch(
            auto_section,
            text="Enable daily automatic wallpaper updates",
            font=ctk.CTkFont(size=12),
            text_color=Theme.TEXT
        )
        auto_switch.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")
        
        config_data = self.config.get_config()
        if config_data.get("auto_update", True):
            auto_switch.select()

        # HD Images Section
        hd_section = ctk.CTkFrame(content_frame, fg_color=Theme.SECONDARY)
        hd_section.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        hd_section.grid_columnconfigure(0, weight=1)

        hd_label = ctk.CTkLabel(
            hd_section,
            text="Image Quality:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=Theme.TEXT
        )
        hd_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        hd_switch = ctk.CTkSwitch(
            hd_section,
            text="Download HD images (when available)",
            font=ctk.CTkFont(size=12),
            text_color=Theme.TEXT
        )
        hd_switch.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")
        
        if self.config.get_hd_preference():
            hd_switch.select()

        # Random Images Section
        random_section = ctk.CTkFrame(content_frame, fg_color=Theme.SECONDARY)
        random_section.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        random_section.grid_columnconfigure(0, weight=1)

        random_label = ctk.CTkLabel(
            random_section,
            text="Random Images:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=Theme.TEXT
        )
        random_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        random_switch = ctk.CTkSwitch(
            random_section,
            text="Get random APOD instead of today's image",
            font=ctk.CTkFont(size=12),
            text_color=Theme.TEXT
        )
        random_switch.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")
        
        if self.config.get_random_image_preference():
            random_switch.select()

        # Buttons
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, pady=20, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        def save_settings():
            # Save auto-update setting
            current_auto = config_data.get("auto_update", True)
            new_auto = auto_switch.get() == 1
            if current_auto != new_auto:
                self.config.toggle_auto_update()
                if new_auto:
                    self.scheduler.start()
                else:
                    self.scheduler.stop()
            
            # Save HD preference
            self.config.set_hd_preference(hd_switch.get() == 1)
            
            # Save random preference
            self.config.set_random_image_preference(random_switch.get() == 1)
            
            show_info(self.root, "Settings", "Settings saved successfully!", "gear")
            settings_dialog.destroy()

        def cancel_settings():
            settings_dialog.destroy()

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=cancel_settings,
            fg_color="transparent",
            border_width=2,
            border_color=Theme.ACCENT,
            text_color=Theme.ACCENT,
            hover_color=Theme.SECONDARY
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            command=save_settings,
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            font=ctk.CTkFont(weight="bold")
        )
        save_btn.grid(row=0, column=1, sticky="ew")

        # Center window
        settings_dialog.update_idletasks()
        x = (settings_dialog.winfo_screenwidth() // 2) - (settings_dialog.winfo_width() // 2)
        y = (settings_dialog.winfo_screenheight() // 2) - (settings_dialog.winfo_height() // 2)
        settings_dialog.geometry(f"+{x}+{y}")

        # Basic modal behavior without problematic attributes
        settings_dialog.focus_set()
        settings_dialog.lift()

    def show_about(self, icon=None, item=None):
        """Show about dialog"""
        from src.gui import WindowUtils, Theme
        about_dialog = ctk.CTkToplevel(self.root)
        about_dialog.title("About APODPaper")
        about_dialog.geometry("400x500")
        about_dialog.resizable(False, False)
        WindowUtils.set_window_icon(about_dialog)

        # Apply dark theme
        about_dialog.configure(fg_color=Theme.SPACE_BLACK)

        # Text content
        text_label = ctk.CTkLabel(
            about_dialog,
            text="APODPaper v1.0.0\n\nNASA Astronomy Picture of the Day\nWallpaper Application",
            font=ctk.CTkFont(size=14),
            text_color=Theme.TEXT
        )
        text_label.pack(pady=20)

        # Add app icon
        try:
            if os.path.exists("assets/icon.png"):
                from PIL import Image
                
                icon_image = Image.open("assets/icon.png")
                icon_image = icon_image.resize((250, 250), Image.Resampling.LANCZOS)
                
                # Use CTkImage instead of PhotoImage
                ctk_image = ctk.CTkImage(light_image=icon_image, dark_image=icon_image, size=(250, 250))
                icon_label = ctk.CTkLabel(
                    about_dialog,
                    image=ctk_image,
                    text=""
                )
                icon_label.pack(pady=10)
        except Exception as e:
            print(f"Could not load icon for about dialog: {e}")

        # Close button
        close_button = ctk.CTkButton(
            about_dialog,
            text="Close",
            command=about_dialog.destroy,
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            width=100
        )
        close_button.pack(pady=20)

        # Center window
        about_dialog.update_idletasks()
        x = (about_dialog.winfo_screenwidth() // 2) - (about_dialog.winfo_width() // 2)
        y = (about_dialog.winfo_screenheight() // 2) - (about_dialog.winfo_height() // 2)
        about_dialog.geometry(f"+{x}+{y}")

        # Basic modal behavior without problematic attributes
        about_dialog.focus_set()
        about_dialog.lift()
    
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
    
    def clean_folder(self):
        """
        Delete all saved image files to save storage
        """
        local_app_data_path = os.getenv("LOCALAPPDATA")
        path = os.path.join(local_app_data_path, "apodpaper")
        extensions = ["png", "jpg", "jpeg", "gif"]

        for filename in os.listdir(path):
            ext = filename.split(".")[1]
            if ext in extensions:
                filepath = os.path.join(path, filename)
                try:
                    os.remove(filepath)
                    print(f"removed {filepath}")
                except OSError as e:
                    print(f"error removing file {filepath}: {e}")

    def _show_success_dialog(self, message):
        """Show success dialog on main thread"""
        dialog = show_info(self._get_dialog_parent(), "Success", message, "success")
        # Keep dialog open by forcing focus and waiting
        self._ensure_dialog_stays_open(dialog)

    def _show_error_dialog(self, title, message):
        """Show error dialog on main thread"""
        dialog = show_info(self._get_dialog_parent(), title, message, "error")
        self._ensure_dialog_stays_open(dialog)

    def _show_warning_dialog(self, title, message):
        """Show warning dialog on main thread"""
        dialog = show_info(self._get_dialog_parent(), title, message, "warning")
        self._ensure_dialog_stays_open(dialog)

    def _get_dialog_parent(self):
        """Get appropriate parent for dialogs"""
        # Always use root as parent - it should be available even if withdrawn
        return self.root

    def _ensure_dialog_stays_open(self, dialog):
        """Ensure dialog stays open and is properly focused"""
        dialog.attributes("-topmost", True)
        dialog.lift()
        dialog.focus_force()
        # Make sure dialog doesn't get destroyed immediately
        dialog.grab_set()
        dialog.wait_window()


def main(root):
    """Entry point for the application"""
    app = APODPaperApp(root)
    app.run()
    root.mainloop()


if __name__ == "__main__":
    import customtkinter as ctk
    root = ctk.CTk()
    root.withdraw()
    main(root)
