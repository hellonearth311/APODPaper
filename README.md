# 🌌 APODPaper

A lightweight Windows application that automatically sets your desktop wallpaper to NASA's stunning **Astronomy Picture of the Day (APOD)**. Wake up to breathtaking space imagery every single day!

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)

## ✨ Features

- 🚀 **Automatic Daily Updates**: Your wallpaper changes to the latest APOD every day at 9 AM
- 🖼️ **Smart Fallback**: If today's APOD is a video, automatically uses yesterday's image
- 🔄 **Manual Updates**: Right-click the system tray icon to update instantly
- ⚙️ **Background Operation**: Runs silently in your system tray
- 🎛️ **Auto-Update Toggle**: Enable/disable automatic updates as needed
- 💾 **Local Storage**: Images saved to your `%LOCALAPPDATA%\apodpaper` folder
- 🔐 **Secure API**: Uses your personal NASA API key (free to obtain)

## 🛠️ Installation

### Option 1: Download Executable (Recommended)
1. Download the latest release from the [Releases](../../releases) page
2. Run `APODPaper.exe`
3. Follow the setup instructions below

### Option 2: Run from Source
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/APODPaper.git
   cd APODPaper
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## 🔧 Setup

### 1. Get Your NASA API Key
1. Visit [NASA API Portal](https://api.nasa.gov/)
2. Click "Generate API Key"
3. Fill out the simple form (no verification required)
4. Copy your API key

### 2. First Run
1. Launch APODPaper
2. Enter your NASA API key when prompted
3. The app will minimize to your system tray
4. Your wallpaper will update automatically!

## 🎮 Usage

### System Tray Menu
Right-click the APODPaper icon in your system tray to access:

- **Update Wallpaper**: Manually fetch and set today's APOD
- **Toggle Auto-Update**: Enable/disable automatic daily updates
- **Quit**: Exit the application

### File Locations
- **Config & Images**: `%LOCALAPPDATA%\apodpaper\`
- **Configuration**: `config.json` (stores API key and settings)
- **Images**: `apod_YYYYMMDD.jpg/png` (daily APOD images)

## ⚙️ Configuration

The app automatically creates a configuration file at `%LOCALAPPDATA%\apodpaper\config.json`:

```json
{
  "NASA_API_KEY": "your_api_key_here",
  "last_update": "2025-07-18",
  "auto_update": true
}
```

## 🔍 Troubleshooting

### Common Issues

**App doesn't start/API key prompt doesn't appear:**
- Ensure you have an active internet connection
- Check Windows Defender hasn't quarantined the executable
- Try running as administrator

**Wallpaper doesn't update:**
- Verify your NASA API key is valid
- Check the system tray - the app should be running
- Try manually updating via the system tray menu

**"APOD is a video" issue:**
- The app automatically falls back to yesterday's image
- Some days NASA features videos instead of images
- This is normal behavior and handled automatically

### Manual Reset
To reset the application:
1. Close APODPaper completely
2. Delete the folder: `%LOCALAPPDATA%\apodpaper\`
3. Restart the application

## 🏗️ Building from Source

To create your own executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller main.spec
```

The executable will be created in the `dist/` folder.

## 📋 Requirements

- **OS**: Windows 7/8/10/11
- **Python**: 3.7+ (if running from source)
- **Internet**: Required for downloading APOD images
- **NASA API Key**: Free from [api.nasa.gov](https://api.nasa.gov/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NASA** for providing the amazing APOD API and imagery
- **Astronomy community** for inspiring this project
- **Contributors** who help improve this application

## 📞 Support

If you encounter any issues or have questions:
- Open an [Issue](../../issues) on GitHub
- Check the troubleshooting section above
- Ensure you're using the latest version

---

*Made with ❤️ for space enthusiasts everywhere*