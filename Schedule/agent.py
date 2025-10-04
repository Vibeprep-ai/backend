import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agno.agent import Agent
from agno.models.groq import Groq
from Tools.get_db_info import get_schedule_info
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv()

class ScheduleAssistant:
    def __init__(self):
        self.agent = Agent(
            model=Groq(id="llama-3.3-70b-versatile"),
            markdown=True,
            tools=[get_schedule_info],
            read_chat_history=True,
            description="""
            You are a helpful study schedule assistant. Your role is to:
            1. Fetch student schedules from the database using the get_schedule_info tool
            2. Answer questions about the schedule accurately
            3. Provide helpful insights and recommendations based on the schedule
            4. Help students understand their time management and study patterns
            
            Always use the get_schedule_info tool to fetch the latest schedule data before answering questions.
            Be clear, concise, and student-friendly in your responses.
            """
        )
    
    def get_student_schedule(self, student_name: Optional[str] = None, 
                            category: Optional[str] = None,
                            target_exam: Optional[str] = None) -> Dict[str, Any]:
        schedules = get_schedule_info(
            student_name=student_name,
            category=category,
            target_exam=target_exam
        )
        
        if schedules:
            return schedules[0] if isinstance(schedules, list) else schedules
        return None
    
    def answer_schedule_question(self, question: str, 
                                 student_name: Optional[str] = None,
                                 category: Optional[str] = None,
                                 target_exam: Optional[str] = None) -> str:
        context = f"""
        Student Question: {question}
        
        Instructions:
        1. Use the get_schedule_info tool to fetch the relevant schedule
        2. Filter criteria: student_name="{student_name}", category="{category}", target_exam="{target_exam}"
        3. Analyze the schedule data carefully
        4. Answer the question accurately based on the schedule
        5. If the schedule is not found, inform the user politely
        
        Provide a helpful, detailed answer that directly addresses the student's question.
        """
        
        response = self.agent.run(context)
        return response.content
    
    def analyze_schedule(self, student_name: Optional[str] = None,
                        category: Optional[str] = None,
                        target_exam: Optional[str] = None) -> str:
        prompt = f"""
        Fetch and analyze the schedule for:
        - Student: {student_name or "Any student"}
        - Category: {category or "Any category"}
        - Target Exam: {target_exam or "Any exam"}
        
        Use the get_schedule_info tool to retrieve the schedule.
        
        Provide a comprehensive analysis including:
        1. **Overview**: Summary of the schedule structure
        2. **Time Distribution**: How time is allocated across subjects/activities
        3. **Study Patterns**: When and how study sessions are organized
        4. **Breaks and Rest**: Balance between study and rest periods
        5. **Strengths**: What's working well in this schedule
        6. **Recommendations**: Potential improvements or adjustments
        7. **Key Highlights**: Important activities and time slots
        
        Make the analysis practical and actionable.
        """
        
        response = self.agent.run(prompt)
        return response.content
    
    def compare_schedules(self, criteria1: Dict[str, str], criteria2: Dict[str, str]) -> str:
        prompt = f"""
        Compare two schedules:
        
        Schedule 1: {criteria1}
        Schedule 2: {criteria2}
        
        Use get_schedule_info tool twice to fetch both schedules.
        
        Provide a detailed comparison:
        1. **Time Allocation Differences**
        2. **Study Approach Variations**
        3. **Efficiency Analysis**
        4. **Pros and Cons of each**
        5. **Which schedule might be better for different situations**
        
        Be objective and provide balanced insights.
        """
        
        response = self.agent.run(prompt)
        return response.content
    
    def get_time_slot_details(self, question: str, 
                             student_name: Optional[str] = None,
                             category: Optional[str] = None) -> str:

        prompt = f"""
        Question about schedule time slot: {question}
        
        Student: {student_name or "Any"}
        Category: {category or "Any"}
        
        Use get_schedule_info to fetch the schedule, then:
        1. Identify the relevant time slot(s)
        2. Provide detailed information about activities during that time
        3. Explain the purpose and importance of that time slot
        4. Suggest tips or modifications if asked
        
        Be specific and reference exact time slots from the schedule.
        """
        
        response = self.agent.run(prompt)
        return response.content
    
    def suggest_modifications(self, modification_request: str,
                             student_name: Optional[str] = None,
                             category: Optional[str] = None) -> str:

        prompt = f"""
        Student wants to modify their schedule: {modification_request}
        
        Student: {student_name or "Any"}
        Category: {category or "Any"}
        
        Steps:
        1. Use get_schedule_info to fetch the current schedule
        2. Understand the modification request
        3. Analyze impact on overall schedule
        4. Suggest specific changes with time slots
        5. Explain the rationale behind suggestions
        6. Highlight any trade-offs
        
        Provide practical, implementable modifications.
        """
        
        response = self.agent.run(prompt)
        return response.content
    
    def chat(self, message: str, context: Optional[Dict[str, str]] = None) -> str:
        context_str = ""
        if context:
            context_str = f"\nContext: {context}"
        
        prompt = f"""
        User Message: {message}{context_str}
        
        You are a helpful schedule assistant. Use the get_schedule_info tool when needed to fetch schedule data.
        Answer the user's question accurately and helpfully based on the schedule information.
        
        If the question is not about schedules, politely guide the user back to schedule-related topics.
        """
        
        response = self.agent.run(prompt)
        return response.content




def main():
    schedule_assistant = ScheduleAssistant()    
    print("=" * 80)
    print("SCHEDULE ASSISTANT DEMO")
    print("=" * 80)
    
    # Example 1: Get schedule analysis
    print("\n### Example 1: Schedule Analysis ###\n")
    analysis = schedule_assistant.analyze_schedule(
        student_name="Rahul Sharma",
        category="Optimized Schedule"
    )
    print(analysis)
    
    print("\n" + "=" * 80 + "\n")
    
    # Example 2: Answer specific question
    print("### Example 2: Specific Question ###\n")
    answer = schedule_assistant.answer_schedule_question(
        question="What time should I study physics on Monday?",
        student_name="Rahul Sharma",
        category="Optimized Schedule"
    )
    print(answer)
    
    print("\n" + "=" * 80 + "\n")
    
    # Example 3: Time slot details
    print("### Example 3: Time Slot Details ###\n")
    time_info = schedule_assistant.get_time_slot_details(
        question="What activities are scheduled between 6 AM and 9 AM?",
        category="Regular Weekdays"
    )
    print(time_info)
    
    print("\n" + "=" * 80 + "\n")
    
    # Example 4: General chat
    print("### Example 4: General Chat ###\n")
    chat_response = schedule_assistant.chat(
        message="How many hours of sleep are scheduled in my routine?",
        context={"student_name": "Rahul Sharma"}
    )
    print(chat_response)
    
    print("\n" + "=" * 80 + "\n")
    
    # Example 5: Modification suggestions
    print("### Example 5: Modification Suggestions ###\n")
    modifications = schedule_assistant.suggest_modifications(
        modification_request="I want to add more time for weak topics in the evening",
        student_name="Rahul Sharma"
    )
    print(modifications)


if __name__ == "__main__":
    main()