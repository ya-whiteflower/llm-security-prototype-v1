import streamlit as st
import pandas as pd

from src.llm_client import OllamaLLMClient
from src.pipeline import SecurityPipeline


st.set_page_config(
    page_title="LLM Security System",
    layout="wide"
)

llm = OllamaLLMClient()
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

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Risk Level", result["input_risk"])
            st.metric("Risk Score", result["input_risk_score"])

        with col2:
            st.metric("Pipeline Status", result["status"])
            st.metric("Input Action", result["input_action"])

        with col3:
            st.metric("Semantic Score", result.get("semantic_score", 0))
            st.metric("Epsilon", result["epsilon"])

        st.markdown("---")

        st.subheader("Detected Threats")

        if result["input_detected_types"]:
            st.write("Detected threat categories:")
            st.write(result["input_detected_types"])
        else:
            st.success("No attack patterns detected.")

        st.write("Matched patterns:")
        st.write(result.get("matched_patterns", []))

        st.markdown("---")

        st.subheader("Semantic Analysis")

        semantic_detected = result.get("semantic_detected", False)

        if semantic_detected:
            st.warning("Semantic similarity detected potentially unsafe intent.")
        else:
            st.success("No high-risk semantic similarity detected.")

        col_sem1, col_sem2 = st.columns(2)

        with col_sem1:
            st.write("Semantic category:")
            st.write(result.get("semantic_category"))

            st.write("Semantic score:")
            st.write(result.get("semantic_score"))

        with col_sem2:
            st.write("Most similar attack example:")
            st.write(result.get("semantic_matched_example"))

        st.markdown("---")

        st.subheader("Privacy Protection")

        st.write("Detected entities:")
        st.write(result["privacy_detected_entities"])

        st.write("DP noise applied:")
        st.write(result["privacy_was_noised"])

        st.write("Detected numeric values:")
        st.write(result["privacy_detected_numbers"])

        st.write("Privacy parameter epsilon:")
        st.write(result["epsilon"])

        st.markdown("---")

        st.subheader("Prompt Processing")

        st.write("Original prompt:")
        st.code(result["original_prompt"])

        st.write("Sanitized prompt:")
        st.code(result["safe_prompt"])

        st.markdown("---")

        st.subheader("Final Response")

        if result["status"] in ["blocked_input", "blocked_output"]:
            st.error(result["final_response"])
        elif result["status"] == "review_required":
            st.warning(result["final_response"])
        else:
            st.success(result["final_response"])

        st.markdown("---")

        st.subheader("Technical Output")

        st.json(result)

    else:
        st.warning("Введите запрос.")