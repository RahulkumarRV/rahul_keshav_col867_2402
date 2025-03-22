# Approach for Predicting Early Termination Time in Speed Tests  

## 1. Introduction  
Network speed tests are used to measure internet bandwidth, but they often run longer than necessary to ensure accuracy. Our goal is to develop a **machine learning model** that predicts when a test can be safely stopped while maintaining a reliable bandwidth estimate.  

This document outlines:  
1. **Data extraction**
2. **preprocessing** for bandwidth prediction and early termination models.  
3. **Feature engineering** for predicting early termination time.  
4. **Model training and evaluation strategy.**  

---

## 2. Data Extraction and Preprocessing  

### 2.1 Data Extraction  
- **Source:** Data is extracted from Google Cloud Storage using `gsutil`.  
- **Decryption & Decompression:** A script (`extract_files.py`) is used to recursively decrypt and extract the compressed files into a single folder.  

### 2.2 Preprocessing for Bandwidth Prediction  
We process **server measurement data** to create a session-level dataset:  
1. **Aggregating Server Measurements:** Each speed test consists of multiple **TCPInfo snapshots** taken at different timestamps.  
2. **Label (Target Variable):**  
   - We use the **average bandwidth ('BW')** of all TCP snapshots as the target for bandwidth prediction.  
3. **Feature Engineering:**  
   - Compute **mean, max, min, and std** for **RTT, Bandwidth, Pacing Rate, and Delivery Rate**.  
   - **Total bytes acknowledged and retransmissions** for network performance evaluation.  
   - Stabilization indicators for detecting bandwidth consistency.  

### 2.3 Preprocessing for Early Termination Prediction  
We prepare the dataset differently for the early termination model:  
1. **Row-wise Processing:** Instead of aggregating, we treat each **TCPInfo snapshot** as a single row in the dataset.  
2. **Elapsed Time Feature:**  
   - The `ElapsedTime` property represents the timestamp at which the snapshot was recorded.  
   - The `UUID` links snapshots to their respective test sessions.  
3. **Label (Target Variable):**  
   - First, compute the **average bandwidth ('BW')** across all snapshots in a session.  
   - For each snapshot, calculate the **absolute difference** between its bandwidth and the session’s average.  
   - The **snapshot with the least difference** (i.e., closest to the session average) is selected, and its `ElapsedTime` is used as the **label** for all snapshots in that session.  

This ensures that the model learns when the **bandwidth stabilizes**, allowing us to predict the **optimal early termination time**.  

---

## 3. Machine Learning Approach  

### 3.1 Feature Engineering for Early Termination  
To improve early termination accuracy, we extract features from **early-stage snapshots**:  
- **10%, 20%, and 30% Aggregations:**  
  - Compute mean, max, min, and std of key metrics (RTT, Pacing Rate, Delivery Rate, Bandwidth) using only **first 10%, 20%, and 30%** of test duration.  
  - Compare early-stage bandwidth trends to full-session values.  
- **Stabilization Indicators:**  
  - Compute variance in bandwidth across early snapshots.  
  - If variance is low, the test is likely stable.  
- **RTT and Loss Trends:**  
  - Increasing RTT and retransmissions suggest network instability.  

### 3.2 Model Selection  
- **Baseline:** Decision Trees, Random Forest.  
- **Advanced Models:** XGBoost, LSTMs (for time-series dependencies).  
- **Real-Time Adaptation:** Reinforcement Learning for dynamic stopping.  

### 3.3 Evaluation Metrics  
- **MAE for \( T_{\text{early}} \)** (how close predicted termination time is to the actual stable time).  
- **R² Score** for early bandwidth prediction.  
- **Classification Accuracy** (if using classification for early vs. full test).  

---

## 4. Implementation Plan  
1. Extract **10%, 20%, 30% aggregated features**.  
2. Train models to detect stabilization.  
3. Evaluate and refine stopping criteria.  
4. Deploy real-time stopping algorithm.  

---

## 5. Conclusion  
We have processed the **server-side TCPInfo measurements** to build a dataset for bandwidth prediction and early termination models. Using **early-stage aggregations** and **stabilization indicators**, we can improve early termination accuracy. The next step is to train and evaluate machine learning models for predicting the optimal stopping time.  

Would you like to refine **stabilization criteria** further?
