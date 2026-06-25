import streamlit as st
import datetime
import os

st.set_page_config(page_title="销售诊断工具", layout="centered")

st.title("🧠 销售增长诊断报告生成器")
st.markdown("**简化调试版** - 先测试能否正常运行")

# ==================== 检查 data 目录 ====================
DATA_DIR = "data"
demo_exists = False
demo_text = "Demo报告未找到"

if os.path.exists(DATA_DIR):
    demo_path = os.path.join(DATA_DIR, "tbs销售-demo 报告.docx")
    if os.path.exists(demo_path):
        demo_exists = True
        demo_text = "✅ Demo报告已加载"
    else:
        demo_text = f"❌ 找到data目录，但未找到 tbs销售-demo 报告.docx"
else:
    demo_text = "❌ 未找到 data 目录，请确认目录结构正确"

st.info(demo_text)

# ==================== 表单 ====================
with st.form("company_form"):
    st.subheader("基本信息")
    company_name = st.text_input("公司名称*", placeholder="例如：山东固丰体育产业有限公司")
    industry = st.text_input("所属行业*", placeholder="例如：工业制造")
    description = st.text_area("公司当前情况描述*", height=180, 
                               placeholder="描述公司规模、问题、优势、核心业务、销售痛点等...")
    
    api_key = st.text_input("阿里千问API Key (sk-开头)", type="password")
    
    submitted = st.form_submit_button("🚀 生成诊断报告", type="primary")

if submitted:
    if not company_name or not industry or not description or not api_key:
        st.error("请填写所有必填项")
    else:
        st.success("✅ 表单提交成功！（当前为简化版，千问调用后续添加）")
        st.info("如果能看到这条消息，说明代码基础运行正常。")
        
        # 简单报告预览
        st.markdown("### 简单报告预览")
        st.write(f"企业名称：{company_name}")
        st.write(f"所属行业：{industry}")
        st.write("报告生成逻辑已就绪，可进一步扩展。")

st.caption("当前版本 | 请确保 data/ 目录存在且包含 tbs销售-demo 报告.docx")
