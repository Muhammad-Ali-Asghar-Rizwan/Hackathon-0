import time
import subprocess
import sys
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler_watcher.log'),
        logging.StreamHandler()
    ]
)

def run_orchestrator():
    """
    Function to run the orchestrator.py script
    """
    try:
        logging.info("Starting orchestrator.py execution...")
        result = subprocess.run(
            [sys.executable, 'orchestrator.py'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout for the orchestrator
        )
        if result.returncode == 0:
            logging.info("Orchestrator execution completed successfully")
        else:
            logging.error(f"Orchestrator execution failed with return code: {result.returncode}")
            logging.error(f"Error output: {result.stderr}")
    except subprocess.TimeoutExpired:
        logging.error("Orchestrator execution timed out after 5 minutes")
    except Exception as e:
        logging.error(f"Error running orchestrator: {str(e)}")

def main():
    """
    Main function to run the scheduler with infinite loop
    """
    logging.info("Scheduler Watcher started")
    logging.info("Running orchestrator.py every 5 minutes")
    logging.info("Press Ctrl+C to stop the scheduler")

    try:
        while True:
            # Print timestamp
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n--- Running orchestrator.py at {current_time} ---")

            # Run orchestrator
            run_orchestrator()

            # Sleep for 5 minutes (300 seconds)
            logging.info("Sleeping for 5 minutes before next run...")
            time.sleep(300)

    except KeyboardInterrupt:
        logging.info("\nScheduler stopped by user (Ctrl+C)")
        print("\nScheduler stopped. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error in scheduler: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()