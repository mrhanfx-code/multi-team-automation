#!/usr/bin/env python3
"""
MFM Corporation - Meeting Scheduler with Calendar Integration
Comprehensive meeting scheduling system with calendar integration
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class MeetingType(Enum):
    TEAM_SYNC = "team_sync"
    PROJECT_REVIEW = "project_review"
    STRATEGY_PLANNING = "strategy_planning"
    INNOVATION_BRIEFING = "innovation_briefing"
    MARKETING_REVIEW = "marketing_review"
    PERFORMANCE_REVIEW = "performance_review"
    EXECUTIVE_MEETING = "executive_meeting"
    ONE_ON_ONE = "one_on_one"
    CLIENT_MEETING = "client_meeting"
    STANDUP = "standup"
    RETROSPECTIVE = "retrospective"

class MeetingStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "no_show"

class RecurrenceType(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

@dataclass
class Meeting:
    """Meeting data structure"""
    id: str
    title: str
    description: str
    meeting_type: MeetingType
    organizer: str
    participants: List[str]
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    location: Optional[str]
    meeting_link: Optional[str]
    agenda: List[str]
    status: MeetingStatus
    recurrence: RecurrenceType
    recurrence_end_date: Optional[datetime]
    calendar_ids: List[str]  # Calendar integration IDs
    meeting_notes: Optional[str]
    action_items: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    reminders: List[Dict[str, Any]]

@dataclass
class CalendarEvent:
    """Calendar event data structure"""
    id: str
    calendar_id: str
    meeting_id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    attendees: List[str]
    location: Optional[str]
    meeting_link: Optional[str]
    external_id: Optional[str]  # External calendar ID

@dataclass
class MeetingTemplate:
    """Meeting template for recurring meetings"""
    id: str
    name: str
    meeting_type: MeetingType
    default_duration: int
    default_participants: List[str]
    default_agenda: List[str]
    recurrence: RecurrenceType
    auto_schedule: bool
    buffer_minutes: int  # Buffer time before/after

class MeetingScheduler:
    """Comprehensive meeting scheduler with calendar integration"""
    
    def __init__(self, supabase_manager):
        self.supabase_manager = supabase_manager
        self.meetings = {}
        self.calendar_events = {}
        self.meeting_templates = {}
        self.calendar_integrations = {}
        self.scheduling_rules = {}
        self.availability_cache = {}
        
    async def initialize(self) -> bool:
        """Initialize the meeting scheduler"""
        logger.info("📅 Initializing MFM Corporation Meeting Scheduler")
        
        try:
            # Load meeting templates
            await self._load_meeting_templates()
            
            # Load calendar integrations
            await self._load_calendar_integrations()
            
            # Set up default templates
            await self._setup_default_templates()
            
            # Set up scheduling rules
            await self._setup_scheduling_rules()
            
            logger.info("✅ Meeting Scheduler initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Meeting Scheduler initialization failed: {e}")
            return False
    
    async def schedule_meeting(self, title: str, description: str,
                             meeting_type: MeetingType,
                             organizer: str,
                             participants: List[str],
                             duration_minutes: int,
                             preferred_time_range: Optional[tuple] = None,
                             location: Optional[str] = None,
                             agenda: Optional[List[str]] = None,
                             recurrence: RecurrenceType = RecurrenceType.NONE,
                             recurrence_end_date: Optional[datetime] = None,
                             auto_find_time: bool = True) -> str:
        """Schedule a new meeting"""
        try:
            meeting_id = f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.meetings)}"
            
            # Find optimal time if auto_find_time is enabled
            if auto_find_time:
                start_time, end_time = await self._find_optimal_meeting_time(
                    participants, duration_minutes, preferred_time_range
                )
            else:
                # Use preferred time range or default
                if preferred_time_range:
                    start_time = preferred_time_range[0]
                    end_time = start_time + timedelta(minutes=duration_minutes)
                else:
                    start_time = datetime.now() + timedelta(hours=1)
                    end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Create meeting
            meeting = Meeting(
                id=meeting_id,
                title=title,
                description=description,
                meeting_type=meeting_type,
                organizer=organizer,
                participants=participants,
                start_time=start_time,
                end_time=end_time,
                duration_minutes=duration_minutes,
                location=location,
                meeting_link=None,  # Will be generated
                agenda=agenda or [],
                status=MeetingStatus.SCHEDULED,
                recurrence=recurrence,
                recurrence_end_date=recurrence_end_date,
                calendar_ids=[],
                meeting_notes=None,
                action_items=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                reminders=[]
            )
            
            # Generate meeting link
            meeting.meeting_link = await self._generate_meeting_link(meeting)
            
            # Add to meetings
            self.meetings[meeting_id] = meeting
            
            # Create calendar events
            await self._create_calendar_events(meeting)
            
            # Set up reminders
            await self._setup_meeting_reminders(meeting)
            
            # Save to Supabase
            await self.supabase_manager.save_meeting(asdict(meeting))
            
            # Send notifications
            await self._send_meeting_notifications(meeting, "scheduled")
            
            logger.info(f"✅ Meeting scheduled: {title}")
            return meeting_id
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule meeting: {e}")
            return ""
    
    async def reschedule_meeting(self, meeting_id: str, new_start_time: datetime,
                                 new_duration_minutes: Optional[int] = None,
                                 reason: Optional[str] = None) -> bool:
        """Reschedule an existing meeting"""
        try:
            if meeting_id not in self.meetings:
                logger.error(f"Meeting {meeting_id} not found")
                return False
            
            meeting = self.meetings[meeting_id]
            
            # Update meeting details
            old_start_time = meeting.start_time
            meeting.start_time = new_start_time
            meeting.end_time = new_start_time + timedelta(
                minutes=new_duration_minutes or meeting.duration_minutes
            )
            if new_duration_minutes:
                meeting.duration_minutes = new_duration_minutes
            
            meeting.status = MeetingStatus.RESCHEDULED
            meeting.updated_at = datetime.now()
            
            # Update calendar events
            await self._update_calendar_events(meeting)
            
            # Update reminders
            await self._update_meeting_reminders(meeting)
            
            # Save to Supabase
            await self.supabase_manager.update_meeting(asdict(meeting))
            
            # Send notifications
            await self._send_meeting_notifications(meeting, "rescheduled", {
                "old_time": old_start_time,
                "new_time": new_start_time,
                "reason": reason
            })
            
            logger.info(f"✅ Meeting rescheduled: {meeting.title}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to reschedule meeting: {e}")
            return False
    
    async def cancel_meeting(self, meeting_id: str, reason: Optional[str] = None) -> bool:
        """Cancel a meeting"""
        try:
            if meeting_id not in self.meetings:
                logger.error(f"Meeting {meeting_id} not found")
                return False
            
            meeting = self.meetings[meeting_id]
            meeting.status = MeetingStatus.CANCELLED
            meeting.updated_at = datetime.now()
            
            # Remove from calendars
            await self._remove_calendar_events(meeting)
            
            # Save to Supabase
            await self.supabase_manager.update_meeting(asdict(meeting))
            
            # Send notifications
            await self._send_meeting_notifications(meeting, "cancelled", {"reason": reason})
            
            logger.info(f"✅ Meeting cancelled: {meeting.title}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel meeting: {e}")
            return False
    
    async def complete_meeting(self, meeting_id: str, meeting_notes: Optional[str] = None,
                             action_items: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Mark a meeting as completed"""
        try:
            if meeting_id not in self.meetings:
                logger.error(f"Meeting {meeting_id} not found")
                return False
            
            meeting = self.meetings[meeting_id]
            meeting.status = MeetingStatus.COMPLETED
            meeting.updated_at = datetime.now()
            
            if meeting_notes:
                meeting.meeting_notes = meeting_notes
            
            if action_items:
                meeting.action_items = action_items
            
            # Save to Supabase
            await self.supabase_manager.update_meeting(asdict(meeting))
            
            # Send follow-up notifications
            await self._send_meeting_notifications(meeting, "completed")
            
            logger.info(f"✅ Meeting completed: {meeting.title}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to complete meeting: {e}")
            return False
    
    async def get_meetings(self, participant: Optional[str] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          status: Optional[MeetingStatus] = None,
                          meeting_type: Optional[MeetingType] = None) -> List[Dict[str, Any]]:
        """Get meetings with optional filters"""
        meetings = list(self.meetings.values())
        
        # Apply filters
        if participant:
            meetings = [m for m in meetings if participant in m.participants or m.organizer == participant]
        
        if start_date:
            meetings = [m for m in meetings if m.start_time >= start_date]
        
        if end_date:
            meetings = [m for m in meetings if m.start_time <= end_date]
        
        if status:
            meetings = [m for m in meetings if m.status == status]
        
        if meeting_type:
            meetings = [m for m in meetings if m.meeting_type == meeting_type]
        
        # Sort by start time
        meetings.sort(key=lambda x: x.start_time)
        
        return [asdict(m) for m in meetings]
    
    async def get_upcoming_meetings(self, participant: str, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming meetings for a participant"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_ahead)
        
        return await self.get_meetings(
            participant=participant,
            start_date=start_date,
            end_date=end_date,
            status=MeetingStatus.SCHEDULED
        )
    
    async def check_availability(self, participants: List[str], 
                                start_time: datetime, 
                                end_time: datetime) -> Dict[str, bool]:
        """Check availability for participants"""
        availability = {}
        
        for participant in participants:
            # Check against existing meetings
            is_available = True
            
            for meeting in self.meetings.values():
                if (meeting.status == MeetingStatus.SCHEDULED and
                    participant in meeting.participants and
                    self._times_overlap(start_time, end_time, meeting.start_time, meeting.end_time)):
                    is_available = False
                    break
            
            availability[participant] = is_available
        
        return availability
    
    async def _find_optimal_meeting_time(self, participants: List[str],
                                        duration_minutes: int,
                                        preferred_range: Optional[tuple] = None) -> tuple:
        """Find optimal meeting time for all participants"""
        # Default to business hours if no preferred range
        if not preferred_range:
            preferred_range = (
                datetime.now().replace(hour=9, minute=0, second=0, microsecond=0),
                datetime.now().replace(hour=17, minute=0, second=0, microsecond=0) + timedelta(days=7)
            )
        
        start_search = preferred_range[0]
        end_search = preferred_range[1]
        
        # Search in 30-minute increments
        current_time = start_search
        search_step = timedelta(minutes=30)
        
        while current_time + timedelta(minutes=duration_minutes) <= end_search:
            proposed_end = current_time + timedelta(minutes=duration_minutes)
            
            # Check availability
            availability = await self.check_availability(participants, current_time, proposed_end)
            
            if all(availability.values()):
                # Found suitable time
                return current_time, proposed_end
            
            current_time += search_step
        
        # If no suitable time found, return next available slot
        return start_search, start_search + timedelta(minutes=duration_minutes)
    
    def _times_overlap(self, start1: datetime, end1: datetime, 
                       start2: datetime, end2: datetime) -> bool:
        """Check if two time ranges overlap"""
        return start1 < end2 and start2 < end1
    
    async def _create_calendar_events(self, meeting: Meeting):
        """Create calendar events for a meeting"""
        try:
            # Create events for each calendar integration
            for calendar_id in self.calendar_integrations:
                event_id = f"event_{calendar_id}_{meeting.id}"
                
                event = CalendarEvent(
                    id=event_id,
                    calendar_id=calendar_id,
                    meeting_id=meeting.id,
                    title=meeting.title,
                    description=meeting.description,
                    start_time=meeting.start_time,
                    end_time=meeting.end_time,
                    attendees=meeting.participants,
                    location=meeting.location,
                    meeting_link=meeting.meeting_link,
                    external_id=None
                )
                
                self.calendar_events[event_id] = event
                meeting.calendar_ids.append(event_id)
                
                # Create event in external calendar (simulation)
                await self._create_external_calendar_event(event, calendar_id)
            
        except Exception as e:
            logger.error(f"Failed to create calendar events: {e}")
    
    async def _update_calendar_events(self, meeting: Meeting):
        """Update calendar events for a meeting"""
        try:
            for event_id in meeting.calendar_ids:
                if event_id in self.calendar_events:
                    event = self.calendar_events[event_id]
                    event.start_time = meeting.start_time
                    event.end_time = meeting.end_time
                    event.title = meeting.title
                    event.description = meeting.description
                    event.attendees = meeting.participants
                    event.location = meeting.location
                    event.meeting_link = meeting.meeting_link
                    
                    # Update in external calendar (simulation)
                    await self._update_external_calendar_event(event)
        
        except Exception as e:
            logger.error(f"Failed to update calendar events: {e}")
    
    async def _remove_calendar_events(self, meeting: Meeting):
        """Remove calendar events for a meeting"""
        try:
            for event_id in meeting.calendar_ids:
                if event_id in self.calendar_events:
                    event = self.calendar_events[event_id]
                    
                    # Remove from external calendar (simulation)
                    await self._delete_external_calendar_event(event)
                    
                    del self.calendar_events[event_id]
            
            meeting.calendar_ids = []
        
        except Exception as e:
            logger.error(f"Failed to remove calendar events: {e}")
    
    async def _generate_meeting_link(self, meeting: Meeting) -> str:
        """Generate meeting link (simulation)"""
        # In production, integrate with Zoom, Teams, Google Meet, etc.
        return f"https://meet.mfmcorporation.com/{meeting.id}"
    
    async def _setup_meeting_reminders(self, meeting: Meeting):
        """Set up meeting reminders"""
        try:
            # Default reminders: 1 day before, 1 hour before, 15 minutes before
            reminder_times = [
                meeting.start_time - timedelta(days=1),
                meeting.start_time - timedelta(hours=1),
                meeting.start_time - timedelta(minutes=15)
            ]
            
            meeting.reminders = [
                {
                    "time": reminder_time.isoformat(),
                    "sent": False,
                    "type": "email"
                }
                for reminder_time in reminder_times
                if reminder_time > datetime.now()
            ]
        
        except Exception as e:
            logger.error(f"Failed to setup meeting reminders: {e}")
    
    async def _update_meeting_reminders(self, meeting: Meeting):
        """Update meeting reminders after reschedule"""
        await self._setup_meeting_reminders(meeting)
    
    async def _create_external_calendar_event(self, event: CalendarEvent, calendar_id: str):
        """Create event in external calendar (simulation)"""
        logger.info(f"📅 Creating calendar event: {event.title}")
        # In production, integrate with Google Calendar, Outlook, etc.
    
    async def _update_external_calendar_event(self, event: CalendarEvent):
        """Update event in external calendar (simulation)"""
        logger.info(f"📅 Updating calendar event: {event.title}")
    
    async def _delete_external_calendar_event(self, event: CalendarEvent):
        """Delete event from external calendar (simulation)"""
        logger.info(f"📅 Deleting calendar event: {event.title}")
    
    async def _send_meeting_notifications(self, meeting: Meeting, action: str,
                                       additional_data: Optional[Dict[str, Any]] = None):
        """Send meeting notifications"""
        try:
            # This would integrate with the notifications system
            title = f"Meeting {action.title()}: {meeting.title}"
            
            if action == "scheduled":
                message = f"Meeting scheduled for {meeting.start_time.strftime('%Y-%m-%d %H:%M')}"
            elif action == "rescheduled":
                message = f"Meeting rescheduled to {meeting.start_time.strftime('%Y-%m-%d %H:%M')}"
            elif action == "cancelled":
                message = "Meeting has been cancelled"
            elif action == "completed":
                message = "Meeting has been completed"
            else:
                message = f"Meeting {action}"
            
            # Send notifications to all participants
            logger.info(f"📧 Sending meeting notifications: {title}")
            
        except Exception as e:
            logger.error(f"Failed to send meeting notifications: {e}")
    
    async def _load_meeting_templates(self):
        """Load meeting templates from Supabase"""
        try:
            # Simulate loading templates
            self.meeting_templates = {}
            logger.info("📋 Meeting templates loaded")
        except Exception as e:
            logger.error(f"Failed to load meeting templates: {e}")
    
    async def _load_calendar_integrations(self):
        """Load calendar integrations from Supabase"""
        try:
            # Simulate loading calendar integrations
            self.calendar_integrations = {
                "google_calendar": "primary",
                "outlook": "secondary"
            }
            logger.info("📅 Calendar integrations loaded")
        except Exception as e:
            logger.error(f"Failed to load calendar integrations: {e}")
    
    async def _setup_default_templates(self):
        """Set up default meeting templates"""
        default_templates = [
            MeetingTemplate(
                id="team_sync",
                name="Team Sync Meeting",
                meeting_type=MeetingType.TEAM_SYNC,
                default_duration=30,
                default_participants=["team_lead", "team_members"],
                default_agenda=["Updates", "Blockers", "Next steps"],
                recurrence=RecurrenceType.WEEKLY,
                auto_schedule=True,
                buffer_minutes=15
            ),
            MeetingTemplate(
                id="project_review",
                name="Project Review",
                meeting_type=MeetingType.PROJECT_REVIEW,
                default_duration=60,
                default_participants=["project_manager", "stakeholders"],
                default_agenda=["Progress review", "Issues", "Timeline", "Resources"],
                recurrence=RecurrenceType.BIWEEKLY,
                auto_schedule=False,
                buffer_minutes=30
            ),
            MeetingTemplate(
                id="innovation_briefing",
                name="Innovation Briefing",
                meeting_type=MeetingType.INNOVATION_BRIEFING,
                default_duration=45,
                default_participants=["innovation_team", "management"],
                default_agenda=["New innovations", "Market impact", "Implementation plan"],
                recurrence=RecurrenceType.WEEKLY,
                auto_schedule=True,
                buffer_minutes=15
            ),
            MeetingTemplate(
                id="executive_meeting",
                name="Executive Meeting",
                meeting_type=MeetingType.EXECUTIVE_MEETING,
                default_duration=90,
                default_participants=["executives", "department_heads"],
                default_agenda=["Strategic review", "Financials", "Operations", "Growth"],
                recurrence=RecurrenceType.MONTHLY,
                auto_schedule=False,
                buffer_minutes=60
            )
        ]
        
        for template in default_templates:
            self.meeting_templates[template.id] = template
        
        logger.info("📋 Default meeting templates created")
    
    async def _setup_scheduling_rules(self):
        """Set up scheduling rules"""
        self.scheduling_rules = {
            "business_hours": {
                "start": "09:00",
                "end": "17:00",
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
            },
            "buffer_time": 15,  # minutes between meetings
            "max_daily_meetings": 6,
            "preferred_meeting_times": ["09:00", "10:30", "14:00", "15:30"],
            "avoid_lunch": "12:00-13:00"
        }
        
        logger.info("📋 Scheduling rules configured")
    
    async def schedule_from_template(self, template_id: str, title: str,
                                     organizer: str, participants: List[str],
                                     custom_agenda: Optional[List[str]] = None,
                                     custom_duration: Optional[int] = None) -> str:
        """Schedule meeting from template"""
        try:
            if template_id not in self.meeting_templates:
                logger.error(f"Template {template_id} not found")
                return ""
            
            template = self.meeting_templates[template_id]
            
            return await self.schedule_meeting(
                title=title,
                description=f"Meeting from template: {template.name}",
                meeting_type=template.meeting_type,
                organizer=organizer,
                participants=participants,
                duration_minutes=custom_duration or template.default_duration,
                agenda=custom_agenda or template.default_agenda,
                recurrence=template.recurrence
            )
        
        except Exception as e:
            logger.error(f"Failed to schedule from template: {e}")
            return ""
    
    async def get_meeting_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get meeting statistics for a date range"""
        try:
            meetings = await self.get_meetings(start_date=start_date, end_date=end_date)
            
            stats = {
                "total_meetings": len(meetings),
                "completed_meetings": len([m for m in meetings if m["status"] == "completed"]),
                "cancelled_meetings": len([m for m in meetings if m["status"] == "cancelled"]),
                "by_type": {},
                "by_duration": {
                    "under_30": 0,
                    "30_to_60": 0,
                    "over_60": 0
                },
                "average_participants": 0,
                "total_duration_minutes": 0
            }
            
            total_participants = 0
            total_duration = 0
            
            for meeting in meetings:
                # Count by type
                meeting_type = meeting["meeting_type"]
                stats["by_type"][meeting_type] = stats["by_type"].get(meeting_type, 0) + 1
                
                # Count by duration
                duration = meeting["duration_minutes"]
                if duration < 30:
                    stats["by_duration"]["under_30"] += 1
                elif duration <= 60:
                    stats["by_duration"]["30_to_60"] += 1
                else:
                    stats["by_duration"]["over_60"] += 1
                
                # Calculate averages
                total_participants += len(meeting["participants"])
                total_duration += duration
            
            if meetings:
                stats["average_participants"] = total_participants / len(meetings)
                stats["total_duration_minutes"] = total_duration
            
            return stats
        
        except Exception as e:
            logger.error(f"Failed to get meeting statistics: {e}")
            return {}
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "total_meetings": len(self.meetings),
            "scheduled_meetings": len([m for m in self.meetings.values() if m.status == MeetingStatus.SCHEDULED]),
            "completed_meetings": len([m for m in self.meetings.values() if m.status == MeetingStatus.COMPLETED]),
            "calendar_integrations": len(self.calendar_integrations),
            "meeting_templates": len(self.meeting_templates),
            "upcoming_meetings_today": len([
                m for m in self.meetings.values() 
                if m.status == MeetingStatus.SCHEDULED and 
                m.start_time.date() == datetime.now().date()
            ])
        }
