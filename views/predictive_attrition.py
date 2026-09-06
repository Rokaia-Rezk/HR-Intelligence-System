"""
predictive_attrition.py
------------------------
Turns the dashboard from descriptive ("what happened") into predictive
("who is likely to leave next"). Reuses the same canonical-field data
that every other page uses, so it stays dataset-agnostic like the rest
of the app -- swap the source CSV and this page retrains itself on
whatever canonical fields are available, no code changes needed.

Model: RandomForestClassifier, trained on employees with a KNOWN
outcome (Active vs Terminated), then used to score the CURRENT active
workforce with a probability of leaving. This mirrors a standard churn
pipeline (train on labelled history, score the live population).

Kept deliberately simple and transparent -- feature importances are
shown directly so the "why" behind the model is never a black box.
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from sklearn.preprocessing import LabelEncoder

from data_loader import load_standard_data
from filters import style_fig

st.title("Predictive Attrition")
st.caption("A classification model trained on historical outcomes, used to flag which "
           "current employees look most like the ones who have left before.")

df = load_standard_data()

NUMERIC_FEATURES = ["salary", "engagement_score", "satisfaction_score",
                     "absences", "days_late", "special_projects_count"]
CATEGORICAL_FEATURES = ["department", "performance_score", "recruitment_source"]

available_numeric = [c for c in NUMERIC_FEATURES if c in df.columns and df[c].notna().any()]
available_categorical = [c for c in CATEGORICAL_FEATURES if c in df.columns and df[c].notna().any()]

if len(available_numeric) < 2:
    st.warning("Not enough numeric fields available in this dataset to train a model.")
    st.stop()

# ---- Build model dataset -------------------------------------------------
model_df = df.dropna(subset=available_numeric, how="all").copy()
for col in available_numeric:
    model_df[col] = model_df[col].fillna(model_df[col].median())

encoders = {}
for col in available_categorical:
    model_df[col] = model_df[col].fillna("Unknown").astype(str)
    le = LabelEncoder()
    model_df[col + "_enc"] = le.fit_transform(model_df[col])
    encoders[col] = le

feature_cols = available_numeric + [c + "_enc" for c in available_categorical]
X = model_df[feature_cols]
y = (~model_df["is_active"]).astype(int)  # 1 = left, 0 = still active

if y.nunique() < 2:
    st.warning("This dataset has no terminated employees to learn from, so a model can't be trained.")
    st.stop()

# ---- Train / evaluate ------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)
clf = RandomForestClassifier(n_estimators=300, max_depth=6, min_samples_leaf=5,
                              class_weight="balanced", random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
y_proba = clf.predict_proba(X_test)[:, 1]
acc = accuracy_score(y_test, y_pred)
try:
    auc = roc_auc_score(y_test, y_proba)
except ValueError:
    auc = float("nan")

c1, c2, c3 = st.columns(3)
c1.metric("Model", "Random Forest")
c2.metric("Test Accuracy", f"{acc:.0%}")
c3.metric("ROC-AUC", f"{auc:.2f}" if auc == auc else "N/A")
st.caption("Trained on 75% of employees with a known outcome, evaluated on the remaining 25% "
           "it never saw during training.")

st.divider()

# ---- Feature importance -----------------------------------------------------
st.subheader("What the Model Is Actually Picking Up On")
importances = pd.Series(clf.feature_importances_, index=feature_cols)
importances.index = [i.replace("_enc", "") for i in importances.index]
importances = importances.sort_values(ascending=True)
fig_imp = px.bar(x=importances.values, y=importances.index, orientation="h",
                  color_discrete_sequence=["#7C5CBF"])
fig_imp.update_layout(xaxis_title="Relative Importance", yaxis_title="")
st.plotly_chart(style_fig(fig_imp), width='stretch', theme=None)
top_feat = importances.index[-1]
st.caption(f"**{top_feat}** is the single strongest predictor of attrition in this dataset.")

st.divider()

# ---- Score the current active workforce -------------------------------------
st.subheader("Attrition Risk — Current Active Workforce")
st.caption("Every active employee scored with the trained model. Not a certainty — a ranked "
           "signal for where to look first.")

active_df = model_df[model_df["is_active"]].copy()
if active_df.empty:
    st.info("No active employees to score in this dataset.")
else:
    active_df["risk_score"] = clf.predict_proba(active_df[feature_cols])[:, 1]
    active_df["risk_band"] = pd.cut(
        active_df["risk_score"], bins=[-0.01, 0.33, 0.66, 1.0],
        labels=["Low", "Medium", "High"]
    )

    band_counts = active_df["risk_band"].value_counts().reindex(["Low", "Medium", "High"]).fillna(0)
    c1, c2, c3 = st.columns(3)
    c1.metric("High Risk", int(band_counts["High"]))
    c2.metric("Medium Risk", int(band_counts["Medium"]))
    c3.metric("Low Risk", int(band_counts["Low"]))

    display_cols = ["employee_name", "department", "position", "risk_score", "risk_band"]
    display_cols = [c for c in display_cols if c in active_df.columns]
    watchlist = active_df.sort_values("risk_score", ascending=False)[display_cols].head(15)
    watchlist = watchlist.rename(columns={"risk_score": "Risk Score", "risk_band": "Risk Band"})
    watchlist["Risk Score"] = watchlist["Risk Score"].round(2)
    st.dataframe(watchlist, width='stretch')

    st.caption("Highest-risk employees to prioritize for a retention conversation, based on how "
               "closely their profile matches employees who have left before.")

st.divider()

# ---- Score a single, hand-entered employee ----------------------------------
st.subheader("Score a Specific Employee")
st.caption("Enter someone's details — a real employee, or a candidate you're evaluating — and get "
           "the same risk score the model above gives everyone else, plus which specific inputs "
           "are driving it.")

# Whether more of a feature is generally a good or bad sign, for writing a
# recommendation in plain language. This is a simple domain heuristic (not
# learned from the model) — it only decides how a flagged input gets worded,
# never which features get flagged (that's still driven by feature_importances_).
DIRECTION = {
    "salary": "higher_is_better", "engagement_score": "higher_is_better",
    "satisfaction_score": "higher_is_better", "special_projects_count": "higher_is_better",
    "absences": "higher_is_worse", "days_late": "higher_is_worse",
}

with st.form("score_employee_form"):
    inputs = {}
    form_cols = st.columns(2)
    active_pop = model_df[model_df["is_active"]]  # for setting sensible ranges/defaults

    for i, col in enumerate(available_numeric):
        with form_cols[i % 2]:
            col_min, col_max = float(model_df[col].min()), float(model_df[col].max())
            col_default = float(active_pop[col].median()) if len(active_pop) else float(model_df[col].median())
            step = 1000.0 if col == "salary" else (0.1 if col in ("engagement_score", "satisfaction_score") else 1.0)
            inputs[col] = st.number_input(col.replace("_", " ").title(), min_value=col_min,
                                           max_value=col_max, value=col_default, step=step,
                                           key=f"score_{col}")
    for i, col in enumerate(available_categorical):
        with form_cols[(len(available_numeric) + i) % 2]:
            choices = list(encoders[col].classes_)
            inputs[col] = st.selectbox(col.replace("_", " ").title(), choices, key=f"score_{col}")

    submitted = st.form_submit_button("Score This Employee")

if submitted:
    row = {}
    for col in available_numeric:
        row[col] = inputs[col]
    for col in available_categorical:
        row[col + "_enc"] = encoders[col].transform([inputs[col]])[0]
    input_df = pd.DataFrame([row])[feature_cols]

    risk = clf.predict_proba(input_df)[0, 1]
    band = "High" if risk >= 0.66 else "Medium" if risk >= 0.33 else "Low"
    band_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}[band]

    rc1, rc2 = st.columns([1, 2])
    with rc1:
        st.metric("Attrition Risk", f"{risk:.0%}", help="Model's estimated probability this person leaves.")
        st.markdown(f"### {band_color} {band} Risk")

    with rc2:
        # Flag whichever of THIS person's inputs look concerning, restricted to
        # the model's own top predictors — so the explanation reflects what the
        # model actually weighs, not every field regardless of relevance.
        ranked_features = importances.sort_values(ascending=False).index.tolist()
        notes = []
        for feat in ranked_features:
            if feat not in inputs or feat not in DIRECTION or len(active_pop) < 5:
                continue
            percentile = (active_pop[feat] < inputs[feat]).mean()
            direction = DIRECTION[feat]
            concerning = (direction == "higher_is_better" and percentile <= 0.25) or \
                         (direction == "higher_is_worse" and percentile >= 0.75)
            if concerning:
                label = feat.replace("_", " ")
                notes.append(f"their **{label}** ({inputs[feat]:g}) is worse than about "
                             f"{(1 - percentile) * 100:.0f}% of the current active workforce" if direction == "higher_is_better"
                             else f"their **{label}** ({inputs[feat]:g}) is higher than about "
                                  f"{percentile * 100:.0f}% of the current active workforce")
            if len(notes) >= 2:
                break

        if band == "High":
            headline = "This profile closely resembles people who have already left — worth a direct, prompt retention conversation."
        elif band == "Medium":
            headline = "Some risk signals here, but not a clear match to people who've left — worth keeping an eye on rather than acting urgently."
        else:
            headline = "This profile looks similar to employees who've stayed — no action indicated based on this alone."

        if notes:
            st.markdown(f"{headline} Specifically, {', and '.join(notes)}.")
        else:
            st.markdown(headline)

        st.caption("This is a model estimate based on patterns in historical data, not a diagnosis of "
                   "this individual — use it to prioritize a conversation, not to replace one.")

