import streamlit as st
import pandas as pd
import os
from openai import OpenAI

# OpenAI API anahtarını güvenli şekilde al
client = OpenAI()

# Örnek veri
data = {
    "id": [1, 2, 3],
    "segment": ["silver", "silver", "silver"],
    "invest_menu_visits": [5, 1, 4],
    "has_investment": [0, 1, 0]  # Kullanıcı 2 zaten yatırıma sahip
}
df = pd.DataFrame(data)

# Kural tabanlı öneri
def base_suggestion(row):
    if row["has_investment"] == 0 and row["invest_menu_visits"] >= 3:
        return "Yatırım yapmayı sıkça düşündüğünü görüyoruz. Sizin için en uygun yatırım hesabını birlikte oluşturalım."
    elif row["has_investment"] == 1:
        return "Yatırım hesabını başarıyla açtın, yatırım ürünleriyle ilgili bilgi almak istersen bana dilediğin zaman ulaşabilirsin veya İşCep ve isbank.com.tr'den de bilgi alabilirsin."
    return "Şu an için öneri yok."

# GPT ile empatik öneri
def generate_gpt_message(message):
    if message.startswith("Yatırım hesabını başarıyla"):
        return message
    if message == "Şu an için öneri yok.":
        return message
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen bir banka müşteri danışmanısısın. Kullanıcılara finansal konularda empatik ve cesaretlendirici mesajlar yazıyorsun."},
            {"role": "user", "content": f"Bu öneriyi daha empatik ve kişisel hale getir: {message}"}
        ]
    )
    return response.choices[0].message.content.strip()

# Seçime göre yanıt

def generate_path_response(path):
    if path == "Yatırım Fonu":
        return """
Yatırım yapmaya yatırım fonlarıyla başlamak, küçük adımlarla büyük birikimler oluşturmanın en dengeli yollarından biridir.
İşCep'teki Robofon Danışmanı sayesinde risk profiline uygun fon önerisi alabilir, sadece 6 adımda Risk Profili Testi'ni tamamlayarak Temkinli, Dengeli veya Atak fonlardan sana uygun olanı seçebilirsin. Üstelik İşCep üzerinden hemen yatırımına başlayabilirsin. 💡
"""
    elif path == "Altın":
        return "Altın, ekonomik belirsizliklerde güvenli liman olarak görülür. Vadesiz altın hesabı veya altın fonları ile küçük adımlarla başlayabilirsin. İşCep üzerinden kolayca alım yapabilirsin."
    elif path == "Hisse Senedi":
        return "Hisse senetleri uzun vadeli kazanç sağlayabilir. Şirketleri inceleyip kademeli olarak pozisyon alabilirsin. İşCep'te emir tiplerini kullanarak daha kontrollü işlem yapabilirsin."
    return "Daha fazla bilgi için İşCep'ten yatırım menüsünü inceleyebilirsin."

# Yatırıma başlama rehberi

def generate_investment_guide():
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen halkın anlayacağı dilden anlatan, sade ve güven veren bir ekonomi uzmanısın."},
            {"role": "user", "content": "Yatırım yapmak isteyen ama hiç tecrübesi olmayan birine, halkın anlayacağı dilde, sade ve yol gösterici bir mesaj yaz. Gereksiz teknik terim kullanma."}
        ]
    )
    return response.choices[0].message.content.strip()

# Streamlit arayüz

st.title("Bondee.AI - Empatik Öneri ve Rehberlik Demo")
st.write("Kullanıcılara GPT destekli yatırım önerileri sunulur. Her bir öneriye olumlu tepki verildiğinde rehber ve yatırım yolu seçimi gösterilir.")

if "show" not in st.session_state:
    st.session_state.show = False
if "clicked_users" not in st.session_state:
    st.session_state.clicked_users = set()
if "investment_choice" not in st.session_state:
    st.session_state.investment_choice = {}

if st.button("Önerileri Göster"):
    st.session_state.show = True

if st.session_state.show:
    df["öneri"] = df.apply(base_suggestion, axis=1)
    df["empatik_mesaj"] = df["öneri"].apply(generate_gpt_message)

    for index, row in df.iterrows():
        st.markdown(f"**Kullanıcı {row['id']}**: {row['empatik_mesaj']}")

        if row['has_investment'] == 0 and row['empatik_mesaj'] != "Şu an için öneri yok.":
            button_key = f"ilgi_{row['id']}"
            if st.button(f"Evet, ilgileniyorum (Kullanıcı {row['id']})", key=button_key):
                st.session_state.clicked_users.add(row['id'])

        if row['id'] in st.session_state.clicked_users:
            st.subheader(f"📘 Yatırıma Nasıl Başlanır? (Kullanıcı {row['id']})")
            st.markdown(generate_investment_guide())
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"Altın ({row['id']})"):
                    st.session_state.investment_choice[row['id']] = "Altın"
            with col2:
                if st.button(f"Yatırım Fonu ({row['id']})"):
                    st.session_state.investment_choice[row['id']] = "Yatırım Fonu"
            with col3:
                if st.button(f"Hisse Senedi ({row['id']})"):
                    st.session_state.investment_choice[row['id']] = "Hisse Senedi"

            if row['id'] in st.session_state.investment_choice:
                selected = st.session_state.investment_choice[row['id']]
                st.success(f"Seçiminiz: {selected}")
                st.markdown(generate_path_response(selected))
