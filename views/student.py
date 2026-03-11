import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import database as db
from utils import load_models, calculate_dsa_score, calculate_company_readiness, create_radar_chart, calculate_resume_score

def student_view():
    st.markdown("## 🎓 Student Analytics Portal")
    st.write(f"Welcome back, **{st.session_state.name}**. Here's your personalized placement analysis.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 New Prediction", "💻 Coding Arena", "🏢 Company Match", "📊 Performance Insights", "👤 Profile Settings"])

    model, scaler, le = load_models()

    # --- TAB 1: PREDICTION ---
    with tab1:
        st.markdown("### 1. Profile Details")
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                cgpa = st.number_input("Cumulative GPA", min_value=0.0, max_value=10.0, value=7.5, step=0.1)
                backlogs = st.number_input("Active Backlogs", min_value=0, value=0, step=1)
            with col2:
                internships = st.number_input("Completed Internships", min_value=0, value=0, step=1)
                coding_rating = st.select_slider("Self-Assessed Coding Proficiency", options=[1, 2, 3, 4, 5], value=3)

        st.markdown("### 2. Technical Skillset")
        with st.container(border=True):
            saved_skills = db.get_student_skills(st.session_state.username)
            c1, c2, c3 = st.columns(3)
            with c1:
                dsa = st.slider("DSA", 0, 100, saved_skills.get("DSA", 50))
                java = st.slider("Java/Python", 0, 100, saved_skills.get("Java/Python", 50))
            with c2:
                system_design = st.slider("System Design", 0, 100, saved_skills.get("System Design", 50))
                os_skill = st.slider("OS", 0, 100, saved_skills.get("OS", 50))
            with c3:
                dbms = st.slider("DBMS", 0, 100, saved_skills.get("DBMS", 50))
            
            if st.button("Save Skills"):
                db.save_student_skills(st.session_state.username, {
                    "DSA": dsa, "Java/Python": java, 
                    "System Design": system_design, "OS": os_skill, "DBMS": dbms
                })
                st.success("Skills updated successfully!")

        st.markdown("### 3. Aptitude Evaluation")
        with st.expander("📝 Start Quick Assessment", expanded=True):
            aptitude_score = 0
            q1 = st.radio("1. What comes next in the series: 2, 6, 12, 20, 30, ...?", ("40", "42", "44", "46"))
            if q1 == "42": aptitude_score += 20
            
            q2 = st.radio("2. If a train 100m long crosses a bridge 200m long in 20 seconds, what is the speed of the train?", ("10 m/s", "15 m/s", "20 m/s", "25 m/s"))
            if q2 == "15 m/s": aptitude_score += 20
            
            q3 = st.radio("3. A is B's sister. C is B's mother. D is C's father. E is D's mother. Then, how is A related to D?", ("Granddaughter", "Daughter", "Grandmother", "Aunt"))
            if q3 == "Granddaughter": aptitude_score += 20
            
            q4 = st.radio("4. Find the odd one out: 3, 5, 7, 12, 17, 19", ("12", "17", "19", "3"))
            if q4 == "12": aptitude_score += 20

            q5 = st.radio("5. In a certain code, COMPUTER is written as RFUVQNPC. How is MEDICINE written in the same code?", ("EOJDJEFM", "EOJDEJFM", "MFEJDJOE", "MFEDJJOE"))
            if q5 == "EOJDJEFM": aptitude_score += 20
        
        st.info(f"Verified Aptitude Score: **{aptitude_score}%**")

        if st.button("Generate Placement Report", type="primary"):
            # Prepare feature vector
            features = np.array([[cgpa, backlogs, internships, coding_rating, aptitude_score]])
            features_scaled = scaler.transform(features)
            
            # Predict
            prediction_idx = model.predict(features_scaled)[0]
            prediction_label = le.inverse_transform([prediction_idx])[0]
            probabilities = model.predict_proba(features_scaled)[0]
            
            db.save_prediction(st.session_state.username, cgpa, backlogs, internships, coding_rating, aptitude_score, prediction_label)
            
            st.divider()
            st.markdown("### 📊 Assessment Results")
            
            res_col1, res_col2 = st.columns([1, 2])
            with res_col1:
                st.metric(label="Predicted Tier", value=prediction_label)
                st.write("---")
                st.success("Report generated and saved to your history.")
            
            with res_col2:
                prob_df = pd.DataFrame({'Category': le.classes_, 'Probability': probabilities})
                fig = px.bar(prob_df, x='Category', y='Probability', 
                            title="Category Confidence Score",
                            color='Probability', color_continuous_scale='Blues')
                fig.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            # Gap Analysis
            st.markdown("### 🛠️ Strategic Improvement Plan")
            target_means = {'CGPA': 8.5, 'Backlogs': 0, 'Internship_Count': 2, 'Coding_Rating': 4, 'Aptitude_Score': 80}
            
            suggestions = []
            if cgpa < target_means['CGPA']:
                suggestions.append(f"🔴 **GPA Optimization**: Focus on core subjects to reach target {target_means['CGPA']}.")
            if backlogs > target_means['Backlogs']:
                suggestions.append(f"🔴 **Backlog Clearance**: Prioritize clearing active backlogs for eligibility.")
            if internships < target_means['Internship_Count']:
                suggestions.append(f"🟡 **Experiential Learning**: Secure at least {target_means['Internship_Count']} internships.")
            if coding_rating < target_means['Coding_Rating']:
                suggestions.append(f"🟡 **Technical Skillset**: Aim for a 4/5 rating on competitive platforms.")
            if aptitude_score < target_means['Aptitude_Score']:
                suggestions.append(f"🟡 **Cognitive Ability**: Enhance logical and mathematical reasoning.")
                
            if not suggestions:
                st.success("✅ **Profile Verified**: You meet all benchmark requirements for Tier 1 placements.")
            else:
                for s in suggestions:
                    st.write(s)

    # --- TAB 2: CODING ARENA ---
    with tab2:
        st.markdown("### 💻 Coding Arena")
        coding_data = db.get_student_coding_data(st.session_state.username)
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("#### 🔗 Profile Integration")
            lc = st.number_input("LeetCode Problems Solved", min_value=0, value=coding_data['leetcode'])
            hr = st.number_input("HackerRank Score", min_value=0, value=coding_data['hackerrank'])
            if st.button("Update Profiles"):
                db.update_student_coding_stats(st.session_state.username, lc, hr)
                st.success("Coding profiles updated!")
                st.rerun()
            
            dsa_score = calculate_dsa_score(lc, hr, coding_data['internal'])
            st.metric("Unified DSA Score", f"{dsa_score}/100")
            
        with c2:
            st.markdown("#### 📝 Internal Coding Challenge")
            questions = db.get_internal_questions()
            if not questions:
                st.info("No internal challenges available yet. Check back later!")
            else:
                q = questions[0] # Just show the first one for demo
                st.info(f"**Challenge**: {q['title']} ({q['difficulty']})")
                st.write(q['description'])
                solution = st.text_area("Write your logic/code here...", height=150)
                if st.button("Submit Solution"):
                    if len(solution) > 20: # Simple validation
                        db.update_internal_score(st.session_state.username, q['points'])
                        st.success(f"Correct! You earned {q['points']} points.")
                        st.rerun()
                    else:
                        st.error("Solution too short or invalid.")

    # --- TAB 3: COMPANY MATCH ---
    with tab3:
        st.markdown("### 🏢 Strategic Company Readiness")
        st.write("Calculated based on CGPA, Skills, and your DSA Score.")
        
        companies = db.get_all_companies()
        my_skills = db.get_student_skills(st.session_state.username)
        history = db.get_student_history(st.session_state.username)
        coding_data = db.get_student_coding_data(st.session_state.username)
        dsa_score = calculate_dsa_score(coding_data['leetcode'], coding_data['hackerrank'], coding_data['internal'])
        
        if not companies:
            st.info("No company data available. Admin needs to add company requirements first.")
        elif not history:
            st.warning("Please complete a 'New Prediction' first to fetch your academic data.")
        else:
            latest_acad = history[0]
            for comp in companies:
                readiness = calculate_company_readiness(latest_acad, comp, my_skills, dsa_score)
                
                with st.container(border=True):
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        st.markdown(f"#### {comp['company_name']}")
                        # Radar Chart for Skill Comparison
                        fig = create_radar_chart(my_skills, comp['required_skills'], comp['company_name'])
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.metric("Readiness", f"{readiness}%")
                        st.progress(readiness / 100)
                        
                        if readiness < 80:
                            st.warning("⚠️ Improvement Needed")
                            missing = []
                            for s, min_val in comp['required_skills'].items():
                                if my_skills.get(s, 0) < min_val:
                                    missing.append(f"{s} (Need {min_val}%)")
                            if missing:
                                st.write("**Focus areas:**")
                                for m in missing:
                                    st.write(f"- {m}")
                            if latest_acad['cgpa'] < comp['min_cgpa']:
                                st.error(f"- CGPA: {latest_acad['cgpa']} < {comp['min_cgpa']}")
                        else:
                            st.success("✅ Good Match!")
                    
                    # --- RESUME ANALYSIS SUB-SECTION ---
                    st.divider()
                    st.markdown("##### 📄 AI Resume Matcher")
                    resume_text = st.text_area("Paste your resume content here to match against this specific company:", 
                                            key=f"resume_{comp['id']}", height=100)
                    if st.button(f"Analyze Resume for {comp['company_name']}", key=f"btn_{comp['id']}"):
                        if resume_text:
                            # Use both academic skills and company required skills for analysis
                            target_keywords = list(comp['required_skills'].keys())
                            match_score, found = calculate_resume_score(resume_text, target_keywords)
                            
                            rcol1, rcol2 = st.columns(2)
                            rcol1.metric("Keyword Match", f"{match_score}%")
                            rcol2.write("**Keywords found:**")
                            rcol2.write(", ".join(found) if found else "None")
                            
                            if match_score > 70:
                                st.balloons()
                                st.success("Your resume has strong alignment with this role!")
                            else:
                                st.info("Tip: Add more keywords related to the required skills to improve your score.")
                        else:
                            st.error("Please paste your resume text first.")

    # --- TAB 4: PROGRESS & ROADMAP ---
    with tab4:
        st.markdown("### 📈 Historical Performance")
        history = db.get_student_history(st.session_state.username)
        
        if history:
            df_hist = pd.DataFrame(history)
            df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'])
            
            latest = df_hist.iloc[0]
            # Calculate Readiness Score: (CGPA * 10) + (Coding * 10) + Aptitude
            # Max possible: 100 + 50 + 100 = 250 -> Scale to 100
            readiness = ((latest['cgpa'] * 10) + (latest['coding_rating'] * 10) + latest['aptitude_score']) / 2.5
            
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Placement Readiness", f"{readiness:.1f}%")
            with m2:
                st.metric("Total Assessments", len(df_hist))
            with m3:
                st.metric("Latest Prediction", latest['predicted_category'])
            
            st.write("---")
            
            # Add Readiness Trend
            df_hist['Readiness_Score'] = ((df_hist['cgpa'] * 10) + (df_hist['coding_rating'] * 10) + df_hist['aptitude_score']) / 2.5
            st.markdown("### 📈 Readiness Score Trend")
            fig_ready = px.area(df_hist, x='timestamp', y='Readiness_Score', 
                                title="Overall Placement Readiness Growth",
                                template="plotly_white")
            st.plotly_chart(fig_ready, use_container_width=True)
            
            c1, c2 = st.columns(2)
            with c1:
                fig_apt = px.line(df_hist, x='timestamp', y='aptitude_score', 
                                 title="Aptitude Growth", markers=True,
                                 template="plotly_white")
                st.plotly_chart(fig_apt, use_container_width=True)
            with c2:
                fig_code = px.line(df_hist, x='timestamp', y='coding_rating', 
                                  title="Coding Skill Trend", markers=True,
                                  template="plotly_white")
                st.plotly_chart(fig_code, use_container_width=True)
                
            st.write("---")
            st.markdown("### 🗺️ Personalized Skill Roadmap")
            
            # Identify top missing skills from latest company analysis
            my_skills = db.get_student_skills(st.session_state.username)
            all_required_skills = set()
            for comp in db.get_all_companies():
                all_required_skills.update(comp['required_skills'].keys())
            
            missing_skills = [s for s in all_required_skills if my_skills.get(s, 0) < 60] # Skill < 60 is "missing"
            
            if not missing_skills:
                st.success("You are well-prepared in all core skills! Admin can add more advanced tracks.")
            else:
                selected_missing = st.selectbox("Select a skill to generate roadmap:", missing_skills)
                resources = db.get_skill_resources(selected_missing)
                
                if resources:
                    for res in resources:
                        with st.expander(f"Week {res['week']}: {res['topic']}"):
                            items = json.loads(res['resources'])
                            for item in items:
                                st.markdown(f"• [{item['name']}]({item['url']}) - {item['desc']}")
                else:
                    st.info(f"No structured roadmap found for {selected_missing}. Contact Admin to add resources.")

            st.write("---")
            st.markdown("### 📋 Detailed Submission Log")
            st.dataframe(df_hist[['timestamp', 'predicted_category', 'cgpa', 'coding_rating', 'aptitude_score']], 
                         use_container_width=True, hide_index=True)
            
        else:
            st.info("No assessment data available. Complete a prediction to unlock your dashboard.")

    # --- TAB 5: PROFILE SETTINGS ---
    with tab5:
        st.markdown("### 👤 Account Settings")
        st.write("Keep your profile information up to date.")
        
        with st.form("profile_edit_form"):
            new_name = st.text_input("Full Name", value=st.session_state.name)
            new_roll = st.text_input("Roll Number", value=st.session_state.roll_no)
            
            st.divider()
            st.write("Change Password (leave blank to keep current)")
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Update Profile", type="primary"):
                if new_pass:
                    if new_pass != confirm_pass:
                        st.error("Passwords do not match!")
                    elif len(new_pass) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        if db.update_user_profile(st.session_state.username, new_name, new_roll, new_pass):
                            st.session_state.name = new_name
                            st.session_state.roll_no = new_roll
                            st.success("Profile and password updated successfully!")
                            st.rerun()
                else:
                    if db.update_user_profile(st.session_state.username, new_name, new_roll):
                        st.session_state.name = new_name
                        st.session_state.roll_no = new_roll
                        st.success("Profile details updated!")
                        st.rerun()
