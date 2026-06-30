import streamlit as st
import os
from docx import Document
import requests
from datetime import datetime
import re

st.set_page_config(page_title="AI销售增长诊断助手", layout="wide")

st.title("🧠 AI销售增长诊断助手")
st.markdown("**填写问卷后自动生成销售增长诊断报告**")

# Questionnaire (same as before)
questions = { ... }  # (保持不变，省略以节省空间)

# Demo data (same)
demo_data = { ... }  # (保持不变)

# Form (same)
with st.form("questionnaire_form"):
    # ... (保持不变)

if submitted:
    questionnaire_data = "\n".join([f"{q}: {answers[q]}" for q in answers if answers[q]])
    
    try:
        prompt_doc = Document('/home/workdir/attachments/销售 tbs-prompt.docx')
        system_prompt = "\n".join([p.text for p in prompt_doc.paragraphs if p.text.strip()])
    except Exception:
        system_prompt = "你是一名企业销售增长诊断顾问。请基于用户提供的问卷答案，严格按照指定结构输出一份专业的《销售增长诊断报告与90天改进方案》。"
    
    full_prompt = f"{system_prompt}\n\n用户问卷答案：\n{questionnaire_data}\n\n请严格按照报告结构输出完整的诊断报告。"
    
    with st.spinner("生成诊断报告中..."):
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            st.error("API Key not configured.")
        else:
            try:
                response = requests.post(
                    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": "qwen-turbo",
                        "input": {"messages": [{"role": "system", "content": "你是一名专业的销售增长诊断顾问。"}, {"role": "user", "content": full_prompt}]},
                        "parameters": {"result_format": "message"}
                    }
                )
                if response.status_code == 200:
                    result = response.json()
                    report = result['output']['choices'][0]['message']['content']
                    
                    # Clean report: remove header and footer as requested
                    report = re.sub(r'销售增长诊断报告与90天改进方案.*?报告日期.*?\n\n', '', report, flags=re.DOTALL | re.IGNORECASE)
                    report = re.sub(r'顾问签名：.*?(日期：.*?)?$', '', report, flags=re.DOTALL | re.IGNORECASE)
                    
                    st.success("报告生成完成！")
                    st.markdown(report)
                    
                    # Download
                    company_name = answers.get("企业名称", "企业").replace(" ", "_").replace("/", "_")
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                    filename = f"{company_name}_销售诊断报告_{timestamp}.md"
                    
                    st.download_button(
                        label="📥 下载完整报告",
                        data=report,
                        file_name=filename,
                        mime="text/markdown"
                    )
                else:
                    st.error(f"API Error")
            except Exception as e:
                st.error(f"生成失败: {str(e)}")

st.sidebar.markdown("### 使用说明")
st.sidebar.info("填写问卷后生成报告。\n报告已去除顶部企业信息栏和底部签名栏。")
