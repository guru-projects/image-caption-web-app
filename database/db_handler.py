import json
import os
from config.config import METADATA_FILE, FEEDBACK_FILE

# METADATA HANDLING
def load_metadata():
    if not os.path.exists(METADATA_FILE):
        save_metadata({})
    with open(METADATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            save_metadata({})
            return {}

def save_metadata(metadata):
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=4)

def remove_image_metadata(filename):
    metadata = load_metadata()
    metadata.pop(filename, None)
    save_metadata(metadata)

# FEEDBACK HANDLING
def load_feedback():
    if not os.path.exists(FEEDBACK_FILE):
        save_feedback({"entries": []})
    with open(FEEDBACK_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            save_feedback({"entries": []})
            return {"entries": []}

def save_feedback(feedback_data):
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(feedback_data, f, indent=4)
