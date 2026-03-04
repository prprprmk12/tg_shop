import streamlit as st
import sqlite3
import json
import streamlit.components.v1 as components
from datetime import datetime

# --- Инициализация БД ---
def init_db():
    conn = sqlite3.connect('shop_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      items TEXT, total REAL, date TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- Дизайн и Стили ---
st.set_page_config(page_title="TG Mini App Shop", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f2f2f7; }
    .product-card {
        background: white; padding: 20px; border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center;
        margin-bottom: 20px; border: 1px solid #e5e5e7;
    }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3em;
        background-color: #007aff; color: white; border: none; font-weight: 600;
    }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- Данные о товарах ---
PRODUCTS = [
    {"id": 1, "name": "iPhone 15 Pro", "price": 110000, "icon": "📱"},
    {"id": 2, "name": "MacBook Air M2", "price": 145000, "icon": "💻"},
    {"id": 3, "name": "iPad Pro", "price": 90000, "icon": "平板"},
]

if 'cart' not in st.session_state:
    st.session_state.cart = {}

# --- Витрина ---
st.title("🍎 iStore Mini")

cols = st.columns(2)
for i, p in enumerate(PRODUCTS):
    with cols[i % 2]:
        st.markdown(f"""<div class='product-card'>
            <div style='font-size:50px'>{p['icon']}</div>
            <h3>{p['name']}</h3>
            <h4 style='color:#007aff'>{p['price']:,} ₽</h4>
        </div>""", unsafe_allow_html=True)
        if st.button(f"В корзину", key=f"p_{p['id']}"):
            st.session_state.cart[p['id']] = st.session_state.cart.get(p['id'], 0) + 1
            st.toast(f"Добавлено: {p['name']}")

# --- Корзина и Оплата ---
if st.session_state.cart:
    st.divider()
    st.subheader("🛒 Ваш заказ")
    total_sum = 0
    items_list = []
    
    for pid, qty in st.session_state.cart.items():
        p = next(x for x in PRODUCTS if x['id'] == pid)
        sum_p = p['price'] * qty
        total_sum += sum_p
        st.write(f"**{p['name']}** x{qty} — {sum_p:,} ₽")
        items_list.append(f"{p['name']} x{qty}")

    st.write(f"### Итого: {total_sum:,} ₽")

    if st.button("💳 Оплатить и оформить"):
        # Сохранение в SQLite
        items_str = ", ".join(items_list)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (items, total, date) VALUES (?, ?, ?)",
                       (items_str, total_sum, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        
        # Отправка данных в Telegram
        order_data = json.dumps({"items": items_str, "total": total_sum})
        components.html(f"""
            <script>
                const tg = window.Telegram.WebApp;
                tg.sendData('{order_data}');
                tg.close();
            </script>
        """, height=0)

# Подключение JS SDK
components.html("<script src='https://telegram.org/js/telegram-web-app.js'></script>", height=0)