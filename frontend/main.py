import streamlit as st
import requests
import pandas as pd
import io

# Sayfa yapılandırması
st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📊",
    layout="wide"
)

# Backend API URL
API_URL = "http://127.0.0.1:8000"

# Ana başlık
st.title("🔮 Customer Churn Prediction System")
st.markdown("---")

# Sidebar - Mode selection
st.sidebar.header("⚙️ Settings")
mode = st.sidebar.radio(
    "Select Prediction Mode:",
    ["Single Prediction", "Batch Prediction (CSV)"]
)

# ==================== MODE 1: SINGLE PREDICTION ====================
if mode == "Single Prediction":
    st.header("👤 Single Customer Prediction")
    st.write("Fill in the form below to predict the customer's churn risk.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📋 Demographics")
        gender = st.selectbox("Gender", ["Male", "Female"])
        senior_citizen = st.selectbox("Senior Citizen", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
        partner = st.selectbox("Partner", ["Yes", "No"])
        dependents = st.selectbox("Dependents", ["Yes", "No"])
        tenure = st.number_input("Tenure (months)", min_value=0, max_value=100, value=12)
    
    with col2:
        st.subheader("📞 Services")
        phone_service = st.selectbox("Phone Service", ["Yes", "No"])
        multiple_lines = st.selectbox("Multiple Lines", ["Yes", "No", "No phone service"])
        internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
        online_security = st.selectbox("Online Security", ["Yes", "No", "No internet service"])
        online_backup = st.selectbox("Online Backup", ["Yes", "No", "No internet service"])
        device_protection = st.selectbox("Device Protection", ["Yes", "No", "No internet service"])
        tech_support = st.selectbox("Tech Support", ["Yes", "No", "No internet service"])
        streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"])
        streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"])
    
    with col3:
        st.subheader("💳 Contract & Billing")
        contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
        paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
        payment_method = st.selectbox("Payment Method", [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)"
        ])
        monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, max_value=200.0, value=70.0, step=0.1)
        total_charges = st.number_input("Total Charges ($)", min_value=0.0, max_value=10000.0, value=1500.0, step=0.1)
    
    st.markdown("---")
    
    if st.button("🔮 Predict", use_container_width=True, type="primary"):
        # Data to send to API
        data = {
            "gender": gender,
            "SeniorCitizen": senior_citizen,
            "Partner": partner,
            "Dependents": dependents,
            "tenure": tenure,  
            "PhoneService": phone_service,
            "MultipleLines": multiple_lines,
            "InternetService": internet_service,
            "OnlineSecurity": online_security,
            "OnlineBackup": online_backup,
            "DeviceProtection": device_protection,
            "TechSupport": tech_support,
            "StreamingTV": streaming_tv,
            "StreamingMovies": streaming_movies,
            "Contract": contract,
            "PaperlessBilling": paperless_billing,
            "PaymentMethod": payment_method,
            "MonthlyCharges": monthly_charges,
            "TotalCharges": total_charges
        }
        
        try:
            with st.spinner("Making prediction..."):
                response = requests.post(f"{API_URL}/predict", json=data)
                
            if response.status_code == 200:
                result = response.json()
                
                # Show results
                st.success("✅ Prediction completed!")
                
                col_result1, col_result2 = st.columns(2)
                
                with col_result1:
                    st.metric(
                        label="Prediction Result",
                        value=result['prediction'],
                        delta="⚠️ Risk" if "CHURN" in result['prediction'] else "✅ Safe"
                    )
                
                with col_result2:
                    probability_percent = result['probability'] * 100
                    st.metric(
                        label="Churn Probability",
                        value=f"{probability_percent:.2f}%"
                    )
                
                # Message based on risk level
                if probability_percent > 70:
                    st.error("🚨 **High Risk!** Immediate action required for this customer.")
                elif probability_percent > 50:
                    st.warning("⚠️ **Medium Risk.** Consider reaching out to the customer.")
                else:
                    st.success("✅ **Low Risk.** Customer appears loyal.")
            else:
                st.error(f"❌ Error: {response.text}")
        
        except Exception as e:
            st.error(f"❌ Cannot connect to API: {str(e)}")
            st.info("Make sure the backend server is running: `python -m uvicorn app:app --reload`")

# ==================== MODE 2: BATCH PREDICTION ====================
else:
    st.header("📂 Batch Customer Prediction (CSV)")
    st.write("Upload your CSV file to identify customers at risk.")
    
    # Show example CSV format
    with st.expander("📄 Example CSV Format"):
        example_data = {
            "gender": ["Male", "Female", "Male"],
            "SeniorCitizen": [0, 1, 0],
            "Partner": ["No", "No", "Yes"],
            "Dependents": ["No", "No", "Yes"],
            "tenure": [1, 3, 48],
            "PhoneService": ["Yes", "Yes", "Yes"],
            "MultipleLines": ["No", "Yes", "Yes"],
            "InternetService": ["Fiber optic", "Fiber optic", "DSL"],
            "OnlineSecurity": ["No", "No", "Yes"],
            "OnlineBackup": ["No", "No", "Yes"],
            "DeviceProtection": ["No", "No", "Yes"],
            "TechSupport": ["No", "No", "Yes"],
            "StreamingTV": ["Yes", "Yes", "No"],
            "StreamingMovies": ["Yes", "Yes", "Yes"],
            "Contract": ["Month-to-month", "Month-to-month", "Two year"],
            "PaperlessBilling": ["Yes", "Yes", "No"],
            "PaymentMethod": ["Electronic check", "Electronic check", "Bank transfer (automatic)"],
            "MonthlyCharges": [85.5, 105.5, 110.5],
            "TotalCharges": [85.5, 316.5, 5304.0]
        }
        example_df = pd.DataFrame(example_data)
        st.dataframe(example_df, use_container_width=True)
        
        st.info("💡 **Tip:** First 2 customers are risky profiles (short tenure, Month-to-month, Electronic check), 3rd customer is safe.")
        
        # Download example CSV
        csv = example_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Example CSV",
            data=csv,
            file_name="example_customers.csv",
            mime="text/csv"
        )
    
    # File upload
    uploaded_file = st.file_uploader("Upload CSV File", type=['csv'])
    
    if uploaded_file is not None:
        try:
            # Show uploaded file
            df = pd.read_csv(uploaded_file)
            
            if df.empty or len(df) == 0:
                st.error("❌ The uploaded CSV file is empty! Please upload a file with data.")
                st.stop()
            
            st.success(f"✅ {len(df)} customer records loaded!")
            
            with st.expander("📊 View Uploaded Data"):
                st.dataframe(df, use_container_width=True)
        
        except pd.errors.EmptyDataError:
            st.error("❌ File is empty! Please upload a valid CSV file.")
            st.stop()
        except Exception as e:
            st.error(f"❌ File reading error: {str(e)}")
            st.stop()
        
        if st.button("🔮 Run Batch Prediction", use_container_width=True, type="primary"):
            try:
                with st.spinner("Making predictions... This may take a moment."):
                    # Send file to API
                    uploaded_file.seek(0)
                    files = {"file": ("customers.csv", uploaded_file, "text/csv")}
                    response = requests.post(f"{API_URL}/predict-batch", files=files)
                
                if response.status_code == 200:
                    st.success("✅ Prediction completed!")
                    
                    # Show results
                    result_df = pd.read_csv(io.BytesIO(response.content))
                    
                    col_stat1, col_stat2 = st.columns(2)
                    
                    with col_stat1:
                        st.metric("Total Customers", len(df))
                    
                    with col_stat2:
                        st.metric("At-Risk Customers", len(result_df))
                    
                    # Risk percentage
                    if len(df) > 0:
                        risk_percent = (len(result_df) / len(df)) * 100
                        st.progress(risk_percent / 100)
                        st.write(f"**Risk Rate:** {risk_percent:.2f}%")
                    
                    # Show at-risk customers if any
                    if len(result_df) > 0:
                        # Download button
                        st.download_button(
                            label="📥 Download Risk Report",
                            data=response.content,
                            file_name="at_risk_customers_report.csv",
                            mime="text/csv",
                            type="primary"
                        )
                        
                        # Show at-risk customers
                        st.subheader("🚨 At-Risk Customers")
                        
                        # Sort by probability and color-code
                        sorted_df = result_df.sort_values('Churn_Probability', ascending=False)
                        
                        # Detailed view for each customer
                        for idx, row in sorted_df.iterrows():
                            prob = row['Churn_Probability'] * 100
                            
                            # Color based on risk level
                            if prob > 70:
                                color = "🔴"
                                risk_level = "High Risk"
                            elif prob > 50:
                                color = "🟡"
                                risk_level = "Medium Risk"
                            else:
                                color = "🟢"
                                risk_level = "Low Risk"
                            
                            with st.expander(f"{color} {risk_level} - Probability: {prob:.2f}%"):
                                # Show customer details
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.write("**Demographics:**")
                                    st.write(f"- Gender: {row.get('gender', 'N/A')}")
                                    st.write(f"- Senior Citizen: {row.get('SeniorCitizen', 'N/A')}")
                                    st.write(f"- Partner: {row.get('Partner', 'N/A')}")
                                    st.write(f"- Dependents: {row.get('Dependents', 'N/A')}")
                                
                                with col2:
                                    st.write("**Services:**")
                                    st.write(f"- Tenure (months): {row.get('tenure', 'N/A')}")
                                    st.write(f"- Internet: {row.get('InternetService', 'N/A')}")
                                    st.write(f"- Contract: {row.get('Contract', 'N/A')}")
                                    st.write(f"- Payment: {row.get('PaymentMethod', 'N/A')}")
                                
                                with col3:
                                    st.write("**Financial:**")
                                    st.write(f"- Monthly Charges: ${row.get('MonthlyCharges', 'N/A'):.2f}")
                                    st.write(f"- Total Charges: ${row.get('TotalCharges', 'N/A'):.2f}")
                                    st.write(f"- Paperless Billing: {row.get('PaperlessBilling', 'N/A')}")
                        
                        # Summary table
                        st.subheader("📊 At-Risk Customers Table")
                        st.dataframe(
                            sorted_df,
                            use_container_width=True
                        )
                    else:
                        st.success("🎉 Great! No customers at risk!")
                        st.balloons()
                    
                else:
                    st.error(f"❌ Error: {response.text}")
            
            except Exception as e:
                st.error(f"❌ Cannot connect to API: {str(e)}")
                st.info("Make sure the backend server is running: `python -m uvicorn app:app --reload`")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🔮 Customer Churn Prediction System | Powered by FastAPI & Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
