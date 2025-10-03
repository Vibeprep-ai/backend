from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
from agno.tools.tavily import TavilyTools
from agno.tools.reasoning import ReasoningTools
from pydantic import BaseModel, Field
from typing import Dict, Any, List

load_dotenv()

class ProposedChange(BaseModel):
    change_id: int = Field(..., description="Unique identifier for the change")
    category: str = Field(..., description="Category of change (e.g., 'sleep', 'break', 'study_time', 'weak_topics', 'stress_management')")
    description: str = Field(..., description="Detailed description of the proposed change")
    reason: str = Field(..., description="Why this change is being proposed")
    impact: str = Field(..., description="Expected impact on exam preparation")


class ProposedChangesSchema(BaseModel):
    proposed_changes: List[ProposedChange] = Field(..., description="List of all proposed changes to the schedule")
    summary: str = Field(..., description="Overall summary of the optimization strategy")


class OptimizedSchema(BaseModel):
    optimized_schedule: str = Field(..., description="Complete optimized weekly schedule with day-wise time slots and activities")
    rationale: str = Field(..., description="Explanation of the optimization strategy and key improvements")
    included_changes: list[str] = Field(..., description="List of changes made to optimize the schedule")
    excluded_changes: list[str] = Field(..., description="List of changes removed from the schedule")
    key_recommendations: list[str] = Field(..., description="Additional recommendations for better exam preparation")


class ScheduleOptimizer:
    def __init__(self):
        self.changes_agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            description="""
                You are an expert schedule optimizer specialized in helping students prepare for competitive exams like JEE, NEET, UPSC, CAT, and other similar entrance tests.
                
                Your task is to analyze a student's existing schedule and PROPOSE specific changes for optimization. Each change should be clear, actionable, and justified.
                
                Focus on:
                1. Identifying specific time slots that need modification
                2. Proposing concrete changes (e.g., "Change sleep time from 11 PM-6 AM to 10 PM-6 AM")
                3. Explaining why each change will help exam preparation
                4. Categorizing changes for easy understanding
                
                Be specific and practical in your proposals.
            """,
            tools=[TavilyTools(), ReasoningTools()],
            output_schema=ProposedChangesSchema,
            markdown=True
        )
        
        self.schedule_agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            description="""
                You are an expert schedule optimizer specialized in helping students prepare for competitive exams like JEE, NEET, UPSC, CAT, and other similar entrance tests.
                
                Your task is to create a COMPLETE NEW OPTIMIZED SCHEDULE based on the selected changes provided by the user.
                
                IMPORTANT: You must provide a COMPLETE WEEKLY SCHEDULE in the 'optimized_schedule' field with all 7 days (Monday to Sunday) showing exact time slots and activities.
                
                When creating the schedule, prioritize evidence-based learning strategies, proper time management, and personalized approaches based on the student's strengths and weaknesses.
            """,
            tools=[TavilyTools(), ReasoningTools()],
            output_schema=OptimizedSchema,
            markdown=True
        )
        
        self.student_data = None
        self.current_schedule = None
        self.proposed_changes = None
        self.selected_changes = []
    
    def load_student_data(self, data: Dict[str, Any]):
        self.student_data = data
    
    def load_current_schedule(self, schedule: str):
        self.current_schedule = schedule
    
    def create_changes_proposal_prompt(self) -> str:
        return f"""
Analyze the following JEE Advanced student's schedule and propose specific changes for optimization.

STUDENT PSYCHOMETRIC DATA:
{self.student_data}

CURRENT WEEKLY SCHEDULE:
{self.current_schedule}

CONCERNS IDENTIFIED:
1. Only 6 hours of sleep (should be 7-8 hours)
2. High stress levels not being addressed
3. Limited breaks between long study sessions
4. No dedicated time for weak topics practice
5. Inconsistent revision strategy
6. Limited time for previous year papers
7. Late night social media usage affecting sleep

Please propose specific, actionable changes. Each change should:
- Have a unique ID
- Be categorized (sleep, breaks, study_time, weak_topics, stress_management, revision, etc.)
- Include a clear description of what to change
- Explain why this change is beneficial
- Describe the expected impact

Consider:
- Weak topics: {self.student_data['psychometric_profile']['weak_topics']}
- Peak productivity: {self.student_data['psychometric_profile']['peak_productivity_hours']}
- Attention span: {self.student_data['psychometric_profile']['attention_span_minutes']} minutes
- Subject proficiency: Physics (65%), Chemistry (78%), Mathematics (72%)

Propose 10-15 specific changes that the student can choose from.
"""
    
    def get_proposed_changes(self) -> ProposedChangesSchema:
        if not self.student_data or not self.current_schedule:
            raise ValueError("Please load student data and current schedule first")
        
        prompt = self.create_changes_proposal_prompt()
        response = self.changes_agent.run(prompt).content
        self.proposed_changes = response
        return response
    
    def select_changes_programmatic(self, change_ids: List[int]):
        valid_ids = [c.change_id for c in self.proposed_changes.proposed_changes]
        invalid_ids = [id for id in change_ids if id not in valid_ids]
        
        if invalid_ids:
            raise ValueError(f"Invalid change IDs: {invalid_ids}")
        
        self.selected_changes = change_ids
    
    def create_final_schedule_prompt(self) -> str:
        selected_change_details = [
            c for c in self.proposed_changes.proposed_changes 
            if c.change_id in self.selected_changes
        ]
        
        excluded_change_details = [
            c for c in self.proposed_changes.proposed_changes 
            if c.change_id not in self.selected_changes
        ]
        
        return f"""
Create a COMPLETE OPTIMIZED WEEKLY SCHEDULE for a JEE Advanced aspirant based on the selected changes.

STUDENT PSYCHOMETRIC DATA:
{self.student_data}

CURRENT WEEKLY SCHEDULE:
{self.current_schedule}

SELECTED CHANGES TO IMPLEMENT:
{[f"ID {c.change_id}: {c.description}" for c in selected_change_details]}

EXCLUDED CHANGES (DO NOT IMPLEMENT):
{[f"ID {c.change_id}: {c.description}" for c in excluded_change_details]}

IMPORTANT: 
1. In the 'optimized_schedule' field, provide a COMPLETE day-by-day schedule for the entire week (Monday through Sunday) with exact time slots and activities.
2. ONLY implement the selected changes listed above.
3. Keep other aspects of the schedule similar to the current one unless modified by selected changes.
4. Format clearly like:

MONDAY:
- 5:30-6:30 AM: Activity
- 6:30-7:00 AM: Activity
... (all time slots for the day)

TUESDAY:
... (all time slots for the day)

... (continue for all 7 days)

Make sure to include all activities: study sessions, breaks, meals, sleep, exercise, revision, tests, etc.

In the 'included_changes' field, list the descriptions of changes that were implemented.
In the 'excluded_changes' field, list the descriptions of changes that were NOT implemented (user rejected).
"""
    
    def generate_final_schedule(self) -> OptimizedSchema:
        if not self.selected_changes:
            raise ValueError("Please select changes first")
        
        prompt = self.create_final_schedule_prompt()
        response = self.schedule_agent.run(prompt).content
        return response


# Sample data
def get_sample_student_data():
    return {
        "name": "Rahul Sharma",
        "age": 17,
        "target_exam": "JEE Advanced 2025",
        "exam_date": "2025-05-25",
        "current_preparation_level": "intermediate",
        "psychometric_profile": {
            "learning_style": "visual and kinesthetic",
            "attention_span_minutes": 45,
            "stress_level": "high (7/10)",
            "sleep_hours": 6,
            "peak_productivity_hours": ["6:00-9:00 AM", "8:00-10:00 PM"],
            "subject_proficiency": {
                "physics": {"score": 65, "comfort_level": "moderate"},
                "chemistry": {"score": 78, "comfort_level": "high"},
                "mathematics": {"score": 72, "comfort_level": "moderate"}
            },
            "weak_topics": {
                "physics": ["Electromagnetism", "Modern Physics", "Optics"],
                "chemistry": ["Organic Reactions", "Chemical Bonding", "Electrochemistry"],
                "mathematics": ["Calculus", "Coordinate Geometry", "Probability"]
            },
            "strong_topics": {
                "physics": ["Mechanics", "Thermodynamics"],
                "chemistry": ["Physical Chemistry", "Inorganic Chemistry basics"],
                "mathematics": ["Algebra", "Trigonometry"]
            }
        }
    }


def get_sample_current_schedule():
    return """
MONDAY:
- 6:00-7:00 AM: Wake up, morning routine
- 7:00-9:00 AM: Physics study (theory)
- 9:00-9:30 AM: Breakfast
- 9:30-12:30 PM: Coaching classes (all subjects)
- 12:30-1:30 PM: Lunch and rest
- 1:30-4:00 PM: Mathematics problems solving
- 4:00-4:30 PM: Tea break
- 4:30-7:00 PM: Chemistry study
- 7:00-8:00 PM: Dinner
- 8:00-10:30 PM: Self-study and homework
- 10:30-11:00 PM: Social media/entertainment
- 11:00 PM-6:00 AM: Sleep

TUESDAY:
- 6:00-7:00 AM: Wake up, morning routine
- 7:00-9:00 AM: Chemistry study (theory)
- 9:00-9:30 AM: Breakfast
- 9:30-12:30 PM: Coaching classes
- 12:30-1:30 PM: Lunch and rest
- 1:30-4:00 PM: Physics numericals
- 4:00-4:30 PM: Tea break
- 4:30-7:00 PM: Mathematics study
- 7:00-8:00 PM: Dinner
- 8:00-10:30 PM: Self-study and revision
- 10:30-11:00 PM: Social media/entertainment
- 11:00 PM-6:00 AM: Sleep

WEDNESDAY:
- 6:00-7:00 AM: Wake up, morning routine
- 7:00-9:00 AM: Mathematics study (theory)
- 9:00-9:30 AM: Breakfast
- 9:30-12:30 PM: Coaching classes
- 12:30-1:30 PM: Lunch and rest
- 1:30-4:00 PM: Chemistry numericals
- 4:00-4:30 PM: Tea break
- 4:30-7:00 PM: Physics study
- 7:00-8:00 PM: Dinner
- 8:00-10:30 PM: Self-study and assignments
- 10:30-11:00 PM: Social media/entertainment
- 11:00 PM-6:00 AM: Sleep

THURSDAY:
- 6:00-7:00 AM: Wake up, morning routine
- 7:00-9:00 AM: Physics study
- 9:00-9:30 AM: Breakfast
- 9:30-12:30 PM: Coaching classes
- 12:30-1:30 PM: Lunch and rest
- 1:30-4:00 PM: Mathematics problems
- 4:00-4:30 PM: Tea break
- 4:30-7:00 PM: Chemistry study
- 7:00-8:00 PM: Dinner
- 8:00-10:30 PM: Self-study
- 10:30-11:00 PM: Social media/entertainment
- 11:00 PM-6:00 AM: Sleep

FRIDAY:
- 6:00-7:00 AM: Wake up, morning routine
- 7:00-9:00 AM: Chemistry revision
- 9:00-9:30 AM: Breakfast
- 9:30-12:30 PM: Coaching classes
- 12:30-1:30 PM: Lunch and rest
- 1:30-4:00 PM: Physics numericals
- 4:00-4:30 PM: Tea break
- 4:30-7:00 PM: Mathematics study
- 7:00-8:00 PM: Dinner
- 8:00-10:30 PM: Weekly revision
- 10:30-11:00 PM: Social media/entertainment
- 11:00 PM-6:00 AM: Sleep

SATURDAY:
- 6:00-7:00 AM: Wake up, morning routine
- 7:00-9:00 AM: Mock test (full syllabus)
- 9:00-10:00 AM: Breakfast
- 10:00-1:00 PM: Mock test analysis
- 1:00-2:00 PM: Lunch and rest
- 2:00-5:00 PM: Doubt clearing session
- 5:00-7:00 PM: Free time/hobby
- 7:00-8:00 PM: Dinner
- 8:00-10:00 PM: Light revision
- 10:00-11:00 PM: Entertainment
- 11:00 PM-6:00 AM: Sleep

SUNDAY:
- 7:00-8:00 AM: Wake up, morning routine
- 8:00-10:00 AM: Previous year papers
- 10:00-11:00 AM: Breakfast
- 11:00-2:00 PM: Weak topic practice
- 2:00-3:00 PM: Lunch
- 3:00-5:00 PM: Recreation/family time
- 5:00-7:00 PM: Light study
- 7:00-8:00 PM: Dinner
- 8:00-10:00 PM: Planning for next week
- 10:00 PM-7:00 AM: Sleep
"""


def main():
    
    print("\n" + "=" * 80)
    print("INTERACTIVE SCHEDULE OPTIMIZER FOR COMPETITIVE EXAM PREPARATION")
    print("=" * 80)
    

    optimizer = ScheduleOptimizer()
    
    student_data = get_sample_student_data()
    current_schedule = get_sample_current_schedule()
    
    optimizer.load_student_data(student_data)
    optimizer.load_current_schedule(current_schedule)
    
    print(f"\nStudent: {student_data['name']}")
    print(f"Target Exam: {student_data['target_exam']}")
    print(f"Current Preparation Level: {student_data['current_preparation_level']}")
    
    print("\n" + "=" * 80)
    print("STEP 1: ANALYZING YOUR SCHEDULE")
    print("=" * 80)
    print("\nPlease wait while we analyze your schedule and propose optimizations...")
    
    proposed_changes = optimizer.get_proposed_changes()
    
    print(f"\n✓ Analysis Complete!")
    print(f"\nSummary: {proposed_changes.summary}")
    print(f"\nWe have identified {len(proposed_changes.proposed_changes)} potential improvements.")
    
    print("\n" + "=" * 80)
    print("STEP 2: PROPOSED CHANGES")
    print("=" * 80)
    
    for change in proposed_changes.proposed_changes:
        print(f"\n┌─ Change ID: [{change.change_id}]")
        print(f"│  Category: {change.category.upper()}")
        print(f"│  Description: {change.description}")
        print(f"│  Reason: {change.reason}")
        print(f"│  Expected Impact: {change.impact}")
        print("└" + "─" * 78)
    
    print("\n" + "=" * 80)
    print("STEP 3: SELECT CHANGES TO APPLY")
    print("=" * 80)
    
    all_ids = [c.change_id for c in proposed_changes.proposed_changes]
    print(f"\nAvailable Change IDs: {', '.join(map(str, all_ids))}")
    print("\nOptions:")
    print("  1. Enter specific IDs (e.g., 1,2,3,5,7)")
    print("  2. Type 'all' to accept all changes")
    print("  3. Type 'none' to reject all changes and exit")
    
    while True:
        try:
            user_input = input("\nYour selection: ").strip().lower()
            
            if user_input == 'none':
                print("\nNo changes selected. Exiting...")
                return None, proposed_changes, None
            
            elif user_input == 'all':
                selected_ids = all_ids
                print(f"\n✓ Selected all {len(selected_ids)} changes")
                break
            
            else:
                selected_ids = [int(x.strip()) for x in user_input.split(',')]
                
                # Validate IDs
                invalid_ids = [id for id in selected_ids if id not in all_ids]
                if invalid_ids:
                    print(f"\n✗ Invalid IDs: {invalid_ids}")
                    print(f"  Please enter IDs from: {', '.join(map(str, all_ids))}")
                    continue
                
                print(f"\n✓ Selected {len(selected_ids)} changes: {selected_ids}")
                break
                
        except ValueError:
            print("\n✗ Invalid input. Please enter comma-separated numbers, 'all', or 'none'")
            continue
    
    print("\n" + "=" * 80)
    print("CHANGES TO BE IMPLEMENTED")
    print("=" * 80)
    
    selected_changes = [c for c in proposed_changes.proposed_changes if c.change_id in selected_ids]
    for change in selected_changes:
        print(f"  ✓ [{change.change_id}] {change.description}")
    
    excluded_changes = [c for c in proposed_changes.proposed_changes if c.change_id not in selected_ids]
    if excluded_changes:
        print("\n" + "=" * 80)
        print("CHANGES NOT IMPLEMENTED")
        print("=" * 80)
        for change in excluded_changes:
            print(f"  ✗ [{change.change_id}] {change.description}")
  
    
    print("\n" + "=" * 80)
    print("STEP 4: GENERATING OPTIMIZED SCHEDULE")
    print("=" * 80)
    print("\nPlease wait while we create your personalized schedule...")
    
    optimizer.select_changes_programmatic(selected_ids)
    final_schedule = optimizer.generate_final_schedule()
    
    print("\n✓ Schedule Generated Successfully!")
    
    print("\n" + "=" * 80)
    print("YOUR OPTIMIZED WEEKLY SCHEDULE")
    print("=" * 80)
    print(f"\n{final_schedule.optimized_schedule}\n")
    
    print("\n" + "=" * 80)
    print("OPTIMIZATION RATIONALE")
    print("=" * 80)
    print(f"\n{final_schedule.rationale}\n")
    
    print("\n" + "=" * 80)
    print(f"IMPLEMENTED CHANGES ({len(final_schedule.included_changes)})")
    print("=" * 80)
    for i, change in enumerate(final_schedule.included_changes, 1):
        print(f"  {i}. {change}")
    
    if final_schedule.excluded_changes:
        print("\n" + "=" * 80)
        print(f"EXCLUDED CHANGES ({len(final_schedule.excluded_changes)})")
        print("=" * 80)
        for i, change in enumerate(final_schedule.excluded_changes, 1):
            print(f"  {i}. {change}")
    
    print("\n" + "=" * 80)
    print("KEY RECOMMENDATIONS")
    print("=" * 80)
    for i, rec in enumerate(final_schedule.key_recommendations, 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "=" * 80)
    print("✓ OPTIMIZATION COMPLETE!")
    print("=" * 80)
    print("\nYour personalized study schedule is ready.")
    print("Remember: Consistency is key to success in competitive exams!")
    print("=" * 80 + "\n")
    
    return optimizer, proposed_changes, final_schedule


if __name__ == "__main__":
    main()


