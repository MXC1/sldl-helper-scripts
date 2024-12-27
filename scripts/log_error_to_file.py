from datetime import datetime
import os

def log_error_to_file(script_name, error_message):
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    # Ensure the error_logs directory exists
    os.makedirs("error_logs", exist_ok=True)

    # Set the error log file path
    error_log_file = f"error_logs/{today_date}_errors.txt"

    # Append error to the file
    with open(error_log_file, "a") as file:
        file.write("--------------------------------------------------\n")
        file.write(f"{script_name}\n")
        file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        file.write("Error log:\n")
        file.write(f"{error_message}\n\n")