import streamlit as st
from openai import OpenAI
import os
import datetime
from docx import Document

# =========================

# 页面配置

# =========================

st.set_page_config(
page_title="AI销售增长诊断助手",
page_icon="📈",
layout="wide"
)

st.title("📈 AI销售增长诊断助手")
st.markdown("### 填写企业信息，自动生成销售增长诊断报告与90天改进方案")

# =========================

# API KEY 获取

# =========================

def get_api_key():

```
try:
    key = st.secrets["QWEN_API_KEY"]
    if key:
        return key
except:
    pass

key = os.getenv("QWEN_API_KEY")
if key:
    return key

return None
```

api_key = get_api_key()

# =========================

# API状态

# =========================

with st.expander("🔧 API配置状态"):

```
try:
    st.write("Secrets Keys:")
    st.write(list(st.secrets.keys()))
except Exception as e:
    st.write("Secrets未加载")
    st.write(str(e))

st.write(
    "环境变量QWEN_API_KEY：",
    "存在" if os.getenv("QWEN_API_KEY") else "不存在"
)
```

if api_key:

```
st.success("✅ 已检测到阿里千问 API")
```

else:

```
st.warning("⚠️ 未检测到 API Key")

api_key = st.text_input(
    "请输入阿里千问API Key",
    type="password",
    placeholder="sk-xxxxxxxxxxxxxxxx"
)
```

# =========================

# 企业信息表单

# =========================

with st.form("diagnosis_form"):

```
col1, col2 = st.columns(2)

with col1:

    company_name = st.text_input(
        "企业名称*",
        placeholder="例如：山东固丰体育产业有限公司"
    )

    industry = st.selectbox(
        "所属行业*",
        [
            "工业制造",
            "建筑工程",
            "企业服务/SaaS",
            "医疗器械",
            "消费品",
            "半导体",
            "新能源",
            "其他"
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

with col2:

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
            "老板个人资源",
            "老客户转介绍",
            "销售主动开发",
            "展会",
            "线上投放",
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
        "有流程但执行不统一",
        "主要靠个人经验",
        "基本没有流程"
    ]
)

sales_dependency = st.selectbox(
    "销售主要依赖",
    [
        "主要依赖老板",
        "主要依赖销售负责人",
        "主要依赖核心销售",
        "团队整体均衡"
    ]
)

bottleneck = st.text_area(
    "当前销售增长最大瓶颈",
    height=120
)

submitted = st.form_submit_button(
    "🚀 生成诊断报告",
    use_container_width=True
)
```

# =========================

# 生成报告

# =========================

if submitted:

```
if not api_key:

    st.error("未检测到阿里千问 API Key")
    st.stop()

if not company_name:

    st.error("请输入企业名称")
    st.stop()

with st.spinner("正在生成销售诊断报告..."):

    try:

        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        prompt = f"""
```

你是一名资深销售增长顾问。

请根据以下企业信息生成一份专业的：

《销售增长诊断报告与90天改进方案》

企业名称：
{company_name}

所属行业：
{industry}

年收入规模：
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

当前瓶颈：
{bottleneck}

请输出：

# 一、企业销售画像

# 二、核心诊断结论

# 三、销售成熟度评分（100分）

# 四、主要销售瓶颈排序

# 五、详细分析

* 客户定位
* 获客能力
* 销售转化
* 团队能力
* 管理体系

# 六、90天行动方案

## 第1-30天

## 第31-60天

## 第61-90天

# 七、老板必须盯住的5个指标

# 八、不建议立即做的事情

# 九、后续需要补充的信息

"""

```
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        report = response.choices[0].message.content

        st.success("✅ 诊断完成")

        st.markdown("---")
        st.markdown(report)

        # Word导出

        doc = Document()

        doc.add_heading(
            f"{company_name}销售增长诊断报告",
            level=1
        )

        doc.add_paragraph(report)

        filename = (
            f"{company_name}_销售诊断报告_"
            f"{datetime.date.today()}.docx"
        )

        doc.save(filename)

        with open(filename, "rb") as f:

            st.download_button(
                "📥 下载Word报告",
                f,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

    except Exception as e:

        st.error(f"调用失败：{str(e)}")
```

st.markdown("---")
st.caption("Powered by Qwen + Streamlit")
