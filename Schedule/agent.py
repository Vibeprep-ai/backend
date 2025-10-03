import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agno.agent import Agent
from agno.models.groq import Groq
from Tools.get_db_info import get_schedule_info
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional

load_dotenv()

class CompetitiveExamScheduler:
    def __init__(self):
        self.agent = Agent(
            model=Groq(id="llama-3.3-70b-versatile"),
            markdown=True,
            tools=[get_schedule_info],
            read_chat_history=True
        )
        
        self.exam_patterns = {
            "JEE": {
                "subjects": ["Physics", "Chemistry", "Mathematics"],
                "study_hours": "8-10",
                "revision_frequency": "weekly",
                "mock_tests": "bi-weekly"
            },
            "NEET": {
                "subjects": ["Physics", "Chemistry", "Biology"],
                "study_hours": "8-10",
                "revision_frequency": "weekly", 
                "mock_tests": "weekly"
            },
            "GRE": {
                "subjects": ["Verbal Reasoning", "Quantitative Reasoning", "Analytical Writing"],
                "study_hours": "4-6",
                "revision_frequency": "daily",
                "mock_tests": "weekly"
            },
            "SAT": {
                "subjects": ["Mathematics", "Reading", "Writing"],
                "study_hours": "4-6",
                "revision_frequency": "daily",
                "mock_tests": "weekly"
            },
            "CFA": {
                "subjects": ["Ethics", "Economics", "Financial Analysis", "Portfolio Management"],
                "study_hours": "6-8",
                "revision_frequency": "weekly",
                "mock_tests": "monthly"
            }
        }
    
    def analyze_student_query(self, query: str) -> Dict[str, Any]:
        exam_type = self.detect_exam_type(query)
        study_phase = self.detect_study_phase(query)
        time_available = self.extract_time_availability(query)
        weak_subjects = self.extract_weak_subjects(query)
        immediate_events = self.extract_immediate_events(query)
        
        return {
            "exam_type": exam_type,
            "study_phase": study_phase,
            "time_available": time_available,
            "weak_subjects": weak_subjects,
            "immediate_events": immediate_events
        }
    
    def detect_exam_type(self, query: str) -> str:
        query_lower = query.lower()
        for exam in self.exam_patterns.keys():
            if exam.lower() in query_lower:
                return exam
        return "JEE"
    
    def detect_study_phase(self, query: str) -> str:
        query_lower = query.lower()
        if any(word in query_lower for word in ["revision", "final", "last month"]):
            return "revision"
        elif any(word in query_lower for word in ["weak", "struggling", "difficulty"]):
            return "intensive"
        else:
            return "regular"
    
    def extract_time_availability(self, query: str) -> str:
        query_lower = query.lower()
        if any(word in query_lower for word in ["3 hours", "limited time", "part time"]):
            return "limited"
        elif any(word in query_lower for word in ["full day", "whole day", "8 hours"]):
            return "full_time"
        else:
            return "moderate"
    
    def extract_weak_subjects(self, query: str) -> List[str]:
        weak_subjects = []
        query_lower = query.lower()
        
        subjects_map = {
            "physics": "Physics",
            "chemistry": "Chemistry", 
            "mathematics": "Mathematics",
            "math": "Mathematics",
            "biology": "Biology",
            "verbal": "Verbal Reasoning",
            "quant": "Quantitative Reasoning",
            "reading": "Reading",
            "writing": "Writing"
        }
        
        for key, subject in subjects_map.items():
            if key in query_lower and ("weak" in query_lower or "struggling" in query_lower):
                weak_subjects.append(subject)
        
        return weak_subjects
    
    def extract_immediate_events(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        events = {}
        
        if "tomorrow" in query_lower:
            events["urgency"] = "tomorrow"
        elif "today" in query_lower:
            events["urgency"] = "today"
        elif "next week" in query_lower:
            events["urgency"] = "next_week"
        
        if any(word in query_lower for word in ["test", "exam", "quiz"]):
            events["type"] = "test"
        elif any(word in query_lower for word in ["assignment", "project"]):
            events["type"] = "assignment"
        elif any(word in query_lower for word in ["presentation", "viva"]):
            events["type"] = "presentation"
        elif any(word in query_lower for word in ["interview", "admission"]):
            events["type"] = "interview"
        
        school_subjects = ["cs", "computer science", "english", "history", "economics", "biology", "chemistry", "physics", "math"]
        for subject in school_subjects:
            if subject in query_lower:
                events["subject"] = subject
        
        return events
    
    def generate_balanced_schedule(self, student_analysis: Dict[str, Any]) -> str:
        exam_type = student_analysis["exam_type"]
        study_phase = student_analysis["study_phase"]
        time_available = student_analysis["time_available"]
        weak_subjects = student_analysis["weak_subjects"]
        immediate_events = student_analysis["immediate_events"]
        
        db_schedules = get_schedule_info(category=exam_type.lower())
        
        prompt = f"""
        You are an expert academic advisor helping a student balance their competitive exam preparation with immediate academic obligations.
        
        STUDENT PROFILE:
        - Main Goal: {exam_type} preparation
        - Current Study Phase: {study_phase}
        - Available Study Time: {time_available}
        - Weak Areas: {', '.join(weak_subjects) if weak_subjects else 'None specified'}
        - Immediate Events: {immediate_events}
        
        EXAM REQUIREMENTS: {self.exam_patterns.get(exam_type, {})}
        
        DATABASE SCHEDULES: {db_schedules[:2] if db_schedules else 'No specific schedules found'}
        
        CRITICAL SITUATION: The student has immediate academic obligations that need attention while maintaining their competitive exam preparation momentum.
        
        Provide a BALANCED STRATEGY that includes:
        
        1. **IMMEDIATE ACTION PLAN** (Next 24-48 hours):
           - Time allocation for urgent tasks vs {exam_type} prep
           - Quick revision strategies for the immediate event
           - How to minimize disruption to main preparation
        
        2. **SHORT-TERM ADJUSTMENT** (This week):
           - Modified daily schedule accommodating both priorities
           - Compensation strategies for reduced {exam_type} study time
           - Priority subjects to focus on
        
        3. **INTEGRATION STRATEGY**:
           - How to relate school subjects to {exam_type} topics (if applicable)
           - Efficient study techniques for dual preparation
           - Stress management during overlap periods
        
        4. **RECOVERY PLAN**:
           - How to get back on track after the immediate event
           - Catch-up strategies for {exam_type} preparation
           - Long-term schedule adjustments
        
        5. **PRACTICAL TIPS**:
           - Time management techniques
           - Study material optimization
           - Energy management strategies
        
        Make it highly actionable with specific time slots, study techniques, and contingency plans. Focus on maintaining {exam_type} preparation quality while handling immediate obligations effectively.
        """
        
        response = self.agent.run(prompt)
        return response.content
    
    def get_schedule_recommendations(self, query: str) -> str:
        student_analysis = self.analyze_student_query(query)
        balanced_schedule = self.generate_balanced_schedule(student_analysis)
        
        return balanced_schedule
    
    def get_subject_specific_help(self, exam_type: str, subject: str) -> str:
        db_schedules = get_schedule_info(subject=subject)
        
        prompt = f"""
        Provide comprehensive study guidance for {subject} in {exam_type} preparation, considering potential schedule disruptions:
        
        Available schedules: {db_schedules[:2] if db_schedules else 'No specific schedules found'}
        
        Include:
        1. **Flexible Topic Breakdown**: Adaptable to changing schedules
        2. **Time-Efficient Study Methods**: For busy periods
        3. **Quick Revision Techniques**: For last-minute situations
        4. **Resource Optimization**: Best materials for maximum impact
        5. **Common Pitfalls**: Mistakes to avoid during stressful periods
        6. **Integration Opportunities**: How this subject connects with school curriculum
        
        Focus on strategies that work even when the student's schedule is disrupted by other academic obligations.
        """
        
        response = self.agent.run(prompt)
        return response.content
    
    def get_crisis_management_schedule(self, exam_type: str, crisis_description: str) -> str:
        prompt = f"""
        CRISIS MANAGEMENT for {exam_type} preparation:
        
        SITUATION: {crisis_description}
        
        Provide an emergency study plan that addresses:
        
        1. **Immediate Damage Control**:
           - What to prioritize right now
           - What can be temporarily paused
           - Minimum daily {exam_type} study to maintain momentum
        
        2. **Resource Reallocation**:
           - High-impact, low-time study activities
           - Which topics to focus on vs skip temporarily
           - Efficient revision methods
        
        3. **Stress Management**:
           - How to stay calm and focused
           - Avoiding burnout during overwhelming periods
           - Maintaining motivation
        
        4. **Recovery Strategy**:
           - How to bounce back once the crisis passes
           - Accelerated catch-up techniques
           - Long-term schedule modifications
        
        Make it a practical survival guide for maintaining {exam_type} preparation during academic chaos.
        """
        
        response = self.agent.run(prompt)
        return response.content

    def get_exam_timeline_schedule(self, exam_type: str, months_left: int) -> str:
        prompt = f"""
        Create a FLEXIBLE {months_left}-month preparation timeline for {exam_type} that accounts for real-world disruptions:
        
        Exam pattern: {self.exam_patterns.get(exam_type, {})}
        
        Provide:
        1. **Month-wise Focus Areas**: With built-in flexibility buffers
        2. **Weekly Targets**: Achievable even with school obligations
        3. **Disruption Management**: How to handle unexpected events
        4. **Buffer Time**: Built-in recovery periods
        5. **Adaptation Strategies**: How to modify when behind schedule
        6. **Final Month Crisis Plan**: Last-minute optimization strategies
        
        Design this as a resilient plan that can withstand academic storms while keeping {exam_type} preparation on track.
        """
        
        response = self.agent.run(prompt)
        return response.content

scheduler = CompetitiveExamScheduler()

if __name__ == "__main__":
    student_query = "I am preparing for JEE but I have my CS exam class test in school tomorrow. Can you help me with a study schedule?"
    
    recommendation = scheduler.get_schedule_recommendations(student_query)
    print("=== Balanced Schedule Recommendation ===")
    print(recommendation)
    
    print("\n" + "="*50 + "\n")
    
    crisis_help = scheduler.get_crisis_management_schedule("JEE", "Multiple school tests this week while JEE prep is falling behind")
    print("=== Crisis Management Plan ===")
    print(crisis_help)