import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.ticker import AutoMinorLocator
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
debug=False

#Get all the JTL files from the directory and put them in a list
jtl_files_list= []

for jtl_file in glob.glob("TestResults/2023 01 30 Peak Load Test Round 1/*.jtl"):
    jtl_files_list.append(jtl_file)

if debug : print(jtl_files_list)


#Read all the JTL files into a single data frame

jmeter_results_df = pd.concat(map(pd.read_csv, jtl_files_list))  
if debug : print(1675109124185//1000)
#print (datetime.fromtimestamp())
jmeter_results_df["DateTime"] = jmeter_results_df["timeStamp"].apply(lambda row: datetime.fromtimestamp(row // 1000))

#Print out some details here to check it worked and if timeStamp has only unique values (it doesn't!)
if debug : print(jmeter_results_df.head())
if debug : print(jmeter_results_df["timeStamp"].is_unique)

jmeter_results_df = jmeter_results_df.sort_values(by=['timeStamp'])

if debug : print(jmeter_results_df.head())


#Get the average response time for each transaction (contains an _ character) and sort longest to shortest, output to CSV

average_responseTimes = jmeter_results_df[jmeter_results_df["label"].str.contains('_')].groupby('label')["elapsed"].mean().sort_values(ascending=False).to_frame()

average_responseTimes.index.name = "Transaction"
average_responseTimes.columns = ["Response Time (seconds)"]

average_responseTimes["Response Time (seconds)"] = average_responseTimes["Response Time (seconds)"] / 1000

average_responseTimes = average_responseTimes.round(decimals=2)

average_responseTimes= average_responseTimes.transpose()

if debug : print(average_responseTimes)

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

if debug : print(transaction_counts)

transaction_counts.to_csv("TestResults/Transaction Counts.csv")

#Error Counts
success_codes = ['200', '302', '401', '201']
error_count = jmeter_results_df.query("responseCode not in @success_codes")

#error_count = jmeter_results_df.apply(lambda row: row[(jmeter_results_df['responseMessage']!="OK") & (jmeter_results_df['responseMessage']!="Created") ])

error_count = jmeter_results_df.apply(lambda row: row[jmeter_results_df['success']==False ])

#error_count = jmeter_results_df.loc[(~jmeter_results_df["responseMessage"].str.contains("Number of samples")) & (~jmeter_results_df["responseCode"].str.contains(['200', '302', '401', '201']))]

if debug : print(error_count["label"].value_counts())

error_count.to_csv("TestResults/Failures.csv")


####Seperate Counts for Pass and Failed Transactions
##Get a transactions only dataframe

def setTransactionName(df_label, df_success):
    #print(df_label)
    append_string = ""
    if df_success == True:
        append_string = " - PASS"
    elif df_success == False:
        append_string = " - FAIL"

    if df_label[0] == "_" :
        return df_label[1:] + append_string
    else:
        return df_label + append_string

jmeter_results_transonly = jmeter_results_df[jmeter_results_df["responseMessage"].str.contains('Number of samples in transaction')]

if debug : print(jmeter_results_transonly)

#jmeter_results_transonly["Transaction Name"] = jmeter_results_transonly["label"].apply(lambda x: x[1:] if x[0]=='_' else x)
jmeter_results_transonly["TransactionName"] = jmeter_results_transonly.apply(lambda x: setTransactionName(x.label, x.success), axis=1)

##Get all of the unique Transaction Names from the dataset

all_transactions = jmeter_results_transonly.TransactionName.unique()

print(all_transactions)

if debug : print(jmeter_results_transonly)

trans_grouped_df=jmeter_results_transonly.groupby("TransactionName").count()

if debug : print(trans_grouped_df)

jmeter_results_transonly = jmeter_results_transonly.set_index(pd.DatetimeIndex(jmeter_results_transonly.DateTime))
if debug : print (jmeter_results_transonly)
time_grouped_trans_df = jmeter_results_transonly.groupby("TransactionName").resample('360S', on='DateTime').count() * 10
if debug : print (time_grouped_trans_df)

fig, ax = plt.subplots(dpi=300, figsize=(24,6))

for transaction in all_transactions:

    single_transaction_results = time_grouped_trans_df.filter(like=transaction, axis=0)

    if debug : print (single_transaction_results)

    if debug : print(single_transaction_results.drop(["TransactionName"], axis=1).reset_index().set_index("DateTime"))

    single_transaction_results = single_transaction_results.drop(["TransactionName"], axis=1).reset_index().set_index("DateTime")

    #pass_only = single_transaction_results.filter(like='CP_EnterOTP - PASS', axis=0)
    #pass_only["label"].plot(ax=ax, kind='bar', label="Pass")

    #fail_only = single_transaction_results.filter(like='CP_EnterOTP - FAIL', axis=0)
    pass_only = single_transaction_results[single_transaction_results["TransactionName"] == transaction]
    #fail_only = single_transaction_results[single_transaction_results["TransactionName"] == "CP_EnterOTP - FAIL"]

    if debug : print(pass_only)

    #single_transaction_results["label"].plot(ax=ax, kind='bar', label="Transactions Per Minute")
    #pass_only["label"].plot(ax=ax, kind='line', label="Passed Transaction Per 6 Minutes", sharex=True, subplots=True)
    #fail_only["label"].plot(ax=ax, kind='line', label="Failed Transaction Per 6 Minutes", sharex=True, subplots=True)

    ax.plot(pass_only["label"], label=transaction)
    #ax.plot(fail_only["label"],  label="FAIL")

#ax.xaxis.set_ticklabels()

#ax2.set_xticklabels(pass_only["DateTime"])
ax.xaxis.set_major_formatter(md.DateFormatter("%H:%M"))
ax.xaxis.set_major_locator(md.MinuteLocator(interval=15))

#ax.xaxis.set_minor_locator(AutoMinorLocator())

#ax.tick_params(which='minor', length=5, width=1, color='red')

#ax.set_xticklabels(pass_only["DateTime"])

ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=3)

#fig.autofmt_xdate()

fig.savefig("TestResults/Debug.png", bbox_inches="tight")


#################################



##Lets see if we can do transactions per minute

times=pd.DatetimeIndex(jmeter_results_df[(jmeter_results_df["success"]==True) & (jmeter_results_df["label"].str.contains('_'))].DateTime)
grouped_success = jmeter_results_df[(jmeter_results_df["success"]==True) & (jmeter_results_df["label"].str.contains('_'))].groupby([times.hour, times.minute]).count()

#grouped_success = grouped_success["DateTime", "label"]

grouped_success = grouped_success.drop(["timeStamp", "elapsed", "responseCode", "responseMessage", "threadName", "dataType", "grpThreads", "allThreads", "URL", "Latency", "IdleTime", "Connect", "success", "failureMessage", "bytes", "sentBytes", "DateTime"], axis=1)
    
#grouped_fail = grouped.loc[grouped["success" == False]]

if debug : print(grouped_success.head(10))
if debug : print(grouped_success.tail(10))

grouped_success.columns = ["Transactions Per Minute"]

fig, ax = plt.subplots(dpi=300, figsize=(24,6))

grouped_success.plot(ax=ax, kind='line', label="Transactions Per Minute")

ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=3)

plt.savefig("TestResults/Transactions per Minute.png", bbox_inches="tight")

