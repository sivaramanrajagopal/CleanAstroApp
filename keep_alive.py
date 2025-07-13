import requests
import time
import threading
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KeepAlive:
    def __init__(self, app_url=None):
        """
        Initialize the keep-alive utility
        
        Args:
            app_url (str): The URL of your Render app (e.g., 'https://your-app.onrender.com')
        """
        self.app_url = app_url or os.environ.get('RENDER_APP_URL')
        self.is_running = False
        self.thread = None
        
        # Auto-detect Render app URL if not provided
        if not self.app_url:
            self.app_url = self._detect_render_url()
            
        if not self.app_url:
            logger.warning("No app URL provided and could not auto-detect. Keep-alive will not start.")
            return
            
        # Add trailing slash if not present
        if not self.app_url.endswith('/'):
            self.app_url += '/'
    
    def _detect_render_url(self):
        """Auto-detect the Render app URL from environment variables"""
        # Check for Render-specific environment variables
        render_app_name = os.environ.get('RENDER_APP_NAME')
        render_service_name = os.environ.get('RENDER_SERVICE_NAME')
        render_external_url = os.environ.get('RENDER_EXTERNAL_URL')
        
        if render_external_url:
            logger.info(f"Detected Render URL: {render_external_url}")
            return render_external_url
        elif render_app_name and render_service_name:
            # Construct URL from app and service names
            url = f"https://{render_app_name}-{render_service_name}.onrender.com"
            logger.info(f"Constructed Render URL: {url}")
            return url
        else:
            logger.warning("Could not auto-detect Render URL. Set RENDER_APP_URL environment variable manually.")
            return None
    
    def ping_server(self):
        """Ping the server to keep it alive"""
        if not self.app_url:
            logger.error("Cannot ping: No app URL configured")
            return
            
        try:
            response = requests.get(self.app_url, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Ping successful at {datetime.now().strftime('%H:%M:%S')}")
            else:
                logger.warning(f"⚠️ Ping returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ping failed: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error during ping: {e}")
    
    def keep_alive_loop(self):
        """Main loop that pings the server every 40 seconds"""
        logger.info(f"🚀 Starting keep-alive service for {self.app_url}")
        logger.info("⏰ Will ping every 40 seconds to prevent inactivity timeout")
        
        while self.is_running:
            self.ping_server()
            time.sleep(40)  # Wait 40 seconds before next ping
    
    def start(self):
        """Start the keep-alive service in a background thread"""
        if not self.app_url:
            logger.error("Cannot start keep-alive: No app URL configured")
            return False
            
        if self.is_running:
            logger.warning("Keep-alive service is already running")
            return False
        
        self.is_running = True
        self.thread = threading.Thread(target=self.keep_alive_loop, daemon=True)
        self.thread.start()
        logger.info("✅ Keep-alive service started successfully")
        return True
    
    def stop(self):
        """Stop the keep-alive service"""
        if not self.is_running:
            logger.warning("Keep-alive service is not running")
            return
        
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("🛑 Keep-alive service stopped")
    
    def is_alive(self):
        """Check if the keep-alive service is running"""
        return self.is_running and self.thread and self.thread.is_alive()

# Global instance
keep_alive_service = None

def start_keep_alive(app_url=None):
    """Start the keep-alive service"""
    global keep_alive_service
    
    if keep_alive_service and keep_alive_service.is_alive():
        logger.warning("Keep-alive service is already running")
        return keep_alive_service
    
    keep_alive_service = KeepAlive(app_url)
    success = keep_alive_service.start()
    
    if success:
        logger.info("🎯 Keep-alive service initialized and started")
    else:
        logger.error("❌ Failed to start keep-alive service")
    
    return keep_alive_service

def stop_keep_alive():
    """Stop the keep-alive service"""
    global keep_alive_service
    
    if keep_alive_service:
        keep_alive_service.stop()
        keep_alive_service = None
        logger.info("🛑 Keep-alive service stopped")

# Auto-start if this module is imported and running on Render
if __name__ == "__main__":
    # Test the keep-alive service
    service = start_keep_alive()
    
    if service and service.is_alive():
        print("Keep-alive service is running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_keep_alive()
            print("\nKeep-alive service stopped.")
    else:
        print("Failed to start keep-alive service. Check your configuration.") 