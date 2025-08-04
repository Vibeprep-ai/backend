from agno.agent import Agent
from agno.models.google import Gemini
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
from dotenv import load_dotenv
load_dotenv()

class OptimizedTask(BaseModel):
    task_id: str = Field(..., description="Task identifier")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: str = Field(..., description="Optimized priority")
    status: str = Field(default="pending", description="Task status")

class OptimizedSlot(BaseModel):
    time_slot: str = Field(..., description="Time slot")
    task: Optional[OptimizedTask] = Field(None, description="Optimized task assignment")
    reasoning: str = Field(..., description="Why this task is assigned to this slot")

class DaySchedule(BaseModel):
    date: str = Field(..., description="Date for this schedule")
    slots: List[OptimizedSlot] = Field(..., description="List of optimized slots for this date")

class OptimizedSchedule(BaseModel):
    user_id: str = Field(..., description="Student user ID")
    optimization_date: str = Field(..., description="Date when optimization was performed")
    daily_schedules: List[DaySchedule] = Field(..., description="Optimized schedule for each date")
    optimization_summary: str = Field(..., description="Summary of optimizations made")
    recommendations: List[str] = Field(..., description="Additional recommendations for the student")
    psychometric_considerations: List[str] = Field(
        ..., 
        description="How psychometric insights influenced the schedule"
    )

schedule_agent = Agent(
    model=Gemini(id="gemini-2.0-flash"),
    description="""You are an AI Schedule Optimization Agent that creates personalized study schedules for students.

Your responsibilities:
1. Analyze student's psychometric insights from JSON input
2. Review current academic progress reports to identify areas needing attention
3. Optimize task scheduling based on:
   - Peak productivity hours and energy patterns
   - Focus duration and break requirements
   - Subject difficulty and student's weak/strong areas
   - Task priorities and deadlines
   - Stress tolerance and personality traits
   - Learning style preferences

Key optimization principles:
- Schedule difficult/weak subjects during peak hours
- Align task types with learning preferences
- Respect natural energy patterns and focus limits
- Balance high-priority tasks with student capacity
- Include appropriate breaks based on personality
- Consider deadline urgency vs. learning effectiveness
- Adapt to introvert/extrovert scheduling patterns

Always provide clear reasoning for each scheduling decision and actionable recommendations.""",
    response_model=OptimizedSchedule,
    show_tool_calls=True,
)

def optimize_with_prompt(user_prompt: str, input_data_json: str) -> OptimizedSchedule:
    
    try:
        input_data = json.loads(input_data_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON input: {e}")
    
    user_id = input_data.get("user_id", "unknown_user")
    target_dates = input_data.get("target_dates", [])
    current_schedule = input_data.get("current_schedule", {})
    psychometric_insights = input_data.get("psychometric_insights", {})
    progress_reports = input_data.get("progress_reports", [])
    available_tasks = input_data.get("available_tasks", [])
    
    optimization_prompt = f"""
    **USER REQUEST:** {user_prompt}

    **Student ID:** {user_id}
    **Target Dates:** {', '.join(target_dates)}

    **Current Schedule:**
    ```json
    {json.dumps(current_schedule, indent=2)}
    ```

    **Psychometric Insights:**
    ```json
    {json.dumps(psychometric_insights, indent=2)}
    ```

    **Progress Reports:**
    ```json
    {json.dumps(progress_reports, indent=2)}
    ```

    **Available Tasks:**
    ```json
    {json.dumps(available_tasks, indent=2)}
    ```

    Based on the user's request: "{user_prompt}" and the provided data, create an optimized schedule.

    Key considerations:
    1. **User's specific request**: {user_prompt}
    2. **Psychometric profile**: Personality ({psychometric_insights.get('personality_type', 'N/A')}), learning style ({psychometric_insights.get('learning_style', 'N/A')}), focus duration ({psychometric_insights.get('focus_duration', 'N/A')} min)
    3. **Academic progress**: Focus on subjects with lower scores or completion rates
    4. **Schedule optimization**: Improve the existing structure for {len(current_schedule)} days
    5. **Task integration**: Place {len(available_tasks)} available tasks strategically
    6. **Target dates**: Optimize for {', '.join(target_dates)}

    Return the schedule using the daily_schedules format with a list of DaySchedule objects, each containing a date and list of slots.
    """
    
    response = schedule_agent.run(optimization_prompt)
    return response.content

def example_simple_optimization():
    
    input_json = json.dumps({
        "user_id": "student_123",
        "target_dates": ["2025-08-05", "2025-08-06"],
        "current_schedule": {
            "2025-08-05": [
                {
                    "time_slot": "09:00-10:00",
                    "task": {
                        "task_id": "task_001",
                        "title": "Math Practice",
                        "subject": "Mathematics",
                        "priority": "high"
                    }
                },
                {
                    "time_slot": "10:00-11:00",
                    "task": None
                }
            ]
        },
        "psychometric_insights": {
            "personality_type": "INTJ",
            "learning_style": "visual",
            "focus_duration": 45,
            "peak_hours": ["09:00-11:00"],
            "energy_level": "morning"
        },
        "progress_reports": [
            {
                "subject": "Mathematics",
                "current_score": 75.0,
                "target_score": 85.0,
                "weak_areas": ["calculus"]
            }
        ],
        "available_tasks": [
            {
                "task_id": "task_002",
                "title": "Physics Study",
                "subject": "Physics",
                "priority": "medium"
            }
        ]
    })
    
    user_request = "Help me balance my study schedule better and focus on my weak areas"
    
    result = optimize_with_prompt(user_request, input_json)
    return result

if __name__ == "__main__":
    result = example_simple_optimization()
    print("Optimization Result:")
    if hasattr(result, 'dict'):
        print(json.dumps(result.dict(), indent=2))
    else:
        print(result)