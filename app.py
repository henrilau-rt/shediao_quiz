import streamlit as st
import json
import os

st.set_page_config(page_title="《射鵰英雄傳》離線導讀互動練習", page_icon="📖", layout="wide")

DATA_DIR = "data"
CHAPTER_LIST = [
    "第一回 風雪驚變", "第二回 江南七怪", "第三回 黃沙莽莽", "第四回 黑風雙煞",
    "第五回 彎弓射鵰", "第六回 崖頂疑陣", "第七回 比武招親", "第八回 各顯神通",
    "第九回 泥犁拔舌", "第十回 冤家聚頭", "第十一回 長春服輸", "第十二回 亢龍有悔",
    "第十三回 五湖廢人", "第十四回 桃花島主", "第十五回 神龍擺尾", "第十六回 九陰真經",
    "第十七回 雙手互搏", "第十八回 三道試題", "第十九回 洪濤群鯊", "第二十回 竄謊洽客",
    "第二十一回 千鈞巨岩", "第二十二回 騎鯊碰到", "第二十三回 大鬧禁宮", "第二十四回 密室療傷",
    "第二十五回 荒村野店", "第二十六回 新盟舊約", "第二十七回 軒轅台前", "第二十八回 鐵掌峰頂",
    "第二十九回 黑沼隱女", "第三十回 一燈大師", "第三十一回 鴛鴦錦帕", "第三十二回 湍石激流",
    "第三十三回 來日大難", "第三十四回 島上巨變", "第三十五回 鐵槍廟中", "第三十六回 大軍西征",
    "第三十七回 從天而降", "第三十八回 錦囊密令", "第三十九回 是非善惡", "第四十回 華山論劍"
]

# 初始化作答狀態
if "active_quiz" not in st.session_state:
    st.session_state.active_quiz = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False

def load_chapter_json(idx):
    path = os.path.join(DATA_DIR, f"chapter_{idx:02d}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def sample_progression(questions, target_n, allowed_types):
    """按情節時間線等距抽題：從題庫均勻抽樣 N 題，保持頭中尾推進"""
    filtered = [q for q in questions if q.get("type") in allowed_types]
    if len(filtered) <= target_n:
        return filtered
    step = (len(filtered) - 1) / (target_n - 1)
    indices = sorted(list(set(round(i * step) for i in range(target_n))))
    while len(indices) < target_n:
        for i in range(len(filtered)):
            if i not in indices:
                indices.append(i)
                break
        indices.sort()
    return [filtered[i] for i in indices]

# --- 側邊欄控制 ---
with st.sidebar:
    st.header("⚙️ 練習設定")
    ch_idx = st.selectbox("選擇章節（共 40 回）", range(1, 41), format_func=lambda x: CHAPTER_LIST[x-1])
    target_count = st.slider("題目數量（最多 25 題）", min_value=3, max_value=25, value=5)
    
    use_mc = st.checkbox("選擇題", value=True)
    use_blank = st.checkbox("填充題", value=True)
    
    allowed_types = []
    if use_mc: allowed_types.append("multiple_choice")
    if use_blank: allowed_types.append("fill_in_the_blank")
    
    start_btn = st.button("🚀 開始章節導讀", type="primary", use_container_width=True)

# --- 主畫面 ---
st.title("🏹 《射鵰英雄傳》離線互動練習系統")

if start_btn:
    if not allowed_types:
        st.error("請至少勾選一種題目類型！")
    else:
        data = load_chapter_json(ch_idx)
        if not data:
            st.warning(f"⚠️ 找不到 `data/chapter_{ch_idx:02d}.json`。請先將該回的題目 JSON 檔放入 `data/` 目錄中。")
            st.session_state.active_quiz = []
        else:
            qs = sample_progression(data.get("questions", []), target_count, allowed_types)
            st.session_state.active_quiz = qs
            st.session_state.user_answers = {}
            st.session_state.submitted = False
            st.session_state.current_title = data.get("chapter_name", CHAPTER_LIST[ch_idx-1])

# 顯示題目
if st.session_state.active_quiz:
    st.subheader(f"📖 當前篇章：{st.session_state.current_title}")
    st.caption(f"由題庫中依情節先後抽樣出 **{len(st.session_state.active_quiz)} 條** 推進題目：")

    with st.form("quiz_form"):
        for i, q in enumerate(st.session_state.active_quiz, 1):
            st.markdown(f"#### 📍 節點 {i}/{len(st.session_state.active_quiz)}：{q['plot_checkpoint']}")
            st.write(f"**第 {i} 題：** {q['question']}")

            if q["type"] == "multiple_choice":
                opts = q["options"]
                cur = st.session_state.user_answers.get(i, None)
                ans = st.radio(f"選擇答案（第 {i} 題）", opts, key=f"mc_{i}", index=None if cur is None else opts.index(cur))
                if ans:
                    st.session_state.user_answers[i] = ans
            else:
                cur = st.session_state.user_answers.get(i, "")
                ans = st.text_input(f"請在空格填入答案（第 {i} 題）", value=cur, key=f"blank_{i}", placeholder="輸入詞語...")
                st.session_state.user_answers[i] = ans
            st.write("---")

        if st.form_submit_button("📝 提交批改", type="primary", use_container_width=True):
            st.session_state.submitted = True

    # 批改與解讀
    if st.session_state.submitted:
        score = 0
        total = len(st.session_state.active_quiz)
        st.subheader("📊 練習結果與情節解析")

        for i, q in enumerate(st.session_state.active_quiz, 1):
            user_val = st.session_state.user_answers.get(i, "")
            correct_val = q["answer"].strip()
            is_correct = False

            if q["type"] == "multiple_choice":
                if user_val and user_val.startswith(correct_val):
                    is_correct = True
            else:
                if user_val.strip().lower() == correct_val.lower():
                    is_correct = True

            if is_correct:
                score += 1
                st.success(f"✅ 第 {i} 題【正確】({q['plot_checkpoint']})")
            else:
                st.error(f"❌ 第 {i} 題【錯誤】({q['plot_checkpoint']})")
                st.write(f"- 你的回答：`{user_val if user_val else '未作答'}`")
                st.write(f"- 正確答案：**`{correct_val}`**")

            with st.expander(f"🔍 查看第 {i} 題原著情節解析"):
                st.write(q["explanation"])

        st.metric("🎯 最終成績", f"{score} / {total} 分 ({int(score/total*100)}%)")
        if score == total:
            st.balloons()