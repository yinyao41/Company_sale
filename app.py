import streamlit as st
from docx import Document
import datetime
import os

st.set_page_config(page_title="销售诊断工具", layout="centered", page_icon="📊")

st.title("🧠 销售增长诊断报告生成器")
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
        except Exception as e:
            return f"Demo报告加载失败: {e}"
    return "未找到Demo报告（请确认 data/ 目录存在）"

demo_template = load_demo_report()

# ==================== API Key ====================
api_key = st.text_input(
    "🔑 请输入阿里千问API Key (sk-开头)", 
    type="password",
    placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
)

# ==================== 表单 ====================
with st.form("company_form"):
    st.subheader("基本信息")
    company_name = st.text_input("公司名称*", placeholder="例如：山东固丰体育产业有限公司")
    
    industry = st.text_input("所属行业*", placeholder="例如：体育产业 / 工业制造")
    
    description = st.text_area(
        "公司当前情况描述*", 
        placeholder="描述公司规模、问题、优势、核心业务、渠道、品牌、销售痛点等...",
        height=220
    )
    
    st.info(f"✅ 已加载 Demo 报告模板（{len(demo_template)} 字符）")
    
    submitted = st.form_submit_button("🚀 生成诊断报告", use_container_width=True, type="primary")

if submitted:
    if not api_key or not company_name or not industry or not description:
        st.error("❌ 请填写完整信息（API Key、公司名称、所属行业、情况描述）")
    else:
        with st.spinner("正在调用阿里千问生成报告，请稍等 15-30 秒..."):
            try:
                # 这里直接调用千问（简化版）
                import dashscope
                dashscope.api_key = api_key
                
                prompt = f"""
你是一名专业销售增长诊断顾问，请严格模仿以下Demo报告的结构和语气：

=== Demo报告参考 ===
{demo_template}
=== Demo报告结束 ===

企业名称：{company_name}
所属行业：{industry}
公司当前情况：{description}

请严格按照以下结构输出完整报告：
1. 企业销售画像
2. 核心诊断结论（3-4条）
3. 销售成熟度评分
4. 主要销售瓶颈排序
5. 分项诊断分析（5.1-5.5）
6. 90天销售改进方案（分三个阶段）
7. 老板需要重点盯的5个指标
8. 暂不建议做的事情
9. 后续需要补充的信息
"""

                response = dashscope.Generation.call(
                    model="qwen-plus",
                    prompt=prompt,
                    result_format='message'
                )
                
                report_text = response.output.choices[0].message.content
                
                st.success("✅ 报告生成成功！")
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
                st.error(f"❌ 生成失败: {str(e)}")
                st.info("常见原因：API Key错误、网络问题或data目录文件不存在")

st.caption("Powered by 阿里千问 Qwen | data/ 目录文件已读取")
