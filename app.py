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
    # 根据您GitHub中的实际文件名
    demo_path = os.path.join(DATA_DIR, "tbs销售-demo 报告.docx")
    
    if os.path.exists(demo_path):
        try:
            doc = Document(demo_path)
            text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            st.success("✅ 已成功加载 Demo 报告模板")
            return text[:8000]  # 取前8000字符作为参考
        except Exception as e:
            st.warning(f"Demo报告读取失败: {e}")
            return "Demo报告读取失败"
    else:
        st.error("❌ 未找到 tbs销售-demo 报告.docx，请确认文件已上传到 data/ 目录")
        return "Demo报告未找到"

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
    
    industry = st.text_input("所属行业*", placeholder="例如：工业制造 / 体育产业")
    
    description = st.text_area(
        "公司当前情况描述*", 
        placeholder="描述公司规模、问题、优势、核心业务、渠道、品牌、销售痛点等...",
        height=220
    )
    
    submitted = st.form_submit_button("🚀 生成诊断报告", type="primary", use_container_width=True)

if submitted:
    if not api_key or not company_name or not industry or not description:
        st.error("请填写完整信息")
    else:
        with st.spinner("正在调用阿里千问生成专业报告..."):
            try:
                import dashscope
                dashscope.api_key = api_key
                
                prompt = f"""
你是一名专业销售增长诊断顾问，请严格模仿以下Demo报告的结构、语气和专业度：

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
5. 分项诊断分析（客户定位、获客能力、销售转化、销售团队、增长问题识别）
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
                
                # 生成并下载Word
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
                st.error(f"生成失败: {str(e)}")

st.caption("已读取 data/ 目录文件 | Powered by 阿里千问")
