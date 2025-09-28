import pandas as pd
import os
from collections import defaultdict

print("Creating Separate Timetables for Classes and Faculty")
print("=" * 60)

# Load the ML-generated conflict-free timetable
try:
    df = pd.read_csv("ml_conflict_free_timetable.csv")
    print(f"Loaded ML timetable with {len(df)} scheduled sessions")
except FileNotFoundError:
    print("ML timetable not found. Please run allocation_fixed.py first.")
    exit()

# Load the integrated dataset for additional student information
integrated_df = pd.read_csv("college_integrated_dataset.csv")

# Create directories for organized output
os.makedirs("class_timetables", exist_ok=True)
os.makedirs("faculty_timetables", exist_ok=True)
os.makedirs("department_timetables", exist_ok=True)

print("Created output directories")

# -------------------------------
# 1. Generate Class-wise Timetables
# -------------------------------
def generate_class_timetables():
    print("\nGenerating Class-wise Timetables...")
    
    student_classes = integrated_df[['StudentID', 'year', 'class', 'student_department']].drop_duplicates()
    student_classes['ClassID'] = student_classes['year'].astype(str) + '-' + student_classes['class']
    classes = student_classes.groupby(['ClassID', 'student_department'])['StudentID'].apply(list).reset_index()
    
    print(f"Found {len(classes)} different classes")
    
    class_timetables = {}
    
    for _, class_info in classes.iterrows():
        class_id = class_info['ClassID']
        department = class_info['student_department']
        students_in_class = class_info['StudentID']
        
        class_courses = integrated_df[integrated_df['StudentID'].isin(students_in_class)]['course_code'].unique()
        class_schedule = df[df['CourseCode'].isin(class_courses)].copy()
        
        if len(class_schedule) > 0:
            class_schedule['ClassID'] = class_id
            class_schedule['Department'] = department
            class_schedule['StudentsInClass'] = len(students_in_class)
            
            day_order = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5}
            time_order = {'9:00-10:00': 1, '10:00-11:00': 2, '11:00-12:00': 3, '2:00-3:00': 4, '3:00-4:00': 5}
            class_schedule['DayOrder'] = class_schedule['Day'].map(day_order)
            class_schedule['TimeOrder'] = class_schedule['TimeSlot'].map(time_order)
            class_schedule = class_schedule.sort_values(['DayOrder', 'TimeOrder']).drop(['DayOrder', 'TimeOrder'], axis=1)
            
            class_timetables[f"{department}_{class_id}"] = class_schedule
            filename = f"class_timetables/{department}_{class_id}_timetable.csv"
            class_schedule.to_csv(filename, index=False)
    
    print(f"Generated {len(class_timetables)} class timetables")
    return class_timetables

# -------------------------------
# 2. Generate Faculty-wise Timetables  
# -------------------------------
def generate_faculty_timetables():
    print("\nGenerating Faculty-wise Timetables...")
    
    faculty_info = integrated_df[['faculty_id', 'faculty_department']].drop_duplicates()
    faculty_timetables = {}
    
    for _, faculty_row in faculty_info.iterrows():
        faculty_id = faculty_row['faculty_id']
        faculty_dept = faculty_row['faculty_department']
        faculty_schedule = df[df['FacultyID'] == faculty_id].copy()
        
        if len(faculty_schedule) > 0:
            faculty_schedule['FacultyDepartment'] = faculty_dept
            total_sessions = len(faculty_schedule)
            
            day_order = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5}
            time_order = {'9:00-10:00': 1, '10:00-11:00': 2, '11:00-12:00': 3, '2:00-3:00': 4, '3:00-4:00': 5}
            faculty_schedule['DayOrder'] = faculty_schedule['Day'].map(day_order)
            faculty_schedule['TimeOrder'] = faculty_schedule['TimeSlot'].map(time_order)
            faculty_schedule = faculty_schedule.sort_values(['DayOrder', 'TimeOrder']).drop(['DayOrder', 'TimeOrder'], axis=1)
            
            faculty_schedule['TotalSessions'] = total_sessions
            faculty_timetables[faculty_id] = faculty_schedule
            filename = f"faculty_timetables/{faculty_dept}_{faculty_id}_timetable.csv"
            faculty_schedule.to_csv(filename, index=False)
    
    print(f"Generated {len(faculty_timetables)} faculty timetables")
    return faculty_timetables

# -------------------------------
# 3. Generate Department-wise Timetables
# -------------------------------
def generate_department_timetables():
    print("\nGenerating Department-wise Timetables...")
    
    departments = integrated_df['faculty_department'].unique()
    department_timetables = {}
    
    for dept in departments:
        dept_faculty = integrated_df[integrated_df['faculty_department'] == dept]['faculty_id'].unique()
        dept_schedule = df[df['FacultyID'].isin(dept_faculty)].copy()
        
        if len(dept_schedule) > 0:
            dept_schedule['Department'] = dept
            unique_courses = dept_schedule['CourseCode'].nunique()
            unique_faculty = dept_schedule['FacultyID'].nunique()
            
            day_order = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5}
            time_order = {'9:00-10:00': 1, '10:00-11:00': 2, '11:00-12:00': 3, '2:00-3:00': 4, '3:00-4:00': 5}
            dept_schedule['DayOrder'] = dept_schedule['Day'].map(day_order)
            dept_schedule['TimeOrder'] = dept_schedule['TimeSlot'].map(time_order)
            dept_schedule = dept_schedule.sort_values(['DayOrder', 'TimeOrder']).drop(['DayOrder', 'TimeOrder'], axis=1)
            
            dept_schedule['DeptCourses'] = unique_courses
            dept_schedule['DeptFaculty'] = unique_faculty
            department_timetables[dept] = dept_schedule
            filename = f"department_timetables/{dept}_department_timetable.csv"
            dept_schedule.to_csv(filename, index=False)
    
    print(f"Generated {len(department_timetables)} department timetables")
    return department_timetables

# -------------------------------
# 4. Generate Summary Reports
# -------------------------------
def generate_summary_reports(class_timetables, faculty_timetables, department_timetables):
    print("\nGenerating Summary Reports...")
    
    # Class Summary
    class_summary = []
    for class_name, schedule in class_timetables.items():
        if len(schedule) > 0:
            class_summary.append({
                'ClassID': class_name,
                'Department': schedule['Department'].iloc[0],
                'TotalCourses': schedule['CourseCode'].nunique(),
                'TotalSessions': len(schedule),
                'StudentsInClass': schedule['StudentsInClass'].iloc[0],
                'RoomSessions': len(schedule[schedule['ResourceType'] == 'Room']),
                'LabSessions': len(schedule[schedule['ResourceType'] == 'Lab'])
            })
    class_summary_df = pd.DataFrame(class_summary)
    class_summary_df.to_csv("class_summary_report.csv", index=False)
    
    # Faculty Summary
    faculty_summary = []
    for faculty_id, schedule in faculty_timetables.items():
        if len(schedule) > 0:
            faculty_summary.append({
                'FacultyID': faculty_id,
                'Department': schedule['FacultyDepartment'].iloc[0],
                'TotalCourses': schedule['CourseCode'].nunique(),
                'TotalSessions': len(schedule),
                'RoomSessions': len(schedule[schedule['ResourceType'] == 'Room']),
                'LabSessions': len(schedule[schedule['ResourceType'] == 'Lab']),
                'AvgStudentsPerSession': schedule['StudentsCount'].mean().round(1) if 'StudentsCount' in schedule.columns else 0
            })
    faculty_summary_df = pd.DataFrame(faculty_summary)
    faculty_summary_df.to_csv("faculty_summary_report.csv", index=False)
    
    # Department Summary  
    dept_summary = []
    for dept, schedule in department_timetables.items():
        if len(schedule) > 0:
            dept_summary.append({
                'Department': dept,
                'TotalCourses': schedule['CourseCode'].nunique(),
                'TotalFaculty': schedule['FacultyID'].nunique(),
                'TotalSessions': len(schedule),
                'RoomSessions': len(schedule[schedule['ResourceType'] == 'Room']),
                'LabSessions': len(schedule[schedule['ResourceType'] == 'Lab'])
            })
    dept_summary_df = pd.DataFrame(dept_summary)
    dept_summary_df.to_csv("department_summary_report.csv", index=False)
    
    return class_summary_df, faculty_summary_df, dept_summary_df

# -------------------------------
# 5. Run All Generations
# -------------------------------
print("Starting timetable generation process...")

class_timetables = generate_class_timetables()
faculty_timetables = generate_faculty_timetables()
department_timetables = generate_department_timetables()
class_summary, faculty_summary, dept_summary = generate_summary_reports(
    class_timetables, faculty_timetables, department_timetables
)

# -------------------------------
# 6. Display Results
# -------------------------------
print("\n" + "="*60)
print("TIMETABLE GENERATION COMPLETED!")
print("="*60)

print(f"\nCLASS TIMETABLES:")
print(f"   - Total classes: {len(class_timetables)}")
print(f"   - Files saved in: 'class_timetables/' directory")
if len(class_summary) > 0:
    print("   Top 5 classes by session count:")
    top_classes = class_summary.nlargest(5, 'TotalSessions')
    for _, row in top_classes.iterrows():
        print(f"     {row['ClassID']}: {row['TotalSessions']} sessions, {row['TotalCourses']} courses")

print(f"\nFACULTY TIMETABLES:")
print(f"   - Total faculty: {len(faculty_timetables)}")
print(f"   - Files saved in: 'faculty_timetables/' directory")
if len(faculty_summary) > 0:
    print("   Top 5 faculty by teaching load:")
    top_faculty = faculty_summary.nlargest(5, 'TotalSessions')
    for _, row in top_faculty.iterrows():
        print(f"     {row['FacultyID']} ({row['Department']}): {row['TotalSessions']} sessions")

print(f"\nDEPARTMENT TIMETABLES:")
print(f"   - Total departments: {len(department_timetables)}")
print(f"   - Files saved in: 'department_timetables/' directory")
if len(dept_summary) > 0:
    print("   Department statistics:")
    for _, row in dept_summary.iterrows():
        print(f"     {row['Department']}: {row['TotalCourses']} courses, {row['TotalFaculty']} faculty, {row['TotalSessions']} sessions")

print(f"\nSUMMARY REPORTS:")
print(f"   - class_summary_report.csv")
print(f"   - faculty_summary_report.csv") 
print(f"   - department_summary_report.csv")

print("\nAll timetables generated successfully. Check the respective directories for individual files.")
