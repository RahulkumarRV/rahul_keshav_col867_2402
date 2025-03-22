# Predicting Early Termination Time in Speed Tests  

## 1. Introduction  
Network speed tests are used to measure internet bandwidth, but they often run longer than necessary to ensure accuracy. Our goal is to develop a **machine learning model** that predicts when a test can be safely stopped while maintaining a reliable bandwidth estimate.  

The rest of the  document is outlined as follows:  
1. **Data extraction**
2. **preprocessing** for bandwidth prediction and early termination models.  
3. **Feature engineering** for predicting early termination time.  
4. **Model training and evaluation strategy.**  
5. **challanges Faced**
6. **Future Works**

---

## 2. Data Extraction and Preprocessing  

### 2.1 Data Extraction  
**Source** 
NDT7 Data is extracted from Google Cloud Storage using `gsutil`.  The datafolder is structured as year -> month -> day and then the session data for different time.
**Decryption & Decompression:** 
For downloading the data we used gsutil. We download data for the first day of January 2024.
A script (`extract_files.py`) is used to recursively decrypt and extract the compressed files into a single folder.  

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


**Note:** --We have decribed the parameter used for training in the Readme.md file along with their significance.--
---

## 3. Machine Learning Models  

We will train multiple models for different value prediction. One is for predicting network characteristics and one for early termination time.


### 3.2 Model Selection  
 

### 3.3 Evaluation Metrics  
- **MAE for \( T_{\text{early}} \)** (how close predicted termination time is to the actual stable time).  
- **R² Score** for early bandwidth prediction.  
- **Classification Accuracy** (if using classification for early vs. full test).  



## 5. Challanges Faced
### 1. Data extraction
   The data was compressed when downloaded where there were 2/3 layers of compressed data.
   The data was in various different files so had to compile it into a single file.
   Solution: write a python script to handle all of this.

### 2. Preprocessing 
   **Some test lacked congestion control metrics or had incomplete RTT data.**
   Solution: Used median imputation and interpolation to fill missing values.
   **Inconsistency in loggin interval** - features were logged at different interval across sessions.
   **Outlier in Throughput and RTT.**
   Some session showed high/low thorughput due to network congestion.
   Solution: Winsorization was applied to remove extreme values.
   **Figuring out the parameters to use.**
   **strategy for creating labels for early termination strategy**

### 3. challenges faced while model training for bandwidth prediction.
- Overfitting in tree based model. Applied L1/L2 regularization and pruning techniques.
- Features like RTT and congestion control fluctuates over time. used rolling average and delta features to capture trends.


## 6. Future Work

#### 1. Improving Parameter Selection for Bandwidth Prediction
 Feature Selection & Importance Analysis
- Use techniques like **SHAP values** or **permutation importance** to identify the most influential features.
- Experiment with **dimensionality reduction** (e.g., PCA) to remove redundant features.

 Hyperparameter Tuning
- Optimize parameters for tree-based models (e.g., **max depth, learning rate, and regularization** in XGBoost).


#### 2. We can explore combining bandwidth prediction and early termination into a single model to improve efficiency and reduce complexity. 
- Multi-Output Regression Model

Use a neural network or tree-based model with two outputs:
Predicted final bandwidth.
Predicted stabilization time.


- Single Model with Early Stopping Criterion

Instead of explicitly predicting stopping time, introduce a stability confidence score to determine when the model is confident enough to stop.
Train using weighted loss functions to balance bandwidth prediction accuracy and stopping precision.

#### 3. Currently we have only created a regression model for bandwidth prediction and for the early termination we have preprocessed the data and created the labels. We will create a regression model for early termination also or make a single model for both the task.


#### 3. Data Refinement & Expansion
**Addressing Missing Data Issues**
- Test different **imputation strategies** (e.g., KNN imputation vs. median interpolation).

**Benchmark Against Real-World Speed Test Data**
- Compare predictions against **user-reported experiences** from third-party speed test platforms.

