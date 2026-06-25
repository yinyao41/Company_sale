import streamlit as st
from docx import Document
import datetime
import os

st.set_page_config(page_title="TBS销售诊断", layout="centered", page_icon="📊")

st.title("🧠 TBS销售增长诊断报告生成器")
st.markdown("**阿里千问驱动** | 参考TBS销售诊断体系")

# ==================== 检查data目录 ====================
DATA_DIR = "data"
demo_text = "Demo报告未找到"

if os.path.exists(DATA_DIR):
    demo_path = os.path.join(DATA_DIR, "tbs销售-demo 报告.docx")
    if os.path.exists(demo_path):
        try:
            doc = Document(demo_path)
            demo_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])[:6000]
            st.success("✅ 已成功加载 Demo报告模板")
        except:
            st.warning("Demo报告读取失败")
    else:
        st.error("❌ 未找到 tbs销售-demo 报告.docx")
else:
    st.error("❌ 未找到 data/ 目录")

# ==================== API Key ====================
api_key = st.text_input("🔑 阿里千问API Key (sk-开头)", type="password")

# ==================== 表单 ====================
with st.form("form"):
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("公司名称*", placeholder="山东固丰体育产业有限公司")
        industry = st.text_input("所属行业*", placeholder="体育产业 / 工业制造")
    with col2:
        pass  # 留空对齐

    description = st.text_area("公司当前情况描述*", height=180,
                               placeholder="描述公司规模、问题、优势、核心业务、销售渠道、当前痛点等...")

    submitted = st.form_submit_button("🚀 生成诊断报告", type="primary", use_container_width=True)

if submitted:
    if not api_key or not company_name or not industry or not description:
        st.error("请填写完整信息")
    else:
        with st.spinner("正在调用阿里千问生成报告..."):
            try:
                import dashscope
                dashscope.api_key = api_key

                prompt = f"""
请严格模仿以下Demo报告的结构和语气，为以下企业生成一份专业诊断报告：

=== Demo参考 ===
{demo_text}
=== Demo结束 ===

企业名称：{company_name}
所属行业：{industry}
公司描述：{description}

请严格输出以下结构：
1. 企业销售画像
2. 核心诊断结论（3-4条）
3. 销售成熟度评分
4. 主要销售瓶颈排序
5. 分项诊断分析
6. 90天改进方案（分3阶段）
7. 老板重点指标
8. 暂不建议事项
9. 后续补充信息
"""

                resp = dashscope.Generation.call(
                    model="qwen-plus",
                    prompt=prompt,
                    result_format='message'
                )

                report = resp.output.choices[0].message.content

                st.success("✅ 报告生成成功！")
                st.markdown("### 报告预览")
                st.markdown(report)

                # 下载Word
                doc = Document()
                doc.add_heading(f"《{company_name}销售增长诊断报告与90天改进方案》", 0)
                doc.add_paragraph(report)
                
                filename = f"{company_name}_诊断报告_{datetime.date.today()}.docx"
                doc.save(filename)

                with open(filename, "rb") as f:
                    st.download_button("📥 下载Word报告", f, filename, use_container_width=True)

            except Exception as e:
                st.error(f"生成失败: {str(e)}")
                st.info("常见原因：API Key错误 或 data目录文件不存在")

st.caption("GitHub: Company_sale | data/ 目录已读取")
