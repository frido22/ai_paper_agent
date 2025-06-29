import streamlit as st
import json
from pathlib import Path

from paper_eval.pipeline.run_pipeline import _process

st.set_page_config(page_title="AI Paper Evaluator", layout="wide")

st.title("AI Paper Evaluator")

pdf_path = st.text_input("Path to PDF")
if pdf_path and Path(pdf_path).exists():
    with st.spinner("Running evaluation..."):
        result = _process(Path(pdf_path))
    st.subheader("Score: ", anchor="score")
    st.metric(label="Overall", value=result["score"])
    st.write(result["justification"])

    st.subheader("Figure support")
    support = result["fig_support"]
    for claim, ok in support.items():
        st.write(f"- {'✅' if ok else '❌'} {claim}")
else:
    st.info("Enter a valid PDF path to evaluate")
