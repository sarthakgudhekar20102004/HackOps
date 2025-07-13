# src/parser_agent.py

# src/parser_agent.py (ULTRA-OPTIMIZED VERSION)
import openai
import json
from typing import Dict, List, Any
import re
from datetime import datetime, timedelta
import pytz

# Configuration
SERVER_IP = "127.0.0.1"
client = openai.OpenAI(base_url=f"http://{SERVER_IP}:4000/v1", api_key="not-needed")
MODEL_PATH = "/app/jupyter/AI_Scheduler/AI-Scheduling-Assistant/meta-llama/Meta-Llama-3.1-8B-Instruct"

# Ultra-fast pattern matching for common cases
URGENCY_PATTERNS = [
    r'\b(asap|urgent|urgently|immediately|promptly|priority|prioritize|quick|quickly)\b',
    r'\b(critical|emergency|rush|fast|rapid)\b',
    r'\b(just received|right away|at once)\b'
]

DAY_PATTERNS = {
    'monday': r'\b(monday|mon)\b',
    'tuesday': r'\b(tuesday|tue|tues)\b', 
    'wednesday': r'\b(wednesday|wed)\b',
    'thursday': r'\b(thursday|thu|thurs)\b',
    'friday': r'\b(friday|fri)\b',
    'saturday': r'\b(saturday|sat)\b',
    'sunday': r'\b(sunday|sun)\b'
}

def fast_extract_day_and_urgency(email_text: str) -> tuple:
    """Ultra-fast regex-based extraction with fallback to LLM"""
    email_lower = email_text.lower()
    
    # Check urgency with regex first
    is_urgent = any(re.search(pattern, email_lower, re.IGNORECASE) for pattern in URGENCY_PATTERNS)
    
    # Check day with regex first
    day_of_week = None
    for day, pattern in DAY_PATTERNS.items():
        if re.search(pattern, email_lower, re.IGNORECASE):
            day_of_week = day.capitalize()
            break
    
    # If regex fails, use LLM as fallback (only when needed)
    if day_of_week is None or not is_urgent:
        try:
            prompt = f"""Extract day and urgency from email. Return JSON only.
Email: "{email_text}"
Format: {{"day_of_week": "Monday/Tuesday/etc or null", "is_urgent": true/false}}"""
            
            response = client.chat.completions.create(
                model=MODEL_PATH,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=100,  # Limit tokens for speed
                response_format={"type": "json_object"}
            )
            
            llm_result = json.loads(response.choices[0].message.content)
            day_of_week = day_of_week or llm_result.get("day_of_week")
            is_urgent = is_urgent or llm_result.get("is_urgent", False)
            
        except Exception as e:
            print(f"LLM fallback failed: {e}")
    
    return day_of_week, is_urgent

def parse_meeting_request(email_text: str, organizer_email: str, attendees: List[Any]) -> Dict:
    """Ultra-optimized parsing with multi-level fallbacks"""
    
    # 1. Fast duration extraction
    duration_patterns = [
        r'(\d+)\s*(min|minute|minutes)',
        r'(\d+)\s*min\b',
        r'for\s+(\d+)\s+minutes?',
        r'(\d+)\s*hr|hour|hours'
    ]
    
    duration_mins = 30  # default
    for pattern in duration_patterns:
        match = re.search(pattern, email_text, re.IGNORECASE)
        if match:
            duration_mins = int(match.group(1))
            if 'hr' in pattern or 'hour' in pattern:
                duration_mins *= 60
            break
    
    # 2. Fast participant extraction
    attendee_emails = [att.email for att in attendees]
    all_participants = [organizer_email] + attendee_emails
    
    # 3. Ultra-fast day and urgency extraction
    day_of_week, is_urgent = fast_extract_day_and_urgency(email_text)
    
    return {
        "participants": all_participants,
        "duration_mins": duration_mins,
        "time_constraints": email_text,
        "day_of_week": day_of_week,
        "is_urgent": is_urgent
    }








