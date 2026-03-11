import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle
import os

# Create dummy data
# Features: 'CGPA', 'Backlogs', 'Internship_Count', 'Coding_Rating', 'Aptitude_Score'
# Target: 'Placement_Status' (TIER_1, TIER_2, MASS_RECRUITER, UNPLACED)

np.random.seed(42)
n_samples = 1000

data = {
    'CGPA': np.random.uniform(6.0, 10.0, n_samples),
    'Backlogs': np.random.randint(0, 3, n_samples),
    'Internship_Count': np.random.randint(0, 4, n_samples),
    'Coding_Rating': np.random.randint(1, 6, n_samples), # 1 to 5 stars
    'Aptitude_Score': np.random.randint(40, 100, n_samples)
}

df = pd.DataFrame(data)

# Logic for synthetic target
def determine_placement(row):
    score = (row['CGPA'] * 10) + (row['Internship_Count'] * 5) + (row['Coding_Rating'] * 5) + (row['Aptitude_Score'] * 0.2) - (row['Backlogs'] * 10)
    
    if score > 150:
        return 'Tier_1'
    elif score > 120:
        return 'Tier_2'
    elif score > 90:
        return 'Mass_Recruiter'
    else:
        return 'Unplaced'

df['Placement_Status'] = df.apply(determine_placement, axis=1)

# Preprocessing
X = df.drop('Placement_Status', axis=1)
y = df['Placement_Status']

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Encoding
le = LabelEncoder()
y_train_encoded = le.fit_transform(y_train)
y_test_encoded = le.transform(y_test)

# Model Training
model = DecisionTreeClassifier(random_state=42)
model.fit(X_train_scaled, y_train_encoded)

# Accuracy Check
print(f"Model Accuracy: {model.score(X_test_scaled, y_test_encoded)}")

# Save Models
os.makedirs('models', exist_ok=True)

with open('models/decision_tree_model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

with open('models/label_encoder.pkl', 'wb') as f:
    pickle.dump(le, f)

print("Models saved successfully in 'models/' directory.")
