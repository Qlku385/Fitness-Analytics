import json
import os
from datetime import date

from calculators import calculate_workout_volume

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
EXERCISES_FILE = os.path.join(DATA_DIR, "exercises.json")
WORKOUTS_FILE = os.path.join(DATA_DIR, "workouts.json")


##Data Access##

def load_exercises():
    with open(EXERCISES_FILE, "r") as f:
        return json.load(f)
    
def load_workouts():
    if not os.path.exists(WORKOUTS_FILE):
        return[
        ]
    with open(WORKOUTS_FILE, "r") as f:
        return json.load(f)
    
def save_workouts(workouts):
    with open(WORKOUTS_FILE, "w") as f:
        json.dump(workouts, f,)

##Exercise Loop##

def get_muscle_groups():
    return list(load_exercises().key())

def get_subgroups(muscle_group):
    exercises=load_exercises()
    return list(exercises.get(muscle_group, {}).key())

def get_exercises_by_muscle(muscle_group, subgroup=None):
    exercises = load_exercises()
    group = exercises.get(muscle_group, {})
    if subgroup:
        return group.get(subgroup, [])
    all_exercises = []
    for ex_list in group.values():
        all_exercises.extend(ex_list)
    return all_exercises

##Logging Workouts##

def log_workout(workout_date, exercises):
    workouts = load_workouts()
    workout = {
        "date": workout_date,
        "exercises": exercises
    }
    workout["volume"] = calculate_workout_volume(workout)
    workouts.append(workout)
    save_workouts(workouts)
    return workout

def get_workout_history():
    return load_workouts()

##Interactive CLI helpers##

def prompt_log_workout():
    print("\n--- Log a New Workout ---")
    workout_date = input("Date (YYYY-MM-DD) [enter for today]: ").strip()
    if not workout_date:
        workout_date = date.today().isoformat()
    
    exercises = []
    while True:
        muscle_groups = get_muscle_groups()
        print("\nMuscle groups:", ",".join(muscle_groups))
        muscle_group = input("Muscle group (or black to finish): ").strip().lower()
        if not muscle_group:
            break
        if muscle_group not in muscle_groups:
            print("Not a recognized muscle group, try again.")
            continue

        subgroups = get_subgroups(muscle_groups)
        print("Subgroups:",",".join(subgroups))
        subgroup = input("Subgroup (or blank for all): ").strip().lower()
        options = get_exercises_by_muscle(muscle_group, subgroup or None)

        if not options:
            print("No exercises found for that selection")

        print("Exercises:")
        for i, name in enumerate(options, 1):
            print(f" {i}. {name}")
        choice = input("Pick a number: ").strip()
        try:
            exercise_name = options[int(choice)-1]
        except (ValueError, IndexError):
            print("Invalid choice, skipping.")
            continue

        sets = []
        while True:
            set_input = input(
                "Enter set as 'reps weight' (e.g. '8 135'), or blank to stop adding sets: "
            ).strip()
            if not set_input:
                break
            try:
                reps_str, weight_str = set_input.split()
                sets.append({"reps": int(reps_str), "weight_lbs": float(weight_str)})
            except ValueError:
                print("Couldn't parse that, use format like '8 135'.")
            
        if sets:
            exercises.append(
                {"name": exercise_name, "muscle_group": muscle_group, "sets": sets}
            )
    
    if not exercises:
        print("No exercises logged, nothing saved.")
        return None
    
    workout = log_workout(workout_date, exercises)
    print(f"\nSaved workout for {workout_date} - total volume: {workout['volume']} lbs")
    return workout

def print_workout_history():
    workouts = get_workout_history()
    if not workouts:
        print("\nNo workouts logged yet.")
        return
    
    print("\n--- Workout History ---")
    for w in workouts:
        print(f"\n{w['date']} - volume: {w.get('volume', calculate_workout_volume(w))} lbs")
        for ex in w["exercises"]:
            set_summary = ",".join(
                f"{s['reps']}x{s['weight_lbs']}lbs" for s in ex["sets"]
            )
            print(f" {ex['name']}: {set_summary}")
