# src/calendar_client.py
# src/calendar_client.py (CACHED VERSION)
import os
from typing import List, Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import time

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Updated token mapping for your users
TOKEN_MAPPING = {
    "sarthakgudhekar@gmail.com": "token_user1.json",
    "demonotion2@gmail.com": "token_user2.json",
    "kalilinux140235@gmail.com": "token_user3.json"
}

# Simple in-memory cache for calendar data
_calendar_cache = {}
_cache_timeout = 300  # 5 minutes

def get_calendar_events(user_email: str, time_min: str, time_max: str) -> List[Dict]:
    """Optimized calendar fetching with caching"""
    
    # Check cache first
    cache_key = f"{user_email}:{time_min}:{time_max}"
    current_time = time.time()
    
    if cache_key in _calendar_cache:
        cached_data, timestamp = _calendar_cache[cache_key]
        if current_time - timestamp < _cache_timeout:
            print(f"📋 CACHE HIT: {user_email} ({len(cached_data)} events)")
            return cached_data
    
    # Get token file
    token_file = TOKEN_MAPPING.get(user_email)
    if not token_file or not os.path.exists(token_file):
        print(f"⚠️  WARNING: No token for {user_email}, returning empty calendar")
        return []
    
    try:
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        service = build('calendar', 'v3', credentials=creds)
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime',
            maxResults=100  # Limit for performance
        ).execute()
        
        events = events_result.get('items', [])
        
        # Cache the result
        _calendar_cache[cache_key] = (events, current_time)
        
        print(f"📅 FETCHED: {user_email} ({len(events)} events)")
        return events
        
    except Exception as e:
        print(f"❌ Calendar fetch error for {user_email}: {e}")
        return []






