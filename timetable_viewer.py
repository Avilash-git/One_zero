import pandas as pd
import os

print("Timetable Viewer - Display Individual Timetables")
print("=" * 60)

def display_menu():
    """Display menu options"""
    print("\nSelect Timetable Type:")
    print("1. View Class Timetable")
    print("2. View Faculty Timetable") 
    print("3. View Department Timetable")
    print("4. View Summary Reports")
    print("5. Show Available Files")
    print("6. Exit")
    return input("\nEnter your choice (1-6): ")

def list_files_in_directory(directory):
    """List all CSV files in a directory"""
    try:
        files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        return sorted(files)
    except FileNotFoundError:
        return []

def display_timetable_formatted(df, title):
    """Display timetable in a formatted way"""
    print(f"\n{title}")
    print("=" * 80)
    
    if len(df) == 0:
        print("No sessions found.")
        return
    
    # Group by day for better display
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    for day in days:
        day_schedule = df[df['Day'] == day]
        if len(day_schedule) > 0:
            print(f"\n{day.upper()}")
            print("-" * 40)
            
            # Sort by time slot
            time_order = ['9:00-10:00', '10:00-11:00', '11:00-12:00', '2:00-3:00', '3:00-4:00']
            for time_slot in time_order:
                slot_sessions = day_schedule[day_schedule['TimeSlot'] == time_slot]
                if len(slot_sessions) > 0:
                    print(f"\n{time_slot}")
                    for _, session in slot_sessions.iterrows():
                        course_name = session.get('CourseName', 'Unknown Course')
                        resource = f"{session.get('ResourceType', 'Room')} {session.get('ResourceID', 'Unknown')}"
                        faculty = session.get('FacultyID', 'Unknown')
                        students = session.get('StudentsCount', 'Unknown')
                        
                        print(f" {course_name}")
                        print(f" {resource}")
                        print(f" Faculty: {faculty}")
                        print(f"Students: {students}")
                        print()

def view_class_timetable():
    """View a specific class timetable"""
    files = list_files_in_directory('class_timetables')
    if not files:
        print("No class timetables found. Please run generate_separate_timetables.py first.")
        return
    
    print(f"\nAvailable Class Timetables ({len(files)} total):")
    for i, file in enumerate(files[:20], 1):  # Show first 20
        class_name = file.replace('_timetable.csv', '')
        print(f"{i:2}. {class_name}")
    
    if len(files) > 20:
        print(f"... and {len(files) - 20} more")
    
    try:
        choice = input(f"\nEnter class name (or number 1-{min(20, len(files))}): ").strip()
        
        if choice.isdigit():
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < min(20, len(files)):
                selected_file = files[choice_idx]
            else:
                print("Invalid choice.")
                return
        else:
            # Try to find by name
            matching_files = [f for f in files if choice.lower() in f.lower()]
            if matching_files:
                selected_file = matching_files[0]
            else:
                print("Class not found.")
                return
        
        # Load and display timetable
        df = pd.read_csv(f'class_timetables/{selected_file}')
        class_name = selected_file.replace('_timetable.csv', '')
        
        display_timetable_formatted(df, f"{class_name} CLASS TIMETABLE")
        
        # Show class statistics
        if len(df) > 0:
            print(f"\nClass Statistics:")
            print(f"   • Total Sessions: {len(df)}")
            print(f"   • Unique Courses: {df['CourseCode'].nunique()}")
            print(f"   • Room Sessions: {len(df[df['ResourceType'] == 'Room'])}")
            print(f"   • Lab Sessions: {len(df[df['ResourceType'] == 'Lab'])}")
            if 'StudentsInClass' in df.columns:
                print(f"   • Students in Class: {df['StudentsInClass'].iloc[0]}")
        
    except Exception as e:
        print(f"Error loading timetable: {e}")

def view_faculty_timetable():
    """View a specific faculty timetable"""
    files = list_files_in_directory('faculty_timetables')
    if not files:
        print("No faculty timetables found.")
        return
    
    print(f"\nAvailable Faculty Timetables ({len(files)} total):")
    for i, file in enumerate(files[:20], 1):  # Show first 20
        faculty_name = file.replace('_timetable.csv', '')
        print(f"{i:2}. {faculty_name}")
    
    if len(files) > 20:
        print(f"... and {len(files) - 20} more")
    
    try:
        choice = input(f"\nEnter faculty ID (or number 1-{min(20, len(files))}): ").strip()
        
        if choice.isdigit():
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < min(20, len(files)):
                selected_file = files[choice_idx]
            else:
                print("Invalid choice.")
                return
        else:
            # Try to find by name
            matching_files = [f for f in files if choice.upper() in f.upper()]
            if matching_files:
                selected_file = matching_files[0]
            else:
                print("Faculty not found.")
                return
        
        # Load and display timetable
        df = pd.read_csv(f'faculty_timetables/{selected_file}')
        faculty_name = selected_file.replace('_timetable.csv', '')
        
        display_timetable_formatted(df, f"{faculty_name} FACULTY TIMETABLE")
        
        # Show faculty statistics
        if len(df) > 0:
            print(f"\nFaculty Statistics:")
            print(f"   • Total Sessions: {len(df)}")
            print(f"   • Courses Taught: {df['CourseCode'].nunique()}")
            print(f"   • Room Sessions: {len(df[df['ResourceType'] == 'Room'])}")
            print(f"   • Lab Sessions: {len(df[df['ResourceType'] == 'Lab'])}")
            if 'FacultyDepartment' in df.columns:
                print(f"   • Department: {df['FacultyDepartment'].iloc[0]}")
        
    except Exception as e:
        print(f"Error loading timetable: {e}")

def view_department_timetable():
    """View a specific department timetable"""
    files = list_files_in_directory('department_timetables')
    if not files:
        print("No department timetables found.")
        return
    
    print(f"\nAvailable Department Timetables:")
    for i, file in enumerate(files, 1):
        dept_name = file.replace('_department_timetable.csv', '')
        print(f"{i}. {dept_name}")
    
    try:
        choice = input(f"\nEnter department name (or number 1-{len(files)}): ").strip()
        
        if choice.isdigit():
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(files):
                selected_file = files[choice_idx]
            else:
                print("Invalid choice.")
                return
        else:
            # Try to find by name
            matching_files = [f for f in files if choice.upper() in f.upper()]
            if matching_files:
                selected_file = matching_files[0]
            else:
                print("Department not found.")
                return
        
        # Load and display timetable
        df = pd.read_csv(f'department_timetables/{selected_file}')
        dept_name = selected_file.replace('_department_timetable.csv', '')
        
        display_timetable_formatted(df, f"{dept_name} DEPARTMENT TIMETABLE")
        
        # Show department statistics
        if len(df) > 0:
            print(f"\nDepartment Statistics:")
            print(f"   • Total Sessions: {len(df)}")
            print(f"   • Unique Courses: {df['CourseCode'].nunique()}")
            print(f"   • Faculty Members: {df['FacultyID'].nunique()}")
            print(f"   • Room Sessions: {len(df[df['ResourceType'] == 'Room'])}")
            print(f"   • Lab Sessions: {len(df[df['ResourceType'] == 'Lab'])}")
        
    except Exception as e:
        print(f"Error loading timetable: {e}")

def view_summary_reports():
    """View summary reports"""
    print("\nSummary Reports:")
    
    # Class Summary
    try:
        class_summary = pd.read_csv('class_summary_report.csv')
        print(f"\nCLASS SUMMARY (Top 10 by sessions):")
        top_classes = class_summary.nlargest(10, 'TotalSessions')
        print(top_classes[['ClassID', 'Department', 'TotalCourses', 'TotalSessions', 'StudentsInClass']].to_string(index=False))
    except FileNotFoundError:
        print("Class summary report not found.")
    
    # Faculty Summary
    try:
        faculty_summary = pd.read_csv('faculty_summary_report.csv')
        print(f"\nFACULTY SUMMARY (Top 10 by sessions):")
        top_faculty = faculty_summary.nlargest(10, 'TotalSessions')
        print(top_faculty[['FacultyID', 'Department', 'TotalCourses', 'TotalSessions']].to_string(index=False))
    except FileNotFoundError:
        print("Faculty summary report not found.")
    
    # Department Summary
    try:
        dept_summary = pd.read_csv('department_summary_report.csv')
        print(f"\nDEPARTMENT SUMMARY:")
        print(dept_summary.to_string(index=False))
    except FileNotFoundError:
        print("Department summary report not found.")

def show_available_files():
    """Show all available timetable files"""
    print(f"\nAvailable Timetable Files:")
    
    class_files = list_files_in_directory('class_timetables')
    faculty_files = list_files_in_directory('faculty_timetables')
    dept_files = list_files_in_directory('department_timetables')
    
    print(f"\nClass Timetables: {len(class_files)} files")
    print(f"Faculty Timetables: {len(faculty_files)} files")
    print(f"Department Timetables: {len(dept_files)} files")
    
    # Show first few of each type
    if class_files:
        print(f"\nSample Class Files:")
        for file in class_files[:5]:
            print(f"   • {file}")
        if len(class_files) > 5:
            print(f"   ... and {len(class_files) - 5} more")
    
    if faculty_files:
        print(f"\nSample Faculty Files:")
        for file in faculty_files[:5]:
            print(f"   • {file}")
        if len(faculty_files) > 5:
            print(f"   ... and {len(faculty_files) - 5} more")

# Main interactive loop
def main():
    while True:
        choice = display_menu()
        
        if choice == '1':
            view_class_timetable()
        elif choice == '2':
            view_faculty_timetable()
        elif choice == '3':
            view_department_timetable()
        elif choice == '4':
            view_summary_reports()
        elif choice == '5':
            show_available_files()
        elif choice == '6':
            print("\n👋 Thank you for using the Timetable Viewer!")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
        
        input("\n📝 Press Enter to continue...")

if __name__ == "__main__":
    main()