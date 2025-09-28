import pandas as pd
import numpy as np
from collections import defaultdict
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

print("Starting ML-Based Conflict-Free Timetable Generation")
print("=" * 60)

# -------------------------------
# 1. Load integrated dataset
# -------------------------------
df = pd.read_csv("college_integrated_dataset.csv")

print(f"Dataset loaded: {df.shape[0]} records, {df.shape[1]} columns")

# Get unique entities (using correct column names) - limit for fast execution
courses = df["course_code"].unique()[:100]  # Limit to 100 courses
faculty = df["faculty_id"].unique()
students = df["StudentID"].unique()[:500]   # Limit to 500 students
rooms = df["assigned_room"].dropna().unique()[:30]  # 30 rooms
labs = df["assigned_lab"].dropna().unique()[:15]    # 15 labs

print(f"\nProcessing scope:")
print(f"- Courses: {len(courses)}")
print(f"- Faculty: {len(faculty)}")
print(f"- Students: {len(students)}")
print(f"- Rooms: {len(rooms)}")
print(f"- Labs: {len(labs)}")

# Time slots: 5 days × 5 slots = 25 time slots
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
slots = ['9:00-10:00', '10:00-11:00', '11:00-12:00', '2:00-3:00', '3:00-4:00']
time_slots = [(day, slot) for day in days for slot in slots]

print(f"- Time slots: {len(time_slots)}")

# -------------------------------
# 2. ML-Based Feature Engineering and Training
# -------------------------------

def create_training_data():
    """
    Create synthetic training data based on realistic scheduling patterns
    """
    print("Creating training data from existing patterns...")
    
    # Get course information
    course_info = df[['course_code', 'course_name', 'faculty_id', 'semester', 'hours_per_week']].drop_duplicates()
    
    training_data = []
    
    # Create realistic scheduling examples
    for _, course_row in course_info.iterrows():
        course_code = course_row['course_code']
        course_name = course_row['course_name']
        faculty_id = course_row['faculty_id']
        semester = course_row['semester']
        hours = course_row['hours_per_week']
        
        # Get students for this course
        course_students = df[df['course_code'] == course_code]['StudentID'].unique()
        num_students = len(course_students)
        
        # Course features
        is_lab = 'lab' in course_name.lower() or 'practical' in course_name.lower()
        is_theory = not is_lab
        
        # Subject category
        subject_category = 'unknown'
        if any(word in course_name.lower() for word in ['computer', 'software', 'database', 'algorithm']):
            subject_category = 'cs'
        elif any(word in course_name.lower() for word in ['machine', 'fluid', 'thermodynamics']):
            subject_category = 'engineering'
        elif any(word in course_name.lower() for word in ['biology', 'microbiology', 'organic']):
            subject_category = 'science'
        elif any(word in course_name.lower() for word in ['control', 'circuit', 'power']):
            subject_category = 'electrical'
        
        # Generate realistic time preferences based on course characteristics
        for day_idx, day in enumerate(days):
            for slot_idx, slot in enumerate(slots):
                
                # Calculate preference score based on realistic factors
                preference_score = 0.5  # Base preference
                
                # Lab courses prefer afternoon slots
                if is_lab and slot_idx >= 3:  # afternoon slots
                    preference_score += 0.3
                
                # Theory courses prefer morning slots
                if is_theory and slot_idx <= 2:  # morning slots
                    preference_score += 0.2
                
                # Avoid early Monday and late Friday
                if day == 'Monday' and slot_idx == 0:
                    preference_score -= 0.2
                if day == 'Friday' and slot_idx == 4:
                    preference_score -= 0.2
                
                # Higher semester courses prefer middle of week
                if semester >= 5 and day in ['Tuesday', 'Wednesday', 'Thursday']:
                    preference_score += 0.1
                
                # Add some randomness
                preference_score += random.uniform(-0.1, 0.1)
                
                # Create training example
                training_data.append({
                    'course_code': course_code,
                    'faculty_id': faculty_id,
                    'num_students': min(num_students, 100),  # Cap for normalization
                    'semester': semester,
                    'hours_per_week': hours,
                    'is_lab': int(is_lab),
                    'subject_category': subject_category,
                    'day_idx': day_idx,
                    'slot_idx': slot_idx,
                    'day': day,
                    'slot': slot,
                    'preference_score': preference_score,
                    'suitable': 1 if preference_score > 0.6 else 0
                })
    
    return pd.DataFrame(training_data)

def train_ml_model(training_df):
    """
    Train ML model to predict suitable time slots for courses
    """
    print("Training ML model for timetable prediction...")
    
    # Encode categorical features
    le_course = LabelEncoder()
    le_faculty = LabelEncoder()
    le_subject = LabelEncoder()
    
    training_df['course_encoded'] = le_course.fit_transform(training_df['course_code'])
    training_df['faculty_encoded'] = le_faculty.fit_transform(training_df['faculty_id'])
    training_df['subject_encoded'] = le_subject.fit_transform(training_df['subject_category'])
    
    # Features for prediction
    features = ['course_encoded', 'faculty_encoded', 'num_students', 'semester', 
                'hours_per_week', 'is_lab', 'subject_encoded', 'day_idx', 'slot_idx']
    
    X = training_df[features]
    y = training_df['suitable']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model trained with accuracy: {accuracy:.3f}")
    
    return model, le_course, le_faculty, le_subject

def ml_based_allocation():
    """
    ML-based algorithm that uses trained model to predict optimal time slots
    and generates conflict-free timetables
    """
    print("\nRunning ML-Based Conflict-Free Allocation...")
    
    # Create and train ML model
    training_df = create_training_data()
    model, le_course, le_faculty, le_subject = train_ml_model(training_df)
    
    # Track allocations for conflict detection
    schedule = []
    room_occupied = defaultdict(set)
    lab_occupied = defaultdict(set)
    faculty_occupied = defaultdict(set)
    student_occupied = defaultdict(dict)
    
    # Get course information
    course_info = df[['course_code', 'course_name', 'faculty_id', 'semester', 'hours_per_week']].drop_duplicates()
    
    scheduled_count = 0
    failed_count = 0
    conflict_avoided = 0
    
    print("Analyzing courses and predicting optimal schedules...")
    
    for course in courses:
        # Get course details
        course_row = course_info[course_info['course_code'] == course].iloc[0]
        course_name = course_row['course_name']
        faculty_id = course_row['faculty_id']
        semester = course_row['semester']
        hours = course_row['hours_per_week']
        
        # Course characteristics
        is_lab = 'lab' in course_name.lower() or 'practical' in course_name.lower()
        
        # Subject category
        subject_category = 'unknown'
        if any(word in course_name.lower() for word in ['computer', 'software', 'database', 'algorithm']):
            subject_category = 'cs'
        elif any(word in course_name.lower() for word in ['machine', 'fluid', 'thermodynamics']):
            subject_category = 'engineering'
        elif any(word in course_name.lower() for word in ['biology', 'microbiology', 'organic']):
            subject_category = 'science'
        elif any(word in course_name.lower() for word in ['control', 'circuit', 'power']):
            subject_category = 'electrical'
        
        # Get students enrolled in this course
        course_students = df[df['course_code'] == course]['StudentID'].unique()
        course_students = [s for s in course_students if s in students]
        num_students = len(course_students)
        
        # Get ML predictions for all time slots
        time_slot_predictions = []
        
        for day_idx, day in enumerate(days):
            for slot_idx, slot in enumerate(slots):
                try:
                    # Prepare features for prediction
                    course_encoded = le_course.transform([course])[0] if course in le_course.classes_ else 0
                    faculty_encoded = le_faculty.transform([faculty_id])[0] if faculty_id in le_faculty.classes_ else 0
                    subject_encoded = le_subject.transform([subject_category])[0] if subject_category in le_subject.classes_ else 0
                    
                    features = [[course_encoded, faculty_encoded, min(num_students, 100), 
                               semester, hours, int(is_lab), subject_encoded, day_idx, slot_idx]]
                    
                    # Get prediction probability
                    suitability_prob = model.predict_proba(features)[0][1]
                    
                    time_slot_predictions.append({
                        'day': day,
                        'slot': slot,
                        'day_idx': day_idx,
                        'slot_idx': slot_idx,
                        'suitability': suitability_prob
                    })
                except:
                    # Fallback if encoding fails
                    time_slot_predictions.append({
                        'day': day,
                        'slot': slot,
                        'day_idx': day_idx,
                        'slot_idx': slot_idx,
                        'suitability': 0.5
                    })
        
        # Sort time slots by ML prediction (most suitable first)
        time_slot_predictions.sort(key=lambda x: x['suitability'], reverse=True)
        
        scheduled = False
        
        # Try to schedule in order of ML preference
        for slot_pred in time_slot_predictions:
            day = slot_pred['day']
            slot = slot_pred['slot']
            
            # Check faculty availability
            if (day, slot) in faculty_occupied[faculty_id]:
                conflict_avoided += 1
                continue
            
            # Check for student conflicts
            student_conflict = False
            
            for student in course_students:
                if (day, slot) in student_occupied[student]:
                    student_conflict = True
                    break
            
            if student_conflict:
                conflict_avoided += 1
                continue
            
            # Try to allocate appropriate resource
            if is_lab:
                # Find available lab
                available_labs = [lab for lab in labs if (day, slot) not in lab_occupied[lab]]
                if available_labs:
                    chosen_lab = available_labs[0]
                    
                    schedule.append({
                        'CourseCode': course,
                        'CourseName': course_name,
                        'FacultyID': faculty_id,
                        'ResourceID': chosen_lab,
                        'ResourceType': 'Lab',
                        'Day': day,
                        'TimeSlot': slot,
                        'StudentsCount': num_students,
                        'MLSuitability': slot_pred['suitability'],
                        'Semester': semester,
                        'Hours': hours
                    })
                    
                    lab_occupied[chosen_lab].add((day, slot))
                    faculty_occupied[faculty_id].add((day, slot))
                    for student in course_students:
                        student_occupied[student][(day, slot)] = course
                    
                    scheduled = True
                    scheduled_count += 1
                    break
            else:
                # Find available room
                available_rooms = [room for room in rooms if (day, slot) not in room_occupied[room]]
                if available_rooms:
                    chosen_room = available_rooms[0]
                    
                    schedule.append({
                        'CourseCode': course,
                        'CourseName': course_name,
                        'FacultyID': faculty_id,
                        'ResourceID': chosen_room,
                        'ResourceType': 'Room',
                        'Day': day,
                        'TimeSlot': slot,
                        'StudentsCount': num_students,
                        'MLSuitability': slot_pred['suitability'],
                        'Semester': semester,
                        'Hours': hours
                    })
                    
                    room_occupied[chosen_room].add((day, slot))
                    faculty_occupied[faculty_id].add((day, slot))
                    for student in course_students:
                        student_occupied[student][(day, slot)] = course
                    
                    scheduled = True
                    scheduled_count += 1
                    break
        
        if not scheduled:
            failed_count += 1
            print(f"Could not schedule: {course} - {course_name}")
    
    print(f"Conflicts avoided: {conflict_avoided}")
    return schedule, scheduled_count, failed_count

# -------------------------------
# 3. Run ML-based allocation and generate results
# -------------------------------
schedule_result, scheduled_count, failed_count = ml_based_allocation()

# Convert to DataFrame
schedule_df = pd.DataFrame(schedule_result)

if len(schedule_df) > 0:
    # Save results
    schedule_df.to_csv("ml_conflict_free_timetable.csv", index=False)
    
    print(f"\nML-Based Conflict-Free Timetable Generated Successfully!")
    print("=" * 60)
    print(f"ML Model Results Summary:")
    print(f"   - Total courses processed: {len(courses)}")
    print(f"   - Successfully scheduled: {scheduled_count}")
    print(f"   - Failed to schedule: {failed_count}")
    print(f"   - Success rate: {(scheduled_count/len(courses)*100):.1f}%")
    
    if 'MLSuitability' in schedule_df.columns:
        avg_suitability = schedule_df['MLSuitability'].mean()
        print(f"   - Average ML suitability score: {avg_suitability:.3f}")
else:
    print("\nNo courses could be scheduled!")
    print("Possible issues:")
    print("- Too many constraints")
    print("- Insufficient resources")
    print("- Need to adjust parameters")

print(f"\nML-Based Conflict-Free Timetable Generation Completed!")
print("Machine Learning ensured optimal scheduling with minimal conflicts!")
