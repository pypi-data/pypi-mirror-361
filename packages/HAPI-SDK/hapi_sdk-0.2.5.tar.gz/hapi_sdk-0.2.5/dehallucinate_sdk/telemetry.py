import os
import json
import datetime
import threading
import time
import requests

def init_telemetry_log(log_path="telemetry.log"):
    """
    Initializes the telemetry log file if it does not exist.
    Returns the log file path.
    """
    if not os.path.exists(log_path):
        with open(log_path, "w") as f:
            f.write("")
    return log_path

def report_usage(license_key, model_id, input_text, output_text, tokenizer, log_path="telemetry.log"):
    input_tokens = len(tokenizer.tokenize(input_text))
    output_tokens = len(tokenizer.tokenize(output_text))
    usage_data = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "model_id": model_id,
        "license_key": license_key, 
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(usage_data) + "\n")
    print("Telemetry:", usage_data)
    return usage_data

def send_telemetry(log_path, endpoint):

    try:
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                data = f.read().strip()
            if data:
                # Send telemetry data as JSON payload.
                response = requests.post(endpoint, json={"telemetry": data})
                print("Sent telemetry data, response status code:", response.status_code)
                if response.status_code == 200:
                    # Clear the log file after successful transmission.
                    with open(log_path, "w") as f:
                        f.write("")
    except Exception as e:
        print("Error sending telemetry data:", e)

def background_telemetry_reporter(log_path, endpoint, interval_minutes=10):
    """
    Background loop that sends telemetry data every 'interval_minutes' minutes.
    """
    while True:
        send_telemetry(log_path, endpoint)
        time.sleep(interval_minutes * 60)

def start_telemetry_reporter(log_path="telemetry.log", endpoint="http://your.telemetry.endpoint/collect", interval_minutes=2):
    thread = threading.Thread(target=background_telemetry_reporter, args=(log_path, endpoint, interval_minutes))
    thread.daemon = True 
    thread.start()
    print(f"Telemetry reporter started, sending data every {interval_minutes} minutes to {endpoint}")
    return thread
