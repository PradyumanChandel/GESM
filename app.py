"""Streamlit advisor: profile in, eligible schemes with reasons out (SIH26092, group G8)."""
import streamlit as st

from eligibility.baseline import checklist_eligible
from eligibility.engine import ELIGIBLE, NOT_ELIGIBLE, UNDETERMINED, evaluate_profile, load_rules
from eligibility.normalize import ProfileError, normalize_profile

RULES_PATH = "rules/schemes.json"
NONE = "Not provided"
YN = [NONE, "Yes", "No"]

st.set_page_config(page_title="Scheme Eligibility Advisor", page_icon="🧭", layout="centered")


@st.cache_resource
def get_rules():
    return load_rules(RULES_PATH)


rules = get_rules()
vocab = rules["vocabulary"]


def choose(label, options, key):
    value = st.selectbox(label, [NONE] + options, key=key)
    return None if value == NONE else value


def yes_no(value):
    return {"Yes": True, "No": False}.get(value)


st.title("Government Scheme Eligibility Advisor")
st.caption("Explains every decision by the condition behind it. Advisory only; "
           "it does not replace the administering authority.")
st.warning(rules.get("_status", ""))

with st.form("profile"):
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("Age", min_value=0, max_value=120, value=None, step=1)
        income = st.number_input("Annual household income (INR)", min_value=0.0, value=None, step=10000.0)
        state = choose("State / UT", vocab["state"], "state")
        social = choose("Social category", vocab["social_category"], "social")
        gender = choose("Gender", vocab["gender"], "gender")
    with c2:
        enterprise_type = choose("Enterprise type", vocab["enterprise_type"], "etype")
        registered = st.selectbox("Enterprise registered?", YN, key="reg")
        notified = st.selectbox("Resident of a notified area?", YN, key="notified")
        start = st.text_input("Enterprise start date (YYYY-MM-DD)", value="", key="start")
    submitted = st.form_submit_button("Check eligibility", type="primary")

if submitted:
    raw = {
        "age": age, "annual_household_income": income, "state": state,
        "social_category": social, "gender": gender, "enterprise_type": enterprise_type,
        "enterprise_registered": yes_no(registered), "notified_area": yes_no(notified),
        "enterprise_start_date": start,
    }
    try:
        st.session_state["profile"] = normalize_profile(raw, vocab)
    except ProfileError as exc:
        st.session_state.pop("profile", None)
        st.error(f"Please correct: {exc}")

profile = st.session_state.get("profile")
if profile is None:
    st.info("Fill in the profile and press **Check eligibility**. Blank fields are treated as unknown, not as no.")
    st.stop()

results = evaluate_profile(rules, profile)
counts = {s: sum(r.status == s for r in results) for s in (ELIGIBLE, UNDETERMINED, NOT_ELIGIBLE)}

tab_advisor, tab_baseline = st.tabs(["Advisor results", "Single-scheme checklist (baseline)"])

with tab_advisor:
    m1, m2, m3 = st.columns(3)
    m1.metric("Eligible", counts[ELIGIBLE])
    m2.metric("Undetermined", counts[UNDETERMINED])
    m3.metric("Not eligible", counts[NOT_ELIGIBLE])

    for status, title in [(ELIGIBLE, "Eligible"),
                          (UNDETERMINED, "Undetermined: more information needed"),
                          (NOT_ELIGIBLE, "Not eligible")]:
        items = [r for r in results if r.status == status]
        st.subheader(f"{title} ({len(items)})")
        for r in items:
            with st.expander(r.scheme_name):
                st.text(r.explanation)
                if r.missing_fields:
                    st.info("Adding these would settle the decision: " + ", ".join(r.missing_fields))

with tab_baseline:
    st.caption("Same profile, one scheme at a time. Returns yes or no only, with no reasons.")
    scheme = st.selectbox("Scheme", rules["schemes"], format_func=lambda s: s["name"])
    answer = checklist_eligible(scheme, profile)
    st.write("**Checklist answer:** " + ("Yes" if answer else "No"))
