import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


jmeter_results_df = pd.read_csv("TestResults/2023 01 30 Peak Load Test Round 1/20230130_TST1_160514_test_results.jtl")

print(jmeter_results_df.head())

print(jmeter_results_df.iloc[1640])
print(jmeter_results_df.columns)
