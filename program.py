#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
from pathlib import Path

from updater import SelfUpdater
from config import Config


class NameTagApplication:
    """
    Main application class that demonstrates the self-updating capability
    
    In a real application, this would contain your actual business logic
    For demo purposes, it shows a simple counter application
    """
    
    def __init__(self):
        self.config = Config()
        self.setup_logging()

        self.updater = SelfUpdater(self.config)
        
        self.counter = 0
        
    def setup_logging(self):
        """Setup logging configuration"""
        # TODO: In production, configure file-based logging with rotation,
        # structured logging (JSON), and proper log levels per environment
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def run_application(self):
        """Main application logic"""
        self.logger.info(f"Starting NameTag Application v{self.config.VERSION}")
        
        # Start periodic update checking
        self.updater.start_periodic_checking(restart_callback=self._restart_application)
        
        print("="*50)
        print(f"{self.config.APP_NAME} Application - Self-Updating Demo")
        print(f"Version: {self.config.VERSION}")
        print("="*50)
        
        try:
            while True:
                self.counter += 1
                self.logger.info(f"Running... Version: {self.config.VERSION} Counter: {self.counter}")
                time.sleep(5)
                    
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
            
    def _restart_application(self):
        """Restart the application after an update"""
        self.logger.info("Restarting application...")
        os.execl(sys.executable, *sys.argv)


def main():
    """Application entry point"""
    app = NameTagApplication()
    app.run_application()


if __name__ == "__main__":
    main()
