import json
import csv
import os
import numpy as np

def extract_and_save_tcp_info(json_file_path, time_threshold_seconds):
    """
    Extracts TCPInfo data from a JSON file, filters it based on elapsed time,
    performs feature engineering, and calculates the average bandwidth for the entire session.

    Args:
        json_file_path (str): Path to the input JSON file.
        time_threshold_seconds (float): The time threshold in seconds.

    Returns:
        tuple: (list of engineered features, average bandwidth)
    """
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        # Check for the existence of the "Download" and "ServerMeasurements" keys
        if "Download" not in data or "ServerMeasurements" not in data["Download"]:
            print(f"Error: Input JSON file {json_file_path} is not in the expected format.  'Download' or 'ServerMeasurements' key is missing.")
            return [], None  # Return empty list to indicate no data

        measurements = data["Download"]["ServerMeasurements"]

        # Calculate average bandwidth for the entire session
        total_bw = 0
        bw_count = 0
        for measurement in measurements:
            bbr_info = measurement.get("BBRInfo")
            if bbr_info and "BW" in bbr_info:
                total_bw += bbr_info["BW"]
                bw_count += 1
        average_bandwidth = total_bw / bw_count if bw_count else None

        # Filter measurements for TCPInfo and elapsed time
        filtered_tcp_info = []
        for measurement in measurements:
            if ("TCPInfo" in measurement and
                    measurement.get("TCPInfo") is not None and
                    "ElapsedTime" in measurement["TCPInfo"] and
                    measurement["TCPInfo"]["ElapsedTime"] <= time_threshold_seconds * 1e6):
                filtered_tcp_info.append(measurement)

        if not filtered_tcp_info:
            print(f"Warning: No TCPInfo data found within the first {time_threshold_seconds} seconds in {json_file_path}.")
            return [], None  # Return empty list and None for no bandwidth

        # Feature extraction and engineering
        engineered_features = []
        cumulative_total_retrans = 0
        cumulative_bytes_transferred = 0
        rtt_window = []
        cwnd_window = []
        pacing_rate_history = []
        prev_pacing_rate = None

        for i, measurement in enumerate(filtered_tcp_info):
            tcp_info = measurement["TCPInfo"]
            connection_info = measurement.get("ConnectionInfo")
            uuid = connection_info.get("UUID") if connection_info else None
            bbr_info = measurement.get("BBRInfo")
            bw = bbr_info.get("BW") if bbr_info else None
            elapsed_time = tcp_info.get("ElapsedTime")

            # Simple features
            rtt = tcp_info.get("RTT")
            rtt_var = tcp_info.get("RTTVar")
            busy_time = tcp_info.get("BusyTime")
            min_rtt = tcp_info.get("MinRTT")
            pacing_gain = bbr_info.get("PacingGain") if bbr_info else None
            cwnd_gain = bbr_info.get("CwndGain") if bbr_info else None
            delivery_rate = tcp_info.get("DeliveryRate")
            pacing_rate = tcp_info.get("PacingRate")
            retransmits = tcp_info.get("Retransmits", 0)

            # Cumulative features
            cumulative_total_retrans += retransmits
            cumulative_bytes_transferred += tcp_info.get("BytesAcked", 0) + tcp_info.get("BytesReceived", 0)

            # Average features
            rtt_window.append(tcp_info.get("RTT", 0))
            cwnd_window.append(tcp_info.get("SndCwnd", 0))
            avg_rtt_window = np.mean(rtt_window) if rtt_window else 0
            avg_cwnd_window = np.mean(cwnd_window) if cwnd_window else 0

            # Rate of Change of Pacing Rate
            rate_of_change_pacing_rate = None
            if prev_pacing_rate is not None and elapsed_time is not None:
                time_diff = elapsed_time  # in microseconds
                rate_of_change_pacing_rate = (pacing_rate - prev_pacing_rate) / (time_diff / 1e6)  # per second
            prev_pacing_rate = pacing_rate

            # Ratio of Busy Time to Elapsed Time
            ratio_busy_time_elapsed_time = (busy_time / elapsed_time) if elapsed_time else None

            # Delivery Rate vs. Pacing Rate
            delivery_rate_vs_pacing_rate = None
            if pacing_rate is not None and delivery_rate is not None:
                delivery_rate_vs_pacing_rate = delivery_rate / pacing_rate if pacing_rate != 0 else None

            # Change in Pacing Gain/Cwnd Gain:
            change_pacing_gain = None
            change_cwnd_gain = None
            if i > 0:
                prev_measurement = filtered_tcp_info[i-1]
                prev_bbr_info = prev_measurement.get("BBRInfo")
                prev_pacing_gain = prev_bbr_info.get("PacingGain") if prev_bbr_info else None
                prev_cwnd_gain = prev_bbr_info.get("CwndGain") if prev_bbr_info else None
                if prev_pacing_gain is not None and pacing_gain is not None:
                    change_pacing_gain = pacing_gain - prev_pacing_gain
                if prev_cwnd_gain is not None and cwnd_gain is not None:
                    change_cwnd_gain = cwnd_gain - prev_cwnd_gain

            # Retransmission Rate
            retransmission_rate = (retransmits / (elapsed_time / 1e6)) if elapsed_time else 0 # retransmits per second


            # Combine features into a dictionary
            features = {
                "UUID": uuid,
                "ElapsedTime": elapsed_time,
                "RTT": rtt,
                "RTTVar": rtt_var,
                "BusyTime": busy_time,
                "MinRTT": min_rtt,
                "CumulativeTotalRetrans": cumulative_total_retrans,
                "CumulativeBytesTransferred": cumulative_bytes_transferred,
                "AvgRTTWindow": avg_rtt_window,
                "AvgCwndWindow": avg_cwnd_window,
                "RateOfChangePacingRate": rate_of_change_pacing_rate,
                "RatioBusyTimeElapsedTime": ratio_busy_time_elapsed_time,
                "PacingGain": pacing_gain,
                "CwndGain": cwnd_gain,
                "DeliveryRateVsPacingRate": delivery_rate_vs_pacing_rate,
                "ChangePacingGain": change_pacing_gain,
                "ChangeCwndGain": change_cwnd_gain,
                "RetransmissionRate": retransmission_rate,
                "BW": bw, # Keep instantaneous BW here
            }
            engineered_features.append(features)
        return engineered_features, average_bandwidth

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file {json_file_path}: {e}")
        return [], None  # Return empty list and None for no bandwidth
    except KeyError as e:
        print(f"Error: Missing key in JSON file {json_file_path}: {e}")
        return [], None  # Return empty list and None for no bandwidth
    except Exception as e:
        print(f"An unexpected error occurred while processing {json_file_path}: {e}")
        return [], None  # Return empty list and None for no bandwidth



def process_files_in_folder(folder_path, time_threshold_seconds):
    """
    Processes all JSON files in a folder, extracts TCPInfo data,
    performs feature engineering, and saves the combined data to a single CSV file.

    Args:
        folder_path (str): Path to the folder containing the JSON files.
        time_threshold_seconds (float): The time threshold in seconds.
    """
    all_data = []
    header_set = set()
    file_count = 0
    all_labels = []
    all_uuids = []  # To store UUIDs and check for consistency
    session_avg_bandwidth = {}  # Dictionary to store average bandwidth for each session
    output_csv_path = f"combined_sec{int(time_threshold_seconds)}_data.csv"

    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            file_count += 1
            print(f"Processing file: {file_path}")
            engineered_features, avg_bandwidth = extract_and_save_tcp_info(file_path, time_threshold_seconds=time_threshold_seconds)
            if engineered_features:
                # Get all unique keys from the TCPInfo entries to use as headers
                for info in engineered_features:
                    if info:
                        header_set.update(info.keys())
                all_data.extend(engineered_features)
                all_labels.append(avg_bandwidth)
                #  Assuming all rows from the same file have the same UUID
                uuid = engineered_features[0].get("UUID")
                all_uuids.extend([uuid] * len(engineered_features))
                session_avg_bandwidth[uuid] = avg_bandwidth  # Store average BW for this session
            else:
                all_labels.append(None)
                all_uuids.append(None)

    if not all_data:
        print(f"No TCPInfo data found within the first {time_threshold_seconds} seconds in any JSON file in the folder.  No CSV file will be created.")
        return

    headers = sorted(list(header_set))  # Sort headers for consistency
    headers.append("AverageBandwidth")  # Add the label to the headers

    # Write the combined data to a CSV file
    with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for i, row in enumerate(all_data):
            uuid = row.get("UUID")
            #  Handle the case where a file had no valid data, resulting in a None label.
            if uuid in session_avg_bandwidth and session_avg_bandwidth[uuid] is not None:
                row["AverageBandwidth"] = session_avg_bandwidth[uuid]
            else:
                row["AverageBandwidth"] = "N/A"
            writer.writerow({k: v if v is not None else '' for k, v in row.items()})

    print(f"Successfully processed {file_count} JSON files and saved the combined data (up to {time_threshold_seconds} seconds) to {output_csv_path}")



if __name__ == "__main__":
    # Specify the path to your folder containing the JSON files
    folder_path = "./extracted_json"  # Replace with the actual path to your folder
    # Specify the time thresholds
    time_thresholds = [2.0, 3.0, 4.0, 5.0]

    for time_threshold in time_thresholds:
        process_files_in_folder(folder_path, time_threshold_seconds=time_threshold)

