"""
GUI components and windows for APODPaper using CustomTkinter
"""
import customtkinter as ctk
import tkinter as tk
import threading
from PIL import Image, ImageDraw, ImageFont
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

def create_emoji_image(emoji_text, size=100):
    # Create a larger canvas to avoid clipping
    canvas_size = int(size * 1.4)  # Increased buffer for better centering
    img = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font_size = int(size * 0.75)  # Slightly smaller font for better fit
        font = ImageFont.truetype("seguiemj.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), emoji_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate center position with extra adjustments for specific emojis
    center_x = canvas_size // 2
    center_y = canvas_size // 2
    
    # Emoji-specific adjustments for better centering
    offset_x = 0
    offset_y = 0
    
    if emoji_text == "⚙️":  # Gear
        offset_x = 40
        offset_y = -3
    elif emoji_text == "⚠️":  # Warning
        offset_x = 40
        offset_y = -2
    elif emoji_text == "❌":  # Error
        offset_x = 0
        offset_y = -1
    elif emoji_text == "✅":  # Success
        offset_x = 0
        offset_y = -1
    
    # Calculate final position
    x = center_x - (text_width // 2) - bbox[0] + offset_x
    y = center_y - (text_height // 2) - bbox[1] + offset_y
    
    # Draw emoji with adjusted positioning
    draw.text((x, y), emoji_text, font=font, embedded_color=True)
    
    # Resize back to the requested size while maintaining aspect ratio
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    return img

def show_info(parent, title, message, icon_type):
    # validate types
    title = str(title)
    message = str(message)
    icon_type = str(icon_type).lower()

    # Icon mapping
    icon_map = {
        "success": "✅",
        "warning": "⚠️", 
        "error": "❌",
        "gear": "⚙️"
    }
    
    # Get the emoji or default to info
    emoji = icon_map.get(icon_type, "ℹ️")

    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("400x350")
    dialog.resizable(False, False)
    
    # Apply theme
    dialog.configure(fg_color=Theme.SPACE_BLACK)
    WindowUtils.set_window_icon(dialog)

    # Create main container
    main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Icon section
    icon_frame = ctk.CTkFrame(main_frame, fg_color="transparent", height=120)
    icon_frame.pack(fill="x", pady=(0, 20))
    icon_frame.pack_propagate(False)
    
    # Create emoji image with proper sizing based on type
    icon_size = 80
    if icon_type in ["warning", "error"]:
        icon_size = 75  # Slightly smaller for better balance
    elif icon_type == "gear":
        icon_size = 85  # Slightly larger for gear
    
    icon_img = ctk.CTkImage(
        light_image=create_emoji_image(emoji, size=icon_size), 
        size=(icon_size, icon_size)
    )

    icon_label = ctk.CTkLabel(
        icon_frame, 
        image=icon_img, 
        text="",
        fg_color="transparent"
    )
    icon_label.pack(expand=True)
    
    # Message section with proper centering and wrapping
    message_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    message_frame.pack(fill="both", expand=True)
    
    # Calculate wrap length based on dialog width
    wrap_length = 320  # Leave margin for padding
    
    message_label = ctk.CTkLabel(
        message_frame,
        text=message,
        font=ctk.CTkFont(size=14),
        text_color=Theme.TEXT,
        wraplength=wrap_length,
        justify="center",
        fg_color="transparent"
    )
    message_label.pack(expand=True, fill="both", pady=(0, 20))
    
    # OK button
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent", height=50)
    button_frame.pack(fill="x")
    button_frame.pack_propagate(False)
    
    ok_button = ctk.CTkButton(
        button_frame,
        text="OK",
        command=dialog.destroy,
        fg_color=Theme.ACCENT,
        hover_color=Theme.ACCENT_HOVER,
        width=100,
        height=35
    )
    ok_button.pack(expand=True)
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Make it modal but handle withdrawn parent
    if parent and parent.winfo_viewable():
        dialog.transient(parent)
        dialog.grab_set()
    else:
        # If parent is withdrawn, just make it stay on top
        dialog.attributes("-topmost", True)
        dialog.grab_set()
    
    dialog.focus_set()
    dialog.lift()
    
    return dialog

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("500x500")

    # Test different icon types
    def test_success():
        show_info(root, "Success!", "Operation completed successfully! This is a longer message to test text wrapping capabilities.", "success")
    
    def test_warning():
        show_info(root, "Warning", "This is a warning message that might be quite long and should wrap properly to multiple lines.", "warning")
    
    def test_error():
        show_info(root, "Error", "An error occurred during the operation.", "error")
    
    def test_gear():
        show_info(root, "Settings", "Settings have been updated successfully!", "gear")

    # Create test buttons
    ctk.CTkButton(root, text="Test Success", command=test_success).pack(pady=10)
    ctk.CTkButton(root, text="Test Warning", command=test_warning).pack(pady=10)
    ctk.CTkButton(root, text="Test Error", command=test_error).pack(pady=10)
    ctk.CTkButton(root, text="Test Gear", command=test_gear).pack(pady=10)

    root.mainloop()