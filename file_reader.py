import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import glob
from datetime import datetime

'''
I WANT THIS CODE TO:
STEP 1:
Look for all JTL files in a directory provided
Add all JTL results into a dataframe
Timestamp as an index? (is this possible or maybe duplicates)
Sorted by time into one big dataframe


STEP 2: Output some stats from the dataframe
A count of all transactions seen during the test
An average response time for each transaction
An error count

'''


#Get all the JTL files from the directory and put them in a list
jtl_files_list= []

for jtl_file in glob.glob("TestResults/2023 01 30 Peak Load Test Round 1/*.jtl"):
    jtl_files_list.append(jtl_file)

print(jtl_files_list)


#Read all the JTL files into a single data frame

jmeter_results_df = pd.concat(map(pd.read_csv, jtl_files_list))  
print(1675109124185//1000)
#print (datetime.fromtimestamp())
jmeter_results_df["DateTime"] = jmeter_results_df["timeStamp"].apply(lambda row: datetime.fromtimestamp(row // 1000))

#Print out some details here to check it worked and if timeStamp has only unique values (it doesn't!)
print(jmeter_results_df.head())
print(jmeter_results_df["timeStamp"].is_unique)

jmeter_results_df = jmeter_results_df.sort_values(by=['timeStamp'])

print(jmeter_results_df.head())


#Get the average response time for each transaction (contains an _ character) and sort longest to shortest, output to CSV

average_responseTimes = jmeter_results_df[jmeter_results_df["label"].str.contains('_')].groupby('label')["elapsed"].mean().sort_values(ascending=False).to_frame()

average_responseTimes.index.name = "Transaction"
average_responseTimes.columns = ["Response Time (seconds)"]

average_responseTimes["Response Time (seconds)"] = average_responseTimes["Response Time (seconds)"] / 1000

average_responseTimes = average_responseTimes.round(decimals=2)

average_responseTimes= average_responseTimes.transpose()

print(average_responseTimes)

average_responseTimes.to_csv("TestResults/Transaction Response Times - Average.csv")

fig, ax = plt.subplots(dpi=300, figsize=(24,6))

ax.set_ylabel("Response Time Seconds")
#average_responseTimes['Adj Close'].plot(ax=ax, label="Share Price")

average_responseTimes.plot(ax=ax, kind='bar')

ax.get_legend().remove()

ax.axes.get_xaxis().set_visible(False)

# Put a legend below current axis
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=3)

#fig.legend()

plt.savefig("TestResults/Transaction Response Times Overall.png", bbox_inches="tight")

#Now lets get the transaction counts

transaction_counts = jmeter_results_df[jmeter_results_df["label"].str.contains('_')].groupby('label')["elapsed"].count().sort_values(ascending=False).to_frame()

transaction_counts.index.name = "Transaction"
transaction_counts.columns = ["Count"]

#transaction_counts["Count"] = transaction_counts["Count"]

transaction_counts = transaction_counts.round(decimals=2)

print(transaction_counts)

transaction_counts.to_csv("TestResults/Transaction Counts.csv")

#Error Counts
success_codes = ['200', '302', '401', '201']
error_count = jmeter_results_df.query("responseCode not in @success_codes")

#error_count = jmeter_results_df.apply(lambda row: row[(jmeter_results_df['responseMessage']!="OK") & (jmeter_results_df['responseMessage']!="Created") ])

error_count = jmeter_results_df.apply(lambda row: row[jmeter_results_df['success']==False ])

#error_count = jmeter_results_df.loc[(~jmeter_results_df["responseMessage"].str.contains("Number of samples")) & (~jmeter_results_df["responseCode"].str.contains(['200', '302', '401', '201']))]

print(error_count["label"].value_counts())

error_count.to_csv("TestResults/Failures.csv")


##Lets see if we can do transactions per minute

##SUCCESSFUL TRANSCTIONS

times=pd.DatetimeIndex(jmeter_results_df[(jmeter_results_df["success"]==True) & (jmeter_results_df["label"].str.contains('_'))].DateTime)
grouped_success = jmeter_results_df[(jmeter_results_df["success"]==True) & (jmeter_results_df["label"].str.contains('_'))].groupby([times.hour, times.minute]).count()

#grouped_success = grouped_success["DateTime", "label"]

grouped_success = grouped_success.drop(["timeStamp", "elapsed", "responseCode", "responseMessage", "threadName", "dataType", "grpThreads", "allThreads", "URL", "Latency", "IdleTime", "Connect", "success", "failureMessage", "bytes", "sentBytes", "DateTime"], axis=1)
    
#grouped_fail = grouped.loc[grouped["success" == False]]

print(grouped_success.head(10))
print(grouped_success.tail(10))

grouped_success.columns = ["Transactions Per Minute (Pass)"]

##TODO: Group by date time first then do the filtering for pass fail etc - this will hopefully sort the data axis on the graph output

####FAILED TRANSACTIONS
times=pd.DatetimeIndex(jmeter_results_df[(jmeter_results_df["success"]==False) & (jmeter_results_df["label"].str.contains('_'))].DateTime)
grouped_fail = jmeter_results_df[(jmeter_results_df["success"]==False) & (jmeter_results_df["label"].str.contains('_'))].groupby([times.hour, times.minute]).count()

#grouped_success = grouped_success["DateTime", "label"]

grouped_fail = grouped_fail.drop(["timeStamp", "elapsed", "responseCode", "responseMessage", "threadName", "dataType", "grpThreads", "allThreads", "URL", "Latency", "IdleTime", "Connect", "success", "failureMessage", "bytes", "sentBytes", "DateTime"], axis=1)
    
#grouped_fail = grouped.loc[grouped["success" == False]]

print(grouped_fail.head(10))
print(grouped_fail.tail(10))

grouped_fail.columns = ["Transactions Per Minute (Fail)"]

#############################################

fig, ax = plt.subplots(dpi=300, figsize=(24,6))

grouped_success.plot(ax=ax, kind='line')
grouped_fail.plot(ax=ax, kind='line')

ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))

ax.legend(loc='upper center',
          fancybox=True, shadow=True, ncol=3)

plt.savefig("TestResults/Transactions per Minute.png", bbox_inches="tight")

