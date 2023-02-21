import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.ticker import AutoMinorLocator
import glob
from datetime import datetime
import file.read_jtl
import dataframeops.ops as ops
import graph.graph as grath

#load_test_folder = "TestResults/2023 01 30 Peak Load Test Round 1"
#load_test_folder = "TestResults/2023 02 02 Peak Load Test Round 2"
#load_test_folder = "TestResults/2023 02 07 Peak of Peak Tests"
load_test_folder = "TestResults/In-Flight Test"
debug=True
group_trans_by_x_secs=60

#If you want to group transctions e.g by process or app - set the groups here.  If not set the "no_filter" flag to true
transaction_grouping = ["Transaction Controller"]
no_filter=True

#Create a JTL Reader object
JTLReader = file.read_jtl.ReadJTL()

#Get all the JTL files from the directory and put them in a list
jmeter_results_df = JTLReader.readDir(load_test_folder + "/*.jtl")

if debug : 
    print("#1: Inital Dataframe")
    print(jmeter_results_df)

#Create a data frame OPS object
df_ops = ops.OPs(jmeter_results_df)
df_ops.setDebugOption(debug)

#Add a DateTime column based on the timestamp
df_ops.addDateTimeFromTimeStamp()

if debug : 
    print("#2: Added Date time sampt")
    print(df_ops.getDF())

#Add a transction name column and update for transactions
df_ops.addTransactionNameColumn()

if debug : 
    print("#3: Added Transaction Name")
    print(df_ops.getDF())

jmeter_results_df = df_ops.getDF()

#Get the average response time for each successful transaction

average_responseTimes = df_ops.getTransactionResponseTimesAverage(" - PASS", True)

if debug : 
    print("#4: Average Response Times")
    print(average_responseTimes)

#Output to CSV

average_responseTimes.to_csv(load_test_folder + "/Transaction Response Times - Average.csv")

#Output to nice graphs

graph_obj = grath.Graph()

graph_obj.setDebugOption(debug)

time_grouped_trans_df, all_transactions = df_ops.TransactionsPerXSeconds(group_trans_by_x_secs)

if debug : 
    print("#5: Time grouped transactions dataframe")
    print(time_grouped_trans_df)
    print("#6 All Transactions")
    print(all_transactions)

#Create a data frame OPS object
df_ops_trans_grouped = ops.OPs(time_grouped_trans_df)

if debug :
    print("#7 Grouped Transactions")
    print(df_ops_trans_grouped)

if no_filter == True :
    transaction_grouping=['none']

for transaction_group in transaction_grouping:

    if transaction_group == "none":
        chart_title = "Overall"
    else:
        chart_title = transaction_group

    subset_df_resp = df_ops.getTransactionResponseTimesAverage(transaction_group, True, True)
    if debug :
        print("#8 Subset Dataframe")
        print(subset_df_resp)
    graph_obj.TransactionResponseTimes(subset_df_resp, load_test_folder + "/" + chart_title + " - Response Times.png", chart_title + " Response Times (Average)")
    subset_df_count = df_ops.getTransactionCounts(decimals=2, filter=transaction_group, sort=False)
    subset_df_count.to_csv(load_test_folder + "/" + chart_title + " - Transaction Counts.csv")
    subset_df_TPX = df_ops_trans_grouped.FilterTransactionsPerX(transaction_group)
    graph_obj.TransactionsPerX(subset_df_TPX, load_test_folder + "/" + chart_title + " - Transaction Per Hour.png")

#Output all errors to CSV
jmeter_results_df[jmeter_results_df['success']==False].to_csv(load_test_folder + "/ErrorLog.csv")

#print(all_transactions)

def RestOfIt():


    ####Seperate Counts for Pass and Failed Transactions
    ##Get a transactions only dataframe



    #################################
    ##Lets see if we can do transactions per minute

    times=pd.DatetimeIndex(jmeter_results_df[(jmeter_results_df["success"]==True) & (jmeter_results_df["label"].str.contains('_'))].DateTime)
    grouped_success = jmeter_results_df[(jmeter_results_df["success"]==True) & (jmeter_results_df["label"].str.contains('_'))].groupby([times.hour, times.minute]).count()
    grouped_success = grouped_success.drop(["timeStamp", "elapsed", "responseCode", "responseMessage", "threadName", "dataType", "grpThreads", "allThreads", "URL", "Latency", "IdleTime", "Connect", "success", "failureMessage", "bytes", "sentBytes", "DateTime"], axis=1)

    if debug : print(grouped_success.head(10))
    if debug : print(grouped_success.tail(10))

    grouped_success.columns = ["Transactions Per Minute"]

    fig, ax = plt.subplots(dpi=300, figsize=(24,6))
    grouped_success.plot(ax=ax, kind='line', label="Transactions Per Minute")

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
            fancybox=True, shadow=True, ncol=3)

    plt.savefig("TestResults/Transactions per Minute.png", bbox_inches="tight")