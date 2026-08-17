def calculate_macros(calories, weight_lbs, goal_type):
    if goal_type == "lose":
        protein = weight_lbs * 1.0
        fat = weight_lbs * 0.3
    
    elif goal_type == "gain":
        protein = weight_lbs * 0.8
        fat = weight_lbs * 0.4

    else:
        protein = weight_lbs * 0.9
        fat = weight_lbs * 0.35

    protein_cal = protein * 4
    fat_cal = fat * 9

    carb_cal = calories - (protein_cal + fat_cal)
    carbs = max(carb_cal, 0) / 4

    return {
        "protein_g": round(protein),
        "fat_g": round(fat),
        "carbs_g": round(carbs),
    }

def generate_diet_plan(weight_lbs, goal_type, calorie_target):

    macros = calculate_macros(calorie_target, weight_lbs, goal_type)

    return {
        "calories": round(calorie_target),
        "protein_g": macros["protein_g"],
        "fat_g": macros["fat_g"],
        "carbs_g": macros["carbs_g"]
    }