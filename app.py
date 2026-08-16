import streamlit as st
import json
import os

DB_FILE = "inventory.json"

DEFAULT_INVENTORY = {
    "TS01": {"name": "เสื้อยืด Size M", "price": 250, "stock": 20, "category": "เสื้อ", "img": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=300"},
    "TS02": {"name": "เสื้อยืด Size L", "price": 250, "stock": 15, "category": "เสื้อ", "img": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=300"},
    "JN01": {"name": "กางเกงยีนส์ Size 32", "price": 590, "stock": 10, "category": "กางเกง", "img": "https://images.unsplash.com/photo-1542272604-780c36856f61?w=300"},
    "HD01": {"name": "เสื้อฮู้ด Free Size", "price": 450, "stock": 8, "category": "เสื้อนอก", "img": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=300"},
}

def load_inventory():
    if not os.path.exists(DB_FILE):
        save_inventory(DEFAULT_INVENTORY)
        return DEFAULT_INVENTORY
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_INVENTORY

def save_inventory(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Clothing POS", page_icon="🛍️", layout="wide")

# โหลดข้อมูลเข้า Session State
if "inventory" not in st.session_state:
    st.session_state.inventory = load_inventory()
if "cart" not in st.session_state:
    st.session_state.cart = {}

st.title("🛍️ ระบบ POS ร้านขายเสื้อผ้า")

col_goods, col_cart = st.columns([2, 1])

# --- ฝั่งซ้าย: แสดงรายการสินค้าเป็นปุ่มกด (เหมือนร้านสะดวกซื้อ) ---
with col_goods:
    st.subheader("📦 รายการสินค้า")
    items = list(st.session_state.inventory.items())
    
    # จัดแสดงสินค้าแบบ Grid 2 คอลัมน์
    for i in range(0, len(items), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(items):
                code, item = items[i + j]
                with cols[j]:
                    with st.container(border=True):
                        st.image(item["img"], use_container_width=True)
                        st.bold(item["name"])
                        st.text(f"ราคา: {item['price']} บาท | เหลือ: {item['stock']} ชิ้น")
                        
                        if item["stock"] > 0:
                            if st.button(f"➕ เพิ่มลงตะกร้า", key=f"btn_{code}"):
                                in_cart = st.session_state.cart.get(code, 0)
                                if in_cart < item["stock"]:
                                    st.session_state.cart[code] = in_cart + 1
                                    st.rerun()
                                else:
                                    st.error("สินค้าในตะกร้าเท่ากับจำนวนสต็อกที่มีแล้ว!")
                        else:
                            st.error("❌ สินค้าหมด")

# --- ฝั่งขวา: ตะกร้าสินค้าและการชำระเงิน ---
with col_cart:
    st.subheader("🛒 ตะกร้าสินค้า")
    
    if not st.session_state.cart:
        st.info("ยังไม่มีสินค้าในตะกร้า เลือกคลิกปุ่มเพิ่มสินค้าได้เลย")
    else:
        total_price = 0
        for code, qty in list(st.session_state.cart.items()):
            item = st.session_state.inventory[code]
            subtotal = item["price"] * qty
            total_price += subtotal
            
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{item['name']}**\n{item['price']} x {qty} บาท")
            c2.write(f"**{subtotal}**")
            if c3.button("❌", key=f"del_{code}"):
                del st.session_state.cart[code]
                st.rerun()
            st.divider()
        
        st.markdown(f"### ราคารวมทั้งสิ้น: :green[{total_price:,}] บาท")
        
        # ส่วนรับเงิน
        payment_method = st.radio("ช่องทางการชำระเงิน", ["เงินสด", "สแกน QR Code"])
        
        if payment_method == "เงินสด":
            cash = st.number_input("จำนวนเงินที่รับมา (บาท)", min_value=0.0, value=float(total_price))
            if st.button("💵 ชำระเงิน / ตัดสต็อก", type="primary", use_container_width=True):
                if cash >= total_price:
                    change = cash - total_price
                    # ตัดสต็อก
                    for code, qty in st.session_state.cart.items():
                        st.session_state.inventory[code]["stock"] -= qty
                    save_inventory(st.session_state.inventory)
                    
                    st.success(f"🎉 ชำระเงินสำเร็จ! เงินทอน: {change:,.2f} บาท")
                    st.session_state.cart = {}
                else:
                    st.error(f"เงินไม่พอ! ขาดอีก {total_price - cash:,.2f} บาท")
        else:
            if st.button("✅ ยืนยันการรับเงินสแกน QR", type="primary", use_container_width=True):
                for code, qty in st.session_state.cart.items():
                    st.session_state.inventory[code]["stock"] -= qty
                save_inventory(st.session_state.inventory)
                st.success("🎉 ชำระเงินผ่าน QR Code เรียบร้อยแล้ว!")
                st.session_state.cart = {}

    if st.button("🗑️ ล้างตะกร้าทั้งหมด", use_container_width=True):
        st.session_state.cart = {}
        st.rerun()
