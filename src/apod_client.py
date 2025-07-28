"""
NASA APOD API integration
"""
import os
import requests
import random
from datetime import datetime, timedelta


class APODClient:
    def __init__(self, api_key, apod_folder):
        self.api_key = api_key
        self.apod_folder = apod_folder
        self.base_url = "https://api.nasa.gov/planetary/apod"
    
    def get_apod_data(self, date=None, hd=True, random_date=False):
        """Get APOD data from NASA API"""
        url = f"{self.base_url}?api_key={self.api_key}"
        
        if random_date:
            # Generate a random date between APOD start date (1995-06-16) and today
            start_date = datetime(1995, 6, 16)
            end_date = datetime.now()
            time_between = end_date - start_date
            days_between = time_between.days
            random_days = random.randrange(days_between)
            random_date_obj = start_date + timedelta(days=random_days)
            date = random_date_obj.strftime("%Y-%m-%d")
        
        if date:
            url += f"&date={date}"
        
        if hd:
            url += "&hd=true"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch APOD data: {e}")
    
    def download_image(self, date=None, silent=False, hd=True, random_date=False):
        """Download APOD image for a specific date"""
        try:
            data = self.get_apod_data(date, hd, random_date)
            
            if data.get("media_type") != "image":
                if not silent:
                    print("APOD is not an image.")
                return None
            
            # Use HD URL if available and requested, otherwise use regular URL
            if hd and "hdurl" in data:
                image_url = data["hdurl"]
            else:
                image_url = data["url"]
            
            image_response = requests.get(image_url, timeout=60)
            image_response.raise_for_status()
            
            # Generate filename
            ext = os.path.splitext(image_url)[1]
            if date:
                timestamp = date.replace("-", "")
            elif random_date:
                timestamp = data.get("date", datetime.now().strftime("%Y-%m-%d")).replace("-", "")
            else:
                timestamp = datetime.now().strftime("%Y%m%d")
            
            quality_suffix = "_hd" if hd and "hdurl" in data else ""
            image_path = os.path.join(self.apod_folder, f"apod_{timestamp}{quality_suffix}{ext}")
            
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
    
    def download_with_fallback(self, silent=False, hd=True, random_date=False):
        """Download today's APOD, fallback to yesterday if it's a video"""
        result = self.download_image(silent=silent, hd=hd, random_date=random_date)
        
        if result is None and not random_date:
            # Try yesterday's image (only if not using random date)
            yesterday = self.get_yesterday_date()
            result = self.download_image(yesterday, silent=silent, hd=hd)
            if result and not silent:
                print("Using yesterday's image as fallback")
        
        return result
