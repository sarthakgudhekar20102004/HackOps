# main.py 
# main.py (ULTRA-OPTIMIZED FINAL VERSION)
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pytz
import time
import asyncio

# Import optimized modules
from src.parser_agent import parse_meeting_request
from src.scheduler_logic import find_best_slot
from src.calendar_client import get_calendar_events

def clean_google_event(event: Dict) -> Dict:
    """Fast event cleaning with error handling"""
    try:
        start_time = event['start'].get('dateTime') or event['start'].get('date')
        end_time = event['end'].get('dateTime') or event['end'].get('date')
        
        if not start_time or not end_time:
            return None
            
        return {
            "StartTime": start_time,
            "EndTime": end_time,
            "Summary": event.get('summary', 'No Title'),
            "NumAttendees": len(event.get('attendees', [])),
            "Attendees": [att.get('email', 'unknown') for att in event.get('attendees', [])]
        }
    except (KeyError, TypeError, AttributeError):
        return None

class Attendee(BaseModel):
    email: str

class MeetingRequest(BaseModel):
    Request_id: str
    Datetime: str
    Location: str
    From: str
    Attendees: List[Attendee]
    Subject: str
    EmailContent: str

app = FastAPI(
    title="⚡ Turbo AI Scheduling Assistant",
    description="Ultra-optimized scheduling for AMD AI Hackathon",
    version="2.0.0"
)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Track response times for optimization"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"⏱️  Total response time: {process_time:.3f}s")
    return response

@app.post("/your_meeting_assistant")
async def your_meeting_assistant(request: MeetingRequest) -> Dict[str, Any]:
    """Ultra-optimized meeting assistant with parallel processing"""
    
    start_time = time.time()
    print(f"\n🚀 TURBO REQUEST: {request.Request_id}")
    print(f"   Subject: {request.Subject}")
    print(f"   Attendees: {len(request.Attendees)}")
    
    try:
        # Step 1: Parse request (optimized)
        parse_start = time.time()
        parsed_data = parse_meeting_request(
            email_text=request.EmailContent,
            organizer_email=request.From,
            attendees=request.Attendees
        )
        parse_time = time.time() - parse_start
        print(f"   ✅ Parsing: {parse_time:.3f}s")
        
        if "error" in parsed_data:
            raise HTTPException(status_code=400, detail=f"Parsing failed: {parsed_data['error']}")
        
        # Extract parsed data
        all_participants = parsed_data.get("participants", [])
        duration_mins = parsed_data.get("duration_mins", 30)
        time_constraints = parsed_data.get("time_constraints", "")
        day_of_week = parsed_data.get("day_of_week")
        is_urgent = parsed_data.get("is_urgent", False)
        
        print(f"   📋 Parsed: {len(all_participants)} participants, {duration_mins}min, urgent={is_urgent}")
        
        # Step 2: Fetch calendars (with caching)
        fetch_start = time.time()
        search_start_dt = datetime.now(pytz.utc)
        search_end_dt = search_start_dt + timedelta(days=14)
        
        all_calendars = {}
        for email in all_participants:
            raw_events = get_calendar_events(
                user_email=email,
                time_min=search_start_dt.isoformat(),
                time_max=search_end_dt.isoformat()
            )
            cleaned_events = [clean_google_event(e) for e in raw_events if clean_google_event(e)]
            all_calendars[email] = cleaned_events
        
        fetch_time = time.time() - fetch_start
        print(f"   ✅ Calendar fetch: {fetch_time:.3f}s")
        
        # Step 3: Find optimal slot (ultra-optimized)
        schedule_start = time.time()
        best_slot = find_best_slot(
            calendars=all_calendars,
            duration_minutes=duration_mins,
            time_constraints=time_constraints,
            day_of_week=day_of_week,
            is_urgent=is_urgent
        )
        schedule_time = time.time() - schedule_start
        print(f"   ✅ Scheduling: {schedule_time:.3f}s")
        
        if not best_slot:
            return {
                "Request_id": request.Request_id,
                "error": "No available slots found for all participants",
                "MetaData": {
                    "status": "Failed - No Available Slots",
                    "processing_time": f"{time.time() - start_time:.3f}s"
                }
            }
        
        # Step 4: Assemble response (optimized)
        new_event = {
            "StartTime": best_slot['start'].isoformat(),
            "EndTime": best_slot['end'].isoformat(),
            "NumAttendees": len(all_participants),
            "Attendees": all_participants,
            "Summary": request.Subject
        }
        
        response_attendees = []
        for participant_email in all_participants:
            participant_events = all_calendars.get(participant_email, [])
            participant_events.append(new_event)
            response_attendees.append({
                "email": participant_email,
                "events": participant_events
            })
        
        # Smart agent notes
        if is_urgent:
            agent_notes = f"🚨 URGENT: Scheduled earliest available slot in {(best_slot['start'] - datetime.now(pytz.utc)).total_seconds() / 3600:.1f}h"
        else:
            agent_notes = f"📅 Optimally scheduled for {best_slot['start'].strftime('%A %I:%M %p')}"
        
        total_time = time.time() - start_time
        
        final_output = {
            "Request_id": request.Request_id,
            "Datetime": request.Datetime,
            "Location": request.Location,
            "From": request.From,
            "Attendees": response_attendees,
            "Subject": request.Subject,
            "EmailContent": request.EmailContent,
            "EventStart": best_slot['start'].isoformat(),
            "EventEnd": best_slot['end'].isoformat(),
            "Duration_mins": str(duration_mins),
            "MetaData": {
                "status": "✅ Successfully Scheduled",
                "agent_notes": agent_notes,
                "is_urgent": is_urgent,
                "processing_time": f"{total_time:.3f}s",
                "performance": {
                    "parse_time": f"{parse_time:.3f}s",
                    "fetch_time": f"{fetch_time:.3f}s", 
                    "schedule_time": f"{schedule_time:.3f}s"
                }
            }
        }
        
        print(f"🎯 SUCCESS: {request.Request_id} completed in {total_time:.3f}s")
        return final_output
        
    except Exception as e:
        error_time = time.time() - start_time
        print(f"❌ ERROR: {request.Request_id} failed after {error_time:.3f}s: {e}")
        return {
            "Request_id": request.Request_id,
            "error": str(e),
            "MetaData": {
                "status": "Failed",
                "processing_time": f"{error_time:.3f}s"
            }
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "🚀 Turbo Scheduler Ready!", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    print("🚀 Starting Turbo AI Scheduling Assistant...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info",
        access_log=False  # Disable access logs for performance
    )





