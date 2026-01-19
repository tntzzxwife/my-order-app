import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 頁面設定 ---
st.set_page_config(page_title="代購智慧管理 Web", layout="wide")

# --- 檔案路徑 (在雲端會存在該平台的硬碟) ---
DATA_FILE = "customer_orders_web.csv"

# --- 初始化資料夾 ---
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["登記時間", "IG帳號", "商品", "貨源", "匯率", "成本(RMB)", "成本(TWD)", "售價(TWD)", "利潤(TWD)", "狀態", "備註"])
    df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

# 讀取資料
def load_data():
    return pd.read_csv(DATA_FILE, encoding="utf-8-sig").fillna("")

# 儲存資料
def save_data(df):
    df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

# --- 側邊欄：新增訂單 ---
st.sidebar.header("📝 新增訂單")
with st.sidebar.form("order_form", clear_on_submit=True):
    ig = st.text_input("IG 帳號")
    prod = st.text_input("商品名稱")
    source = st.text_input("貨源")
    rate = st.number_input("匯率", value=4.5, step=0.01)
    cost_rmb = st.number_input("成本 (RMB)", value=0.0)
    price_twd = st.number_input("售價 (TWD)", value=0)
    note = st.text_area("備註")
    shipped = st.checkbox("已出貨")
    
    submit = st.form_submit_button("💾 儲存訂單")
    
    if submit:
        if ig and prod:
            df = load_data()
            cost_twd = round(cost_rmb * rate)
            new_row = {
                "登記時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "IG帳號": ig, "商品": prod, "貨源": source, "匯率": rate,
                "成本(RMB)": cost_rmb, "成本(TWD)": cost_twd, "售價(TWD)": price_twd,
                "利潤(TWD)": price_twd - cost_twd,
                "狀態": "已出貨" if shipped else "未出貨",
                "備註": note
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("儲存成功！")
        else:
            st.error("帳號與商品不能空白")

# --- 主畫面：搜尋與管理 ---
st.title("📦 代購訂單管理系統")

df = load_data()

# 搜尋功能
search_query = st.text_input("🔍 搜尋帳號、商品或備註", "")
if search_query:
    df_display = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
else:
    df_display = df

# 顯示表格
st.subheader("📋 訂單清單")

# 狀態顏色標記 (未出貨顯示紅色)
def color_status(val):
    color = 'red' if val == "未出貨" else 'black'
    return f'color: {color}'

if not df_display.empty:
    st.dataframe(df_display.style.applymap(color_status, subset=['狀態']), use_container_width=True)
    
    # 批次操作區
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        target_ig = st.selectbox("選擇要操作的 IG 帳號", [""] + list(df_display["IG帳號"].unique()))
        new_status = st.radio("變更狀態為：", ["已出貨", "未出貨"], horizontal=True)
        if st.button("更新狀態"):
            if target_ig:
                df.loc[df['IG帳號'] == target_ig, '狀態'] = new_status
                save_data(df)
                st.rerun()
    
    with col2:
        st.write("🗑️ 刪除功能")
        if st.button("刪除搜尋到的所有訂單"):
            df = df.drop(df_display.index)
            save_data(df)
            st.rerun()
else:
    st.info("目前沒有資料。")