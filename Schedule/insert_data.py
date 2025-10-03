from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


MONGO_URL = "mongodb+srv://vibeprep4:123%40Vibeprep@vibeprepcluster.cv1ltqj.mongodb.net"
DATABASE_NAME = "Vibeprep_Users"
COLLECTION_NAME = "jee_weekly_schedules" 

weekly_schedule_data = [
    {
        "category": "Regular Weekdays",
        "day": "Monday-Friday",
        "description": "Optimal weekday schedule balancing school/coaching with intensive self-study sessions",
        "schedule": [
            {"time_slot": "6:00 AM - 6:30 AM", "activity": "Wake Up, Freshen Up, Quick Hydration", "subject_focus": "-", "tips": "Start with water and light stretching"},
            {"time_slot": "6:30 AM - 8:00 AM", "activity": "Study Session 1: Deep Concept Focus", "subject_focus": "Maths: Calculus / Coordinate Geometry", "tips": "Best time for complex mathematical concepts when mind is fresh"},
            {"time_slot": "8:00 AM - 2:30 PM", "activity": "School / Coaching Classes + Commute + Lunch Break", "subject_focus": "As per class schedule", "tips": "Take detailed notes, ask doubts immediately"},
            {"time_slot": "2:30 PM - 4:00 PM", "activity": "Rest & Recharge: Power Nap, Light Snack", "subject_focus": "-", "tips": "15-20 min nap maximum, avoid heavy meals"},
            {"time_slot": "4:00 PM - 6:00 PM", "activity": "Study Session 2: Problem Solving", "subject_focus": "Physics: Mechanics / Electromagnetism Problems", "tips": "Focus on numerical problems and derivations"},
            {"time_slot": "6:00 PM - 6:30 PM", "activity": "Short Break: Walk, listen to music, talk to family", "subject_focus": "-", "tips": "Physical activity helps refresh the mind"},
            {"time_slot": "6:30 PM - 8:30 PM", "activity": "Study Session 3: Memorization & Understanding", "subject_focus": "Chemistry: Organic / Inorganic Reactions", "tips": "Use visual aids and mnemonics for better retention"},
            {"time_slot": "8:30 PM - 9:15 PM", "activity": "Dinner Break", "subject_focus": "-", "tips": "Light, nutritious meal for better evening study"},
            {"time_slot": "9:15 PM - 10:30 PM", "activity": "Daily Revision: Review notes of all topics studied today", "subject_focus": "Quick review of Maths, Physics, and Chemistry", "tips": "Active recall technique - test yourself without looking at notes"},
            {"time_slot": "10:30 PM - 11:00 PM", "activity": "Wind Down: Plan for the next day, pack your bag, no screen time", "subject_focus": "-", "tips": "Prepare tomorrow's study plan and materials"},
            {"time_slot": "11:00 PM", "activity": "Sleep", "subject_focus": "-", "tips": "Consistent sleep schedule is crucial for memory consolidation"}
        ]
    },
    {
        "category": "Weekend Intensive",
        "day": "Saturday",
        "description": "Saturday intensive schedule for comprehensive revision and problem-solving",
        "schedule": [
            {"time_slot": "7:00 AM - 7:30 AM", "activity": "Wake Up, Freshen Up", "subject_focus": "-", "tips": "Weekend allows slightly later wake-up for recovery"},
            {"time_slot": "7:30 AM - 9:30 AM", "activity": "Weekly Revision 1: Go through all Physics notes from the week", "subject_focus": "Physics", "tips": "Focus on concepts learned during weekdays, make summary notes"},
            {"time_slot": "9:30 AM - 10:00 AM", "activity": "Breakfast Break", "subject_focus": "-", "tips": "Nutritious breakfast for sustained energy"},
            {"time_slot": "10:00 AM - 12:30 PM", "activity": "Intense Problem Solving: Solve chapter-wise test or DPPs", "subject_focus": "Maths: Solve 40-50 challenging problems", "tips": "Time yourself, simulate exam conditions"},
            {"time_slot": "12:30 PM - 2:00 PM", "activity": "Lunch & Long Break", "subject_focus": "-", "tips": "Longer break to recharge for afternoon session"},
            {"time_slot": "2:00 PM - 4:00 PM", "activity": "Weekly Revision 2: Go through all Chemistry notes from the week", "subject_focus": "Chemistry", "tips": "Review reactions, mechanisms, and important compounds"},
            {"time_slot": "4:00 PM - 6:00 PM", "activity": "Clear Backlogs: Work on topics you couldn't finish during the week", "subject_focus": "Any subject that needs extra attention", "tips": "Prioritize weak areas identified during the week"},
            {"time_slot": "6:00 PM - 7:30 PM", "activity": "Recreation / Hobby / Sport: Essential for mental reset", "subject_focus": "-", "tips": "Physical activity or creative hobbies for stress relief"},
            {"time_slot": "7:30 PM - 9:00 PM", "activity": "Light Study Session: Review formulas or read NCERT for Chemistry", "subject_focus": "Light revision", "tips": "Easy reading, no intensive problem solving"},
            {"time_slot": "9:00 PM onwards", "activity": "Dinner & Relax with family", "subject_focus": "-", "tips": "Social time is important for mental health"}
        ]
    },
    {
        "category": "Mock Test Day",
        "day": "Sunday",
        "description": "Sunday mock test schedule with comprehensive analysis and improvement planning",
        "schedule": [
            {"time_slot": "7:30 AM - 8:00 AM", "activity": "Wake Up, Light Breakfast", "subject_focus": "-", "tips": "Light meal to avoid discomfort during test"},
            {"time_slot": "8:00 AM - 8:45 AM", "activity": "Formula Revision: Quickly browse your formula notebook", "subject_focus": "Physics, Chemistry, Maths (PCM)", "tips": "Quick glance at important formulas, don't try to learn new concepts"},
            {"time_slot": "9:00 AM - 12:00 PM", "activity": "Full-Length Mock Test (JEE Main/Advanced Pattern)", "subject_focus": "Simulates real exam environment", "tips": "Follow exact exam timing, no breaks except allowed ones"},
            {"time_slot": "12:00 PM - 1:30 PM", "activity": "Lunch & Complete Rest (Do not discuss the paper yet)", "subject_focus": "-", "tips": "Avoid discussing answers immediately after test"},
            {"time_slot": "1:30 PM - 4:30 PM", "activity": "Deep Analysis of Mock Test: The most important task of the week!", "subject_focus": "Detailed performance analysis", "tips": "1. Check correct/incorrect/unattempted questions.\n2. Analyze why mistakes happened (silly error, concept gap, time pressure).\n3. Note down weak topics in a diary.\n4. Calculate subject-wise scores and time distribution"},
            {"time_slot": "4:30 PM - 5:00 PM", "activity": "Break", "subject_focus": "-", "tips": "Short refreshment break"},
            {"time_slot": "5:00 PM - 7:00 PM", "activity": "Concept Reinforcement: Study one weak topic identified from the test", "subject_focus": "Based on Mock Test Analysis", "tips": "Focus on understanding, not just memorizing"},
            {"time_slot": "7:00 PM onwards", "activity": "Free Time: Relax, watch a movie, spend time with family", "subject_focus": "-", "tips": "Complete relaxation to recharge for the new week"},
            {"time_slot": "10:00 PM", "activity": "Plan for the coming week based on your analysis", "subject_focus": "-", "tips": "Set specific goals for weak areas identified"},
            {"time_slot": "11:00 PM", "activity": "Sleep", "subject_focus": "-", "tips": "Good rest before starting new week"}
        ]
    },
    {
        "category": "Exam Preparation",
        "day": "Pre-Exam Day",
        "description": "Schedule for the day before JEE Main/Advanced exam",
        "schedule": [
            {"time_slot": "8:00 AM - 8:30 AM", "activity": "Wake Up, Light Breakfast", "subject_focus": "-", "tips": "Maintain normal routine, avoid heavy meals"},
            {"time_slot": "8:30 AM - 10:00 AM", "activity": "Light Formula Revision", "subject_focus": "Important formulas and shortcuts", "tips": "Only revise, don't learn anything new"},
            {"time_slot": "10:00 AM - 11:00 AM", "activity": "Previous Year Questions (Easy ones)", "subject_focus": "Confidence building problems", "tips": "Solve only those you're confident about"},
            {"time_slot": "11:00 AM - 12:00 PM", "activity": "Break & Relaxation", "subject_focus": "-", "tips": "Light physical activity or meditation"},
            {"time_slot": "12:00 PM - 1:00 PM", "activity": "Check Exam Documents & Route", "subject_focus": "Logistics preparation", "tips": "Admit card, ID proof, route planning, time calculation"},
            {"time_slot": "1:00 PM - 2:00 PM", "activity": "Lunch", "subject_focus": "-", "tips": "Familiar, light, nutritious food"},
            {"time_slot": "2:00 PM - 4:00 PM", "activity": "Rest & Light Entertainment", "subject_focus": "-", "tips": "Avoid studying, watch light comedy or listen to music"},
            {"time_slot": "4:00 PM - 5:00 PM", "activity": "Final Preparation Check", "subject_focus": "Exam essentials", "tips": "Pack exam kit: pens, pencils, eraser, admit card, water bottle"},
            {"time_slot": "5:00 PM onwards", "activity": "Family Time & Early Dinner", "subject_focus": "-", "tips": "Spend time with family, eat early and light"},
            {"time_slot": "9:00 PM", "activity": "Early Sleep", "subject_focus": "-", "tips": "Sleep early for fresh mind on exam day"}
        ]
    },
    {
        "category": "Exam Day",
        "day": "JEE Exam Day",
        "description": "Schedule for the actual JEE Main/Advanced exam day",
        "schedule": [
            {"time_slot": "6:00 AM", "activity": "Wake Up", "subject_focus": "-", "tips": "Wake up 3-4 hours before exam time"},
            {"time_slot": "6:00 AM - 6:30 AM", "activity": "Freshen Up & Light Exercise", "subject_focus": "-", "tips": "Light stretching to feel alert"},
            {"time_slot": "6:30 AM - 7:00 AM", "activity": "Light Breakfast", "subject_focus": "-", "tips": "Familiar food, not too heavy, avoid dairy if sensitive"},
            {"time_slot": "7:00 AM - 7:30 AM", "activity": "Final Document Check", "subject_focus": "Logistics", "tips": "Admit card, photo ID, stationery, water bottle"},
            {"time_slot": "7:30 AM - 8:30 AM", "activity": "Travel to Exam Center", "subject_focus": "-", "tips": "Reach 30 minutes early, carry extra time buffer"},
            {"time_slot": "8:30 AM - 9:00 AM", "activity": "Final Settling & Relaxation", "subject_focus": "-", "tips": "Find your seat, settle down, take deep breaths"},
            {"time_slot": "9:00 AM - 12:00 PM", "activity": "JEE Exam", "subject_focus": "Physics, Chemistry, Mathematics", "tips": "Read instructions carefully, manage time wisely, attempt easy questions first"},
            {"time_slot": "12:00 PM onwards", "activity": "Post-Exam Rest", "subject_focus": "-", "tips": "Don't discuss answers immediately, rest and recharge for next session if applicable"}
        ]
    },
    {
        "category": "Subject-Specific Focus",
        "day": "Maths Intensive Day",
        "description": "Special schedule for Mathematics intensive study",
        "schedule": [
            {"time_slot": "6:30 AM - 8:30 AM", "activity": "Calculus Deep Dive", "subject_focus": "Differential and Integral Calculus", "tips": "Start with theory, then move to numerical problems"},
            {"time_slot": "9:00 AM - 11:00 AM", "activity": "Coordinate Geometry", "subject_focus": "Straight lines, Circles, Parabola, Ellipse, Hyperbola", "tips": "Focus on graphical interpretation and problem-solving techniques"},
            {"time_slot": "11:30 AM - 1:00 PM", "activity": "Algebra Practice", "subject_focus": "Complex Numbers, Quadratic Equations, Sequences & Series", "tips": "Practice a variety of problems to build speed and accuracy"},
            {"time_slot": "2:00 PM - 4:00 PM", "activity": "Trigonometry & Vector", "subject_focus": "Trigonometric identities, Inverse functions, 3D Geometry", "tips": "Memorize key identities and practice visualization"},
            {"time_slot": "5:00 PM - 7:00 PM", "activity": "Statistics & Probability", "subject_focus": "Permutation-Combination, Probability, Statistics", "tips": "Focus on conceptual understanding and application problems"}
        ]
    },
    {
        "category": "Subject-Specific Focus",
        "day": "Physics Intensive Day",
        "description": "Special schedule for Physics intensive study",
        "schedule": [
            {"time_slot": "6:30 AM - 8:30 AM", "activity": "Mechanics Fundamentals", "subject_focus": "Laws of Motion, Work Energy Power, Rotational Motion", "tips": "Focus on conceptual understanding and derivations"},
            {"time_slot": "9:00 AM - 11:00 AM", "activity": "Electromagnetism", "subject_focus": "Electric Field, Magnetic Field, Electromagnetic Induction", "tips": "Practice circuit problems and field calculations"},
            {"time_slot": "11:30 AM - 1:00 PM", "activity": "Modern Physics", "subject_focus": "Atomic Structure, Nuclear Physics, Dual Nature of Matter", "tips": "Focus on theory and conceptual questions"},
            {"time_slot": "2:00 PM - 4:00 PM", "activity": "Thermodynamics & Waves", "subject_focus": "Heat, Thermodynamics, Sound Waves, Light Waves", "tips": "Understand processes and wave properties"},
            {"time_slot": "5:00 PM - 7:00 PM", "activity": "Optics & Numerical Practice", "subject_focus": "Ray Optics, Wave Optics, Numerical Problems", "tips": "Practice ray diagrams and interference problems"}
        ]
    },
    {
        "category": "Subject-Specific Focus",
        "day": "Chemistry Intensive Day",
        "description": "Special schedule for Chemistry intensive study",
        "schedule": [
            {"time_slot": "6:30 AM - 8:30 AM", "activity": "Organic Chemistry", "subject_focus": "Reaction Mechanisms, Name Reactions, Organic Synthesis", "tips": "Focus on understanding mechanisms rather than rote learning"},
            {"time_slot": "9:00 AM - 11:00 AM", "activity": "Inorganic Chemistry", "subject_focus": "Periodic Properties, Chemical Bonding, Coordination Compounds", "tips": "Use periodic trends to understand properties"},
            {"time_slot": "11:30 AM - 1:00 PM", "activity": "Physical Chemistry", "subject_focus": "Chemical Kinetics, Equilibrium, Thermodynamics", "tips": "Focus on numerical problems and concept application"},
            {"time_slot": "2:00 PM - 4:00 PM", "activity": "Electrochemistry & Solutions", "subject_focus": "Redox Reactions, Electrochemical Cells, Colligative Properties", "tips": "Practice electrode potential calculations"},
            {"time_slot": "5:00 PM - 7:00 PM", "activity": "Environmental & Analytical Chemistry", "subject_focus": "Environmental Chemistry, Qualitative Analysis", "tips": "Focus on real-world applications and detection methods"}
        ]
    },
    {
        "category": "Revision Strategy",
        "day": "Final Month Preparation",
        "description": "Schedule structure for the final month before JEE",
        "schedule": [
            {"time_slot": "Daily 2 hours", "activity": "Formula and Concept Revision", "subject_focus": "All subjects rotation", "tips": "Quick revision of all important formulas and concepts daily"},
            {"time_slot": "Daily 3 hours", "activity": "Previous Year Questions", "subject_focus": "JEE Main and Advanced papers", "tips": "Solve at least 2-3 years of papers with proper timing"},
            {"time_slot": "Daily 1 hour", "activity": "Weak Topic Focus", "subject_focus": "Based on mock test analysis", "tips": "Identify and work on consistently weak areas"},
            {"time_slot": "Alternate days", "activity": "Full Mock Tests", "subject_focus": "Complete JEE pattern tests", "tips": "Maintain exam rhythm and identify remaining gaps"},
            {"time_slot": "Daily 30 minutes", "activity": "Current Affairs (if applicable)", "subject_focus": "Science and technology updates", "tips": "Light reading of recent developments in science"}
        ]
    },
    {
        "category": "Machine Learning Study Schedule",
        "day": "ML Preparation Day",
        "description": "Comprehensive schedule for Machine Learning mock test preparation",
        "schedule": [
            {"time_slot": "6:00 AM - 6:30 AM", "activity": "Wake Up, Light Exercise", "subject_focus": "-", "tips": "Fresh start with physical activity for mental clarity"},
            {"time_slot": "6:30 AM - 8:00 AM", "activity": "Mathematics Fundamentals for ML", "subject_focus": "Linear Algebra, Calculus, Statistics", "tips": "Review matrix operations, derivatives, probability distributions"},
            {"time_slot": "8:00 AM - 8:30 AM", "activity": "Breakfast", "subject_focus": "-", "tips": "Brain food: nuts, fruits, and adequate hydration"},
            {"time_slot": "8:30 AM - 10:30 AM", "activity": "Core ML Algorithms Study", "subject_focus": "Supervised Learning: Linear Regression, Decision Trees, SVM", "tips": "Focus on algorithm intuition and mathematical foundations"},
            {"time_slot": "10:30 AM - 11:00 AM", "activity": "Break", "subject_focus": "-", "tips": "Short walk to maintain focus"},
            {"time_slot": "11:00 AM - 12:30 PM", "activity": "Unsupervised Learning & Neural Networks", "subject_focus": "Clustering, PCA, Basic Neural Networks", "tips": "Understand concepts behind dimensionality reduction and clustering"},
            {"time_slot": "12:30 PM - 1:30 PM", "activity": "Lunch Break", "subject_focus": "-", "tips": "Nutritious meal for sustained afternoon energy"},
            {"time_slot": "1:30 PM - 3:00 PM", "activity": "Practice Problems & Code Review", "subject_focus": "Python ML libraries: sklearn, pandas, numpy", "tips": "Hands-on coding practice with real datasets"},
            {"time_slot": "3:00 PM - 3:15 PM", "activity": "Short Break", "subject_focus": "-", "tips": "Hydration and light stretching"},
            {"time_slot": "3:15 PM - 4:45 PM", "activity": "Model Evaluation & Validation", "subject_focus": "Cross-validation, Metrics, Bias-Variance Trade-off", "tips": "Understand performance metrics and validation techniques"},
            {"time_slot": "4:45 PM - 5:00 PM", "activity": "Break", "subject_focus": "-", "tips": "Prepare for final study session"},
            {"time_slot": "5:00 PM - 6:30 PM", "activity": "Mock Test Simulation", "subject_focus": "Previous ML test papers or sample questions", "tips": "Time yourself, practice exam conditions"},
            {"time_slot": "6:30 PM - 7:00 PM", "activity": "Test Analysis", "subject_focus": "Review mistakes and weak areas", "tips": "Identify concepts that need more focus"},
            {"time_slot": "7:00 PM - 8:00 PM", "activity": "Dinner", "subject_focus": "-", "tips": "Relax and recharge"},
            {"time_slot": "8:00 PM - 9:00 PM", "activity": "Quick Revision", "subject_focus": "Key formulas, algorithms summary", "tips": "Light revision of important concepts"},
            {"time_slot": "9:00 PM - 10:00 PM", "activity": "Relaxation", "subject_focus": "-", "tips": "Light entertainment, avoid screens 1 hour before sleep"},
            {"time_slot": "10:00 PM", "activity": "Sleep Preparation", "subject_focus": "-", "tips": "Early sleep for fresh mind on test day"}
        ]
    },
    {
        "category": "Stress Management",
        "day": "High Stress Periods",
        "description": "Schedule modifications for managing exam stress and anxiety",
        "schedule": [
            {"time_slot": "Morning", "activity": "Meditation & Breathing Exercises", "subject_focus": "Stress relief", "tips": "10-15 minutes of deep breathing or meditation to start the day calmly"},
            {"time_slot": "Study Sessions", "activity": "Pomodoro Technique", "subject_focus": "All subjects", "tips": "25 minutes focused study + 5 minutes break to maintain concentration"},
            {"time_slot": "Afternoon", "activity": "Physical Exercise", "subject_focus": "Stress relief", "tips": "30 minutes of physical activity to release tension and improve mood"},
            {"time_slot": "Evening", "activity": "Relaxation Activities", "subject_focus": "Mental health", "tips": "Listen to music, practice hobbies, spend time with family"},
            {"time_slot": "Night", "activity": "Journaling", "subject_focus": "Emotional well-being", "tips": "Write down worries and achievements to clear the mind before sleep"}
        ]
    },
    {
        "category": "Time Management Strategies",
        "day": "Efficiency Focused",
        "description": "Strategies for maximizing study efficiency and time management",
        "schedule": [
            {"time_slot": "Planning Phase", "activity": "Daily Goal Setting", "subject_focus": "All subjects", "tips": "Set 3-5 specific, measurable goals for each day"},
            {"time_slot": "Peak Hours", "activity": "Difficult Topics", "subject_focus": "Challenging concepts", "tips": "Tackle hardest subjects when energy levels are highest (usually morning)"},
            {"time_slot": "Low Energy Periods", "activity": "Revision & Light Reading", "subject_focus": "Previously learned topics", "tips": "Use afternoon slumps for reviewing familiar material"},
            {"time_slot": "Evening", "activity": "Active Recall Practice", "subject_focus": "All subjects", "tips": "Test yourself without looking at notes to strengthen memory"},
            {"time_slot": "Weekly", "activity": "Progress Review", "subject_focus": "Study plan evaluation", "tips": "Assess what worked, what didn't, and adjust strategy accordingly"}
        ]
    },
    {
        "category": "Competitive Exam Strategies",
        "day": "Exam Techniques",
        "description": "Specific strategies for competitive exam success",
        "schedule": [
            {"time_slot": "Preparation Phase", "activity": "Question Paper Analysis", "subject_focus": "Previous years' patterns", "tips": "Analyze last 5 years of papers to understand question distribution and difficulty"},
            {"time_slot": "Practice Phase", "activity": "Time-bound Problem Solving", "subject_focus": "All subjects", "tips": "Practice with strict time limits to improve speed and accuracy"},
            {"time_slot": "Strategy Phase", "activity": "Attempt Strategy Planning", "subject_focus": "Exam tactics", "tips": "Decide order of attempting questions: easy first, then moderate, then difficult"},
            {"time_slot": "Review Phase", "activity": "Error Analysis", "subject_focus": "Mistake patterns", "tips": "Categorize errors: silly mistakes, concept gaps, time pressure issues"},
            {"time_slot": "Final Phase", "activity": "Confidence Building", "subject_focus": "Mental preparation", "tips": "Focus on strengths, review past successes, positive self-talk"}
        ]
    },
    {
        "category": "Technology Integration",
        "day": "Digital Learning",
        "description": "Effective use of technology for enhanced learning",
        "schedule": [
            {"time_slot": "Morning", "activity": "Educational Apps & Videos", "subject_focus": "Concept clarification", "tips": "Use Khan Academy, Coursera, or subject-specific apps for visual learning"},
            {"time_slot": "Practice Time", "activity": "Online Mock Tests", "subject_focus": "Exam simulation", "tips": "Use platforms like Testbook, Unacademy for realistic test experience"},
            {"time_slot": "Doubt Clearing", "activity": "Online Forums & Study Groups", "subject_focus": "Problem solving", "tips": "Participate in study communities, ask questions on Stack Overflow, Reddit"},
            {"time_slot": "Revision", "activity": "Digital Flashcards", "subject_focus": "Quick recall", "tips": "Use Anki or Quizlet for spaced repetition of formulas and concepts"},
            {"time_slot": "Note-taking", "activity": "Digital Organization", "subject_focus": "Study material management", "tips": "Use Notion, Evernote, or OneNote for organized, searchable study notes"}
        ]
    },
    {
        "category": "Health & Wellness",
        "day": "Holistic Development",
        "description": "Maintaining physical and mental health during intensive study periods",
        "schedule": [
            {"time_slot": "6:00 AM - 6:30 AM", "activity": "Morning Exercise", "subject_focus": "Physical fitness", "tips": "Yoga, jogging, or basic exercises to boost energy and focus"},
            {"time_slot": "Meal Times", "activity": "Nutritious Eating", "subject_focus": "Brain health", "tips": "Include omega-3 rich foods, nuts, fruits, vegetables; avoid junk food"},
            {"time_slot": "Study Breaks", "activity": "Eye Care", "subject_focus": "Vision health", "tips": "Follow 20-20-20 rule: every 20 minutes, look at something 20 feet away for 20 seconds"},
            {"time_slot": "Afternoon", "activity": "Power Nap", "subject_focus": "Mental rejuvenation", "tips": "15-20 minute nap to recharge without affecting night sleep"},
            {"time_slot": "Evening", "activity": "Social Interaction", "subject_focus": "Emotional well-being", "tips": "Spend quality time with family and friends for mental balance"},
            {"time_slot": "Night", "activity": "Sleep Hygiene", "subject_focus": "Rest and recovery", "tips": "7-8 hours of quality sleep, avoid screens 1 hour before bed"}
        ]
    },
    {
        "category": "Subject-wise Time Allocation",
        "day": "Balanced Study Approach",
        "description": "Optimal time distribution across different subjects based on difficulty and weightage",
        "schedule": [
            {"time_slot": "High Concentration (Morning)", "activity": "Mathematics", "subject_focus": "Complex problem solving", "tips": "40% of study time - requires maximum mental effort"},
            {"time_slot": "Mid-day Energy", "activity": "Physics", "subject_focus": "Conceptual understanding & numerical", "tips": "35% of study time - balance of theory and practice"},
            {"time_slot": "Evening Session", "activity": "Chemistry", "subject_focus": "Memorization & reactions", "tips": "25% of study time - good for memory-based learning"},
            {"time_slot": "Weekly Adjustment", "activity": "Performance-based Reallocation", "subject_focus": "Weak area focus", "tips": "Increase time for subjects showing lower performance in tests"},
            {"time_slot": "Daily Integration", "activity": "Cross-subject Connections", "subject_focus": "Interdisciplinary learning", "tips": "Find connections between subjects to strengthen overall understanding"}
        ]
    }
]

# Additional study tips and strategies
study_tips_data = [
    {
        "category": "Memory Techniques",
        "techniques": [
            {"name": "Spaced Repetition", "description": "Review material at increasing intervals", "application": "Formulas, reactions, definitions"},
            {"name": "Active Recall", "description": "Test yourself without looking at notes", "application": "All subjects - strengthens memory"},
            {"name": "Mnemonics", "description": "Memory aids using associations", "application": "Chemistry reactions, Physics constants"},
            {"name": "Visual Learning", "description": "Use diagrams, mind maps, charts", "application": "Complex concepts, process flows"},
            {"name": "Teaching Method", "description": "Explain concepts to others or yourself", "application": "Ensures deep understanding"}
        ]
    },
    {
        "category": "Problem Solving Strategies",
        "strategies": [
            {"name": "Pattern Recognition", "description": "Identify similar problem types", "application": "Mathematics problem solving"},
            {"name": "Elimination Method", "description": "Rule out incorrect options systematically", "application": "Multiple choice questions"},
            {"name": "Approximation", "description": "Use rough calculations for quick solutions", "application": "Time-pressured situations"},
            {"name": "Backward Working", "description": "Start from answer choices", "application": "When direct method is complex"},
            {"name": "Dimensional Analysis", "description": "Check units for correctness", "application": "Physics numerical problems"}
        ]
    },
    {
        "category": "Exam Day Strategies",
        "strategies": [
            {"name": "Time Management", "description": "Allocate time per section/question", "application": "Prevents rushing in final sections"},
            {"name": "Easy First Approach", "description": "Attempt easy questions first", "application": "Builds confidence and secures marks"},
            {"name": "Guessing Strategy", "description": "Intelligent guessing when unsure", "application": "When negative marking is minimal"},
            {"name": "Review Process", "description": "Systematic checking of answers", "application": "Final 15-20 minutes of exam"},
            {"name": "Stress Management", "description": "Deep breathing, positive self-talk", "application": "When feeling overwhelmed during exam"}
        ]
    }
]

# Combine all data
weekly_schedule_data.extend([
    {
        "category": "Study Tips Database",
        "day": "Reference Material",
        "description": "Comprehensive collection of proven study techniques and strategies",
        "content": study_tips_data
    }
])

def main():
    client = None
    try:
        print("Connecting to MongoDB Atlas cluster...")
        client = MongoClient(MONGO_URL)
        client.admin.command('ping')
        print("MongoDB connection successful.")
        
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        print(f"Preparing to insert data into '{DATABASE_NAME}.{COLLECTION_NAME}'...")
        print("Clearing any existing data in the collection...")
        collection.delete_many({})
        
        print("Inserting the new weekly schedule data...")
        result = collection.insert_many(weekly_schedule_data)
        
        print("\n--- Success! ---")
        print(f"Successfully inserted {len(result.inserted_ids)} documents into the collection.")
        print("You can now view this data in your MongoDB database.")
        
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        print("Please ensure your IP address is whitelisted on MongoDB Atlas.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if client:
            client.close()
            print("\nMongoDB connection closed.")

if __name__ == "__main__":
    main()