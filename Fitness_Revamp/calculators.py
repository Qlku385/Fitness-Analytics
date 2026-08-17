# things that need to be calculated
# BMI
##BMR and tdee for calorie deficit
# Progress toward goal
# Calorie deficit / Intake
# Starting weight for each workout

def calculate_bmi (weight_lbs, height_inches):
    return (weight_lbs / (height_inches ** 2)) * 703

def calculate_bmr(weight_lbs, height_inches, age, sex):
    weight_kg = weight_lbs * 0.453592
    height_cm = height_inches * 2.54
    if sex.lower() == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
def calculate_tdee(bmr, activity_multiplier):
    return bmr * activity_multiplier

def calculate_calorie_goal(tdee, goal_type):
    if goal_type == "lose":
        return tdee - 500
    elif goal_type == "gain":
        return tdee + 300
    else:
        return tdee
    
def calculate_goal_progress(start_weight, current_weight, target_weight):
    total_change = abs(start_weight - target_weight)
    completed_change = abs(start_weight - current_weight)

    if total_change == 0:
        return 100

    return round((completed_change / total_change) * 100, 1)

def calculate_workout_volume(workout):
    total = 0
    for exercise in workout.get("exercises", []):
        for s in exercise.get("sets", []):
            total += s.get("reps", 0) * s.get("weight_lbs", 0)
    return total