from database.db_handler import load_feedback, save_feedback

def submit_feedback(name, feedback):
    feedback_data = load_feedback()
    feedback_data["entries"].append({
        "name": name,
        "feedback": feedback
    })
    save_feedback(feedback_data)

def get_all_feedback():
    return load_feedback().get("entries", [])
