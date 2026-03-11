import streamlit as st
import pandas as pd
import plotly.express as px
import database as db

def admin_view():
    st.markdown("## 📊 Institutional Oversight Dashboard")
    st.write("Comprehensive overview of student performance and placement readiness across the institution.")
    
    tab1, tab2, tab3 = st.tabs(["Dashboard Overview", "🏢 Company Management", "📚 Knowledge & Challenges"])

    with tab1:
        df = db.get_all_student_data()
    
    if not df.empty:
        # Key Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Assessments", len(df))
        with m2:
            st.metric("Institutional CGPA", f"{df['CGPA'].mean():.2f}")
        with m3:
            st.metric("Avg Coding Proficiency", f"{df['Coding_Rating'].mean():.2f}/5")
        with m4:
            st.metric("Avg Aptitude Score", f"{df['Aptitude_Score'].mean():.1f}%")
        
        st.write("---")
        
        # Charts
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### 🏛️ Tier Distribution")
            if 'Predicted_Category' in df.columns:
                fig_cat = px.pie(df, names='Predicted_Category', 
                                title="Student Placement Classification",
                                hole=0.4,
                                color_discrete_sequence=px.colors.qualitative.Safe)
                fig_cat.update_layout(height=400)
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.warning("Prediction telemetry not available.")
            
        with c2:
            st.markdown("### 🔍 Skill Gap Analysis")
            ideal = {'CGPA': 9.0, 'Aptitude': 90, 'Coding': 5}
            gaps = {
                'Metric': ['CGPA Gap', 'Aptitude Gap', 'Coding Gap'],
                'Value': [
                    max(0, ideal['CGPA'] - df['CGPA'].mean()),
                    max(0, ideal['Aptitude'] - df['Aptitude_Score'].mean()),
                    max(0, ideal['Coding'] - df['Coding_Rating'].mean())
                ]
            }
            gap_df = pd.DataFrame(gaps)
            fig_gap = px.bar(gap_df, x='Metric', y='Value', 
                            title="Average Deviations from Ideal Profile", 
                            color='Value', color_continuous_scale='Reds')
            fig_gap.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_gap, use_container_width=True)
            
            critical_metric = gap_df.loc[gap_df['Value'].idxmax(), 'Metric']
            st.error(f"**Action Item**: Institutional deficit identified in **{critical_metric}**.")

        # Batch Skill Heatmap / Averages
        st.divider()
        st.markdown("### 🗺️ Institutional Skill Heatmap")
        skill_avgs = db.get_skill_averages()
        if skill_avgs:
            skill_df = pd.DataFrame(list(skill_avgs.items()), columns=['Skill', 'Average Score'])
            fig_skills = px.bar(skill_df, x='Skill', y='Average Score', 
                               title="Average Skill Proficiency Across Institution",
                               color='Average Score', color_continuous_scale='Viridis',
                               labels={'Average Score': 'Average (0-100)'})
            fig_skills.update_layout(height=400)
            st.plotly_chart(fig_skills, use_container_width=True)
            
            lowest_skill = skill_df.loc[skill_df['Average Score'].idxmin(), 'Skill']
            st.info(f"💡 Recommendation: Consider organizing a workshop for **{lowest_skill}** as it has the lowest institutional average.")
        else:
            st.info("No detailed skill data available yet. Encourage students to update their technical skillset in the Student Portal.")

        # At-Risk Students
        st.divider()
        st.subheader("⚠️ At-Risk Students (Predicted: Unplaced)")
        if 'Predicted_Category' in df.columns:
            at_risk = df[df['Predicted_Category'] == 'Unplaced']
            
            if not at_risk.empty:
                st.dataframe(at_risk[['Name', 'Roll_No', 'CGPA', 'Backlogs', 'Predicted_Category']])
                st.error(f"Action Required: {len(at_risk)} students are at high risk of remaining unplaced.")
            else:
                st.success("No students currently predicted as 'Unplaced'. Great job!")
            
        # Full Data View
        st.write("---")
        with st.expander("📂 Access Raw Institutional Data"):
            st.dataframe(df, use_container_width=True)
            
    else:
        st.info("System Standby: Awaiting student assessment data to populate dashboard.")

    with tab2:
        st.markdown("### 🏢 Management Console: Company Requirements")
        
        # Form to add new company
        with st.form("add_company_form", clear_on_submit=True):
            st.markdown("#### 📝 Add New Company Requirement")
            name = st.text_input("Company Name", placeholder="e.g., Google, Microsoft")
            min_cgpa = st.number_input("Minimum CGPA", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
            st.markdown("**Skill Set (Score 0-100)**")
            c1, c2, c3 = st.columns(3)
            with c1:
                dsa = st.slider("DSA", 0, 100, 50)
                java = st.slider("Java/Python", 0, 100, 50)
            with c2:
                system_design = st.slider("System Design", 0, 100, 50)
                os = st.slider("OS", 0, 100, 50)
            with c3:
                dbms = st.slider("DBMS", 0, 100, 50)
            
            submitted = st.form_submit_button("Add Company")
            if submitted and name:
                db.add_company(name, min_cgpa, {
                    "DSA": dsa, "Java/Python": java, 
                    "System Design": system_design, "OS": os, "DBMS": dbms
                })
                st.success(f"Added requirements for {name}.")
        
        st.write("---")
        
        # Display existing companies
        st.markdown("#### 📋 Registered Companies")
        companies = db.get_all_companies()
        if companies:
            for comp in companies:
                with st.expander(f"{comp['company_name']} (Min CGPA: {comp['min_cgpa']})"):
                    st.json(comp['required_skills'])
                    if st.button(f"Delete {comp['company_name']}", key=f"del_{comp['id']}"):
                        db.delete_company(comp['id'])
                        st.rerun()
        else:
            st.info("No companies registered yet.")

    with tab3:
        st.markdown("### 📚 Knowledge & Challenges Management")
        
        q_tab, r_tab = st.tabs(["Coding Questions", "Roadmap Resources"])
        
        with q_tab:
            st.markdown("#### 📝 Manage Internal Challenges")
            with st.form("add_question_form", clear_on_submit=True):
                q_title = st.text_input("Question Title")
                q_desc = st.text_area("Description / Problem Statement")
                c1, c2 = st.columns(2)
                with c1:
                    q_diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
                with c2:
                    q_points = st.number_input("Points", min_value=10, max_value=100, step=10)
                
                if st.form_submit_button("Add Question"):
                    if q_title and q_desc:
                        db.add_internal_question(q_title, q_desc, q_diff, q_points)
                        st.success(f"Question '{q_title}' added!")
                    else:
                        st.error("Please fill all fields.")
            
            st.write("---")
            st.markdown("#### 📋 Existing Questions")
            questions = db.get_internal_questions()
            if questions:
                for q in questions:
                    st.write(f"**{q['title']}** ({q['difficulty']}) - {q['points']} pts")
            else:
                st.info("No questions added yet.")

        with r_tab:
            st.markdown("#### 🗺️ Manage Roadmap Resources")
            with st.form("add_resource_form", clear_on_submit=True):
                skill = st.selectbox("For Skill", ["DSA", "Java/Python", "System Design", "OS", "DBMS"])
                week = st.number_input("Week Number", min_value=1, max_value=12, step=1)
                topic = st.text_input("Topic Name")
                
                st.write("**Resource Links (JSON Format)**")
                res_example = '[{"name": "Course Link", "url": "https://...", "desc": "Short description"}]'
                resources_json = st.text_area("Resources JSON", value=res_example)
                
                if st.form_submit_button("Add Roadmap Node"):
                    try:
                        import json
                        json.loads(resources_json) # Validate JSON
                        db.add_skill_resource(skill, int(week), topic, resources_json)
                        st.success(f"Roadmap node for {skill} week {week} added!")
                    except Exception as e:
                        st.error(f"Invalid JSON: {e}")
            
            st.write("---")
            st.markdown("#### 📋 Current Roadmap Nodes")
            for sk in ["DSA", "Java/Python", "System Design", "OS", "DBMS"]:
                res_list = db.get_skill_resources(sk)
                if res_list:
                    with st.expander(f"Roadmap for {sk}"):
                        for r in res_list:
                            st.write(f"Week {r['week']}: {r['topic']}")
                            if st.button(f"Delete Node {r['id']}", key=f"del_res_{r['id']}"):
                                db.delete_skill_resource(r['id'])
                                st.rerun()

