import streamlit as st
import plotly.graph_objects as go
import pickle
import os
import re

# --- PATHS ---
MODEL_PATH = 'models/decision_tree_model.pkl'
SCALER_PATH = 'models/scaler.pkl'
LE_PATH = 'models/label_encoder.pkl'

@st.cache_resource
def load_models():
    """Load the trained machine learning models."""
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        with open(SCALER_PATH, 'rb') as f:
            scaler = pickle.load(f)
        with open(LE_PATH, 'rb') as f:
            le = pickle.load(f)
        return model, scaler, le
    except FileNotFoundError:
        st.error("Models not found. Please run 'generate_dummy_models.py' first.")

def calculate_dsa_score(leetcode_solved, hackerrank_score, internal_score):
    """
    Calculates a DSA Score (0-100).
    Weights: LeetCode (40%), HackerRank (30%), Internal (30%)
    Assumptions: 300 LC problems = 100%, 1000 HR score = 100%, 500 Internal = 100%
    """
    lc_score = min(leetcode_solved / 300, 1.0) * 40
    hr_score = min(hackerrank_score / 1000, 1.0) * 30
    int_score = min(internal_score / 500, 1.0) * 30
    return round(lc_score + hr_score + int_score, 1)

def calculate_company_readiness(student_data, company_req, student_skills, dsa_score):
    """
    Calculates readiness for a specific company (0-100).
    Weights: CGPA (30%), Technical Skills (40%), DSA Score (30%)
    """
    # 1. CGPA Component (30%)
    cgpa_req = company_req['min_cgpa']
    student_cgpa = student_data.get('cgpa', 0)
    if student_cgpa >= cgpa_req:
        cgpa_score = 30
    else:
        cgpa_score = max(0, (student_cgpa / cgpa_req) * 20) # Penalty for not meeting min

    # 2. Technical Skills Component (40%)
    req_skills = company_req['required_skills']
    if not req_skills:
        skills_score = 40
    else:
        met_count = 0
        total_skills = len(req_skills)
        for skill, min_val in req_skills.items():
            if student_skills.get(skill, 0) >= min_val:
                met_count += 1
        skills_score = (met_count / total_skills) * 40

    # 3. DSA Score Component (30%)
    # Higher DSA score means better readiness
    dsa_comp = (dsa_score / 100) * 30
    
    total_readiness = cgpa_score + skills_score + dsa_comp
    return min(round(total_readiness, 1), 100.0)

def calculate_resume_score(resume_text, target_skills):
    """
    Simple keyword-based resume matching.
    """
    if not resume_text or not target_skills:
        return 0
    
    score = 0
    found_skills = []
    
    for skill in target_skills:
        # Simple regex for word boundary matching
        if re.search(rf'\b{re.escape(skill)}\b', resume_text, re.IGNORECASE):
            score += 1
            found_skills.append(skill)
            
    match_percentage = (score / len(target_skills)) * 100 if target_skills else 0
    return round(match_percentage, 1), found_skills

def create_radar_chart(my_skills, target_skills, company_name):
    """
    Generates a Radar Chart comparing student skills vs company requirements.
    """
    categories = list(target_skills.keys())
    
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[my_skills.get(cat, 0) for cat in categories],
        theta=categories,
        fill='toself',
        name='My Skills',
        line_color='#007BFF'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[target_skills[cat] for cat in categories],
        theta=categories,
        fill='toself',
        name=f'{company_name} Req',
        line_color='#FF4B4B'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=True,
        title=f"Skill Comparison: {company_name}",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig
