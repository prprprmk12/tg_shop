import streamlit as st
import sqlite3
from datetime import datetime
import streamlit.components.v1 as components
import json

# --- ИНИЦИАЛИЗАЦИЯ БД ---
def init_db():
    conn = sqlite3.connect('shop_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id TEXT, items TEXT, total REAL, date TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- КОНФИГУРАЦИЯ И ДИЗАЙН ---
st.set_page_config(page_title="TG Shop", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f7f9fb; }
    .product-card {
        background: white; padding: 20px; border-radius: 24px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05); text-align: center;
        margin-bottom: 15px; border: 1px solid #eee;
    }
    .stButton>button {
        width: 100%; border-radius: 15px; height: 3.5em;
        background-color: #0088cc; color: white; border: none; font-weight: bold;
    }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_status=True)

# --- ДАННЫЕ ---
PRODUCTS = [
    {"id": 1, "name": "iPhone 15", "price": 95000, "emoji": "📱"},
    {"id": 2, "name": "AirPods 3", "price": 18000, "emoji": "🎧"},
    {"id": 3, "name": "Apple Watch", "price": 45000, "emoji": "⌚"},
]

if 'cart' not in st.session_state:
    st.session_state.cart = {}

# --- ИНТЕРФЕЙС ---
st.title("🍏 Apple Store")

cols = st.columns(2)
for i, p in enumerate(PRODUCTS):
    with cols[i % 2]:
        st.markdown(f"""<div class='product-card'>
            <div style='font-size:40px'>{p['emoji']}</div>
            <b>{p['name']}</b><br><span style='color:#0088cc'>{p['price']:,} ₽</span>
        </div>""", unsafe_allow_status=True)
        if st.button(f"Купить", key=f"p_{p['id']}"):
            st.session_state.cart[p['id']] = st.session_state.cart.get(p['id'], 0) + 1
            st.toast(f"Добавлено: {p['name']}")

# --- КОРЗИНА ---
if st.session_state.cart:
    st.divider()
    st.subheader("🛒 Ваша корзина")
    total = 0
    summary = []
    for pid, qty in st.session_state.cart.items():
        p = next(x for x in PRODUCTS if x['id'] == pid)
        total += p['price'] * qty
        st.write(f"{p['name']} x{qty} — {p['price']*qty:,} ₽")
        summary.append(f"{p['name']} (x{qty})")

    st.subheader(f"Итого: {total:,} ₽")

    if st.button("💳 Оформить и оплатить"):
        # Сохранение в БД
        items_str = ", ".join(summary)
        c = conn.cursor()
        c.execute("INSERT INTO orders (items, total, date) VALUES (?, ?, ?)",
                  (items_str, total, datetime.now().strftime("%H:%M:%S")))
        conn.commit()
        
        # Отправка данных боту через Telegram SDK
        js_data = json.dumps({"status": "paid", "total": total, "items": items_str})
        components.html(f"""
            <script>
            const tg = window.Telegram.WebApp;
            tg.sendData('{js_data}');
            tg.close();
            </script>
        """, height=0)

# Подключаем SDK
components.html("<script src='https://telegram.org/js/telegram-web-app.js'></script>", height=0)
