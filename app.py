# app.py
# Phiên bản rút gọn hoàn chỉnh hỗ trợ nhiều người
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Thuế TNCN 2026", page_icon="💰")

st.title("💰 Ứng dụng tính thuế TNCN 2026")

def tinh_thue_tncn(gross, bonus, overtime, lunch, other, deps):
    total_income = gross + bonus + overtime + lunch + other
    bhxh = gross * 0.08
    bhyt = gross * 0.015
    bhtn = gross * 0.01
    total_insurance = bhxh + bhyt + bhtn
    self_reduction = 15500000
    dependent_reduction = deps * 6200000
    exempt_lunch = min(lunch,730000)
    exempt_allowance = other
    exempt_income = overtime + exempt_lunch + exempt_allowance
    assessable = max(0,total_income-exempt_income-total_insurance-self_reduction-dependent_reduction)

    tax=0
    prev=0
    for limit,rate in [(10000000,0.05),(30000000,0.10),(60000000,0.20),(100000000,0.30),(10**18,0.35)]:
        if assessable<=0: break
        span=limit-prev
        part=min(assessable,span)
        tax+=part*rate
        assessable-=part
        prev=limit
    net=total_income-total_insurance-tax
    return total_income,total_insurance,tax,net

mode=st.radio("Chọn cách nhập",["Slider","Nhập số"])
if mode=="Slider":
    n=st.slider("Số người",1,100,1)
else:
    n=st.number_input("Số người",1,10000,1)

people=[]
for i in range(int(n)):
    with st.expander(f"Người {i+1}",expanded=(i==0)):
        name=st.text_input("Họ tên",key=f"n{i}")
        gross=st.number_input("Lương BHXH",0,10**9,30000000,500000,key=f"g{i}")
        bonus=st.number_input("Thưởng",0,10**9,0,500000,key=f"b{i}")
        ot=st.number_input("Tăng ca",0,10**9,0,500000,key=f"o{i}")
        c1,c2=st.columns(2)
        with c1:
            lunch=st.number_input("Ăn trưa",0,10**9,0,50000,key=f"l{i}")
        with c2:
            other=st.number_input("Điện thoại/Xăng xe",0,10**9,0,50000,key=f"a{i}")
        dep=st.number_input("Người phụ thuộc",0,20,1,1,key=f"d{i}")
        people.append((name,gross,bonus,ot,lunch,other,dep))

if st.button("🧮 Tính thuế",type="primary"):
    rows=[]
    for p in people:
        total,ins,tax,net=tinh_thue_tncn(*p[1:])
        rows.append({
            "Họ tên":p[0] or "Chưa nhập",
            "Tổng thu nhập":total,
            "Bảo hiểm":ins,
            "Thuế":tax,
            "Thực nhận":net
        })
    df=pd.DataFrame(rows)
    st.dataframe(df,use_container_width=True)
    c1,c2,c3=st.columns(3)
    c1.metric("Số người",len(df))
    c2.metric("Tổng thuế",f"{df['Thuế'].sum():,.0f}")
    c3.metric("Tổng thực nhận",f"{df['Thực nhận'].sum():,.0f}")
    st.bar_chart(df.set_index("Họ tên")["Thuế"])
    st.download_button("📥 Xuất CSV",df.to_csv(index=False).encode("utf-8-sig"),"ket_qua_thue.csv","text/csv")

