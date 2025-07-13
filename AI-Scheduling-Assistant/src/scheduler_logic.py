# src/scheduler_logic.py
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pytz
from dateutil import parser
import bisect

def get_next_weekday(start_date: datetime, weekday_name: str) -> datetime:
    """Optimized weekday calculation"""
    if not weekday_name:
        return start_date
        
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    
    target_weekday = weekdays.get(weekday_name.lower())
    if target_weekday is None:
        return start_date
        
    days_ahead = target_weekday - start_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return start_date + timedelta(days=days_ahead)

def merge_busy_slots(busy_slots: List[Dict]) -> List[Dict]:
    """Optimized slot merging using sorted approach"""
    if not busy_slots:
        return []
    
    # Sort by start time
    busy_slots.sort(key=lambda x: x['start'])
    
    merged = [busy_slots[0]]
    for current in busy_slots[1:]:
        last_merged = merged[-1]
        if current['start'] <= last_merged['end']:
            # Overlapping slots - merge them
            last_merged['end'] = max(last_merged['end'], current['end'])
        else:
            # Non-overlapping - add as new slot
            merged.append(current)
    
    return merged

def score_slot_fast(slot: Dict, is_urgent: bool, preferences: Dict = None) -> int:
    """Ultra-fast scoring algorithm"""
    start_time = slot['start']
    score = 100
    
    if is_urgent:
        # For urgent meetings, heavily prioritize earliest slots
        time_diff_hours = (start_time - datetime.now(pytz.utc)).total_seconds() / 3600
        if time_diff_hours < 48:  # Next 2 days
            return 1000 - int(time_diff_hours * 20)
        else:
            return 50
    
    # Standard scoring
    hour = start_time.hour
    
    # Business hours preference
    if 9 <= hour <= 17:
        score += 20
    
    # Optimal meeting times
    if 10 <= hour <= 11 or 14 <= hour <= 16:
        score += 10
    
    # Avoid lunch time
    if 12 <= hour <= 13:
        score -= 10
    
    # Avoid very early or very late
    if hour < 9 or hour > 17:
        score -= 30
    
    return score

def find_best_slot(
    calendars: Dict[str, List[Dict]], 
    duration_minutes: int,
    time_constraints: str, 
    day_of_week: str, 
    is_urgent: bool = False
) -> Optional[Dict]:
    """Ultra-optimized slot finding with intelligent search"""
    
    print(f"🚀 TURBO SCHEDULER: Finding slot for {len(calendars)} participants")
    print(f"   Duration: {duration_minutes}min, Day: {day_of_week}, Urgent: {is_urgent}")
    
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)
    
    # Smart search window based on urgency and day
    if is_urgent:
        # For urgent meetings, search starting from now
        search_start = now.replace(minute=0, second=0, microsecond=0)
        search_end = search_start + timedelta(days=2)
    else:
        # For regular meetings, use specified day or start tomorrow
        if day_of_week:
            target_day = get_next_weekday(now, day_of_week)
        else:
            target_day = now + timedelta(days=1)  # Default to tomorrow
        
        search_start = target_day.replace(hour=9, minute=0, second=0, microsecond=0)
        search_end = target_day.replace(hour=18, minute=0, second=0, microsecond=0)
    
    print(f"   Search window: {search_start} to {search_end}")
    
    # Collect and merge all busy slots
    all_busy_slots = []
    for email, events in calendars.items():
        for event in events:
            try:
                start = parser.parse(event['StartTime'])
                end = parser.parse(event['EndTime'])
                
                # Only include events that overlap with search window
                if end > search_start and start < search_end:
                    all_busy_slots.append({'start': start, 'end': end})
            except (KeyError, TypeError, ValueError):
                continue
    
    # Merge overlapping busy slots
    merged_busy_slots = merge_busy_slots(all_busy_slots)
    
    # Find available slots with optimized algorithm
    available_slots = []
    slot_start = search_start
    
    for busy_slot in merged_busy_slots:
        # Check gap before this busy slot
        gap_end = busy_slot['start']
        
        # Generate slots in this gap
        while slot_start + timedelta(minutes=duration_minutes) <= gap_end:
            slot_end = slot_start + timedelta(minutes=duration_minutes)
            available_slots.append({'start': slot_start, 'end': slot_end})
            slot_start += timedelta(minutes=15)  # 15-minute increments
        
        # Move past this busy slot
        slot_start = max(slot_start, busy_slot['end'])
    
    # Check for slots after the last busy period
    while slot_start + timedelta(minutes=duration_minutes) <= search_end:
        slot_end = slot_start + timedelta(minutes=duration_minutes)
        available_slots.append({'start': slot_start, 'end': slot_end})
        slot_start += timedelta(minutes=15)
    
    if not available_slots:
        print("   ❌ No available slots found")
        return None
    
    print(f"   ✅ Found {len(available_slots)} potential slots")
    
    # Score and select best slot
    best_slot = None
    best_score = -1
    
    for slot in available_slots:
        score = score_slot_fast(slot, is_urgent)
        if score > best_score:
            best_score = score
            best_slot = slot
    
    if best_slot:
        print(f"   🎯 Selected slot: {best_slot['start'].strftime('%A %I:%M %p')} (Score: {best_score})")
    
    return best_slot







