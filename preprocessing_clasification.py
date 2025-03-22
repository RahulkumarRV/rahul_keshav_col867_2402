import os
import json
import pandas as pd
import numpy as np
from glob import glob

# Define function to process a single JSON file
def process_ndt7_file(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    download_data = data.get("Download", {})
    server_measurements = download_data.get("ServerMeasurements", [])
    serssion_id = download_data.get("UUID")
    
    if not server_measurements:
        return None
    
    records = []
    for entry in server_measurements:
        bbr_info = entry.get("BBRInfo", {})
        tcp_info = entry.get("TCPInfo", {})
        
        if not tcp_info:
            continue
        
        # Extract raw features
        record = {**bbr_info, **tcp_info}
        record["ElapsedTime"] = tcp_info.get("ElapsedTime", 1) / 1e6  # Convert microseconds to seconds
        record['UUID'] = serssion_id
        # Compute throughput
        record["Throughput_DeliveryRate"] = (tcp_info.get("DeliveryRate", 0) * 8) / 1e6  # Mbps
        record["Throughput_BytesAcked"] = (tcp_info.get("BytesAcked", 0) * 8) / (record["ElapsedTime"] * 1e6)  # Mbps
        record["Throughput_SegsOut"] = (tcp_info.get("SegsOut", 0) * tcp_info.get("SndMSS", 1) * 8) / (record["ElapsedTime"] * 1e6)  # Mbps
        
        records.append(record)
    
    if not records:
        return None
    
    df = pd.DataFrame(records)
    total_duration = df["ElapsedTime"].max()
    
    # Derived Features
    df["Latency"] = df["MinRTT"] / 1000  # Convert MinRTT to ms
    df["LossRatio"] = (df["Lost"] / (df["Lost"] + df["Unacked"] + 1)).fillna(0)  # Avoid division by zero
    df["Retransmit_Ratio"] = (df["Retrans"] / (df["Lost"] + 1)).fillna(0)
    
    # Compute session-wide mean throughput
    session_mean_throughput = df[["Throughput_DeliveryRate", "Throughput_BytesAcked", "Throughput_SegsOut"]].mean().mean()
    
    # Find the escape time based on closest throughput match
    closest_throughput_row = df.iloc[(df[["Throughput_DeliveryRate", "Throughput_BytesAcked", "Throughput_SegsOut"]].mean(axis=1) - session_mean_throughput).abs().idxmin()]
    escape_time = closest_throughput_row["ElapsedTime"]
    df["Escape_Time"] = escape_time  # Assign escape time to all entries
    
    # Rolling statistics
    df["Throughput_Mean"] = df[["Throughput_DeliveryRate", "Throughput_BytesAcked", "Throughput_SegsOut"]].mean(axis=1)
    df["Latency_Mean"] = df["Latency"].rolling(3, min_periods=1).mean()
    df["Loss_Trend"] = df["LossRatio"].diff().fillna(0)
    
    return df

# Process all JSON files and combine results
def create_dataset(json_folder, output_csv="ndt7_dataset.csv"):
    all_files = glob(os.path.join(json_folder, "*.json"))
    dataset = []
    
    for file in all_files:
        df = process_ndt7_file(file)
        if df is not None:
            dataset.append(df)
    
    if dataset:
        final_df = pd.concat(dataset, ignore_index=True)
        final_df.to_csv(output_csv, index=False)
        print(f"Dataset saved: {output_csv}")
    else:
        print("No valid data extracted from any files. Dataset creation skipped.")

# Example usage
json_folder = "extracted_json"  # Change to the correct path
create_dataset(json_folder)
