import streamlit as st
from openai import OpenAI
from docx import Document
import datetime

# =========================
# 页面配置
# =========================
st.set_page_config(
    page_title="AI销售增长诊断助手",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI销售增长诊断助手")
st.markdown("**填写企业信息，自动生成销售增长诊断报告与90天改进方案**")

# =========================
# API Key 获取（优先 Secrets）
# =========================
api_key = None
try:
    api_key = st.secrets["QWEN_API_KEY"]
except:
    pass

if not api_key:
    api_key = st.text_input(
        "🔑 请输入阿里千问 API Key",
        type="password",
        placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
    )

if not api_key:
    st.warning("⚠️ 请配置阿里千问 API Key（推荐在 Streamlit Secrets 中设置 QWEN_API_KEY）")
    st.stop()

# =========================
# 企业信息表单
# =========================
with st.form("diagnosis_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input("企业名称*", placeholder="例如：山东固丰体育产业有限公司")
        industry = st.selectbox(
            "所属行业*",
            ["工业制造", "建筑工程", "企业服务/SaaS", "医疗器械", "消费品", "半导体", "其他"]
        )
        revenue = st.selectbox(
            "年收入规模",
            ["500万以下", "500-1000万", "1000-3000万", "3000万-1亿", "1-3亿", "3亿以上"]
        )
    
    with col2:
        customer_profile = st.selectbox(
            "客户画像是否清晰",
            ["非常清晰", "大致清楚", "不太清楚", "基本没有"]
        )
        lead_channel = st.multiselect(
            "主要获客渠道",
            ["老板个人资源", "老客户转介绍", "销售主动开发", "展会", "线上投放", "合作伙伴推荐"]
        )
        lead_count = st.selectbox(
            "每月新增线索",
            ["10条以下", "10-30条", "30-100条", "100条以上"]
        )

    sales_process = st.selectbox(
        "销售流程情况",
        ["标准流程", "有流程但执行不统一", "主要靠个人经验", "基本没有流程"]
    )
    
    sales_dependency = st.selectbox(
        "销售主要依赖",
        ["主要依赖老板", "主要依赖销售负责人", "主要依赖核心销售", "团队整体均衡"]
    )
    
    bottleneck = st.text_area("当前销售增长最大瓶颈是什么？（可选）", height=100)

    submitted = st.form_submit_button("🚀 生成诊断报告", type="primary", use_container_width=True)

# =========================
# 生成报告
# =========================
if submitted:
    if not company_name.strip():
        st.error("请输入企业名称")
        st.stop()
    
    with st.spinner("正在生成专业诊断报告..."):
        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )

            prompt = f"""
你是一名专业的销售增长诊断顾问，请根据以下企业信息生成一份结构清晰、专业完整的《销售增长诊断报告与90天改进方案》：

企业名称：{company_name}
所属行业：{industry}
年收入规模：{revenue}
客户画像清晰度：{customer_profile}
主要获客渠道：{lead_channel}
每月新增线索：{lead_count}
销售流程情况：{sales_process}
销售主要依赖：{sales_dependency}
当前最大瓶颈：{bottleneck if bottleneck else "未详细说明"}

请严格按照以下结构输出（使用Markdown格式）：
1. 企业销售画像
2. 核心诊断结论（3-4条）
3. 销售成熟度评分
4. 主要销售瓶颈排序
5. 分项诊断分析（客户定位、获客能力、销售转化、销售团队、增长问题识别）
6. 90天销售改进方案（分第1-30天、第31-60天、第61-90天三个阶段）
7. 老板需要重点盯的5个指标
8. 暂不建议做的事情
9. 后续需要补充的信息
"""

            response = client.chat.completions.create(
                model="qwen-plus",
                messages=[{"role": "user", "content": prompt}]
            )

            report = response.choices[0].message.content

            st.success("✅ 诊断报告生成成功！")
            st.markdown("### 📋 诊断报告")
            st.markdown(report)

            # Word 下载
            doc = Document()
            doc.add_heading(f"《{company_name}销售增长诊断报告与90天改进方案》", 0)
            doc.add_paragraph(report)
            filename = f"{company_name}_销售诊断报告_{datetime.date.today()}.docx"
            doc.save(filename)

            with open(filename, "rb") as f:
                st.download_button(
                    label="📥 下载Word完整报告",
                    data=f,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"生成失败: {str(e)}")

st.caption("Powered by 阿里千问 Qwen")
