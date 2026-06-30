import streamlit as st
from openai import OpenAI
from docx import Document
import datetime
import os
import requests

# =========================
# 页面配置
# =========================
st.set_page_config(
    page_title="AI销售增长诊断助手",
    page_icon="📈",
    layout="wide"
)

# =========================
# 从GitHub加载data目录文件
# =========================
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/yinyao41/Company_sale/main/data"

@st.cache_data(ttl=3600)
def load_github_file(filename):
    url = f"{GITHUB_RAW_BASE}/{filename}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return f"[文件加载失败: {filename} - {str(e)}]"

# 预加载data目录下的参考文件（供AI使用）
def load_reference_docs():
    files = {
        "prompt":    "销售 tbs-prompt.docx",
        "questionnaire": "tbs-销售 问卷.docx",
        "scoring":   "tbs-销售 评分规则表.docx",
        "demo":      "tbs销售-demo 报告.docx",
    }
    # 直接用requests下载docx二进制并用python-docx解析
    docs = {}
    for key, filename in files.items():
        url = f"{GITHUB_RAW_BASE}/{filename}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            import io
            doc = Document(io.BytesIO(resp.content))
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            docs[key] = text
        except Exception as e:
            docs[key] = f"[加载失败: {str(e)}]"
    return docs

# =========================
# API KEY 获取
# =========================
def get_api_key():
    # 方式1：Streamlit Secrets
    try:
        key = st.secrets.get("QWEN_API_KEY", None)
        if key:
            return key
    except Exception:
        pass
    # 方式2：环境变量
    try:
        key = os.environ.get("QWEN_API_KEY", None)
        if key:
            return key
    except Exception:
        pass
    return None

api_key = get_api_key()

if not api_key:
    st.error("⚠️ 未检测到 API Key，请确认 Streamlit Cloud → Settings → Secrets 中已添加：\n\nQWEN_API_KEY = \"sk-xxxxxxxx\"")
    # 调试信息（确认后可删除）
    try:
        st.info(f"当前 Secrets 中的 keys：{list(st.secrets.keys())}")
    except Exception as e:
        st.info(f"Secrets 读取异常：{str(e)}")
    st.stop()

# =========================
# 页面标题
# =========================
st.title("📈 AI销售增长诊断助手")
st.markdown("**填写问卷后自动生成销售增长诊断报告**")

# =========================
# 企业信息表单（完整问卷）
# =========================
with st.form("diagnosis_form"):

    st.subheader("一、企业基本情况")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("企业名称 *")
        industry = st.selectbox("所属行业 *", [
            "工业制造", "企业服务 / SaaS", "医疗器械 / 医疗服务",
            "消费品", "半导体 / 硬科技", "建筑 / 工程 / 设备",
            "教育培训", "咨询服务", "其他"
        ])
        product_desc = st.text_input("公司主要产品或服务是什么？")
    with col2:
        revenue = st.selectbox("当前年收入规模", [
            "500万元以下", "500万–1000万元", "1000万–3000万元",
            "3000万–1亿元", "1亿–3亿元", "3亿元以上", "不方便透露"
        ])
        avg_price = st.selectbox("产品/服务平均客单价", [
            "1万元以下", "1万–5万元", "5万–20万元",
            "20万–50万元", "50万–100万元", "100万元以上", "不清楚"
        ])

    st.subheader("二、客户与市场")
    col3, col4 = st.columns(2)
    with col3:
        customer_type = st.multiselect("主要客户类型（可多选）", [
            "大型企业", "中小企业", "政府 / 事业单位",
            "经销商 / 代理商", "个人消费者", "工厂 / 制造企业",
            "医院 / 学校 / 园区等机构", "其他"
        ])
        customer_industry = st.text_input("最主要的客户来自哪些行业？")
    with col4:
        customer_profile = st.selectbox("是否形成清晰的目标客户画像？", [
            "非常清晰，知道重点卖给谁",
            "大致清楚，但还不够聚焦",
            "不太清楚，什么客户都想做",
            "基本没有客户画像"
        ])
        easy_customer = st.text_input("最容易成交的客户有什么共同特征？")

    st.subheader("三、获客渠道")
    col5, col6 = st.columns(2)
    with col5:
        lead_channel = st.multiselect("主要获客渠道（可多选）", [
            "老板个人资源", "老客户转介绍", "销售主动开发",
            "展会 / 行业会议", "经销商 / 代理商", "线上投放",
            "短视频 / 公众号 / 内容获客", "政府 / 园区 / 协会资源",
            "合作伙伴推荐", "电话 / 邮件 / 陌拜", "其他"
        ])
        best_channel = st.text_input("当前最有效的获客渠道是什么？为什么？")
    with col6:
        lead_count = st.selectbox("每月新增客户线索数量", [
            "10条以下", "10–30条", "30–100条", "100条以上", "没有统计"
        ])
        lead_difficulty = st.multiselect("当前获客最大困难（可多选）", [
            "线索数量少", "线索质量差", "获客成本高", "客户不信任",
            "品牌知名度低", "不知道该找谁", "销售主动开发能力弱",
            "老板资源用完后增长乏力", "其他"
        ])

    st.subheader("四、销售转化")
    col7, col8 = st.columns(2)
    with col7:
        sales_cycle = st.selectbox("平均销售周期", [
            "1周以内", "1周–1个月", "1–3个月",
            "3–6个月", "6个月以上", "不清楚"
        ])
        sales_process = st.selectbox("是否有明确的销售流程？", [
            "有标准流程，销售都按流程执行",
            "有大致流程，但执行不统一",
            "主要靠销售个人经验",
            "基本没有流程"
        ])
    with col8:
        stuck_stage = st.multiselect("销售过程最容易卡在哪个环节？（可多选）", [
            "找不到合适客户", "客户愿意见面但不推进", "需求沟通不清楚",
            "报价后客户不回复", "客户觉得价格高", "决策链条复杂",
            "竞争对手截单", "合同流程慢", "回款慢", "其他"
        ])
        lost_reason = st.text_input("客户最终不成交，最常见的原因是什么？")

    st.subheader("五、销售团队与管理")
    col9, col10 = st.columns(2)
    with col9:
        team_size = st.selectbox("目前有多少名销售人员？", [
            "0–2人", "3–5人", "6–10人", "11–30人", "30人以上"
        ])
    with col10:
        sales_dependency = st.selectbox("当前销售主要依赖谁？", [
            "主要依赖老板", "主要依赖销售负责人",
            "主要依赖少数核心销售", "销售团队整体比较均衡",
            "主要依赖渠道代理"
        ])

    st.subheader("六、当前问题与目标")
    bottleneck = st.text_area(
        "当前销售增长最大的瓶颈是什么？未来90天最希望改善什么？",
        height=120,
        placeholder="请从客户定位、线索数量、成交率、销售周期、销售团队、销售管理、渠道代理、价格竞争、回款等角度描述……"
    )

    submitted = st.form_submit_button("🚀 生成诊断报告", type="primary", use_container_width=True)

# =========================
# 生成报告
# =========================
if submitted:
    if not company_name.strip():
        st.error("请输入企业名称")
        st.stop()

    with st.spinner("正在加载参考文件并生成诊断报告，请稍候（约30–60秒）..."):
        try:
            # 加载GitHub data目录参考文件
            ref_docs = load_reference_docs()
            prompt_template = ref_docs.get("prompt", "")
            scoring_rules   = ref_docs.get("scoring", "")
            demo_report     = ref_docs.get("demo", "")

            client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )

            system_prompt = f"""
{prompt_template}

以下是评分规则（请严格按此规则对企业销售成熟度打分）：
{scoring_rules}

以下是一份示例报告供参考（格式和深度对标此报告）：
{demo_report}
"""

            user_content = f"""
请根据以下企业填写的问卷信息，生成一份《销售增长诊断报告与90天改进方案》：

【企业基本情况】
企业名称：{company_name}
所属行业：{industry}
主要产品/服务：{product_desc if product_desc else "未填写"}
年收入规模：{revenue}
平均客单价：{avg_price}

【客户与市场】
主要客户类型：{", ".join(customer_type) if customer_type else "未选择"}
主要客户行业：{customer_industry if customer_industry else "未填写"}
客户画像清晰度：{customer_profile}
易成交客户特征：{easy_customer if easy_customer else "未填写"}

【获客渠道】
主要获客渠道：{", ".join(lead_channel) if lead_channel else "未选择"}
最有效渠道及原因：{best_channel if best_channel else "未填写"}
每月新增线索：{lead_count}
获客最大困难：{", ".join(lead_difficulty) if lead_difficulty else "未选择"}

【销售转化】
平均销售周期：{sales_cycle}
销售流程情况：{sales_process}
最容易卡住环节：{", ".join(stuck_stage) if stuck_stage else "未选择"}
不成交最常见原因：{lost_reason if lost_reason else "未填写"}

【销售团队与管理】
销售人员数量：{team_size}
销售主要依赖：{sales_dependency}

【当前问题与目标】
销售增长最大瓶颈 / 90天希望改善：{bottleneck if bottleneck else "未填写"}

请按照以下结构输出完整报告：
1. 企业销售画像
2. 核心诊断结论（每条含：问题/原因/影响/建议）
3. 销售成熟度评分（总分100分，按评分规则打分并说明理由）
4. 主要销售瓶颈排序
5. 分项诊断分析（客户定位 / 获客能力 / 销售转化 / 团队能力 / 管理体系）
6. 90天行动方案（第1–30天 / 第31–60天 / 第61–90天，每阶段含：核心目标、关键动作、负责人建议、执行频率、交付物）
7. 老板必须盯住的5个核心指标
8. 不建议立即做的事情
9. 后续需要补充的信息
"""

            response = client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_content}
                ],
                max_tokens=4000
            )

            report = response.choices[0].message.content

            st.success("✅ 诊断报告生成成功！")
            st.markdown("---")
            st.markdown(report)

            # Word导出
            doc = Document()
            doc.add_heading(f"{company_name} 销售增长诊断报告", level=1)
            doc.add_paragraph(f"生成日期：{datetime.date.today()}")
            doc.add_paragraph("")
            for line in report.split("\n"):
                if line.startswith("# "):
                    doc.add_heading(line[2:], level=1)
                elif line.startswith("## "):
                    doc.add_heading(line[3:], level=2)
                elif line.startswith("### "):
                    doc.add_heading(line[4:], level=3)
                else:
                    doc.add_paragraph(line)

            filename = f"{company_name}_销售诊断报告_{datetime.date.today()}.docx"
            doc.save(filename)

            with open(filename, "rb") as f:
                st.download_button(
                    label="📥 下载Word报告",
                    data=f,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"生成失败：{str(e)}")

st.markdown("---")
st.caption("Powered by 阿里千问 Qwen + Streamlit | 数据来源：GitHub yinyao41/Company_sale")
