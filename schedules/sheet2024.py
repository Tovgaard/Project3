import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# Setup Google Sheets API credentials
def setup_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('schedules/Credentials/dh-sheets-cd85d22bf527.json', scope)
    client = gspread.authorize(creds)
    return client

# Get schedule for a person on specified days with retry mechanism
def get_schedule(person_name, sheet, name_cells, days_to_fetch, max_retries=3):
    try:
        person_col = name_cells.index(person_name) + 12  # Column L is index 12
    except ValueError:
        return f"Person {person_name} not found."

    # Updated day ranges for each day
    days_ranges = {
        'friday': (10, 49),
        'saturday': (51, 93),
        'sunday': (95, 132)
    }

    schedule = {}

    for day, (start, end) in days_ranges.items():
        if day in days_to_fetch:
            retries = 0
            while retries < max_retries:
                try:
                    # Fetch all cells for the person in the given range
                    day_cells = sheet.col_values(person_col)[start-1:end]
                    time_cells = sheet.col_values(8)[start-1:end]  # Column H for times
                    task_cells = sheet.col_values(9)[start-1:end]  # Column I for activities
                    tasks = [
                        f"{task_time} | {task_activity}" 
                        for task_time, task_activity, cell in zip(time_cells, task_cells, day_cells) if cell.lower() == 'x'
                    ]
                    schedule[day.capitalize()] = tasks
                    break  # Exit the retry loop if successful
                except gspread.exceptions.APIError as e:
                    retries += 1
                    print(f"Error encountered (attempt {retries}): {e}")
                    if retries < max_retries:
                        print("Retrying...")
                        time.sleep(2 * retries)  # Exponential backoff
                    else:
                        print("Max retries reached. Skipping this day.")
                        schedule[day.capitalize()] = "Error fetching data"
    
    return schedule

# Function to get schedules for multiple people with delay
def get_schedules(names=None, days_to_fetch=None, sleep_time=5):
    client = setup_google_sheets()
    # Open the specified sheet and worksheet
    sheet = client.open('Kopi af [DHSTHML24] Creator Hub Master Sheet').worksheet('Schedule DATA')
    
    # Fetch all names from row 8, starting from column L and onward
    name_cells = sheet.row_values(8)[11:]  # Column L is index 11 (0-based)

    # If no names are provided, fetch schedule for all people
    if not names:
        names = name_cells

    results = {}
    
    # Open the output file in write mode
    with open("schedules/schedules.txt", "w") as file:
        for name in names:
            schedule = get_schedule(name.strip(), sheet, name_cells, days_to_fetch)
            results[name] = schedule

            # Write each entry in the desired format
            if isinstance(schedule, dict):
                for day, tasks in schedule.items():
                    if tasks:
                        for task in tasks:
                            task_time, activity = task.split(" | ")
                            file.write(f"{name} | {day} | {task_time} | {activity}\n")
                    else:
                        file.write(f"{name} | {day} | No tasks\n")
            else:
                file.write(f"{schedule}\n")  # Error message if person not found
            
            # Flush the file buffer to ensure data is written immediately
            file.flush()
            
            # Delay to prevent hitting API rate limits
            time.sleep(sleep_time)

    return results

# This function formats schedules for printing to console
def format_schedules(schedules):
    result = ""
    for person, schedule in schedules.items():
        if isinstance(schedule, dict):
            for day, tasks in schedule.items():
                if tasks:
                    for task in tasks:
                        task_time, activity = task.split(" | ")
                        result += f"{person} | {day} | {task_time} | {activity}\n"
                else:
                    result += f"{person} | {day} | No tasks\n"
        else:
            result += f"{schedule}\n"  # Error message if person not found
    return result.strip()

# Main function to get input and print schedules
if __name__ == "__main__":
    # Prompt the user for days (comma-separated)
    input_days = input("Enter the days you want to fetch (Friday, Saturday, Sunday, or all): ").lower().strip()
    
    # Parse the days to fetch
    days_to_fetch = [day.strip() for day in input_days.split(',')] if input_days != 'all' else ['friday', 'saturday', 'sunday']
    
    # Set sleep time based on number of days
    sleep_time = 2 if len(days_to_fetch) == 1 else 5
    
    # Prompt the user for names (comma-separated)
    input_names = input("Enter the names of the people (comma-separated), or leave blank for all: ")
    
    # Split the input by commas, or set names to None if blank
    names = [name.strip() for name in input_names.split(',')] if input_names else None

    # Print the names and days that will be processed
    print(f"Processing schedules for days: {', '.join(days_to_fetch).capitalize()}")
    if names:
        print(f"Processing schedules for: {', '.join(names)}")
    else:
        print("Processing schedules for all people.")

    # Fetch schedules with dynamic sleep time
    schedules = get_schedules(names, days_to_fetch, sleep_time)
    
    # Only print schedules to console if specific names were provided
    if names:
        print(format_schedules(schedules))
