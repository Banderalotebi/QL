"""
Meritocracy Panel - Streamlit UI Component
Displays agent leaderboard, Agent of the Day, and reward system
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MeritocracyPanel:
    """
    Streamlit UI component for the meritocracy system
    Displays rankings, rewards, and agent metrics
    """
    
    def __init__(self):
        self.section_key = "meritocracy_panel"
    
    @staticmethod
    def render_leaderboard_widget(leaderboard: List[Dict]) -> None:
        """Render the leaderboard as a ranked table with visualizations"""
        if not leaderboard:
            st.info("📊 No agents registered yet")
            return
        
        # Convert to DataFrame for display
        df = pd.DataFrame(leaderboard)
        
        # Create display dataframe with ranks
        display_df = df.copy()
        display_df.insert(0, 'Rank', range(1, len(display_df) + 1))
        
        # Rename columns for display
        display_df.columns = [
            'Rank', 'Agent ID', 'Role', 'Credits 💎',
            'Accuracy %', 'Tasks Completed', 'Tasks Successful'
        ]
        
        # Format numeric columns
        display_df['Accuracy %'] = display_df['Accuracy %'].apply(lambda x: f"{x:.1f}%")
        display_df['Credits 💎'] = display_df['Credits 💎'].apply(lambda x: f"{x:,}")
        
        # Display table
        st.dataframe(display_df, use_container_width=True)
        
        # Add mini charts for top 3 agents
        if len(leaderboard) >= 1:
            col1, col2, col3 = st.columns(3)
            
            for i, col in enumerate([col1, col2, col3]):
                if i < len(leaderboard):
                    agent = leaderboard[i]
                    with col:
                        st.metric(
                            label=f"#{i+1}: {agent['agent_id']}",
                            value=f"{agent['total_credits']:,} 💎",
                            delta=f"{agent['accuracy_score']:.1f}% accuracy"
                        )
    
    @staticmethod
    def render_agent_of_the_day_widget(aotd: Optional[Dict]) -> None:
        """Render the Agent of the Day spotlight widget"""
        st.subheader("🌟 Agent of the Day")
        
        if aotd and aotd.get('agent_id') != 'None':
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"### 🏆 {aotd['agent_id']}")
                st.write(f"**Performance Score:** {aotd.get('performance_score', 0):.2f}")
                st.write(f"**Achievement:** {aotd.get('achievement_summary', 'Excellent work!')}")
            
            with col2:
                st.info(f"Tasks: {aotd.get('patternstask_count', 0)}\n\n+500 💎 Bonus!")
        else:
            st.warning("⏱️ Calculating today's leader...")
    
    @staticmethod
    def render_agent_metrics_widget(agent_metrics: Optional[Dict]) -> None:
        """Render detailed metrics for a selected agent"""
        if not agent_metrics:
            st.warning("Agent not found")
            return
        
        st.write(f"### 👤 {agent_metrics['agent_id']}")
        st.write(f"**Role:** {agent_metrics['role']}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Total Credits", f"{agent_metrics['total_credits']:,} 💎")
        col2.metric("Accuracy Score", f"{agent_metrics['accuracy_score']:.1f}%")
        col3.metric("Tasks Done", agent_metrics['tasks_completed'])
        col4.metric("Success Rate", f"{agent_metrics.get('success_rate', 0):.1%}")
        
        if agent_metrics['tasks_completed'] > 0:
            # Progress bar for success rate
            success_rate = agent_metrics.get('success_rate', 0)
            st.progress(success_rate, text=f"Success Rate: {success_rate:.1%}")
    
    @staticmethod
    def render_reward_panel() -> None:
        """Render the reward awarding panel for admins"""
        st.subheader("🎁 Award Credits")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            agent_to_reward = st.text_input(
                "Agent to Reward",
                placeholder="e.g., Senior Architect",
                key="reward_agent_input"
            )
        
        with col2:
            credits = st.number_input(
                "Credits",
                min_value=1,
                max_value=10000,
                value=100,
                key="reward_amount_input"
            )
        
        with col3:
            st.write("")
            st.write("")
            if st.button("🎉 Award!", use_container_width=True):
                if agent_to_reward:
                    st.success(f"✅ Awarded {credits} 💎 to {agent_to_reward}!")
                else:
                    st.error("Please select an agent")
        
        reason = st.text_area(
            "Reason for reward",
            placeholder="e.g., Excellent pattern analysis",
            key="reward_reason_input"
        )
    
    @staticmethod
    def render_stats_summary(metrics: Dict) -> None:
        """Render summary statistics"""
        st.subheader("📈 Hive Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Total Agents", len(metrics.get('agents', [])))
        col2.metric("Total Credits Distributed", f"{sum(a.get('total_credits', 0) for a in metrics.get('agents', [])):,}")
        col3.metric("Average Accuracy", f"{(sum(a.get('accuracy_score', 0) for a in metrics.get('agents', [])) / max(len(metrics.get('agents', [])), 1)):.1f}%")
        col4.metric("Tasks Completed", sum(a.get('tasks_completed', 0) for a in metrics.get('agents', [])))
    
    @staticmethod
    def render_history_widget(agent_id: str, history: List[Dict]) -> None:
        """Render reward history for an agent"""
        st.subheader(f"📜 Recent Rewards for {agent_id}")
        
        if not history:
            st.info("No recent rewards")
            return
        
        # Create DataFrame
        df = pd.DataFrame(history)
        df.columns = ['Agent', 'Amount 💎', 'Reason', 'Date', 'By']
        
        # Format date
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(df, use_container_width=True)
    
    @staticmethod
    def render_comparison_widget(selected_agents: List[str], metrics_map: Dict) -> None:
        """Render comparison between selected agents"""
        st.subheader("⚖️ Agent Comparison")
        
        if not selected_agents or not metrics_map:
            st.info("Select agents to compare")
            return
        
        # Prepare comparison data
        comparison_data = []
        for agent_id in selected_agents:
            if agent_id in metrics_map:
                metrics = metrics_map[agent_id]
                comparison_data.append({
                    'Agent': agent_id,
                    'Credits': metrics['total_credits'],
                    'Accuracy': metrics['accuracy_score'],
                    'Tasks': metrics['tasks_completed'],
                    'Success Rate': metrics.get('success_rate', 0)
                })
        
        if comparison_data:
            df = pd.DataFrame(comparison_data)
            
            # Display metrics vertically
            for col_name in ['Credits', 'Accuracy', 'Tasks', 'Success Rate']:
                col = 'Credits' if col_name == 'Credits' else col_name
                st.write(f"### {col}")
                chart_df = df[['Agent', col]].set_index('Agent')
                st.bar_chart(chart_df)


class LeaderboardWidget:
    """Simple widget for displaying top agents"""
    
    @staticmethod
    def render_compact(leaderboard: List[Dict], max_agents: int = 5) -> None:
        """Render compact leaderboard (sidebar or small space)"""
        st.markdown("### 🏆 Top Agents")
        
        for i, agent in enumerate(leaderboard[:max_agents]):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            st.write(
                f"{medal} **{agent['agent_id']}** - {agent['total_credits']:,} 💎 "
                f"({agent['accuracy_score']:.1f}%)"
            )
    
    @staticmethod
    def render_expanded(leaderboard: List[Dict]) -> None:
        """Render expanded leaderboard with full details"""
        MeritocracyPanel.render_leaderboard_widget(leaderboard)


def create_meritocracy_tab(hive) -> None:
    """
    Create a complete meritocracy tab for the Streamlit dashboard
    
    Args:
        hive: HiveCouncil instance
    """
    tab1, tab2, tab3 = st.tabs(["🏆 Leaderboard", "🌟 Agent of the Day", "👤 Agent Detail"])
    
    with tab1:
        st.header("Agent Leaderboard")
        leaderboard = hive.get_leaderboard(limit=20)
        MeritocracyPanel.render_leaderboard_widget(leaderboard)
    
    with tab2:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            aotd = hive.get_agent_of_the_day()
            MeritocracyPanel.render_agent_of_the_day_widget(aotd)
        
        with col2:
            if st.button("🔄 Recalculate"):
                winner = hive.calculate_agent_of_the_day()
                if winner:
                    st.success(f"🎉 {winner} is today's champion!")
                else:
                    st.info("Calculation complete")
        
        st.divider()
        MeritocracyPanel.render_reward_panel()
    
    with tab3:
        st.header("Agent Details")
        leaderboard = hive.get_leaderboard(limit=100)
        agent_ids = [a['agent_id'] for a in leaderboard]
        
        selected_agent = st.selectbox("Select Agent", agent_ids)
        
        if selected_agent:
            metrics = hive.get_agent_metrics(selected_agent)
            if metrics:
                MeritocracyPanel.render_agent_metrics_widget(metrics)
                
                st.divider()
                
                # Show history
                history = hive.meritocracy_db.get_agent_history(selected_agent, days=30)
                MeritocracyPanel.render_history_widget(selected_agent, history)
