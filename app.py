import streamlit as st
import os
from docx import Document
import requests
from datetime import datetime
import re

st.set_page_config(page_title="AI销售增长诊断助手", layout="wide")

# multiselect 标签：白底灰边深色字
st.markdown("""
<style>
span[data-baseweb="tag"] {
    background-color: #F5F5F5 !important;
    border: 1px solid #CCCCCC !important;
    border-radius: 4px !important;
}
span[data-baseweb="tag"] span {
    color: #333333 !important;
}
span[data-baseweb="tag"] svg {
    fill: #666666 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 AI销售增长诊断助手")
st.markdown("**填写问卷后自动生成销售增长诊断报告**")

questions = {
    "企业名称": {"type": "text"},
    "所属行业": {"type": "select", "options": ["工业制造", "企业服务 / SaaS", "医疗器械 / 医疗服务", "消费品", "半导体 / 硬科技", "建筑 / 工程 / 设备", "教育培训", "咨询服务", "其他"]},
    "公司主要产品或服务是什么？": {"type": "text"},
    "当前年收入规模大概是多少？": {"type": "select", "options": ["500万元以下", "500万–1000万元", "1000万–3000万元", "3000万–1亿元", "1亿–3亿元", "3亿元以上", "不方便透露"]},
    "产品或服务的平均客单价大概是多少？": {"type": "select", "options": ["1万元以下", "1万–5万元", "5万–20万元", "20万–50万元", "50万–100万元", "100万元以上", "不清楚"]},
    "公司主要客户类型是什么？": {"type": "multiselect", "options": ["大型企业", "中小企业", "政府 / 事业单位", "经销商 / 代理商", "个人消费者", "工厂 / 制造企业", "医院 / 学校 / 园区等机构"]},
    "公司目前最主要的客户来自哪些行业？": {"type": "text"},
    "公司是否已经形成清晰的目标客户画像？": {"type": "select", "options": ["非常清晰，知道重点卖给谁", "大致清楚，但还不够聚焦", "不太清楚，什么客户都想做", "基本没有客户画像"]},
    "公司目前最容易成交的客户有什么共同特征？": {"type": "text"},
    "公司目前主要通过哪些方式获得客户线索？": {"type": "multiselect", "options": ["老板个人资源", "老客户转介绍", "销售主动开发", "展会 / 行业会议", "经销商 / 代理商", "线上投放", "短视频 / 公众号 / 内容获客", "政府 / 园区 / 协会资源", "合作伙伴推荐", "电话 / 邮件 / 陌拜"]},
    "当前最有效的获客渠道是什么？为什么？": {"type": "text"},
    "公司每月大概新增多少条客户线索？": {"type": "select", "options": ["10条以下", "10–30条", "30–100条", "100条以上", "没有统计"]},
    "当前获客最大的困难是什么？": {"type": "multiselect", "options": ["线索数量少", "线索质量差", "获客成本高", "客户不信任", "品牌知名度低", "不知道该找谁", "销售主动开发能力弱", "老板资源用完后增长乏力"]},
    "从首次接触客户到最终成交，平均销售周期大概多久？": {"type": "select", "options": ["1周以内", "1周–1个月", "1–3个月", "3–6个月", "6个月以上", "不清楚"]},
    "公司是否有明确的销售流程？": {"type": "select", "options": ["有标准流程，销售都按流程执行", "有大致流程，但执行不统一", "主要靠销售个人经验", "基本没有流程"]},
    "当前销售过程最容易卡在哪个环节？": {"type": "multiselect", "options": ["找不到合适客户", "客户愿意见面但不推进", "需求沟通不清楚", "报价后客户不回复", "客户觉得价格高", "决策链条复杂", "竞争对手截单", "合同流程慢", "回款慢"]},
    "客户最终不成交，最常见的原因是什么？": {"type": "text"},
    "公司目前有多少名销售人员？": {"type": "select", "options": ["0–2人", "3–5人", "6–10人", "11–30人", "30人以上"]},
    "当前销售主要依赖谁？": {"type": "select", "options": ["主要依赖老板", "主要依赖销售负责人", "主要依赖少数核心销售", "销售团队整体比较均衡", "主要依赖渠道代理"]},
    "公司当前销售增长最大的瓶颈是什么？未来90天最希望改善什么？": {"type": "text"}
}

demo_data = {
    "企业名称": "华东某某智造装备有限公司",
    "所属行业": "工业制造",
    "公司主要产品或服务是什么？": "自动化检测设备和产线改造方案，产品包括视觉检测设备、自动分拣设备和非标自动化产线升级服务",
    "当前年收入规模大概是多少？": "3000万–1亿元",
    "产品或服务的平均客单价大概是多少？": "50万–100万元",
    "公司主要客户类型是什么？": ["工厂 / 制造企业"],
    "公司目前最主要的客户来自哪些行业？": "汽车零部件、电子制造、精密五金和家电制造",
    "公司是否已经形成清晰的目标客户画像？": "大致清楚，但还不够聚焦",
    "公司目前最容易成交的客户有什么共同特征？": "收入规模较大、有自动化改造需求、人工检测成本较高、老板或生产负责人重视降本增效",
    "公司目前主要通过哪些方式获得客户线索？": ["老板个人资源", "老客户转介绍", "展会 / 行业会议", "合作伙伴推荐"],
    "当前最有效的获客渠道是什么？为什么？": "老板个人资源和老客户转介绍（质量较高）",
    "公司每月大概新增多少条客户线索？": "10条以下",
    "当前获客最大的困难是什么？": ["线索数量少", "老板资源用完后增长乏力"],
    "从首次接触客户到最终成交，平均销售周期大概多久？": "3–6个月",
    "公司是否有明确的销售流程？": "有大致流程，但执行不统一",
    "当前销售过程最容易卡在哪个环节？": ["客户愿意见面但不推进", "报价后客户不回复", "客户觉得价格高", "决策链条复杂"],
    "客户最终不成交，最常见的原因是什么？": "价格高、需求不匹配、决策链复杂",
    "公司目前有多少名销售人员？": "6–10人",
    "当前销售主要依赖谁？": "主要依赖老板",
    "公司当前销售增长最大的瓶颈是什么？未来90天最希望改善什么？": "获客机制不稳定、销售流程不标准、过度依赖老板资源"
}

with st.form("questionnaire_form"):
    st.subheader("填写企业销售诊断问卷")
    st.caption("💡 **Demo案例**：已自动填入「华东某某智造装备有限公司」示例数据。你可以直接点击「生成报告」查看效果，或修改任意字段。")
    answers = {}

    for q, config in questions.items():
        default = demo_data.get(q)
        if config["type"] == "text":
            answers[q] = st.text_input(q, value=default or "", key=q)
        elif config["type"] == "select":
            idx = config["options"].index(default) if default in config.get("options", []) else 0
            answers[q] = st.selectbox(q, config["options"], index=idx, key=q)
        elif config["type"] == "multiselect":
            default_list = default if isinstance(default, list) else []
            answers[q] = st.multiselect(q, config["options"], default=default_list, key=q)

    submitted = st.form_submit_button("🚀 生成诊断报告")

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

                    report = re.sub(r'销售增长诊断报告与90天改进方案.*?报告日期.*?\n\n', '', report, flags=re.DOTALL | re.IGNORECASE)
                    report = re.sub(r'顾问签名：.*?(日期：.*?)?\s*$', '', report, flags=re.DOTALL | re.IGNORECASE)
                    report = re.sub(r'顾问：销售增长诊断顾问', '', report, flags=re.IGNORECASE)
                    report = re.sub(r'联系方式：\[您的邮箱/电话\]', '', report, flags=re.IGNORECASE)

                    st.success("报告生成完成！")
                    st.markdown(report)

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
                    st.error(f"API Error: {response.text}")
            except Exception as e:
                st.error(f"生成失败: {str(e)}")

st.sidebar.markdown("### 使用说明")
st.sidebar.info("填写问卷后生成报告。\n该报告由大模型生成仅做参考，不构成正式建议")
