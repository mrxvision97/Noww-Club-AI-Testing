import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from core.user_profile import UserProfileManager
from utils.notifications import NotificationManager
from ui.analytics import AnalyticsDashboard

class SidebarInterface:
    def __init__(self, profile_manager: UserProfileManager, notification_manager: NotificationManager, user_id: str):
        self.profile_manager = profile_manager
        self.notification_manager = notification_manager
        self.user_id = user_id
        self.analytics = AnalyticsDashboard(profile_manager, user_id)
    
    def render(self):
        """Render the sidebar interface."""
        
        with st.sidebar:
            st.markdown("<h3>🧠 Noww Club AI</h3>", unsafe_allow_html=True)
            
            # User Profile Section
            self._render_profile_section()
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Active Habits
            self._render_active_habits()
            
            # Active Goals
            self._render_active_goals()
            
            st.markdown("<hr>", unsafe_allow_html=True)

            # Mood Tracking
            self._render_mood_section()

            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Settings
            self._render_settings_section()

    def _render_profile_section(self):
        """Renders the 'Your Profile' section of the sidebar."""
        st.markdown("<h5>Your Profile</h5>", unsafe_allow_html=True)
        
        profile = self.profile_manager.get_user_profile(self.user_id)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Conversations", value=len(st.session_state.get("chat_history", [])))
        with col2:
            # Placeholder for relationship status
            st.metric(label="Relationship", value="New")
            
    def _render_active_habits(self):
        """Renders the 'Active Habits' section."""
        st.markdown("<h5>🌿 Active Habits</h5>", unsafe_allow_html=True)
        habits = self.profile_manager.get_user_profile(self.user_id).get("habits", [])
        if not habits:
            st.info("No active habits yet. Start a flow to create one!")
        else:
            for habit in habits[:3]: # Show top 3
                st.info(f"{habit['title']}")

    def _render_active_goals(self):
        """Renders the 'Active Goals' section."""
        st.markdown("<h5>🎯 Active Goals</h5>", unsafe_allow_html=True)
        goals = self.profile_manager.get_user_profile(self.user_id).get("goals", [])
        if not goals:
            st.info("No active goals yet. Start a flow to set one!")
        else:
            for goal in goals[:3]: # Show top 3
                st.info(f"📌 {goal['title']}")

    def _render_mood_section(self):
        """Renders the 'Recent Moods' section."""
        st.markdown("<h5>😊 Recent Moods</h5>", unsafe_allow_html=True)
        moods = self.profile_manager.db_manager.get_mood_entries(self.user_id, limit=3)
        if not moods:
            st.info("No mood entries yet!")
        else:
            for mood in moods:
                emoji = self._get_mood_emoji(mood['mood_score'])
                st.info(f"{emoji} {mood['mood_score']}/5 on {datetime.fromisoformat(mood['timestamp']).strftime('%b %d')}")

    def _render_settings_section(self):
        """Renders the 'Notification Settings' and other actions."""
        with st.expander("⚙️ Notification Settings"):
            preferences = self.profile_manager.get_notification_preferences(self.user_id)
            
            reminders = st.checkbox("Reminders", preferences.get("reminders_enabled", True))
            mood_checkins = st.checkbox("Mood Check-ins", preferences.get("mood_check_ins", True))
            
            if st.button("Save Settings"):
                new_prefs = {
                    "reminders_enabled": reminders,
                    "mood_check_ins": mood_checkins,
                }
                self.profile_manager.update_notification_preferences(self.user_id, new_prefs)
                st.success("Settings saved!")

    def _get_mood_emoji(self, mood_score: float) -> str:
        """Get emoji for mood score"""
        if mood_score >= 4.5:
            return "😄"
        elif mood_score >= 3.5:
            return "😊"
        elif mood_score >= 2.5:
            return "😐"
        elif mood_score >= 1.5:
            return "😔"
        else:
            return "😢"
    
    def render_analytics_modal(self):
        """Render analytics modal if requested"""
        if st.session_state.get("show_analytics", False):
            st.session_state.show_analytics = False
            
            # Create a new page/modal for analytics
            st.subheader("📈 Analytics Dashboard")
            
            try:
                self.analytics.render_full_dashboard()
            except Exception as e:
                st.error(f"Error loading analytics: {str(e)}")
            
            if st.button("Close Analytics"):
                st.rerun()
