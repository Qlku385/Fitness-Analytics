import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from goal_service import load_user, load_weight_log
from workout_tracker import get_workout_history
from calculators import calculate_goal_progress

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "charts")

def _ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def plot_weight_progress(save_path=None):
    data = load_user()
    goal = data["goal"]
    log = load_weight_log()

    dates = [goal.get("start_date", "start")] + [entry["date"] for entry in log]
    weights = [goal["start_weight_lbs"]] + [entry["weight_lbs"] for entry in log]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(dates, weights, marker="o", label="weight (lbs)")
    ax.axhline(goal["target_weight_lbs"], color="green", linestyle="--", label="Target")
    ax.set_title("Weight Progress")
    ax.set_xlabel("Date")
    ax.set_ylabel("Weight (lbs)")
    ax.legend()
    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()

    _ensure_output_dir()
    save_path = save_path or os.path.join(OUTPUT_DIR, "weight_progress.png")
    fig.savefig(save_path)
    plt.close(fig)
    print(f"Saved weight progress chart to {save_path}")
    return save_path

def plot_workout_volume(save_path = None):
    workouts = get_workout_history()
    if not workouts:
        print("No workouts logged yet - nothing to plot")
        return None
    dates = [w["date"] for w in workouts]
    volumes = [w.get("volume", 0) for w in workouts]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(dates, volumes, color = "steelblue")
    ax.set_title("workout Volume Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Volume (reps x weight, lbs)")
    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()

    _ensure_output_dir()
    save_path = save_path or os.path.join(OUTPUT_DIR, "workout_volume.png")
    fig.savefig(save_path)
    plt.close(fig)
    print(f"Saved workout volume chart to {save_path}")
    return save_path

def print_goal_summary():
    data = load_user()
    goal = data["goal"]
    log = load_weight_log()
    current_weight = log[-1]["weight_lbs"] if log else goal["start_weight_lbs"]

    progress_pct = calculate_goal_progress(
        goal["start_weight_lbs"], current_weight, goal["target_weight_lbs"]
    )

    print("\n--- Goal Progress ---")
    print(f"Start weight: {goal['start_weight_lbs']} lbs")
    print(f"Current weight: {current_weight} lbs")
    print(f"Target weight: {goal['target_weight_lbs']} lbs") 
    print(f"Timeline: {goal['timeline_weeks']} weeks")
    print(f"Progress: {progress_pct}%")