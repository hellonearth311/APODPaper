"""
NASA APOD API integration
"""
import os
import requests
from datetime import datetime, timedelta


class APODClient:
    def __init__(self, api_key, apod_folder):
        self.api_key = api_key
        self.apod_folder = apod_folder
        self.base_url = "https://api.nasa.gov/planetary/apod"
    
    def get_apod_data(self, date=None):
        """Get APOD data from NASA API"""
        url = f"{self.base_url}?api_key={self.api_key}"
        if date:
            url += f"&date={date}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch APOD data: {e}")
    
    def download_image(self, date=None, silent=False):
        """Download APOD image for a specific date"""
        try:
            data = self.get_apod_data(date)
            
            if data.get("media_type") != "image":
                if not silent:
                    print("APOD is not an image.")
                return None
            
            image_url = data["url"]
            image_response = requests.get(image_url, timeout=60)
            image_response.raise_for_status()
            
            # Generate filename
            ext = os.path.splitext(image_url)[1]
            if date:
                timestamp = date.replace("-", "")
            else:
                timestamp = datetime.now().strftime("%Y%m%d")
            
            image_path = os.path.join(self.apod_folder, f"apod_{timestamp}{ext}")
            
            # Save image
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            
            if not silent:
                print(f"Image downloaded to {image_path}")
            
            return image_path, data
            
        except Exception as e:
            if not silent:
                print(f"Error downloading APOD: {e}")
            return None
    
    def get_yesterday_date(self):
        """Get yesterday's date in YYYY-MM-DD format"""
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    def download_with_fallback(self, silent=False):
        """Download today's APOD, fallback to yesterday if it's a video"""
        result = self.download_image(silent=silent)
        
        if result is None:
            # Try yesterday's image
            yesterday = self.get_yesterday_date()
            result = self.download_image(yesterday, silent=silent)
            if result and not silent:
                print("Using yesterday's image as fallback")
        
        return result
