def prac_1():
  print("""
  print("Practical 1: Fitting and plotting of modified exponential curve")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import seaborn as sns

# Load the CO2 dataset
path = "co2-ppm-daily.csv"
data = pd.read_csv(path)

# Convert 'date' to datetime format
data['date'] = pd.to_datetime(data['date'])

# Sort by date to keep the data in time order
data.sort_values('date', inplace=True)

# Create a 'Time' column: number of days since the first date
data['Time'] = (data['date'] - data['date'].min()).dt.days

# Define x (independent) and y (dependent) data
x_data = data['date']
y_data = data['value']
x_neumerical = data['Time']

# Plot the original CO2 emission data
plt.figure(figsize=(12, 6))
plt.plot(x_data, y_data, label='CO2 Emission')
plt.xlabel('Year')
plt.ylabel('CO2 (ppm)')
plt.title('Daily CO2 Emission Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Step 1: Define the exponential model function
def mod_exp_func(t, a, b, c):
    return a * np.exp(b * t) + c

# Step 2: Initial guess for a, b, c
a_guess = y_data.iloc[0]
middle_index = len(x_data) // 2
year_mid = pd.to_datetime(x_data.iloc[middle_index]).year
b_guess = 1 / year_mid
c_guess = y_data.iloc[0]

print(f"Initial guess values: a = {a_guess:.2f}, b = {b_guess:.5f}, c = {c_guess:.2f}")

# Step 3: Fit the model to the data
p0 = (a_guess, b_guess, c_guess)
popt, pcov = curve_fit(mod_exp_func, x_neumerical, y_data, p0=p0, maxfev=8000)

# Step 4: Print optimized parameters
print(f"\nOptimized values: a = {popt[0]:.2f}, b = {popt[1]:.5f}, c = {popt[2]:.2f}")
print("\nCovariance matrix of parameters:")
print(pcov)

# Step 5: Plot covariance heatmap
plt.figure(figsize=(6, 4))
sns.heatmap(pcov, cmap='coolwarm', annot=True, fmt=".2e")
plt.title("Covariance Matrix Heatmap")
plt.tight_layout()
plt.show()

# Step 6: Plot fitted curve with original data
fitted_y = mod_exp_func(x_neumerical, *popt)

plt.figure(figsize=(12, 6))
plt.plot(x_data, y_data, label='Original CO2 Emission')
plt.plot(x_data, fitted_y, color='red', label='Exponential Fit', linestyle='--')
plt.xlabel('Year')
plt.ylabel('CO2 (ppm)')
plt.title('CO2 Emission with Exponential Curve Fit')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
  """)

def prac_2():
  print("""
  print("practical 2: ")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import seaborn as sns

# Load the stock price dataset
path = "stock_price_txt.txt"
stock = pd.read_csv(path, sep='\s+')

# Combine date + time into one datetime column
stock['Datetime'] = pd.to_datetime(
    stock['date'].astype(str) + ' ' +
    stock['hour'].astype(str) + ':' +
    stock['minute'].astype(str) + ':' +
    stock['second'].astype(str)
)

# Drop the original separate columns
stock.drop(['date', 'hour', 'minute', 'second'], axis=1, inplace=True)

# Sort and set index
stock.sort_values('Datetime', inplace=True)
stock.set_index('Datetime', inplace=True)

# Prepare data for fitting
x_data = stock.index
y_data = stock['price']
x_numeric = (x_data - x_data.min()).total_seconds()

# Plot original stock price data
plt.figure(figsize=(12, 6))
plt.plot(x_data, y_data, label='Stock Price')
plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Stock Price Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Gompertz curve function
def gompertz_curve(t, a, b, c):
    return a * np.exp(b * np.exp(-c * t))

# Initial guess for parameters a, b, c
a_guess = y_data.iloc[0]
middle_index = len(x_data) // 2
year_mid = x_data[middle_index].year
c_guess = 1 / year_mid
b_guess = np.exp(c_guess * year_mid)

print(f"Initial guess: a = {a_guess:.2f}, b = {b_guess:.2f}, c = {c_guess:.5f}")

# Fit the curve
p0 = (a_guess, b_guess, c_guess)
popt, pcov = curve_fit(gompertz_curve, x_numeric, y_data, p0=p0, maxfev=8000)

print(f"\nOptimized parameters: a = {popt[0]:.2f}, b = {popt[1]:.5f}, c = {popt[2]:.5f}")
print("\nCovariance matrix:")
print(pcov)

# Heatmap of parameter confidence
plt.figure(figsize=(6, 4))
sns.heatmap(pcov, annot=True, fmt=".2e", cmap="coolwarm")
plt.title("Covariance Matrix Heatmap")
plt.tight_layout()
plt.show()

# Predict and plot fitted curve
y_pred = gompertz_curve(x_numeric, *popt)

plt.figure(figsize=(12, 6))
plt.plot(x_data, y_data, label='Original Data')
plt.plot(x_data, y_pred, '--', color='red', label='Fitted Gompertz Curve')
plt.xlabel('Date')
plt.ylabel('Stock Price')
plt.title('Stock Price and Gompertz Curve Fit')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
  """)

def prac_3():
  print("""
  print("prac3 :  Fitting and plotting of logistic curve")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import seaborn as sns

# Load the microbial growth data
path = "microbial_growth_curve.csv"
data = pd.read_csv(path)

# Extract time (x) and growth (y)
x_data = data['t [h]']
y_data = data['microbes(g)']

# Convert time to numerical scale starting from 0
x_numerical = x_data - x_data.min()

# Plot the original microbial growth data
plt.figure(figsize=(12, 6))
plt.plot(x_data, y_data, label='Microbial Growth')
plt.xlabel('Time (hours)')
plt.ylabel('Growth (g)')
plt.title('Microbes Growth Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Define the logistic growth curve function
def logistic_curve(t, k, r, t0):
    return k / (1 + np.exp(-r * (t - t0)))

# Step 1: Initial guesses
k_guess = max(y_data)            # Max value of growth
t0_guess = x_data.median()       # Middle time point
r_guess = 0.1                    # Reasonable growth rate guess

print(f"Initial guess: k = {k_guess:.2f}, r = {r_guess:.3f}, t0 = {t0_guess:.2f}")

# Step 2: Fit the logistic model
p0 = (k_guess, r_guess, t0_guess)
popt, pcov = curve_fit(logistic_curve, x_numerical, y_data, p0=p0, maxfev=10000)

# Step 3: Print fitted parameters
print(f"\nOptimized parameters: k = {popt[0]:.4f}, r = {popt[1]:.6f}, t0 = {popt[2]:.4f}")
print("\nCovariance matrix:")
print(pcov)

# Step 4: Heatmap of confidence in parameters
plt.figure(figsize=(6, 4))
sns.heatmap(pcov, annot=True, fmt=".2e", cmap='coolwarm')
plt.title("Covariance Matrix Heatmap")
plt.tight_layout()
plt.show()

# Step 5: Predict and plot the fitted curve
y_pred = logistic_curve(x_numerical, *popt)

plt.figure(figsize=(12, 6))
plt.plot(x_data, y_data, label='Original Data')
plt.plot(x_data, y_pred, '--', color='red', label='Logistic Fit')
plt.xlabel('Time (hours)')
plt.ylabel('Growth (g)')
plt.title('Microbial Growth and Fitted Logistic Curve')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
  """)


def prac_4():
  print("""
  print("practical 4 : Fitting of trend by Moving Average Method")
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load dataset and clean it
path = r"Symphony-Data.csv"
df = pd.read_csv(path)

# Keep only the columns we need
df = df[['DATE', 'PRICE']]
df['DATE'] = pd.to_datetime(df['DATE'], format='%d-%b-%y')
df = df.sort_values(by='DATE')

# Step 2: Calculate 30-day moving average (trend)
df['Moving_Avg'] = df['PRICE'].rolling(window=30).mean()


# Step 3: Calculate trend (rate of change of moving average)
df['Trend'] = df['Moving_Avg'].diff()

# Step 4: Calculate seasonal variation (actual - trend)
df['Seasonal_Variation'] = df['PRICE'] - df['Moving_Avg']

# Step 5: Plot original vs moving average
plt.figure(figsize=(12, 6))
plt.plot(df['DATE'], df['PRICE'], label='Raw Price Data')
plt.plot(df['DATE'], df['Moving_Avg'], label='30-Day Moving Average', color='orange')
plt.xlabel('Date')
plt.ylabel('Price (Rs.)')
plt.title('Stock Price and Moving Average')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Step 6: Plot trend and seasonal variation
plt.figure(figsize=(12, 6))
plt.plot(df['DATE'], df['Trend'], label='Trend', color='green')
plt.plot(df['DATE'], df['Seasonal_Variation'], label='Seasonal Variation', color='red')
plt.xlabel('Date')
plt.ylabel('Price Difference')
plt.title('Trend and Seasonal Variation')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
  """)


def prac_5():
  print("""
print(" Measurement of Seasonal indices Ratio-to-Trend metho")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Step 1: Load and clean the dataset
path = r"Symphony-Data.csv"
df = pd.read_csv(path)
df = df[['DATE', 'PRICE']]
df['DATE'] = pd.to_datetime(df['DATE'], format='%d-%b-%y')
df = df.sort_values('DATE')

# Step 2: Extract Year and Month
df['Year'] = df['DATE'].dt.year
df['Month'] = df['DATE'].dt.month

# Step 3: Calculate monthly average price per year
monthly_mean = df.groupby(['Month', 'Year'])['PRICE'].mean().unstack()

# Step 4: Plot month-wise average stock prices
for year in monthly_mean.columns:
    plt.plot(monthly_mean.index, monthly_mean[year], marker='o', label=str(year))
plt.legend()
plt.title('Month-wise Avg Stock Price')
plt.xlabel('Month')
plt.ylabel('Avg Price (Rs.)')
plt.grid(True)
plt.tight_layout()
plt.show()

# Step 5: Calculate yearly trend (mean)
yearly_means = monthly_mean.mean()
plt.plot(yearly_means.index, yearly_means.values, marker='o')
plt.title('Yearly Trend (Mean Price)')
plt.xlabel('Year')
plt.ylabel('Avg Price (Rs.)')
plt.grid(True)
plt.tight_layout()
plt.show()

# Step 6: Compute Ratio-to-Trend = month avg / yearly avg
ratios = monthly_mean.copy()
for year in monthly_mean.columns:
    ratios[year] = monthly_mean[year] / yearly_means[year]

# Step 7: Calculate seasonal indices (average of ratios)
seasonal_indices = ratios.mean(axis=1)
seasonal_indices = seasonal_indices.reindex(range(1, 13), fill_value=np.nan)

# Plot normalized seasonal indices
plt.plot(seasonal_indices.index, seasonal_indices.values, marker='o')
plt.title('Normalized Seasonal Indices')
plt.xlabel('Month')
plt.ylabel('Index Value')
plt.grid(True)
plt.tight_layout()
plt.show()

# Step 8: Deseasonalize the prices (Actual / Seasonal Index)
monthly_avg = df.groupby(['Year', 'Month'])['PRICE'].mean().unstack()
deseasonalized = monthly_avg.copy()

for month in range(1, 13):
    if not np.isnan(seasonal_indices[month]) and month in deseasonalized.columns:
        deseasonalized[month] = deseasonalized[month] / seasonal_indices[month]

# Step 9: Plot deseasonalized data
deseasonalized = deseasonalized.T  # Transpose for better plotting
for year in deseasonalized.columns:
    plt.plot(deseasonalized.index, deseasonalized[year], marker='o', label=str(year))
plt.title('Deseasonalized Stock Prices')
plt.xlabel('Month')
plt.ylabel('Price (Rs.)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
  """)


def prac_6():
  print("""
print("Practical 6: Measurement of Seasonal indices Ratio-to-Moving Average method")
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load and clean dataset
path = r"Symphony-Data2.csv"
df = pd.read_csv(path)
df = df[['DATE', 'PRICE']]
df['DATE'] = pd.to_datetime(df['DATE'], format="%d-%b-%y")
df = df.sort_values('DATE')

# Step 2: Extract Year and Month
df['Year'] = df['DATE'].dt.year
df['Month'] = df['DATE'].dt.month

# Step 3: Calculate monthly average prices per year
monthly_avg = df.groupby(['Month', 'Year'])['PRICE'].mean().unstack()

# Step 4: Compute overall monthly averages across years
monthly_avg['Monthly_Average'] = monthly_avg.mean(axis=1)

# Step 5: Calculate Centered Moving Average (CMA) of Monthly_Average
monthly_avg['Centered_MA'] = monthly_avg['Monthly_Average'].rolling(window=2, center=True).mean()

# Step 6: Ratio of Actual to CMA
monthly_avg['Ratio'] = monthly_avg['Monthly_Average'] / monthly_avg['Centered_MA']

# Step 7: Normalize Seasonal Indices
sum_ratios = monthly_avg['Ratio'].sum()
monthly_avg['Seasonal_Index'] = monthly_avg['Ratio'] * (len(monthly_avg) / sum_ratios)

# Step 8: Deseasonalize data for each year
for year in range(2019, 2025):
    monthly_avg[f'Deseasonalized_{year}'] = monthly_avg[year] / monthly_avg['Seasonal_Index']

# Step 9: Plot the results
plt.figure(figsize=(14, 10))

# 1. Original Data
plt.subplot(3, 1, 1)
for year in range(2019, 2025):
    plt.plot(monthly_avg.index, monthly_avg[year], marker='o', label=str(year))
plt.title('Original Monthly Stock Prices')
plt.ylabel('Price (Rs.)')
plt.legend()

# 2. Seasonal Index
plt.subplot(3, 1, 2)
plt.plot(monthly_avg.index, monthly_avg['Seasonal_Index'], marker='o', color='orange', label='Seasonal Index')
plt.title('Seasonal Indices')
plt.ylabel('Index')
plt.legend()

# 3. Deseasonalized Data
plt.subplot(3, 1, 3)
for year in range(2019, 2025):
    plt.plot(monthly_avg.index, monthly_avg[f'Deseasonalized_{year}'], marker='o', label=f'{year} - Deseasonalized')
plt.title('Deseasonalized Prices')
plt.xlabel('Month')
plt.ylabel('Deseasonalized Price')
plt.legend()

plt.tight_layout()
plt.show()
  """)


def prac_7():
  print("""
print("practical 7:  Measurement of seasonal indices Link Relative method")
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load and clean the dataset
path = r"Symphony-Data2.csv"
df = pd.read_csv(path)
df = df[['DATE', 'PRICE']]
df['DATE'] = pd.to_datetime(df['DATE'], format="%d-%b-%y")
df = df.sort_values('DATE')

# Step 2: Extract Year and Month
df['Year'] = df['DATE'].dt.year
df['Month'] = df['DATE'].dt.month

# Step 3: Calculate monthly average prices by year
monthly_avg = df.groupby(['Month', 'Year'])['PRICE'].mean().unstack()

# Step 4: Calculate Link Relatives (year-on-year ratios)
monthly_avg['LR_2020'] = monthly_avg[2020] / monthly_avg[2019]
monthly_avg['LR_2021'] = monthly_avg[2021] / monthly_avg[2020]
monthly_avg['LR_2022'] = monthly_avg[2022] / monthly_avg[2021]
monthly_avg['LR_2023'] = monthly_avg[2023] / monthly_avg[2022]
monthly_avg['LR_2024'] = monthly_avg[2024] / monthly_avg[2023]

# Step 5: Compute average link relative for each month
monthly_avg['Avg_Link_Relative'] = monthly_avg[['LR_2020', 'LR_2021', 'LR_2022', 'LR_2023', 'LR_2024']].mean(axis=1)

# Step 6: Normalize the seasonal indices (sum = 12 months)
seasonal_index = monthly_avg['Avg_Link_Relative']
seasonal_index = seasonal_index / seasonal_index.sum() * 12

# Step 7: Deseasonalize the data for all years
for year in range(2019, 2025):
    monthly_avg[f'Deseasonalized_{year}'] = monthly_avg[year] / seasonal_index

# Step 8: Plot original, seasonal indices, and deseasonalized data
plt.figure(figsize=(14, 10))

# Original data
plt.subplot(3, 1, 1)
for year in range(2019, 2025):
    plt.plot(monthly_avg.index, monthly_avg[year], marker='o', label=str(year))
plt.title('Original Monthly Prices')
plt.ylabel('Price (Rs.)')
plt.legend()

# Seasonal Index
plt.subplot(3, 1, 2)
plt.plot(monthly_avg.index, seasonal_index, marker='o', color='orange', label='Seasonal Index')
plt.title('Seasonal Indices')
plt.ylabel('Index')
plt.legend()

# Deseasonalized data
plt.subplot(3, 1, 3)
for year in range(2019, 2025):
    plt.plot(monthly_avg.index, monthly_avg[f'Deseasonalized_{year}'], marker='o', label=f'{year}')
plt.title('Deseasonalized Monthly Prices')
plt.xlabel('Month')
plt.ylabel('Deseasonalized Price')
plt.legend()

plt.tight_layout()
plt.show()
  """)
  

def prac_8():
  print("""
print("practical 8:  Calculation of variance of random component by variate difference method")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load dataset and preprocess
path = r"Symphony-Data2.csv"
df = pd.read_csv(path)
df = df[['DATE', 'PRICE']]
df['DATE'] = pd.to_datetime(df['DATE'], format="%d-%b-%y")
df = df.sort_values('DATE')

# Convert PRICE column to a NumPy array
prices = df['PRICE'].to_numpy()

# Step 1: Calculate first-order differences (yt - yt-1)
differences = np.diff(prices)

# Step 2: Calculate mean and variance of these differences
mean_diff = np.mean(differences)
var_diff = np.var(differences)

# Step 3: Variance of random component = variance of difference ÷ 2
var_random = var_diff / 2

# Output
print(f"Mean of Differences: {mean_diff:.4f}")
print(f"Variance of Differences: {var_diff:.4f}")
print(f"Estimated Variance of Random Component: {var_random:.4f}")

# Step 4: Visualize the differences
plt.plot(differences, marker='o')
plt.title('Differences Between Successive Observations')
plt.xlabel('Time Index')
plt.ylabel('Difference Value')
plt.grid(True)
plt.tight_layout()
plt.show()
  """)

def prac_9():
  print("""
print("practical 9:  Forecasting by exponential smoothing.")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Load and clean the dataset
path = r"Symphony-Data2.csv"
df = pd.read_csv(path)
df = df[['DATE', 'PRICE']]
df['DATE'] = pd.to_datetime(df['DATE'], format="%d-%b-%y")
df = df.sort_values('DATE')

# Set DATE as index for time series
df.set_index('DATE', inplace=True)

# Step 1: Create the model (Exponential Smoothing with additive seasonality)
model = ExponentialSmoothing(df['PRICE'], trend=None, seasonal='add', seasonal_periods=365)

# Step 2: Fit the model to the data
fit = model.fit()

# Step 3: Forecast for the next 365 days
forecast = fit.forecast(365)

# Step 4: Plot the original, fitted, and forecasted values
plt.figure(figsize=(12, 6))
plt.plot(df['PRICE'], label='Original Data')
plt.plot(fit.fittedvalues, label='Fitted Values', linestyle='--')
plt.plot(forecast, label='Forecast (Next 365 Days)', linestyle='--', color='green')
plt.title("Exponential Smoothing Forecast")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Step 5: Print forecasted values
print(forecast)
  """)

def prac_10():
  print("""
print("practical 10: Forecasting by short term forecasting methods.")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# Load and clean the dataset
path = r"Symphony-Data2.csv"
df = pd.read_csv(path)
df = df[['DATE', 'PRICE']]  # Keep only required columns
df['DATE'] = pd.to_datetime(df['DATE'], format="%d-%b-%y")
df = df.sort_values(by='DATE')

# Set DATE as index for time series analysis
df.set_index('DATE', inplace=True)

# Step 1: Fit the ARIMA model
# ARIMA(p=5, d=1, q=1) -> with seasonal component (P=1, D=1, Q=1, S=12)
model = ARIMA(df['PRICE'], order=(5, 1, 1))
fit = model.fit()

# Step 2: Forecast next 365 days
forecast = fit.forecast(steps=365)

# Step 3: Plot results
plt.figure(figsize=(12, 6))
plt.plot(df['PRICE'], label='Original Data')
plt.plot(fit.fittedvalues, label='Fitted Values', linestyle='--')
plt.plot(forecast, label='Forecast (Next 365 Days)', linestyle='--', color='green')
plt.title("ARIMA Model Forecast")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Step 4: Print forecasted values
print(forecast)
  """)



# def prac_1():
#   print("""
#   print("Prac 1: Write a program to implement logical gates AND, OR and NOT, with McCulloch-Pitts.")
#   print("1.	For AND gate implementation:")
#   x1 = [0, 0, 1, 1]
#   x2 = [0, 1, 0, 1]
#   w1 = [1, 1, 1, 1]
#   w2 = [1, 1, 1, 1]
#   threshold = 2

#   print("x1 x2 w1 w2 Sum Output")
#   for i in range(4):
#       sum_input = x1[i] * w1[i] + x2[i] * w2[i]
#       output = 1 if sum_input >= threshold else 0
#       print(x1[i], x2[i], w1[i], w2[i], " ", sum_input, "  ", output)

# # OR Gate using McCulloch-Pitts Neuron (with weights)
#   print("2. OR Gate using McCulloch-Pitts Neuron (with weights)")
  

#   x1 = [0, 0, 1, 1]      # Input 1
#   x2 = [0, 1, 0, 1]      # Input 2
#   w1 = [1, 1, 1, 1]      # Weight for x1
#   w2 = [1, 1, 1, 1]      # Weight for x2
#   t = 1                 # Threshold

#   print("x1 x2 w1 w2  t  Output")

#   for i in range(len(x1)):
#       total = x1[i] * w1[i] + x2[i] * w2[i]
#       output = 1 if total >= t else 0
#       print(x1[i], x2[i], w1[i], w2[i], " ", t, "   ", output)


#   # NOT Gate using McCulloch-Pitts Neuron (with weight)
#   print("NOT Gate using McCulloch-Pitts Neuron (with weight)")
#   x = [0, 1]       # Input
#   w = [-1, -1]     # Weight (inverts the input)
#   t = 0            # Threshold

#   print("x  w  t  Output")

#   for i in range(len(x)):
#       total = x[i] * w[i]
#       output = 1 if total >= t else 0
#       print(x[i], w[i], t, " ", output)
#   """)

# def prac_2():
#   print("""
#   print("prac 2 :Write a program to implement Hebb’s learning rule.")
#   !pip install numpy
#   import numpy as np

#   # Inputs
#   x1 = np.array([1, 1, 1, -1, 1, -1, 1, 1, 1])   # First input
#   x2 = np.array([1, 1, 1,  1, -1, 1, 1, 1, 1])   # Second input
#   y = np.array([1, -1])                         # Target outputs

#   # Initialize weights and bias
#   weights = np.zeros(9, dtype=int)
#   bias = 0

#   # --- First input with target = 1 ---
#   print("First input with target = 1")

#   # Update weights using: w_new = w_old + x * y
#   weights = weights + x1 * y[0]
#   bias += y[0]

#   print("Weights after 1st update:", weights)
#   print("Bias after 1st update:   ", bias)
#   print("\n")

#   # --- Second input with target = -1 ---
#   print("Second input with target = -1")

#   # Update weights again using new input
#   weights = weights + x2 * y[1]
#   bias += y[1]

#   print("Weights after 2nd update:", weights)
#   print("Bias after 2nd update:   ", bias)
#   """)




# def prac_3():
#   print("""
#   import numpy as np
#   import matplotlib.pyplot as plt

#   class KohonenSOM:
#       def __init__(self, x, y, input_len, learning_rate=0.5, radius=None, radius_decay=0.99, learning_rate_decay=0.99):
#           # Initialize SOM grid and parameters
#           self.x = x
#           self.y = y
#           self.input_len = input_len
#           self.learning_rate = learning_rate
#           self.radius = radius if radius is not None else max(x, y) / 2
#           self.radius_decay = radius_decay
#           self.learning_rate_decay = learning_rate_decay
#           self.weights = np.random.rand(x, y, input_len)  # Random initial weights

#       def train(self, data, num_iterations):
#           for _ in range(num_iterations):
#               sample = data[np.random.randint(len(data))]        # Pick a random input
#               bmu_index = self.find_bmu(sample)                  # Find best matching unit
#               self.update_weights(sample, bmu_index)             # Update BMU & neighbors
#               self.learning_rate *= self.learning_rate_decay     # Decay learning rate
#               self.radius *= self.radius_decay                   # Decay radius

#       def find_bmu(self, sample):
#           distances = np.linalg.norm(self.weights - sample, axis=-1)
#           bmu_index = np.unravel_index(np.argmin(distances), (self.x, self.y))
#           return bmu_index

#       def update_weights(self, sample, bmu_index):
#           for i in range(self.x):
#               for j in range(self.y):
#                   distance_to_bmu = np.linalg.norm(np.array([i, j]) - np.array(bmu_index))
#                   if distance_to_bmu <= self.radius:
#                       influence = np.exp(-distance_to_bmu**2 / (2 * (self.radius**2)))
#                       self.weights[i, j] += influence * self.learning_rate * (sample - self.weights[i, j])

#       def visualize(self):
#           reshaped = self.weights.reshape(self.x * self.y, self.input_len)
#           plt.imshow(reshaped, cmap='viridis')
#           plt.colorbar()
#           plt.title("SOM Weight Map")
#           plt.show()

#   # Example usage
#   if __name__ == "__main__":
#       data = np.random.rand(100, 3)  # 100 data points with 3 features (like RGB)
#       som = KohonenSOM(x=10, y=10, input_len=3, learning_rate=0.5)
#       som.train(data, num_iterations=1000)
#       som.visualize()
#       """)



# def prac_4():
#   print("""
#   print("practical 4: Solve the Hamming Network, given the exemplar vectors.")
#   import numpy as np

#   # Predefined exemplar vectors (patterns)
#   exemplar_vectors = np.array([
#       [1, 0, 1, 0, 1, 1, 0, 1],
#       [0, 1, 0, 1, 0, 0, 1, 0],
#       [1, 1, 1, 1, 0, 1, 0, 0]
#   ])

#   # Input vector to compare
#   input_vector = np.array([1, 0, 1, 1, 0, 1, 0, 1])

#   # Function to calculate Hamming distance
#   def hamming_distance(v1, v2):
#       return np.sum(v1 != v2)

#   # Function to find closest exemplar
#   def hamming_network(input_vector, exemplar_vectors):
#       distances = [hamming_distance(input_vector, ev) for ev in exemplar_vectors]
#       min_index = np.argmin(distances)
#       return min_index, distances[min_index]

#   # Run the Hamming Network
#   index, distance = hamming_network(input_vector, exemplar_vectors)

#   # Output
#   print(f"Closest match is exemplar at index {index} with Hamming distance {distance}.")
#   """)



# def prac_5():
#   print("""
#   print("prac 5:  Write a program for implementing BAM network.")
#   import numpy as np

#   # Define BAM class
#   class BAM:
#       def __init__(self):
#           self.weights = None  # weight matrix between patterns A and B

#       def train(self, patterns_A, patterns_B):
#           # Initialize the weight matrix to zeros
#           self.weights = np.zeros((patterns_A.shape[1], patterns_B.shape[1]))

#           # Hebbian learning: outer product for each pair (A, B)
#           for a, b in zip(patterns_A, patterns_B):
#               self.weights += np.outer(a, b)

#       def recall_A(self, pattern_B):
#           # Recall pattern A from pattern B
#           return np.sign(np.dot(pattern_B, self.weights.T))

#       def recall_B(self, pattern_A):
#           # Recall pattern B from pattern A
#           return np.sign(np.dot(pattern_A, self.weights))

#   # Example usage
#   if __name__ == "__main__":
#       # Training data: pattern pairs
#       patterns_A = np.array([
#           [1, 1, -1],
#           [-1, 1, 1],
#           [-1, -1, -1]
#       ])

#       patterns_B = np.array([
#           [1, -1],
#           [-1, 1],
#           [1, 1]
#       ])

#       # Create BAM network and train it
#       bam = BAM()
#       bam.train(patterns_A, patterns_B)

#       # Recall A from a given B
#       test_pattern_B = np.array([1, -1])
#       recalled_A = bam.recall_A(test_pattern_B)
#       print("Recalled A from B", test_pattern_B, ":", recalled_A)

#       # Recall B from a given A
#       test_pattern_A = np.array([1, 1, -1])
#       recalled_B = bam.recall_B(test_pattern_A)
#       print("Recalled B from A", test_pattern_A, ":", recalled_B)
#   """)




# def prac_6():
#     print("""
# print("Prac six: Implement a program to find the winning neuron using MaxNet.")
# import numpy as np

# def maxnet(input_vector, epsilon=0.1, max_iterations=100):
#     \"\"\"
#     MaxNet algorithm to find the winning neuron.
#     input_vector: Initial values (activations) of the neurons
#     epsilon: Small positive inhibition factor (e.g., 0.1)
#     Returns: Index of the strongest neuron (winner)
#     \"\"\"
#     activations = np.copy(input_vector)
#     num_neurons = len(input_vector)

#     for _ in range(max_iterations):
#         # Inhibit each neuron by subtracting small value from all other neurons
#         inhibition = epsilon * (np.sum(activations) - activations)
#         new_activations = activations - inhibition

#         # Remove negative values (simulate neuron being shut off)
#         new_activations[new_activations < 0] = 0

#         # If only one neuron is active (non-zero), we found the winner
#         if np.count_nonzero(new_activations) == 1:
#             break

#         activations = new_activations

#     return np.argmax(activations)  # Return index of winning neuron

# # Example usage
# input_vector = np.array([0.2, 0.5, 0.1, 0.7, 0.4])
# winner_index = maxnet(input_vector)
# print(f"The winning neuron is at index {winner_index} with activation {input_vector[winner_index]}")
# """)




# def prac_7():
#   print("""
#   print("practical 7:Implement De-Morgan’s Law" )
# def de_morgans_law_1(A, B):
#     # Law 1: ~(A OR B) == ~A AND ~B
#     left = not (A or B)
#     right = (not A) and (not B)
#     return left, right

# def de_morgans_law_2(A, B):
#     # Law 2: ~(A AND B) == ~A OR ~B
#     left = not (A and B)
#     right = (not A) or (not B)
#     return left, right

# # Taking input from user
# A_input = input("Enter A (True/False): ").strip().lower()
# B_input = input("Enter B (True/False): ").strip().lower()

# # Convert string to boolean
# A = A_input == "true"
# B = B_input == "true"

# # Apply De Morgan's Law 1
# result1 = de_morgans_law_1(A, B)
# print("\nDe Morgan's Law 1: ~(A ∨ B) = ~A ∧ ~B")
# print(f"~({A} ∨ {B}) = {result1[0]}")
# print(f"~{A} ∧ ~{B} = {result1[1]}")
# print(f"Law holds: {result1[0] == result1[1]}")

# # Apply De Morgan's Law 2
# result2 = de_morgans_law_2(A, B)
# print("\nDe Morgan's Law 2: ~(A ∧ B) = ~A ∨ ~B")
# print(f"~({A} ∧ {B}) = {result2[0]}")
# print(f"~{A} ∨ ~{B} = {result2[1]}")
# print(f"Law holds: {result2[0] == result2[1]}")
#   """)




# def prac_8():
#   print("""
# print("practical 8: Implement Union, Intersection, Complement, and Difference operations, on fuzzy sets)
# # Fuzzy Union
# def fuzzy_union(A, B):
#     return {x: max(A.get(x, 0), B.get(x, 0)) for x in set(A).union(B)}

# # Fuzzy Intersection
# def fuzzy_intersection(A, B):
#     return {x: min(A.get(x, 0), B.get(x, 0)) for x in set(A).intersection(B)}

# # Fuzzy Complement
# def fuzzy_complement(A):
#     return {x: 1 - A[x] for x in A}

# # Fuzzy Difference
# def fuzzy_difference(A, B):
#     return {x: min(A.get(x, 0), 1 - B.get(x, 0)) for x in set(A).union(B)}

# # Example fuzzy sets
# A = {'x1': 0.1, 'x2': 0.4, 'x3': 0.7}
# B = {'x2': 0.5, 'x3': 0.2, 'x4': 0.8}

# # Perform operations
# union_result = fuzzy_union(A, B)
# intersection_result = fuzzy_intersection(A, B)
# complement_result_A = fuzzy_complement(A)
# difference_result = fuzzy_difference(A, B)

# # Display
# print("Fuzzy Set A:", A)
# print("Fuzzy Set B:", B)
# print("\n--- Results ---")
# print("Union (A ∪ B):", union_result)
# print("Intersection (A ∩ B):", intersection_result)
# print("Complement (A′):", complement_result_A)
# print("Difference (A − B):", difference_result)
#  """)





# def prac_9():
#     print("""
# print("practical 9: Create Fuzzy relation by Cartesian product of any two fuzzy sets.")
# # Define function to compute Cartesian product fuzzy relation
# def cartesian_product_fuzzy_relation(A, B):
#     \"\"\"
#     Create fuzzy relation using Cartesian product.
#     Each pair (x, y) gets min(A(x), B(y)) as membership.
#     \"\"\"
#     relation = {}
#     for x in A:
#         for y in B:
#             relation[(x, y)] = min(A[x], B[y])
#     return relation

# # Example fuzzy sets
# A = {'x1': 0.7, 'x2': 0.4, 'x3': 0.9}
# B = {'y1': 0.6, 'y2': 0.8, 'y3': 0.5}

# # Get the fuzzy relation
# relation = cartesian_product_fuzzy_relation(A, B)

# # Display results
# print("Fuzzy Set A:", A)
# print("Fuzzy Set B:", B)

# print("\\nCartesian Product Fuzzy Relation (min(A(x), B(y))):")
# for (x, y), value in relation.items():
#     print(f"({x}, {y}): {value}")
# """)

# # Call the function




# def prac_10():
#     print("""
# print("practical 10: Perform max-min composition on any two fuzzy relations.")
# # Cartesian product: fuzzy relation from A to B
# def cartesian_product_fuzzy_relation(A, B):
#     return {(x, y): min(A[x], B[y]) for x in A for y in B}

# # Max–Min Composition
# def max_min_composition(R, S):
#     T = {}
#     x_elements = set(x for x, _ in R)
#     y_elements = set(y for _, y in R)
#     z_elements = set(z for _, z in S)

#     for x in x_elements:
#         for z in z_elements:
#             min_values = []
#             for y in y_elements:
#                 if (x, y) in R and (y, z) in S:
#                     min_values.append(min(R[(x, y)], S[(y, z)]))
#             if min_values:
#                 T[(x, z)] = max(min_values)
#     return T

# # Define fuzzy sets
# A = {'x1': 0.7, 'x2': 0.4, 'x3': 0.9}
# B = {'y1': 0.6, 'y2': 0.8, 'y3': 0.5}
# C = {'z1': 0.5, 'z2': 0.9, 'z3': 0.3}

# # Build relations
# R = cartesian_product_fuzzy_relation(A, B)  # A × B
# S = cartesian_product_fuzzy_relation(B, C)  # B × C

# # Compose: A × C
# T = max_min_composition(R, S)

# # Output results
# print("Fuzzy Set A:", A)
# print("Fuzzy Set B:", B)
# print("Fuzzy Set C:", C)

# print("\nFuzzy Relation R (A × B):")
# for key in sorted(R): print(f"{key}: {R[key]}")

# print("\nFuzzy Relation S (B × C):")
# for key in sorted(S): print(f"{key}: {S[key]}")

# print("\nMax-Min Composition (R o S):")
# for key in sorted(T): print(f"{key}: {T[key]}")
# """)
    
