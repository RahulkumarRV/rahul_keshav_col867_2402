# Speed Test Data Analysis and Regression Model

This project aims to analyze speed test data and build a regression model to predict early termination of speed tests. The dataset contains various attributes extracted from network performance metrics, which are crucial for understanding the factors influencing early termination.

## Dataset Overview

#### we have collected approximately 6000 rows of data for the Bandwidth Prediction model. We will later generalize this by collecting data from different time and date. 

The dataset is stored in `data_set.csv` and contains the following attributes:

| Attribute Name               | Description                                                                                     | Relevance for Regression Model                                                                 |
|------------------------------|-------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| `uuid`                       | Unique identifier for each session.                                                            | Used to uniquely identify each test session.                                                  |
| `filename`                   | Name of the JSON file containing raw data for the session.                                      | Useful for traceability and debugging.                                                        |
| `SessionDuration_seconds`    | Duration of the session in seconds.                                                            | Key target variable for predicting early termination.                                          |
| `NumFlows`                   | Number of flows in the session.                                                                | Indicates the complexity of the session, which may impact termination likelihood.             |
| `MaxBandwidth_Mbps`          | Maximum bandwidth achieved during the session (in Mbps).                                       | High bandwidth may correlate with successful test completion.                                 |
| `MeanBandwidth_Mbps`         | Average bandwidth during the session (in Mbps).                                               | Provides an overall measure of network performance.                                           |
| `MinBandwidth_Mbps`          | Minimum bandwidth during the session (in Mbps).                                               | Low bandwidth may indicate poor network conditions leading to early termination.              |
| `StdBandwidth_Mbps`          | Standard deviation of bandwidth during the session (in Mbps).                                 | High variability in bandwidth may indicate instability, which could lead to termination.      |
| `MaxPacingRate_Mbps`         | Maximum pacing rate during the session (in Mbps).                                             | Reflects the maximum rate at which data was sent, which may influence session stability.       |
| `MeanPacingRate_Mbps`        | Average pacing rate during the session (in Mbps).                                             | Indicates the overall pacing behavior of the session.                                         |
| `MinRTT_ms`                  | Minimum round-trip time during the session (in milliseconds).                                  | Low RTT indicates better network conditions, which may reduce the likelihood of termination.  |
| `MaxRTT_ms`                  | Maximum round-trip time during the session (in milliseconds).                                  | High RTT may indicate network congestion or instability.                                      |
| `MeanRTT_ms`                 | Average round-trip time during the session (in milliseconds).                                 | Provides an overall measure of latency during the session.                                    |
| `StdRTT_ms`                  | Standard deviation of round-trip time during the session (in milliseconds).                   | High RTT variability may indicate unstable network conditions.                                |
| `MaxCwnd_packets`            | Maximum congestion window size (in packets).                                                  | Larger congestion windows may indicate better network performance.                            |
| `MeanCwnd_packets`           | Average congestion window size (in packets).                                                  | Reflects the overall congestion control behavior during the session.                          |
| `MaxRcvWindow_bytes`         | Maximum receive window size (in bytes).                                                       | Indicates the maximum buffer size available for receiving data.                               |
| `MeanRcvWindow_bytes`        | Average receive window size (in bytes).                                                       | Reflects the overall buffering behavior during the session.                                   |
| `TotalBytesAcked_bytes`      | Total bytes acknowledged during the session.                                                   | Indicates the amount of data successfully transmitted.                                        |
| `TotalBytesSent_bytes`       | Total bytes sent during the session.                                                           | Reflects the overall data transmission volume.                                                |
| `TotalBytesReceived_bytes`   | Total bytes received during the session.                                                       | Indicates the amount of data successfully received.                                           |
| `TotalRetransmissions_count` | Total number of retransmissions during the session.                                            | High retransmissions may indicate poor network conditions leading to termination.             |
| `LossRate_percent`           | Percentage of lost packets during the session.                                                | High loss rates may correlate with early termination.                                         |
| `MaxDeliveryRate_Mbps`       | Maximum delivery rate during the session (in Mbps).                                           | Reflects the peak data delivery performance.                                                  |
| `MeanDeliveryRate_Mbps`      | Average delivery rate during the session (in Mbps).                                           | Indicates the overall delivery performance of the session.                                    |
| `TotalBusyTime_microseconds` | Total time the network was busy during the session (in microseconds).                         | High busy time may indicate network congestion.                                               |
| `MaxThroughput_Mbps`         | Maximum throughput achieved during the session (in Mbps).                                     | High throughput may correlate with successful test completion.                                |
| `MeanThroughput_Mbps`        | Average throughput during the session (in Mbps).                                             | Reflects the overall data transfer efficiency.                                                |
| `MinThroughput_Mbps`         | Minimum throughput during the session (in Mbps).                                             | Low throughput may indicate poor network conditions leading to termination.                   |
| `StdThroughput_Mbps`         | Standard deviation of throughput during the session (in Mbps).                               | High variability in throughput may indicate instability, which could lead to termination.     |

## Importance of Each Column

### 1. `uuid`
- **Description**: A unique identifier for each session.
- **Importance**: Helps in uniquely identifying and tracking individual sessions. It is useful for debugging and linking the data back to the original JSON file.

### 2. `filename`
- **Description**: The name of the JSON file containing raw data for the session.
- **Importance**: Provides traceability to the source file, which is helpful for validation and debugging.

### 3. `SessionDuration_seconds`
- **Description**: The total duration of the session in seconds.
- **Importance**: This is a key feature for predicting early termination. Shorter durations may indicate early termination or network issues.

### 4. `NumFlows`
- **Description**: The number of flows in the session.
- **Importance**: Indicates the complexity of the session. A higher number of flows may increase the likelihood of congestion or instability.

### 5. `MaxBandwidth_Mbps`
- **Description**: The maximum bandwidth achieved during the session (in Mbps).
- **Importance**: High bandwidth often correlates with better network performance and lower chances of early termination.

### 6. `MeanBandwidth_Mbps`
- **Description**: The average bandwidth during the session (in Mbps).
- **Importance**: Provides an overall measure of network performance. Low average bandwidth may indicate poor network conditions.

### 7. `MinBandwidth_Mbps`
- **Description**: The minimum bandwidth during the session (in Mbps).
- **Importance**: Low minimum bandwidth may indicate temporary network issues, which could lead to early termination.

### 8. `StdBandwidth_Mbps`
- **Description**: The standard deviation of bandwidth during the session (in Mbps).
- **Importance**: High variability in bandwidth may indicate unstable network conditions, increasing the likelihood of early termination.

### 9. `MaxPacingRate_Mbps`
- **Description**: The maximum pacing rate during the session (in Mbps).
- **Importance**: Reflects the peak rate at which data was sent. High pacing rates may indicate efficient data transmission.

### 10. `MeanPacingRate_Mbps`
- **Description**: The average pacing rate during the session (in Mbps).
- **Importance**: Indicates the overall pacing behavior of the session. Low pacing rates may suggest network throttling or congestion.

### 11. `MinRTT_ms`
- **Description**: The minimum round-trip time during the session (in milliseconds).
- **Importance**: Low RTT indicates better network conditions, which may reduce the likelihood of early termination.

### 12. `MaxRTT_ms`
- **Description**: The maximum round-trip time during the session (in milliseconds).
- **Importance**: High RTT may indicate network congestion or instability, which could lead to early termination.

### 13. `MeanRTT_ms`
- **Description**: The average round-trip time during the session (in milliseconds).
- **Importance**: Provides an overall measure of latency during the session. High latency may correlate with poor network performance.

### 14. `StdRTT_ms`
- **Description**: The standard deviation of round-trip time during the session (in milliseconds).
- **Importance**: High RTT variability may indicate unstable network conditions, which could lead to early termination.

### 15. `MaxCwnd_packets`
- **Description**: The maximum congestion window size (in packets).
- **Importance**: Larger congestion windows may indicate better network performance and higher throughput.

### 16. `MeanCwnd_packets`
- **Description**: The average congestion window size (in packets).
- **Importance**: Reflects the overall congestion control behavior during the session. Smaller windows may indicate network congestion.

### 17. `MaxRcvWindow_bytes`
- **Description**: The maximum receive window size (in bytes).
- **Importance**: Indicates the maximum buffer size available for receiving data. Larger windows may correlate with better performance.

### 18. `MeanRcvWindow_bytes`
- **Description**: The average receive window size (in bytes).
- **Importance**: Reflects the overall buffering behavior during the session. Smaller windows may indicate limited capacity.

### 19. `TotalBytesAcked_bytes`
- **Description**: The total bytes acknowledged during the session.
- **Importance**: Indicates the amount of data successfully transmitted. Higher values suggest better network performance.

### 20. `TotalBytesSent_bytes`
- **Description**: The total bytes sent during the session.
- **Importance**: Reflects the overall data transmission volume. Lower values may indicate early termination.

### 21. `TotalBytesReceived_bytes`
- **Description**: The total bytes received during the session.
- **Importance**: Indicates the amount of data successfully received. Lower values may indicate poor network conditions.

### 22. `TotalRetransmissions_count`
- **Description**: The total number of retransmissions during the session.
- **Importance**: High retransmissions may indicate poor network conditions, which could lead to early termination.

### 23. `LossRate_percent`
- **Description**: The percentage of lost packets during the session.
- **Importance**: High loss rates are a strong indicator of network issues, which may correlate with early termination.

### 24. `MaxDeliveryRate_Mbps`
- **Description**: The maximum delivery rate during the session (in Mbps).
- **Importance**: Reflects the peak data delivery performance. Higher rates suggest better network conditions.

### 25. `MeanDeliveryRate_Mbps`
- **Description**: The average delivery rate during the session (in Mbps).
- **Importance**: Indicates the overall delivery performance of the session. Lower rates may correlate with early termination.

### 26. `TotalBusyTime_microseconds`
- **Description**: The total time the network was busy during the session (in microseconds).
- **Importance**: High busy time may indicate network congestion, which could lead to early termination.

### 27. `MaxThroughput_Mbps`
- **Description**: The maximum throughput achieved during the session (in Mbps).
- **Importance**: High throughput often correlates with successful test completion and better network performance.

### 28. `MeanThroughput_Mbps`
- **Description**: The average throughput during the session (in Mbps).
- **Importance**: Reflects the overall data transfer efficiency. Lower throughput may indicate poor network conditions.

### 29. `MinThroughput_Mbps`
- **Description**: The minimum throughput during the session (in Mbps).
- **Importance**: Low throughput may indicate poor network conditions, which could lead to early termination.

### 30. `StdThroughput_Mbps`
- **Description**: The standard deviation of throughput during the session (in Mbps).
- **Importance**: High variability in throughput may indicate instability, which could lead to early termination.



## data collected for training ealry termination model 
<list all the colunms here>
<talk about how the labels are collected>


## File Descriptions

### **1. `extract_files.py`**
This script is responsible for extracting `.tar.gz` archives, finding `.gz` files within the extracted content, decompressing them into JSON files, and organizing the JSON files into a specified destination folder.

#### **Key Functions:**
1. **`extract_tarball(tarball_path, extract_folder)`**:
   - Extracts a `.tar.gz` archive into a specified folder.
   - Ensures the extraction folder exists before extracting.
   - Useful for handling large compressed archives containing multiple `.gz` files.

2. **`find_and_extract_gz_files(root_folder, json_destination)`**:
   - Recursively searches for `.gz` files in the extracted folder.
   - Decompresses each `.gz` file into a JSON file.
   - Moves the JSON files to a destination folder, ensuring unique filenames to avoid overwriting.
   - Validates the JSON structure to ensure the files are properly formatted.

#### **Usage**:
- **Step 1**: Extract a `.tar.gz` archive using `extract_tarball`.
- **Step 2**: Process the extracted folder to find `.gz` files, decompress them, and move the resulting JSON files to a destination folder.

#### **Output**:
- A folder containing all the extracted and validated JSON files.

---

### **2. `preprocessing.py`**
This script processes the extracted JSON files to extract relevant features for building a regression model. It reads the JSON files, extracts network performance metrics, and saves the processed data into a CSV file.

#### **Key Functions:**
1. **`extract_ndt7_features(json_file)`**:
   - Reads a single JSON file and extracts key features related to network performance.
   - Handles metrics such as bandwidth, RTT (latency), congestion window size, retransmissions, and throughput.
   - Computes session-level statistics (e.g., max, mean, min, standard deviation) for each metric.
   - Returns a dictionary of extracted features for the session.

2. **`process_json_folder(folder_path, output_csv)`**:
   - Processes all JSON files in a specified folder.
   - Calls `extract_ndt7_features` for each file to extract features.
   - Aggregates the extracted features into a Pandas DataFrame.
   - Saves the DataFrame to a CSV file for further analysis.

#### **Usage**:
- **Step 1**: Provide the folder containing JSON files.
- **Step 2**: Specify the output CSV filename.
- The script processes all JSON files, extracts features, and saves them to the CSV.

#### **Output**:
- A CSV file containing session-level features for all processed JSON files.

---

### **How These Files Work Together**
1. **`extract_files.py`**:
   - Extracts `.tar.gz` archives and decompresses `.gz` files into JSON files.
   - Organizes the JSON files into a single folder for easy processing.

2. **`preprocessing.py`**:
   - Processes the JSON files extracted by `extract_files.py`.
   - Extracts relevant features and saves them into a structured CSV file for analysis and modeling.

---

### **Example Workflow**
1. **Extract `.tar.gz` Archive**:
   - Run `extract_files.py` to extract the `.tar.gz` archive and decompress `.gz` files into JSON files.
   - Example:
     ```bash
     python extract_files.py
     ```
   - Output: A folder containing all extracted JSON files.

2. **Process JSON Files**:
   - Run [preprocessing.py](http://_vscodecontentref_/0) to extract features from the JSON files and save them into a CSV file.
   - Example:
     ```bash
     python preprocessing.py
     ```
   - Output: A CSV file (e.g., [ndt7_features.csv](http://_vscodecontentref_/1)) containing extracted features.

---

### **Conclusion**
- **`extract_files.py`**: Handles the extraction and organization of raw data files.
- **`preprocessing.py`**: Processes the raw data to extract meaningful features for analysis and modeling.
- Together, these scripts streamline the process of preparing network performance data for building regression models.

## Conclusion

The attributes in this dataset provide a comprehensive view of network performance during speed tests. By analyzing these attributes, we can build a robust regression model to predict early termination and identify the key factors contributing to it. This analysis can help improve network performance and user experience.
