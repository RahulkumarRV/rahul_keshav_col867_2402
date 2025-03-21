import json
import numpy as np
import pandas as pd
import os

def extract_ndt7_features(json_file):
    try:
        with open(json_file, "r") as f:
            data = json.load(f)

        # Check if the required data structure exists
        if "Download" not in data or "ServerMeasurements" not in data["Download"] or "UUID" not in data["Download"]:
            print(f"Warning: Invalid JSON structure in {json_file}, skipping...")
            return None

        server_measurements = data["Download"]["ServerMeasurements"]
        session_uuid = data["Download"]["UUID"]

        # If there are no server measurements, skip
        if not server_measurements:
            print(f"Warning: No server measurements in {json_file}, skipping...")
            return None

        # Initialize lists for flow-level metrics
        bandwidths, pacing_rates, rtts, retransmissions, delivery_rates = [], [], [], [], []
        congestion_windows, rcv_windows, segs_out, segs_in = [], [], [], []
        busy_times, bytes_acked, bytes_sent, bytes_retrans, bytes_received = [], [], [], [], []
        throughputs = []

        min_rtt, max_rtt, avg_rtt, std_rtt = [], [], [], []

        for flow in server_measurements:
            bbr_info = flow.get("BBRInfo", {})
            tcp_info = flow.get("TCPInfo", {})

            # Bandwidth related (in Mbps)
            bandwidths.append(bbr_info.get("BW", 0) / 1e6)  # Convert bits/sec to Mbps
            pacing_rates.append(tcp_info.get("PacingRate", 0) / 1e6)  # Convert bits/sec to Mbps
            
            # Latency related (RTT in milliseconds)
            rtt = tcp_info.get("RTT", 0) / 1000  # Convert microseconds to milliseconds
            min_rtt.append(bbr_info.get("MinRTT", 0) / 1000)
            max_rtt.append(rtt)
            avg_rtt.append(rtt)
            std_rtt.append(tcp_info.get("RTTVar", 0) / 1000)

            # Congestion & buffering (in packets)
            congestion_windows.append(tcp_info.get("SndCwnd", 0))
            rcv_windows.append(tcp_info.get("RcvSpace", 0))

            # Packet Transmission (in count)
            segs_out.append(tcp_info.get("SegsOut", 0))
            segs_in.append(tcp_info.get("SegsIn", 0))
            bytes_acked.append(tcp_info.get("BytesAcked", 0))
            bytes_sent.append(tcp_info.get("BytesSent", 0))
            bytes_retrans.append(tcp_info.get("BytesRetrans", 0))
            bytes_received.append(tcp_info.get("BytesReceived", 0))

            # Throughput Calculation (in Mbps)
            elapsed_time = tcp_info.get("ElapsedTime", 1) / 1e6  # Convert microseconds to seconds
            throughput = (tcp_info.get("BytesAcked", 0) * 8) / (elapsed_time * 1e6) if elapsed_time > 0 else 0  # Convert to Mbps
            throughputs.append(throughput)

            # Loss & Retransmissions (in count)
            retransmissions.append(tcp_info.get("Retrans", 0))

            # Delivery Rate (in Mbps)
            delivery_rates.append(tcp_info.get("DeliveryRate", 0) / 1e6)  # Convert bits/sec to Mbps

            # Network Load (in microseconds)
            busy_times.append(tcp_info.get("BusyTime", 0))

        # Safely compute session-level statistics, handle empty arrays
        session_features = {
            "uuid": session_uuid,
            "filename": os.path.basename(json_file),
            "SessionDuration_seconds": 0  # Default value
        }

        # Try to calculate session duration
        try:
            session_features["SessionDuration_seconds"] = (pd.to_datetime(data["Download"]["EndTime"]) - 
                                                          pd.to_datetime(data["Download"]["StartTime"])).total_seconds()
        except (KeyError, TypeError, ValueError) as e:
            print(f"Warning: Could not calculate session duration for {json_file}: {e}")

        # Add remaining features
        if len(server_measurements) > 0:
            session_features.update({
                "NumFlows": len(server_measurements),
                
                # Bandwidth Features
                "MaxBandwidth_Mbps": np.max(bandwidths) if bandwidths else 0,
                "MeanBandwidth_Mbps": np.mean(bandwidths) if bandwidths else 0,
                "MinBandwidth_Mbps": np.min(bandwidths) if bandwidths else 0,
                "StdBandwidth_Mbps": np.std(bandwidths) if bandwidths else 0,
                
                # Pacing Features
                "MaxPacingRate_Mbps": np.max(pacing_rates) if pacing_rates else 0,
                "MeanPacingRate_Mbps": np.mean(pacing_rates) if pacing_rates else 0,
                
                # RTT Features (in milliseconds)
                "MinRTT_ms": np.min(min_rtt) if min_rtt else 0,
                "MaxRTT_ms": np.max(max_rtt) if max_rtt else 0,
                "MeanRTT_ms": np.mean(avg_rtt) if avg_rtt else 0,
                "StdRTT_ms": np.mean(std_rtt) if std_rtt else 0,
                
                # Congestion Features (in packets)
                "MaxCwnd_packets": np.max(congestion_windows) if congestion_windows else 0,
                "MeanCwnd_packets": np.mean(congestion_windows) if congestion_windows else 0,
                
                # TCP Window Features (in bytes)
                "MaxRcvWindow_bytes": np.max(rcv_windows) if rcv_windows else 0,
                "MeanRcvWindow_bytes": np.mean(rcv_windows) if rcv_windows else 0,
                
                # Packet Transmission Features (in bytes)
                "TotalBytesAcked_bytes": np.sum(bytes_acked) if bytes_acked else 0,
                "TotalBytesSent_bytes": np.sum(bytes_sent) if bytes_sent else 0,
                "TotalBytesReceived_bytes": np.sum(bytes_received) if bytes_received else 0,
                
                # Packet Loss & Retransmissions (in count & percentage)
                "TotalRetransmissions_count": np.sum(retransmissions) if retransmissions else 0,
                "LossRate_percent": (np.sum(bytes_retrans) / np.sum(bytes_sent)) * 100 if (np.sum(bytes_sent) > 0 and bytes_retrans) else 0,
                
                # Delivery Rate Features (in Mbps)
                "MaxDeliveryRate_Mbps": np.max(delivery_rates) if delivery_rates else 0,
                "MeanDeliveryRate_Mbps": np.mean(delivery_rates) if delivery_rates else 0,
                
                # Network Load Features (in microseconds)
                "TotalBusyTime_microseconds": np.sum(busy_times) if busy_times else 0,

                # Throughput Features (in Mbps)
                "MaxThroughput_Mbps": np.max(throughputs) if throughputs else 0,
                "MeanThroughput_Mbps": np.mean(throughputs) if throughputs else 0,
                "MinThroughput_Mbps": np.min(throughputs) if throughputs else 0,
                "StdThroughput_Mbps": np.std(throughputs) if throughputs else 0,
            })

        return session_features
    
    except Exception as e:
        print(f"Error processing {json_file}: {str(e)}")
        return None

def process_json_folder(folder_path, output_csv):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist")
        return
    
    # Get all JSON files from the folder
    json_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                 if f.lower().endswith('.json') and os.path.isfile(os.path.join(folder_path, f))]
    
    if not json_files:
        print(f"No JSON files found in '{folder_path}'")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    # Process all files
    all_features = []
    
    for i, json_file in enumerate(json_files):
        print(f"Processing file {i+1}/{len(json_files)}: {os.path.basename(json_file)}")
        features = extract_ndt7_features(json_file)
        if features:
            all_features.append(features)
    
    if not all_features:
        print("No valid features extracted from any files")
        return
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(all_features)
    df.to_csv(output_csv, index=False)
    print(f"Features from {len(all_features)} files saved to {output_csv}")
    print(f"CSV contains {len(df.columns)} columns with the following features:")
    print(", ".join(df.columns.tolist()))

if __name__ == "__main__":
    # Get folder path from user
    folder_path = input("Enter the folder path containing JSON files: ")
    output_csv = input("Enter the output CSV filename (default: ndt7_features.csv): ") or "ndt7_features.csv"
    
    process_json_folder(folder_path, output_csv)