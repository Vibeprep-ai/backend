import os
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

def get_schedule_info(category: Optional[str] = None, day: Optional[str] = None, subject: Optional[str] = None, activity: Optional[str] = None, time_slot: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        client = MongoClient(os.getenv('MONGODB_URL'))
        db = client[os.getenv('DATABASE_NAME')]
        collection = db['jee_weekly_schedules']
        
        query = {}
        
        if category:
            query['category'] = {"$regex": category, "$options": "i"}
        if day:
            query['day'] = {"$regex": day, "$options": "i"}
        if subject:
            query['schedule.subject_focus'] = {"$regex": subject, "$options": "i"}
        if activity:
            query['schedule.activity'] = {"$regex": activity, "$options": "i"}
        if time_slot:
            query['schedule.time_slot'] = {"$regex": time_slot, "$options": "i"}
        
        if not query:
            schedules = list(collection.find())
        else:
            schedules = list(collection.find(query))
        
        for schedule in schedules:
            schedule['_id'] = str(schedule['_id'])
        
        client.close()
        return schedules
        
    except Exception as e:
        print(f"Error fetching schedule info: {e}")
        return []
    
if __name__ == "__main__":
    schedules = get_schedule_info(day="Monday")
    for schedule in schedules:
        print(schedule)