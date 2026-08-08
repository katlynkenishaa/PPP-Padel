with tab2:
    rec_id = st.text_input("Customer ID", key="rec_id")
    rec_name = st.text_input("Customer Name")
    
    rec_voucher = st.selectbox("Voucher Code", ["Promo A", "Promo B", "No Promo"])
    
    if st.button("Save Visit to Google Sheets", type="primary"):
        if not rec_id or not rec_name:
            st.error("Please enter both Customer ID and Name.")
        else:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # This line now directly records exactly what is in the dropdown
            sheet.append_row([str(rec_id).strip(), rec_name.strip(), rec_voucher, current_time])
            st.success(f"✅ Recorded visit for {rec_name}!")
