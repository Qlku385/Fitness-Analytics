from goal_service import generate_goal_plan, log_weight
from diet_planner import generate_diet_plan
import workout_tracker as wt
import progress_visualizer as pv

def print_menu():
    print("\n==== Fitness Tracker ====")
    print("1. View calorie & macro plan")
    print("2. Log a workout")
    print("3. View workout history")
    print("4. Chart workout volume")
    print("5. Chart weight progress")
    print("6. Log today's weight")
    print("7. View goal progress")
    print("0. Exit")

def show_diet_plan():
    plan = generate_goal_plan()
    diet = generate_diet_plan(
        plan["current_weight_lbs"], plan["goal_type"], plan["calorie_target"]
    )
    print("\n--- Calorie & Macro Plan ---")
    print(f"Goal: {plan['goal_type']}")
    print(f"BMR: {plan['bmr']} kcal")
    print(f"TDEE: {plan['tdee']} kcal")
    print(f"Daily calorie target: {diet['calories']} kcal")
    print(f"Protein: {diet['protein_g']} g")
    print(f"Fat: {diet['fat_g']} g")
    print(f"Carbs: {diet['carbs_g']} g")

def log_todays_weight():
    from datetime import date
    weight = input("Current weight (lbs): ").strip()
    try:
        weight = float(weight)
    except ValueError:
        print("Please enter a number.")
        return
    today = date.today().isoformat()
    log_weight(today, weight)
    print(f"Logged {weight} lbs for {today}.")

def main():
    actions = {
        "1": show_diet_plan,
        "2": wt.prompt_log_workout,
        "3": wt.print_workout_history,
        "4": pv.plot_workout_volume,
        "5": pv.plot_weight_progress,
        "6": log_todays_weight,
        "7": pv.print_goal_summary
    }

    while True:
        print_menu()
        choice = input("> ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice, try again")

if __name__ == "__main__":
    main()