from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
from agno.tools.tavily import TavilyTools
from agno.tools.reasoning import ReasoningTools
from pydantic import BaseModel, Field
from typing import Dict, Any

load_dotenv()

class OptimizedSchema(BaseModel):
    optimized_schedule: str = Field(..., description="Complete optimized weekly schedule with day-wise time slots and activities")
    rationale: str = Field(..., description="Explanation of the optimization strategy and key improvements")
    included_changes: list[str] = Field(..., description="List of changes made to optimize the schedule")
    excluded_changes: list[str] = Field(..., description="List of changes removed from the schedule")
    key_recommendations: list[str] = Field(..., description="Additional recommendations for better exam preparation")


class ScheduleOptimizer:
    def __init__(self):
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            description="""
                You are an expert schedule optimizer specialized in helping students prepare for competitive exams like JEE, NEET, UPSC, CAT, and other similar entrance tests.
                
                Your task is to analyze a student's existing schedule and create a completely NEW OPTIMIZED SCHEDULE for maximum effectiveness in exam preparation by:
                
                1. Balancing study time across different subjects based on syllabus weightage and student's proficiency
                2. Incorporating regular breaks to prevent burnout and improve retention
                3. Allocating time for revision, practice tests, and solving previous years' papers
                4. Suggesting optimal study techniques based on subject matter (e.g., active recall for theory, timed practice for numerical problems)
                5. Integrating spaced repetition for difficult topics
                6. Creating a sustainable long-term schedule that accounts for the student's other commitments
                7. Prioritizing weak topics while maintaining strong topics
                
                IMPORTANT: You must provide a COMPLETE NEW WEEKLY SCHEDULE in the 'optimized_schedule' field with all 7 days (Monday to Sunday) showing exact time slots and activities.
                
                When optimizing, prioritize evidence-based learning strategies, proper time management, and personalized approaches based on the student's strengths and weaknesses. Your goal is to create a balanced, effective, and sustainable study plan that maximizes exam performance.
            """,
            tools=[TavilyTools(), ReasoningTools()],
            output_schema=OptimizedSchema,
            markdown=True
        )
        
        self.student_data = None
        self.current_schedule = None
    
    def load_student_data(self, data: Dict[str, Any]):
        self.student_data = data
    
    def load_current_schedule(self, schedule: str):
        self.current_schedule = schedule
    
    def create_optimization_prompt(self) -> str:
        return f"""
Please create a COMPLETE OPTIMIZED WEEKLY SCHEDULE for a JEE Advanced aspirant.

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

OPTIMIZATION REQUIREMENTS:
- Address the weak topics identified: {self.student_data['psychometric_profile']['weak_topics']}
- Ensure adequate sleep (7-8 hours)
- Incorporate stress management and meditation/yoga sessions
- Use spaced repetition for retention
- Allocate more time to Physics (65%) and Mathematics (72%) compared to Chemistry (78%)
- Include regular 5-10 minute breaks between study sessions
- Include mental health activities and physical exercise
- Optimize study sessions during peak productivity hours: {self.student_data['psychometric_profile']['peak_productivity_hours']}
- Respect attention span of {self.student_data['psychometric_profile']['attention_span_minutes']} minutes per session
- Include daily revision slots
- Dedicate specific slots for weak topic practice
- Include weekly mock tests and analysis

IMPORTANT: In the 'optimized_schedule' field, provide a COMPLETE day-by-day schedule for the entire week (Monday through Sunday) with exact time slots and activities. Format it clearly like:

MONDAY:
- 5:30-6:30 AM: Activity
- 6:30-7:00 AM: Activity
... (all time slots for the day)

TUESDAY:
... (all time slots for the day)

... (continue for all 7 days)

Make sure to include all activities: study sessions, breaks, meals, sleep, exercise, revision, tests, etc.
"""
    
    def optimize_schedule(self) -> OptimizedSchema:
        """Run the schedule optimization"""
        if not self.student_data or not self.current_schedule:
            raise ValueError("Please load student data and current schedule first")
        
        prompt = self.create_optimization_prompt()
        response = self.agent.run(prompt).content
        return response
    
    def print_results(self, response: OptimizedSchema):
        """Print the optimization results in a formatted way"""
        print("\n" + "=" * 80)
        print("OPTIMIZED WEEKLY SCHEDULE")
        print("=" * 80)
        print(f"\n{response.optimized_schedule}\n")
        
        print("\n" + "=" * 80)
        print("RATIONALE")
        print("=" * 80)
        print(f"\n{response.rationale}\n")
        
        print("\n" + "=" * 80)
        print("CHANGES INCLUDED")
        print("=" * 80)
        for i, change in enumerate(response.included_changes, 1):
            print(f"{i}. {change}")
        
        print("\n" + "=" * 80)
        print("CHANGES EXCLUDED")
        print("=" * 80)
        for i, change in enumerate(response.excluded_changes, 1):
            print(f"{i}. {change}")
        
        print("\n" + "=" * 80)
        print("KEY RECOMMENDATIONS")
        print("=" * 80)
        for i, rec in enumerate(response.key_recommendations, 1):
            print(f"{i}. {rec}")
        
        print("\n" + "=" * 80)


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


if __name__ == "__main__":
    print("=" * 80)
    print("SCHEDULE OPTIMIZATION FOR JEE PREPARATION")
    print("=" * 80)
    print("\nInitializing Schedule Optimizer...\n")
    
    # Create optimizer instance
    optimizer = ScheduleOptimizer()
    
    # Load data
    optimizer.load_student_data(get_sample_student_data())
    optimizer.load_current_schedule(get_sample_current_schedule())
    
    print("Processing optimization request...\n")
    
    # Run optimization
    response = optimizer.optimize_schedule()
    
    # Print results
    optimizer.print_results(response)


