"""
GUI components and windows for APODPaper using CustomTkinter
"""
import customtkinter as ctk
import tkinter as tk
import threading
from PIL import Image
import io
import os


# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class Theme:
    """Custom space theme configuration for CustomTkinter"""
    # Color palette
    SPACE_BLACK = "#0B0C10"
    DARK_BLUE = "#1F2833"
    STEEL_BLUE = "#45A29E"
    LIGHT_CYAN = "#66FCF1"
    WHITE = "#C5C6C7"
    
    # CustomTkinter compatible colors
    PRIMARY = "#212121"
    SECONDARY = "#1F2833"
    ACCENT = "#45A29E"
    ACCENT_HOVER = "#66FCF1"
    TEXT = "#C5C6C7"
    ERROR = "#FF6B6B"
    SUCCESS = "#4ECDC4"


class WindowUtils:
    @staticmethod
    def set_window_icon(window):
        """Set the window icon for windows"""
        try:
            if os.path.exists("assets/icon.ico"):
                print("Setting icon from assets/icon.ico")
                window.iconbitmap("assets/icon.ico")
            elif os.path.exists("assets/icon.png"):
                print("Setting icon from assets/icon.png")
                icon_image = Image.open("assets/icon.png")
                icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
                bio = io.BytesIO()
                icon_image.save(bio, format='PNG')
                bio.seek(0)
                photo = tk.PhotoImage(data=bio.getvalue())
                window._icon_ref = photo  # Retain reference to prevent garbage collection
                window.iconphoto(False, photo)
            else:
                print("No valid icon file found in assets/")
        except Exception as e:
            print(f"Failed to set window icon: {e}")


class APIKeyDialog:
    def __init__(self, config, parent):
        self.config = config
        self.api_key = None
        self.parent = parent

    def show(self):
        """Show API key input dialog using CustomTkinter"""
        if not os.path.exists(self.config.config_path):
            default_config = {
                "NASA_API_KEY": "DEMO_KEY",
                "last_update": "",
                "auto_update": True
            }
            self.config.save_config(default_config)

        # Create dialog as Toplevel
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("APODPaper - NASA API Key Setup")
        dialog.geometry("550x400")
        dialog.resizable(False, False)

        WindowUtils.set_window_icon(dialog)

        # Configure grid weights
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(1, weight=1)

        # Header frame
        header_frame = ctk.CTkFrame(dialog, height=100, fg_color=Theme.SECONDARY, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)

        # Header content
        title_label = ctk.CTkLabel(
            header_frame,
            text="🌌 NASA API Key Required",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=Theme.ACCENT_HOVER
        )
        title_label.pack(pady=30)

        # Main content frame
        content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
        content_frame.grid_columnconfigure(0, weight=1)

        # Instructions
        inst_text = ("To access NASA's Astronomy Picture of the Day,\nyou need a free API key from NASA.")
        inst_label = ctk.CTkLabel(
            content_frame,
            text=inst_text,
            font=ctk.CTkFont(size=14),
            text_color=Theme.TEXT
        )
        inst_label.grid(row=0, column=0, pady=(0, 10))

        # Link label
        link_label = ctk.CTkLabel(
            content_frame,
            text="→ Get your free API key at: https://api.nasa.gov/",
            font=ctk.CTkFont(size=12),
            text_color=Theme.ACCENT,
            cursor="hand2"
        )
        link_label.grid(row=1, column=0, pady=(0, 20))

        # Entry label
        entry_label = ctk.CTkLabel(
            content_frame,
            text="Enter your NASA API Key:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=Theme.TEXT
        )
        entry_label.grid(row=2, column=0, sticky="w", pady=(0, 10))

        # API key entry
        api_key_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Paste your NASA API key here...",
            height=40,
            font=ctk.CTkFont(size=12),
            border_color=Theme.ACCENT,
            fg_color=Theme.SECONDARY
        )
        api_key_entry.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        # Error label
        error_label = ctk.CTkLabel(
            content_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=Theme.ERROR
        )
        error_label.grid(row=4, column=0, pady=5)

        # Button frame
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, pady=20, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        def submit():
            self.api_key = api_key_entry.get().strip()
            if self.api_key and len(self.api_key) > 10:
                self.config.set_api_key(self.api_key)
                dialog.destroy()
            else:
                error_label.configure(text="⚠ Please enter a valid API key (should be 40+ characters)")

        def cancel():
            dialog.destroy()

        # Buttons
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=cancel,
            fg_color="transparent",
            border_width=2,
            border_color=Theme.ACCENT,
            text_color=Theme.ACCENT,
            hover_color=Theme.SECONDARY
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        submit_btn = ctk.CTkButton(
            button_frame,
            text="Continue",
            command=submit,
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            font=ctk.CTkFont(weight="bold")
        )
        submit_btn.grid(row=0, column=1, sticky="ew")

        # Bind Enter key
        dialog.bind('<Return>', lambda e: submit())
        dialog.bind('<Escape>', lambda e: cancel())

        # Center window
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        dialog.grab_set()
        self.parent.deiconify()  # Ensure root is visible if hidden
        dialog.wait_window()
        return self.api_key


class NotificationWindow:
    @staticmethod
    def show(title, message, notification_type="info", parent=None):
        """Show an enhanced notification window using CustomTkinter"""
        def create_notification():
            try:
                # Comprehensive message validation and type conversion
                if message is None:
                    msg_str = ""
                elif isinstance(message, str):
                    msg_str = message
                else:
                    msg_str = str(message)
                
                # Provide default for success notifications
                if notification_type == "success" and (not msg_str or msg_str.strip() == ""):
                    msg_str = "Operation completed successfully!"
                
                print(f"Creating notification: title='{title}', type='{notification_type}', message_length={len(msg_str)}")
                
                # Create notification window
                notification = ctk.CTkToplevel(parent)
                notification.title(title)

                # Calculate window size with proper type checking
                lines = msg_str.count('\n') + 1
                try:
                    # Ensure we're working with integers throughout
                    msg_length = len(str(msg_str))
                    width = min(max(msg_length * 8, 350), 450)
                    width = int(width)
                    height = min(max(lines * 25 + 120, 180), 280)
                    height = int(height)
                except Exception as e:
                    print(f"Width calculation error: {e}")
                    width = 350
                    height = 200

                print(f"Notification window size: {width}x{height}")

                # Center the notification window on the screen
                notification.update_idletasks()
                x = (notification.winfo_screenwidth() // 2) - (width // 2)
                y = (notification.winfo_screenheight() // 2) - (height // 2)
                notification.geometry(f"{width}x{height}+{x}+{y}")
                notification.attributes("-topmost", True)
                notification.resizable(False, False)

                WindowUtils.set_window_icon(notification)

                # Configure grid
                notification.grid_columnconfigure(0, weight=1)
                notification.grid_rowconfigure(1, weight=1)

                # Icon mapping
                icons = {
                    "success": "✅",
                    "error": "❌",
                    "warning": "⚠️",
                    "info": "ℹ️",
                    "settings": "⚙️"
                }

                # Determine icon and color
                icon = icons.get(notification_type, "ℹ️")
                if "success" in title.lower() or notification_type == "success":
                    icon = icons["success"]
                    header_color = Theme.SUCCESS
                elif "error" in title.lower() or notification_type == "error":
                    icon = icons["error"]
                    header_color = Theme.ERROR
                elif "settings" in title.lower() or notification_type == "settings":
                    icon = icons["settings"]
                    header_color = Theme.ACCENT
                else:
                    header_color = Theme.ACCENT

                # Header frame
                header_frame = ctk.CTkFrame(
                    notification,
                    height=60,
                    fg_color=header_color,
                    corner_radius=(10, 10, 0, 0)
                )
                header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
                header_frame.grid_propagate(False)

                # Header label
                header_label = ctk.CTkLabel(
                    header_frame,
                    text=f"{icon} {title}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="white"
                )
                header_label.pack(pady=20)

                # Content frame
                content_frame = ctk.CTkFrame(notification, fg_color="transparent")
                content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=15)
                content_frame.grid_columnconfigure(0, weight=1)
                content_frame.grid_rowconfigure(0, weight=1)

                # Message label with safe wraplength calculation
                try:
                    # Ensure width is an integer and calculate safe wrap length
                    safe_width = int(width) if isinstance(width, (int, float)) else 350
                    wrap_length = max(safe_width - 60, 200)
                    wrap_length = int(wrap_length)
                except Exception as e:
                    print(f"Wraplength calculation error: {e}")
                    wrap_length = 290
                    
                message_label = ctk.CTkLabel(
                    content_frame,
                    text=msg_str,
                    font=ctk.CTkFont(size=13),
                    text_color=Theme.TEXT,
                    wraplength=wrap_length,
                    justify="center"
                )
                message_label.grid(row=0, column=0, pady=10)

                # OK button
                ok_button = ctk.CTkButton(
                    content_frame,
                    text="OK",
                    command=notification.destroy,
                    fg_color=Theme.ACCENT,
                    hover_color=Theme.ACCENT_HOVER,
                    width=80,
                    height=32
                )
                ok_button.grid(row=1, column=0, pady=10)

                # Auto-close after 7 seconds
                notification.after(7000, notification.destroy)

                # Focus and show
                notification.focus()
                notification.lift()

                # Don't use wait_window() as it can interfere with other dialogs

            except Exception as e:
                print(f"Notification error: {e}")

        # Run in main thread using after_idle
        try:
            # Try to schedule in main thread
            import tkinter as tk
            root = tk._default_root
            if root:
                root.after_idle(create_notification)
            else:
                # Fallback to thread if no main loop
                threading.Thread(target=create_notification, daemon=True).start()
        except:
            # Final fallback
            threading.Thread(target=create_notification, daemon=True).start()


class UnsupportedOSWindow:
    @staticmethod
    def show(parent):
        """Show enhanced unsupported OS message using CustomTkinter"""
        dialog = ctk.CTkToplevel(parent)
        dialog.title("APODPaper - Unsupported OS")
        dialog.geometry("500x300")
        dialog.resizable(False, False)

        WindowUtils.set_window_icon(dialog)

        # Configure grid
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(dialog, height=80, fg_color=Theme.ERROR, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="🚫 Unsupported Operating System",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=25)

        # Content
        content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
        content_frame.grid_columnconfigure(0, weight=1)

        error_text = ("APODPaper currently only supports Windows.\n\n"
                     "We are working on adding support for macOS and Linux\n"
                     "in future releases.\n\n"
                     "Thank you for your interest in APODPaper!")

        error_label = ctk.CTkLabel(
            content_frame,
            text=error_text,
            font=ctk.CTkFont(size=14),
            text_color=Theme.TEXT,
            justify="center"
        )
        error_label.grid(row=0, column=0, pady=20)

        # Button
        close_button = ctk.CTkButton(
            content_frame,
            text="Exit Application",
            command=dialog.destroy,
            fg_color=Theme.ERROR,
            hover_color="#FF8A8A",
            font=ctk.CTkFont(weight="bold"),
            height=40
        )
        close_button.grid(row=1, column=0, pady=20)

        # Center window
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        dialog.grab_set()
        parent.deiconify()
        dialog.wait_window()
