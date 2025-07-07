import os
import json
import requests
import tkinter as tk
import ctypes

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
        # If file/folder missing or DEMO_KEY, prompt user
        return prompt_for_api_key()

def prompt_for_api_key():
    def write_api_key():
        API_KEY = api_key_dialog.get()
        data_to_write = {"NASA_API_KEY": API_KEY}
        with open(config_path, "w") as f:
            json.dump(data_to_write, f, indent=2)
        root.destroy()

    os.makedirs(apod_folder, exist_ok=True)
    # Write DEMO_KEY as placeholder if file doesn't exist
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump({"NASA_API_KEY": "DEMO_KEY"}, f, indent=2)

    root = tk.Tk()
    root.title("Enter NASA API Key")

    root.geometry("300x100")
    root.title("Missing API Key")

    api_key_dialog = tk.Entry(root, width=100)
    api_key_dialog.insert(0, "API KEY HERE")
    api_key_dialog.pack(padx=10, pady=10)

    submit_button = tk.Button(root, text="OK", command=write_api_key)
    submit_button.pack(pady=5)

    root.mainloop()

    # After dialog, read the new key
    with open(config_path, "r") as f:
        config = json.load(f)
    return config.get("NASA_API_KEY", "DEMO_KEY")

API_KEY = get_api_key()

def get_apod():
    return get_apod_with_date()

def get_apod_with_date(date=None):
    url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"
    if date:
        url += f"&date={date}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("media_type") == "image":
            image_url = data["url"]
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            ext = os.path.splitext(image_url)[1]
            image_path = os.path.join(apod_folder, f"apod{ext}")
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            print(f"Image downloaded to {image_path}")
            return image_path
        else:
            print("APOD is not an image.")
            return None
    except Exception as e:
        def end():
            root.destroy()
            exit()
        root = tk.Tk()
        root.title("Error!")
        root.geometry("300x100")
        exceptionLabel = tk.Label(root, text=f"An exception occured: {e}")
        exceptionLabel.pack()
        okButton = tk.Button(root, text="Ok", command=end)
        okButton.pack()
        root.mainloop()

def get_yesterday_date():
    from datetime import datetime, timedelta
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def set_apod_as_wallpaper(image_path):
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 0)


# get the apod
image_path = get_apod()
print('ladies and gentlemen, we gottem (the apod)')


# check if video
if image_path is None:
    def end():
        root.destroy()
        exit()

    def download_yesterday():
        yesterday = get_yesterday_date()
        img_path = get_apod_with_date(yesterday)
        if img_path:
            set_apod_as_wallpaper(img_path)
            root.destroy()
            show_success()
        else:
            tk.messagebox.showerror("Error", "Yesterday's APOD is also not an image.")

    def show_success():
        success_root = tk.Tk()
        success_root.title("Success!")
        success_root.geometry("300x100")
        label = tk.Label(success_root, text="Yesterday's wallpaper has been set :D")
        label.pack()
        okButton = tk.Button(success_root, text="Ok", command=success_root.destroy)
        okButton.pack()
        success_root.mainloop()

    root = tk.Tk()
    root.title("APOD Is Video")
    root.geometry("350x120")

    alertLabel = tk.Label(root, text="APOD for the day is a video.\nWould you like to download yesterday's image instead?")
    alertLabel.pack(pady=10)

    okButton = tk.Button(root, text="Ok", command=end)
    okButton.pack(side="left", padx=20, pady=10)

    downloadButton = tk.Button(root, text="Download Yesterday's Image", command=download_yesterday)
    downloadButton.pack(side="right", padx=20, pady=10)

    root.mainloop()
else:
    # yay
    # set it as the wallpaper
    set_apod_as_wallpaper(image_path)

# notify the user that it has been set as the wallpaper

def end():
    root.destroy()
    exit()

root = tk.Tk()
root.title("Success!")
root.geometry("300x100")

label = tk.Label(root, text="Your wallpaper has beeen set :D")
label.pack()

okButton = tk.Button(root, text="Ok", command=end)
okButton.pack()

root.mainloop()