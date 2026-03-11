import streamlit as st
import database as db
import pandas as pd

def leaderboard_view():
    st.markdown("## 🏆 Placement Readiness Leaderboard")
    st.write("Top-performing students based on their cumulative placement readiness scores.")

    df = db.get_leaderboard_data()

    if not df.empty:
        # Style the dataframe
        df.reset_index(drop=True, inplace=True)
        df.index += 1
        df.index.name = 'Rank'
        
        # Display top 3 as cards
        top_3 = df.head(3)
        cols = st.columns(3)
        
        for i, (idx, row) in enumerate(top_3.iterrows()):
            with cols[i]:
                medal = ["🥇", "🥈", "🥉"][i]
                st.markdown(f"""
                <div style="padding: 1rem; border-radius: 10px; background-color: white; border: 1px solid #E9ECEF; text-align: center;">
                    <h1 style="margin:0;">{medal}</h1>
                    <h3 style="margin:0.5rem 0;">{row['name']}</h3>
                    <p style="color: #007BFF; font-weight: bold; font-size: 1.2rem; margin:0;">{row['Readiness_Score']:.1f}%</p>
                    <p style="color: #6C757D; font-size: 0.8rem;">Ready for Tier 1</p>
                </div>
                """, unsafe_allow_html=True)

        st.write("---")
        
        # Display full table
        st.markdown("### 📋 Full Rankings")
        st.dataframe(
            df[['name', 'cgpa', 'coding_rating', 'aptitude_score', 'Readiness_Score']],
            use_container_width=True,
            column_config={
                "name": "Student Name",
                "cgpa": "CGPA",
                "coding_rating": "Coding",
                "aptitude_score": "Aptitude",
                "Readiness_Score": st.column_config.ProgressColumn(
                    "Readiness Score",
                    help="Placement Readiness Percentage",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
            },
            hide_index=False
        )
    else:
        st.info("The leaderboard is currently empty. Start taking assessments to appear here!")
