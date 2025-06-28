import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
from core.user_profile import UserProfileManager

class AnalyticsDashboard:
    def __init__(self, profile_manager: UserProfileManager, user_id: str):
        self.profile_manager = profile_manager
        self.user_id = user_id
    
    def render_full_dashboard(self):
        """Render the complete analytics dashboard"""
        try:
            profile = self.profile_manager.get_user_profile(self.user_id)
            
            # Overview metrics
            self._render_overview_metrics(profile)
            
            # Mood analytics
            self._render_mood_analytics(profile)
            
            # Goals and habits analytics
            self._render_goals_habits_analytics(profile)
            
            # Activity patterns
            self._render_activity_patterns(profile)
        
        except Exception as e:
            st.error(f"Error rendering analytics dashboard: {str(e)}")
    
    def render_mood_chart_sidebar(self):
        """Render a simplified mood chart for the sidebar"""
        try:
            mood_history = self.profile_manager.db_manager.get_mood_history(self.user_id, days=7)
            
            if mood_history:
                # Create simple line chart
                df = pd.DataFrame(mood_history)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['mood_score'],
                    mode='lines+markers',
                    line=dict(color='#007acc', width=2),
                    marker=dict(size=4),
                    name='Mood'
                ))
                
                fig.update_layout(
                    height=150,
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=False,
                    xaxis=dict(showticklabels=False),
                    yaxis=dict(range=[1, 5], tickmode='linear', tick0=1, dtick=1)
                )
                
                st.sidebar.plotly_chart(fig, use_container_width=True)
            else:
                st.sidebar.info("No mood data yet. Log your mood to see trends!")
        
        except Exception as e:
            st.sidebar.error(f"Error loading mood chart: {str(e)}")
    
    def _render_overview_metrics(self, profile: Dict[str, Any]):
        """Render overview metrics"""
        st.subheader("📊 Overview")
        
        stats = profile.get("statistics", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Goals",
                stats.get("total_goals", 0),
                delta=None
            )
        
        with col2:
            st.metric(
                "Active Habits",
                stats.get("active_habits", 0),
                delta=None
            )
        
        with col3:
            avg_mood = stats.get("average_mood", 0)
            st.metric(
                "Average Mood",
                f"{avg_mood:.1f}",
                delta=None
            )
        
        with col4:
            st.metric(
                "Mood Entries",
                stats.get("mood_entries_count", 0),
                delta=None
            )
    
    def _render_mood_analytics(self, profile: Dict[str, Any]):
        """Render mood analytics section"""
        st.subheader("😊 Mood Analytics")
        
        mood_history = profile.get("mood_history", [])
        
        if not mood_history:
            st.info("No mood data available. Start logging your mood to see analytics!")
            return
        
        # Create DataFrame
        df = pd.DataFrame(mood_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Mood trend over time
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['mood_score'],
                mode='lines+markers',
                line=dict(color='#007acc', width=3),
                marker=dict(size=6),
                name='Mood Score'
            ))
            
            # Add trend line
            if len(df) > 1:
                z = np.polyfit(range(len(df)), df['mood_score'], 1)
                p = np.poly1d(z)
                fig_trend.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=p(range(len(df))),
                    mode='lines',
                    line=dict(color='red', width=2, dash='dash'),
                    name='Trend'
                ))
            
            fig_trend.update_layout(
                title="Mood Trend Over Time",
                xaxis_title="Date",
                yaxis_title="Mood Score (1-5)",
                yaxis=dict(range=[1, 5]),
                height=400
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # Mood distribution
            mood_counts = df['mood_score'].value_counts().sort_index()
            
            fig_dist = go.Figure(data=[go.Bar(
                x=['Very Bad', 'Bad', 'Neutral', 'Good', 'Excellent'],
                y=[mood_counts.get(i, 0) for i in range(1, 6)],
                marker_color=['#ff4444', '#ff8844', '#ffbb44', '#88dd44', '#44dd44']
            )])
            
            fig_dist.update_layout(
                title="Mood Distribution",
                xaxis_title="Mood Level",
                yaxis_title="Count",
                height=400
            )
            
            st.plotly_chart(fig_dist, use_container_width=True)
        
        # Weekly mood patterns
        if len(df) >= 7:
            df['day_of_week'] = df['timestamp'].dt.day_name()
            df['hour'] = df['timestamp'].dt.hour
            
            col3, col4 = st.columns(2)
            
            with col3:
                # Day of week patterns
                day_avg = df.groupby('day_of_week')['mood_score'].mean()
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_avg = day_avg.reindex([day for day in day_order if day in day_avg.index])
                
                fig_day = go.Figure(data=[go.Bar(
                    x=day_avg.index,
                    y=day_avg.values,
                    marker_color='#007acc'
                )])
                
                fig_day.update_layout(
                    title="Average Mood by Day of Week",
                    xaxis_title="Day",
                    yaxis_title="Average Mood Score",
                    yaxis=dict(range=[1, 5]),
                    height=300
                )
                
                st.plotly_chart(fig_day, use_container_width=True)
            
            with col4:
                # Hour of day patterns (if enough data)
                if len(df) >= 14:
                    hour_avg = df.groupby('hour')['mood_score'].mean()
                    
                    fig_hour = go.Figure(data=[go.Scatter(
                        x=hour_avg.index,
                        y=hour_avg.values,
                        mode='lines+markers',
                        line=dict(color='#007acc', width=2),
                        marker=dict(size=4)
                    )])
                    
                    fig_hour.update_layout(
                        title="Average Mood by Hour",
                        xaxis_title="Hour of Day",
                        yaxis_title="Average Mood Score",
                        yaxis=dict(range=[1, 5]),
                        height=300
                    )
                    
                    st.plotly_chart(fig_hour, use_container_width=True)
    
    def _render_goals_habits_analytics(self, profile: Dict[str, Any]):
        """Render goals and habits analytics"""
        st.subheader("🎯 Goals & Habits")
        
        goals = profile.get("goals", [])
        habits = profile.get("habits", [])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Goals Overview**")
            
            if goals:
                # Goals by status
                goal_status = {}
                for goal in goals:
                    status = goal.get('status', 'active')
                    goal_status[status] = goal_status.get(status, 0) + 1
                
                fig_goals = go.Figure(data=[go.Pie(
                    labels=list(goal_status.keys()),
                    values=list(goal_status.values()),
                    hole=0.3
                )])
                
                fig_goals.update_layout(
                    title="Goals by Status",
                    height=300
                )
                
                st.plotly_chart(fig_goals, use_container_width=True)
                
                # Goals timeline
                goals_with_dates = [g for g in goals if g.get('target_date')]
                if goals_with_dates:
                    st.write("**Upcoming Goals**")
                    for goal in sorted(goals_with_dates, key=lambda x: x['target_date'])[:3]:
                        st.write(f"• {goal['title']} - Target: {goal['target_date']}")
            else:
                st.info("No goals set yet!")
        
        with col2:
            st.write("**Habits Overview**")
            
            if habits:
                # Habits by frequency
                habit_freq = {}
                for habit in habits:
                    freq = habit.get('frequency', 'daily')
                    habit_freq[freq] = habit_freq.get(freq, 0) + 1
                
                fig_habits = go.Figure(data=[go.Bar(
                    x=list(habit_freq.keys()),
                    y=list(habit_freq.values()),
                    marker_color='#4CAF50'
                )])
                
                fig_habits.update_layout(
                    title="Habits by Frequency",
                    height=300
                )
                
                st.plotly_chart(fig_habits, use_container_width=True)
                
                # Active habits list
                active_habits = [h for h in habits if h.get('status') == 'active']
                if active_habits:
                    st.write("**Active Habits**")
                    for habit in active_habits[:5]:
                        st.write(f"• {habit['title']} ({habit.get('frequency', 'daily')})")
            else:
                st.info("No habits created yet!")
    
    def _render_activity_patterns(self, profile: Dict[str, Any]):
        """Render activity patterns"""
        st.subheader("📈 Activity Patterns")
        
        try:
            # Get conversation history for activity analysis
            conversation_history = self.profile_manager.db_manager.get_conversation_history(
                self.user_id, limit=100
            )
            
            if conversation_history:
                # Create activity heatmap
                df_conv = pd.DataFrame(conversation_history)
                df_conv['timestamp'] = pd.to_datetime(df_conv['timestamp'])
                df_conv['date'] = df_conv['timestamp'].dt.date
                df_conv['hour'] = df_conv['timestamp'].dt.hour
                
                # Activity by day
                daily_activity = df_conv.groupby('date').size().reset_index(name='messages')
                daily_activity['date'] = pd.to_datetime(daily_activity['date'])
                
                fig_activity = go.Figure()
                fig_activity.add_trace(go.Scatter(
                    x=daily_activity['date'],
                    y=daily_activity['messages'],
                    mode='lines+markers',
                    line=dict(color='#FF6B6B', width=2),
                    marker=dict(size=6),
                    name='Messages per Day'
                ))
                
                fig_activity.update_layout(
                    title="Daily Activity Pattern",
                    xaxis_title="Date",
                    yaxis_title="Number of Messages",
                    height=300
                )
                
                st.plotly_chart(fig_activity, use_container_width=True)
                
                # Most active hours
                if len(df_conv) >= 10:
                    hourly_activity = df_conv.groupby('hour').size()
                    
                    col3, col4 = st.columns(2)
                    
                    with col3:
                        fig_hours = go.Figure(data=[go.Bar(
                            x=hourly_activity.index,
                            y=hourly_activity.values,
                            marker_color='#9C27B0'
                        )])
                        
                        fig_hours.update_layout(
                            title="Activity by Hour",
                            xaxis_title="Hour of Day",
                            yaxis_title="Messages",
                            height=300
                        )
                        
                        st.plotly_chart(fig_hours, use_container_width=True)
                    
                    with col4:
                        # Top conversation topics (based on intent if available)
                        st.write("**Recent Activity Summary**")
                        total_messages = len(conversation_history)
                        user_messages = len([m for m in conversation_history if m['message_type'] == 'human'])
                        ai_messages = len([m for m in conversation_history if m['message_type'] == 'ai'])
                        
                        st.metric("Total Messages", total_messages)
                        st.metric("Your Messages", user_messages)
                        st.metric("AI Responses", ai_messages)
                        
                        if conversation_history:
                            last_activity = pd.to_datetime(conversation_history[-1]['timestamp'])
                            days_since = (datetime.now() - last_activity).days
                            st.metric("Days Since Last Chat", days_since)
            
            else:
                st.info("Start chatting to see activity patterns!")
        
        except Exception as e:
            st.error(f"Error rendering activity patterns: {str(e)}")

# Import numpy for trend calculation
try:
    import numpy as np
except ImportError:
    # Fallback if numpy is not available
    class np:
        @staticmethod
        def polyfit(x, y, deg):
            return [0, 0]
        
        @staticmethod
        def poly1d(coeffs):
            return lambda x: [0] * len(x) if hasattr(x, '__len__') else 0
