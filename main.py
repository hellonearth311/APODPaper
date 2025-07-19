import os
import json
import requests
import tkinter as tk
import ctypes
import platform
import schedule
import time
import threading
import subprocess
from datetime import datetime, timedelta
import pystray
from PIL import Image, ImageDraw

def set_window_icon(window):
    """Set the window icon for tkinter windows"""
    try:
        if os.path.exists("assets/icon.ico"):
            # Use ICO file directly (best for Windows)
            window.iconbitmap("assets/icon.ico")
        elif os.path.exists("assets/icon.png"):
            # Convert PNG to PhotoImage for tkinter
            icon_image = Image.open("assets/icon.png")
            icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
            # Convert to tkinter PhotoImage
            import io
            bio = io.BytesIO()
            icon_image.save(bio, format='PNG')
            bio.seek(0)
            photo = tk.PhotoImage(data=bio.getvalue())
            # Store reference to prevent garbage collection
            window._icon_ref = photo
            window.iconphoto(False, photo)
    except Exception:
        pass  # If icon loading fails, just continue without icon

OS = platform.system()
if OS.lower() == "windows":
    appdata_local = os.getenv('LOCALAPPDATA')
    apod_folder = os.path.join(appdata_local, 'apodpaper')
    config_path = os.path.join(apod_folder, 'config.json')

    def get_api_key():
        # Try to read the API key from config file
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            api_key = config.get("NASA_API_KEY", "DEMO_KEY")
            if api_key == "DEMO_KEY":
                raise Exception("API KEY MUST NOT BE DEMO KEY")
            return api_key
        except Exception:
            return prompt_for_api_key()

    def prompt_for_api_key():
        def write_api_key():
            API_KEY = api_key_dialog.get()
            data_to_write = {"NASA_API_KEY": API_KEY, "last_update": "", "auto_update": True}
            with open(config_path, "w") as f:
                json.dump(data_to_write, f, indent=2)
            root.destroy()

        os.makedirs(apod_folder, exist_ok=True)
        if not os.path.exists(config_path):
            with open(config_path, "w") as f:
                json.dump({"NASA_API_KEY": "DEMO_KEY", "last_update": "", "auto_update": True}, f, indent=2)

        root = tk.Tk()
        root.title("Enter NASA API Key")
        root.geometry("300x100")
        set_window_icon(root)

        api_key_dialog = tk.Entry(root, width=50)
        api_key_dialog.insert(0, "Enter your NASA API key here")
        api_key_dialog.pack(padx=10, pady=10)

        submit_button = tk.Button(root, text="OK", command=write_api_key)
        submit_button.pack(pady=5)

        root.mainloop()

        with open(config_path, "r") as f:
            config = json.load(f)
        return config.get("NASA_API_KEY", "DEMO_KEY")

    API_KEY = get_api_key()

    def get_config():
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except:
            return {"NASA_API_KEY": API_KEY, "last_update": "", "auto_update": True}

    def save_config(config_data):
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)

    def get_apod_with_date(date=None, silent=False):
        url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"
        if date:
            url += f"&date={date}"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data.get("media_type") == "image":
                image_url = data["url"]
                image_response = requests.get(image_url, timeout=60)
                image_response.raise_for_status()
                ext = os.path.splitext(image_url)[1]
                timestamp = datetime.now().strftime("%Y%m%d")
                image_path = os.path.join(apod_folder, f"apod_{timestamp}{ext}")
                with open(image_path, "wb") as f:
                    f.write(image_response.content)
                
                if not silent:
                    print(f"Image downloaded to {image_path}")
                
                # Update last update date
                config = get_config()
                config["last_update"] = datetime.now().strftime("%Y-%m-%d")
                save_config(config)
                
                return image_path
            else:
                if not silent:
                    print("APOD is not an image.")
                return None
        except Exception as e:
            if not silent:
                print(f"Error downloading APOD: {e}")
            return None

    def set_apod_as_wallpaper(image_path):
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 0)

    def check_and_update_wallpaper():
        """Check if we need to update the wallpaper and do it silently"""
        config = get_config()
        if not config.get("auto_update", True):
            return
        
        last_update = config.get("last_update", "")
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Only update if we haven't updated today
        if last_update != today:
            image_path = get_apod_with_date(silent=True)
            if image_path:
                set_apod_as_wallpaper(image_path)
                print(f"Wallpaper automatically updated at {datetime.now()}")
            else:
                # Try yesterday's image
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                image_path = get_apod_with_date(yesterday, silent=True)
                if image_path:
                    set_apod_as_wallpaper(image_path)
                    print(f"Wallpaper updated with yesterday's image at {datetime.now()}")

    def create_image(width=64, height=64, color1="blue", color2="white"):
        """Create a simple icon for the system tray"""
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle([width // 4, height // 4, width * 3 // 4, height * 3 // 4], fill=color2)
        return image

    def manual_update():
        """Manually update wallpaper"""
        image_path = get_apod_with_date()
        if image_path:
            set_apod_as_wallpaper(image_path)
            show_notification("Success!", "Wallpaper updated successfully!")
        else:
            # Try yesterday's image
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            image_path = get_apod_with_date(yesterday)
            if image_path:
                set_apod_as_wallpaper(image_path)
                show_notification("Success!", "Updated with yesterday's image!")
            else:
                show_notification("Error", "Could not update wallpaper")

    def toggle_auto_update():
        """Toggle automatic updates on/off"""
        config = get_config()
        config["auto_update"] = not config.get("auto_update", True)
        save_config(config)
        status = "enabled" if config["auto_update"] else "disabled"
        show_notification("Settings", f"Auto-update {status}")

    def show_notification(title, message):
        """Show a simple notification"""
        def create_notification():
            # Create a new Tk instance for the notification
            notification_root = tk.Tk()
            notification_root.title(title)
            notification_root.geometry("300x100+{}+{}".format(
                notification_root.winfo_screenwidth() - 320,
                notification_root.winfo_screenheight() - 120
            ))
            notification_root.attributes("-topmost", True)
            notification_root.attributes("-toolwindow", True)  # Prevents taskbar entry
            notification_root.resizable(False, False)
            
            # Set the icon
            set_window_icon(notification_root)
            
            # Add the message
            label = tk.Label(notification_root, text=message, wraplength=280, justify="center")
            label.pack(pady=20)
            
            # Add OK button
            ok_button = tk.Button(notification_root, text="OK", command=notification_root.destroy)
            ok_button.pack(pady=(0, 10))
            
            # Auto-close after 5 seconds
            notification_root.after(5000, notification_root.destroy)
            
            # Center and focus
            notification_root.focus_force()
            notification_root.lift()
            
            # Run the notification window
            notification_root.mainloop()
        
        # Run in a separate thread to avoid blocking the system tray
        import threading
        threading.Thread(target=create_notification, daemon=True).start()

    def quit_app(icon, item):
        """Quit the application"""
        icon.stop()

    def setup_system_tray():
        """Create system tray icon and menu"""
        # Create a simple icon
        image = Image.open("assets/icon.png") if os.path.exists("assets/icon.png") else create_image()
        image = image.resize((256, 256))

        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem("Update Wallpaper", manual_update),
            pystray.MenuItem("Toggle Auto-Update", toggle_auto_update),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", quit_app)
        )
        
        # Create and run icon
        icon = pystray.Icon("APOD Wallpaper", image, "APOD Wallpaper", menu)
        return icon

    def run_scheduler():
        """Run the background scheduler"""
        # Schedule checks every hour
        schedule.every().hour.do(check_and_update_wallpaper)
        
        # Also schedule a daily check at 9 AM
        schedule.every().day.at("09:00").do(check_and_update_wallpaper)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def main():
        """Main function to start the background service"""
        # Check for initial update
        check_and_update_wallpaper()
        
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # Setup and run system tray
        icon = setup_system_tray()
        icon.run()

    if __name__ == "__main__":
        # Set up the root window (hidden)
        root = tk.Tk()
        root.withdraw()
        
        # Set the window icon
        set_window_icon(root)
        
        # Run the main function
        main()

else:
    # Non-Windows OS message
    root = tk.Tk()
    root.title("Incorrect OS")
    root.geometry("300x175")
    set_window_icon(root)

    errorLabel = tk.Label(root, text="This program currently only supports Windows, \n but we are looking to add \nmultiplatform support in a later update.")
    errorLabel.place(relx=0.1, rely=0, anchor="nw")

    sorryLabel = tk.Label(root, text="Sorry!", font=("arial", 40))
    sorryLabel.place(relx = 0.27, rely=0.35)

    closeButton = tk.Button(root, text="Exit Application", command=root.destroy)
    closeButton.place(relx=0.37, rely=0.8, anchor="nw")

    # Set the window icon
    set_window_icon(root)

    root.mainloop()