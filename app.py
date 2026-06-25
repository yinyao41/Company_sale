import streamlit as st
from docx import Document
import datetime
import os
from utils.report_generator import generate_report_with_qwen

st.set_page_config(page_title="销售诊断工具", layout="centered", page_icon="📊")

st.title("销售增长诊断报告生成器")
st.markdown("**阿里千问大模型驱动** | 参考TBS销售诊断体系")

# ==================== 加载 data 目录文件 ====================
DATA_DIR = "data"

def load_demo_report():
    demo_path = os.path.join(DATA_DIR, "tbs销售-demo 报告.docx")
    if os.path.exists(demo_path):
        try:
            doc = Document(demo_path)
            text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            return text[:7000]
        except:
            return "Demo报告加载失败"
    return "未找到Demo报告"

demo_template = load_demo_report()

# ==================== 表单 ====================
with st.form("company_form"):
    st.subheader("基本信息")
    company_name = st.text_input("公司名称*", placeholder="例如：山东固丰体育产业有限公司")
    
    industry = st.text_input("所属行业*", placeholder="例如：体育产业 / 工业制造 / 建筑业")
    
    description = st.text_area(
        "公司当前情况描述*", 
        placeholder="描述公司规模、问题、优势、核心业务、渠道、品牌、销售痛点等...",
        height=220
    )
    
    st.info("✅ 系统已自动读取 data/ 目录下的TBS诊断文件作为模板参考")
    
    submitted = st.form_submit_button("🚀 生成诊断报告", use_container_width=True, type="primary")

if submitted:
    if not company_name or not industry or not description:
        st.error("请填写公司名称、所属行业和当前情况描述")
    else:
        with st.spinner("正在调用阿里千问生成专业报告..."):
            try:
                report_text = generate_report_with_qwen(
                    company_name=company_name,
                    industry=industry,
                    description=description,
                    demo_template=demo_template
                )
                
                st.success("报告生成成功！")
                
                st.markdown("### 📋 报告预览")
                st.markdown(report_text)
                
                # 生成Word
                doc = Document()
                doc.add_heading(f"《{company_name}销售增长诊断报告与90天改进方案》", 0)
                doc.add_paragraph(report_text)
                
                filename = f"{company_name}_销售诊断报告_{datetime.date.today()}.docx"
                doc.save(filename)
                
                with open(filename, "rb") as f:
                    st.download_button(
                        label="📥 下载完整Word报告",
                        data=f,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"生成失败: {str(e)}\n请检查 Secrets 中 QWEN_API_KEY 是否正确配置")

st.caption("Powered by  | 数据文件已从 data/ 目录读取")
