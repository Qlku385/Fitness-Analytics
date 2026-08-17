import json
import os
from calculators import (
    calculate_bmr,
    calculate_tdee,
    calculate_calorie_goal,
    calculate_goal_progress
    )

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USER_FILE = os.path.join(DATA_DIR, "user.json")
WEIGHT_LOG_FILE = os.path.join(DATA_DIR, "weight_log.json")

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "activate": 1.725,
    "very active": 1.9
}

def load_user():
    with open(USER_FILE, "r") as f:
        return json.load(f)
    
def load_weight_log():
    if not os.path.exists(WEIGHT_LOG_FILE):
        return[]
    with open(WEIGHT_LOG_FILE, "r") as f:
        return json.load(f)
    
def log_weight(date, weight_lbs):
    log = load_weight_log()
    log.append({"date": date, "weight_lbs": weight_lbs})
    with open(WEIGHT_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)
    return log

def get_current_weight(user_data=None):
    log = load_weight_log()
    if log:
        return log[-1]["weight_lbs"]
    if user_data is None:
        user_data = load_user()
    return user_data["user"]["weight_lbs"]

def generate_calorie_profile():
    data = load_user()
    user = data["user"]
    goal = data["goal"]

    weight = get_current_weight(data)
    height = user["height_in"]
    age = user["age"]
    sex = user["sex"]
    activity = user["activity_level"]

    multiplier = ACTIVITY_MULTIPLIERS.get(activity.lower(), 1.2)

    bmr = calculate_bmr(weight, height, age, sex)
    tdee = calculate_tdee(bmr, multiplier)
    calorie_target = calculate_calorie_goal(tdee,goal["type"])

    return{
        "bmr": round(bmr,2),
        "tdee": round(tdee,2),
        "calorie_target": round(calorie_target,2)
    }

def generate_goal_plan():
    data = load_user()
    goal = data["goal"]

    current_weight = get_current_weight(data)
    progress_pct = calculate_goal_progress(
        goal["start_weight_lbs"], current_weight, goal["target_weight_lbs"]
    )
    calorie_data = generate_calorie_profile()

    return{
        "goal_type": goal["type"],
        "start_weight_lbs": goal["start_weight_lbs"],
        "current_weight_lbs": current_weight,
        "target_weight_lbs": goal["target_weight_lbs"],
        "timeline_weeks": goal["timeline_weeks"],
        "progress_pct": progress_pct,
        **calorie_data,
    }