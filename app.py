import streamlit as st
import pandas as pd

from src.llm_client import FakeLLMClient
from src.pipeline import SecurityPipeline


st.set_page_config(
    page_title="LLM Security System",
    layout="wide"
)

llm = FakeLLMClient()
pipeline = SecurityPipeline(llm)

st.title("LLM Security Protection System")

st.markdown(
    """
    Демонстрационный прототип системы обеспечения безопасности
    большой языковой модели.
    """
)

user_prompt = st.text_area(
    "Введите пользовательский запрос:",
    height=150
)

if st.button("Analyze Request"):

    if user_prompt.strip():

        result = pipeline.process(user_prompt)

        st.subheader("Security Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Risk Level", result["input_risk"])
            st.metric("Risk Score", result["input_risk_score"])

        with col2:
            st.metric("Pipeline Status", result["status"])
            st.metric("Epsilon", result["epsilon"])

        st.markdown("---")

        st.subheader("Detected Threats")

        if result["input_detected_types"]:
            st.write(result["input_detected_types"])
        else:
            st.success("No attack patterns detected.")

        st.subheader("Privacy Protection")

        st.write("Detected entities:")
        st.write(result["privacy_detected_entities"])

        st.write("DP noise applied:")
        st.write(result["privacy_was_noised"])

        st.write("Detected numeric values:")
        st.write(result["privacy_detected_numbers"])

        st.markdown("---")

        st.subheader("Prompt Processing")

        st.write("Original prompt:")
        st.code(result["original_prompt"])

        st.write("Sanitized prompt:")
        st.code(result["safe_prompt"])

        st.markdown("---")

        st.subheader("Final Response")

        st.success(result["final_response"])

        st.markdown("---")

        st.subheader("Technical Output")

        st.json(result)

    else:
        st.warning("Введите запрос.")
