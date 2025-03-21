import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Step 1: Load the Dataset
df = pd.read_csv("ndt7_features.csv")

# Step 2: Select Features and Target
features = [
    "SessionDuration_seconds", "NumFlows", "MaxBandwidth_Mbps", "MeanBandwidth_Mbps",
    "MinBandwidth_Mbps", "StdBandwidth_Mbps", "MaxPacingRate_Mbps", "MeanPacingRate_Mbps",
    "MinRTT_ms", "MaxRTT_ms", "MeanRTT_ms", "StdRTT_ms", "LossRate_percent",
    "TotalRetransmissions_count", "MaxDeliveryRate_Mbps", "MeanDeliveryRate_Mbps",
    "TotalBusyTime_microseconds"
]

target = "MeanThroughput_Mbps"

X = df[features]
y = df[target]

# Step 3: Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Feature Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Step 5: Train Model (Using Random Forest)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Step 6: Predict on Test Data
y_pred = model.predict(X_test_scaled)

# Step 7: Evaluate Model
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"Model Performance:")
print(f"MAE: {mae:.3f} Mbps")
print(f"RMSE: {rmse:.3f} Mbps")
print(f"R² Score: {r2:.3f}")

# Step 8: Plot Predictions vs Actual
plt.figure(figsize=(8, 6))
sns.scatterplot(x=y_test, y=y_pred)
plt.xlabel("Actual Throughput (Mbps)")
plt.ylabel("Predicted Throughput (Mbps)")
plt.title("Actual vs Predicted Throughput")
plt.show()
