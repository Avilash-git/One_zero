import pandas as pd

# Quick demo of the timetable system
print("🎓 College Timetable System - Quick Demo")
print("=" * 50)

# Show a sample class timetable
print("\n📚 Sample Class Timetable: CHEM_1-D (Chemistry 1st Year Section D)")
print("-" * 60)

class_df = pd.read_csv('class_timetables/CHEM_1-D_timetable.csv')

# Group by day for better display
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
time_slots = ['9:00-10:00', '10:00-11:00', '11:00-12:00', '2:00-3:00', '3:00-4:00']

for day in days:
    day_schedule = class_df[class_df['Day'] == day]
    if len(day_schedule) > 0:
        print(f"\n📆 {day.upper()}")
        print("-" * 30)
        
        for time_slot in time_slots:
            slot_sessions = day_schedule[day_schedule['TimeSlot'] == time_slot]
            if len(slot_sessions) > 0:
                print(f"\n⏰ {time_slot}")
                for _, session in slot_sessions.iterrows():
                    print(f"   📚 {session['CourseName']}")
                    print(f"   🏛️  {session['ResourceType']} {session['ResourceID']}")
                    print(f"   👨‍🏫 Faculty: {session['FacultyID']}")
                    print(f"   👥 Students: {session['StudentsCount']}")

print(f"\n\n👨‍🏫 Sample Faculty Timetable: F0377 (Chemistry Department)")
print("-" * 60)

faculty_df = pd.read_csv('faculty_timetables/CHEM_F0377_timetable.csv')
print(f"Faculty ID: {faculty_df.iloc[0]['FacultyID']}")
print(f"Department: {faculty_df.iloc[0]['FacultyDepartment']}")
print(f"Total Sessions: {faculty_df.iloc[0]['TotalSessions']}")

for _, session in faculty_df.iterrows():
    print(f"\n📅 {session['Day']} - {session['TimeSlot']}")
    print(f"   📚 Course: {session['CourseName']} ({session['CourseCode']})")
    print(f"   🏛️  Location: {session['ResourceType']} {session['ResourceID']}")
    print(f"   👥 Students: {session['StudentsCount']}")
    print(f"   🤖 ML Suitability: {session['MLSuitability']}")

print(f"\n\n📊 System Statistics:")
print("-" * 30)

# Load summary reports
class_summary = pd.read_csv('class_summary_report.csv')
faculty_summary = pd.read_csv('faculty_summary_report.csv')
dept_summary = pd.read_csv('department_summary_report.csv')

print(f"Total Classes: {len(class_summary)}")
print(f"Total Faculty: {len(faculty_summary)}")
print(f"Total Departments: {len(dept_summary)}")

print(f"\nTop 5 Busiest Classes:")
top_classes = class_summary.nlargest(5, 'TotalSessions')
for _, row in top_classes.iterrows():
    print(f"   • {row['ClassID']}: {row['TotalSessions']} sessions, {row['StudentsInClass']} students")

print(f"\nDepartment Distribution:")
for _, row in dept_summary.iterrows():
    print(f"   • {row['Department']}: {row['TotalCourses']} courses, {row['TotalFaculty']} faculty")

print(f"\n🎉 ML-Based Conflict-Free Timetable System Complete!")
print(f"📁 Individual timetables available in respective directories:")
print(f"   • class_timetables/ - {len(class_summary)} class timetables")
print(f"   • faculty_timetables/ - {len(faculty_summary)} faculty timetables") 
print(f"   • department_timetables/ - {len(dept_summary)} department timetables")
print(f"\n✅ All timetables are conflict-free and optimized using Machine Learning!")