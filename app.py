import streamlit as st
from openai import OpenAI

# =========================
# 页面配置
# =========================

st.set_page_config(
    page_title="AI销售增长诊断",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI销售增长诊断助手")
st.markdown("填写问卷后自动生成销售增长诊断报告")

# =========================
# API Key
# =========================

api_key = st.sidebar.text_input(
    "请输入阿里千问 API KEY",
    type="password"
)

# =========================
# 企业信息
# =========================

company_name = st.text_input("企业名称")

industry = st.selectbox(
    "所属行业",
    [
        "工业制造",
        "企业服务/SaaS",
        "医疗器械",
        "消费品",
        "半导体",
        "建筑工程",
        "教育培训",
        "咨询服务"
    ]
)

revenue = st.selectbox(
    "年收入规模",
    [
        "500万以下",
        "500-1000万",
        "1000-3000万",
        "3000万-1亿",
        "1-3亿",
        "3亿以上"
    ]
)

customer_profile = st.selectbox(
    "客户画像是否清晰",
    [
        "非常清晰",
        "大致清楚",
        "不太清楚",
        "基本没有"
    ]
)

lead_channel = st.multiselect(
    "主要获客渠道",
    [
        "老板资源",
        "老客户转介绍",
        "销售主动开发",
        "展会",
        "线上投放",
        "内容营销",
        "合作伙伴推荐"
    ]
)

lead_count = st.selectbox(
    "每月新增线索",
    [
        "10条以下",
        "10-30条",
        "30-100条",
        "100条以上"
    ]
)

sales_process = st.selectbox(
    "销售流程情况",
    [
        "标准流程",
        "有流程但不统一",
        "靠个人经验",
        "没有流程"
    ]
)

sales_dependency = st.selectbox(
    "销售主要依赖",
    [
        "老板",
        "销售负责人",
        "核心销售",
        "团队"
    ]
)

bottleneck = st.text_area(
    "当前销售增长最大瓶颈"
)

# =========================
# AI诊断
# =========================

if st.button("生成诊断报告"):

    if not api_key:
        st.error("请输入阿里云DashScope API Key")
        st.stop()

    prompt = f"""
你是一位顶级销售增长顾问。

请根据以下企业信息：

企业名称：
{company_name}

行业：
{industry}

收入规模：
{revenue}

客户画像：
{customer_profile}

获客渠道：
{lead_channel}

新增线索：
{lead_count}

销售流程：
{sales_process}

销售依赖：
{sales_dependency}

销售瓶颈：
{bottleneck}

请按照以下格式输出：

# 一、销售增长成熟度判断

# 二、五大维度评分

客户定位：
获客能力：
销售转化：
团队复制：
增长问题识别：

# 三、三个核心问题

# 四、90天行动计划

第一阶段（1-30天）

第二阶段（31-60天）

第三阶段（61-90天）

# 五、CEO建议
"""

    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    with st.spinner("正在生成诊断报告..."):

        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {
                    "role": "system",
                    "content": "你是一名销售增长咨询顾问"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        report = response.choices[0].message.content

        st.success("诊断完成")

        st.markdown(report)
