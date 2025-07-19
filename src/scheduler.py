"""
Scheduling and background tasks for APODPaper
"""
import schedule
import time
import threading
from datetime import datetime


class Scheduler:
    def __init__(self, app_controller):
        self.app = app_controller
        self.running = False
        self.thread = None
    
    def setup_schedule(self):
        """Set up the scheduling tasks"""
        # Clear any existing jobs
        schedule.clear()
        
        # Schedule checks every hour
        schedule.every().hour.do(self.app.check_and_update_wallpaper)
        
        # Schedule daily check at 9 AM
        schedule.every().day.at("09:00").do(self.app.check_and_update_wallpaper)
        
        # You can add more scheduling options here based on user preferences
        config = self.app.config.get_config()
        frequency = config.get("update_frequency", "daily")
        
        if frequency == "6hours":
            schedule.every(6).hours.do(self.app.check_and_update_wallpaper)
        elif frequency == "12hours":
            schedule.every(12).hours.do(self.app.check_and_update_wallpaper)
    
    def run_scheduler(self):
        """Main scheduler loop"""
        self.running = True
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def start(self):
        """Start the scheduler in a background thread"""
        if not self.thread or not self.thread.is_alive():
            self.setup_schedule()
            self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.thread.start()
            print("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        print("Scheduler stopped")
