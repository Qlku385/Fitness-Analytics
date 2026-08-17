import json
import os
import random
import sys
from datetime import date, timedelta

import pandas as pd

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_DIR)

from calculators import calculate_bmr, calculate_tdee, calculate_calorie_goal
from goal_service import ACTIVITY_MULTIPLIERS
from diet_planner import calculate_macros

random.seed(42)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(OUT_DIR, exist_ok=True)

with open(os.path.join(APP_DIR, "data", "user.json")) as f:
    profile = json.load(f)
with open(os.path.join(APP_DIR, "data", "exercises.json")) as f:
    exercise_db = json.load(f)

user = profile["user"]
goal = profile["goal"]

START_DATE = date(2026, 5, 11)
WEEKS = goal["timeline_weeks"]
END_DATE = START_DATE + timedelta(weeks = WEEKS)

start_weight = goal["start_weight_lbs"]
target_weight = goal["target_weight_lbs"]
total_loss = start_weight - target_weight

weight_rows = []
weigh_in_days = {0,2,4}
current_weight = start_weight
day_counter = 0
total_days = (END_DATE - START_DATE).days

for i in range(total_days + 1):
    d = START_DATE + timedelta(days=i)
    weekday = d.weekday()
    week_num = i // 7

    weekly_rate = total_loss / WEEKS
    if week_num in (4,5):
        weekly_rate *= 0.3
    elif week_num in (10,11):
        weekly_rate *= 1.2

    daily_drift = -weekly_rate / 7
    noise = random.uniform(-0.4, 0.4)
    current_weight = current_weight + daily_drift + noise

    if weekday in weigh_in_days:
        weight_rows.append({"date": d.isoformat(), "weight_lbs": round(current_weight, 1)})

weight_rows[-1]["weight_lbs"] = round(target_weight + 0.8, 1)
weight_df = pd.DataFrame(weight_rows)
weight_df.to_csv(os.path.join(OUT_DIR, "fact_weight_log.csv"), index = False)

PUSH_TEMPLATES = [
    [("chest", "upper_chest"), ("shoulders", "front_delt"), ("tricep", "lateral_medial")],
    [("chest", "mid_chest"), ("shoulders", "side_delt"), ("tricep", "long_head")],
    [("chest", "lower_chest"), ("shoulders", "rear_delt"), ("tricep", "lateral_medial")]
]

PULL_TEMPLATES = [
    [("back","upper_back"), ("back", "lats"), ("bicep", "supinated"), ("bicep", "nuetral")],
    [("back", "traps"), ("back", "lats"), ("bicep", "supinated"), ("bicep", "nuetral")],
    [("back", "lower_back"), ("back", "lats"), ("bicep", "supinated"), ("bicep", "nuetral")],
]

LEGS_TEMPLATES = [
    [("legs", "quads"), ("legs", "hamstrings"), ("legs", "glutes")],
    [("legs", "hamstrings"), ("legs", "glutes"), ("legs", "calves")]
]

DAY_TYPE = {
    0: "push",
    1: "pull",
    2: "legs",
    3: "push",
    4: "pull",
    5: "legs"
}

TEMPLATES= {"push": PUSH_TEMPLATES, "pull": PULL_TEMPLATES, "legs": LEGS_TEMPLATES}
template_counters = {"push": 0, "pull": 0, "legs": 0}

BASE_WEIGHT={
    "chest": 115, "back": 120, "bicep":30, "tricep": 40,
    "shoulders": 35, "legs": 150
    }

workout_rows = []
set_rows = []
workout_id = 0

for i in range(total_days+1):
    d = START_DATE+ timedelta(days=i)
    weekday = d.weekday()
    week_num = 1 // 7

    if weekday not in DAY_TYPE:
        continue
    if random.random() < 0.12:
        continue

    day_type = DAY_TYPE[weekday]
    templates = TEMPLATES[day_type]
    template = templates[template_counters[day_type] % len(templates)]
    template_counters[day_type] += 1

    workout_id == 1
    session_sets = []
    total_volume = 0

    for muscle_group, subgroup in template:
        options = exercise_db[muscle_group][subgroup]
        exercise_name = random.choice(options)

        progression_bonus = (week_num // 2) * (BASE_WEIGHT[muscle_group] * 0.04)
        working_weight = BASE_WEIGHT[muscle_group] + progression_bonus

        n_sets = random.choice([3,4])
        for set_num in range(1, n_sets + 1):
            reps = random.randint(6,12)
            weight_lbs = round(working_weight + random.uniform(-5,5), 1)
            set_volume = reps * weight_lbs
            total_volume += set_volume
            session_sets.append({
                "workout_id": workout_id,
                "date": d.isoformat(),
                "muscle_group": muscle_group,
                "subgroup": subgroup,
                "exercise_name": exercise_name,
                "set_number": set_num,
                "reps": reps,
                "weight_lbs": weight_lbs,
                "set_volume": round(set_volume, 1)
                })
    set_rows.extend(session_sets)
    workout_rows.append({
        "workout_id": workout_id,
        "date": d.isoformat(),
        "day_type": day_type,
        "muscle_groups_trained": ",".join(sorted({s[0] for s in template})),
        "total_sets": len(session_sets),
        "total_volume": round(total_volume, 1),
        "duration_min": random.randint(40,75)
    })

pd.DataFrame(set_rows).to_csv(os.path.join(OUT_DIR, "fact_workout_sets.csv"), index = False)
pd.DataFrame(workout_rows).to_csv(os.path.join(OUT_DIR, "fact_workouts.csv"), index=False)

multiplier = ACTIVITY_MULTIPLIERS.get(user["activity_level"].lower(), 1.2)
weight_lookup = {row["date"]: row["weight_lbs"] for row in weight_rows}

calorie_rows = []
last_known_weight = start_weight
for i in range(total_days +1):
    d = START_DATE + timedelta(days = i)
    iso = d.isoformat()
    if iso in weight_lookup:
        last_known_weight = weight_lookup[iso]
    
    bmr = calculate_bmr(last_known_weight, user["height_in"], user["age"], user["sex"])
    tdee = calculate_tdee(bmr, multiplier)
    target = calculate_calorie_goal(tdee, goal["type"])
    macros = calculate_macros(target, last_known_weight, goal["type"])

    if random.random() < 0.15:
        logged = target + random.uniform(300, 700)
    else:
        logged = target + random.uniform(-150, 150)

    calorie_rows.append({
        "date": iso,
        "weight_lbs" : last_known_weight,
        "calorie_target": round(target),
        "calories_logged": round(logged),
        "protein_g_target": macros["protein_g"],
        "fat_g_target": macros["fat_g"],
        "carbs_g_target": macros["carbs_g"]
    })


pd.DataFrame(calorie_rows).to_csv(os.path.join(OUT_DIR, "fact_calorie_log.csv"), index=False)

dim_dates = []
for i in range(total_days + 1):
    d = START_DATE + timedelta(days = i)
    dim_dates.append({
        "date": d.isoformat(),
        "day_of_week": d.strftime("%A"),
        "week_number": (i // 7) + 1,
        "month": d.strftime("%B"),
        "is_weekend": d.weekday() >= 5
    })
pd.DataFrame(dim_dates).to_csv(os.path.join(OUT_DIR, "dim_date.csv"), index = False)
dim_exercises = []
for muscle_group, subgroups in exercise_db.items():
    for subgroup, names in subgroups.items():
        for name in names:
            dim_exercises.append({
                "exercise_name": name,
                "muscle_group": muscle_group,
                "subgroup": subgroup,
            })

pd.DataFrame(dim_exercises).to_csv(os.path.join(OUT_DIR, "dim_exercises.csv"), index=False)

goal_summary = pd.DataFrame([{
    "goal_type": goal["type"],
    "start_date": START_DATE.isoformat(),
    "end_date": END_DATE.isoformat(),
    "timeline_weeks":WEEKS,
    "start_weight_lbs": start_weight,
    "target_weight_lbs": target_weight,
    "final_logged_weight_lbs": weight_rows[-1]["weight_lbs"]
}])
goal_summary.to_csv(os.path.join(OUT_DIR, "goal_summary.csv"), index=False)

print("Done. Files written to:", OUT_DIR)
for fname in sorted(os.listdir(OUT_DIR)):
    print(" -", fname)