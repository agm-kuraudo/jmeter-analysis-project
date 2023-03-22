import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.ticker import AutoMinorLocator
import glob
from datetime import datetime

class OPs :
    def __init__(self, df="blank"):
        self.df = df
        self.Debug=False

    def setDebugOption(self, option):
        self.Debug = option

    def updateDF(self, df):
        self.df = df

    def getDF(self):
        return self.df

    def addDateTimeFromTimeStamp(self, sort=True):
        self.df["DateTime"] = self.df["timeStamp"].apply(lambda row: datetime.fromtimestamp(row // 1000))
        if sort : self.df = self.df.sort_values(by=['timeStamp'])

    def addTransactionNameColumn(self):
        self.df["TransactionName"] = self.df.apply(lambda x: self.setTransactionName(x.label, x.success), axis=1)

    def combineJTLs(self, list_of_jtls):
        '''Accepts a list containing JTLs, writes them into a single PANDAS dataframe'''
        #Read all the JTL files into a single data frame
        self.df = pd.concat(map(lambda x: pd.read_csv(x, low_memory=False), list_of_jtls)) 
        return self.df

    def setTransactionName(self, df_label, df_success):
        '''Used to set a transaciton name with a PASS/FAIl append for relavent transactions'''
        append_string = ""
        
        if df_label == None:
            return ""

        #The transaction labels all contain an underscore, ignore everything else
        if "_" not in df_label:
            return ""

        if df_success == True:
                append_string = " - PASS"
        elif df_success == False:
                append_string = " - FAIL"

        if df_label[0] == "_" :
            return df_label[1:] + append_string
        else:
            return df_label + append_string

    def getTransactionResponseTimesAverage(self, filter="none", sort=True, pass_only=True):
        '''Returns average transction response times as a dataframe'''
        trans_only_df = self.df
        
        if filter != "none":
            trans_only_df = self.df[self.df["TransactionName"].str.contains(filter)]

        if pass_only:
            trans_only_df = trans_only_df[trans_only_df["success"] == True]
            trans_only_df = trans_only_df[trans_only_df["TransactionName"].str.len()>0]

        if self.Debug:
            print("getTransactionResponseTimesAverage")
            print(trans_only_df)

        average_responseTimes = trans_only_df.groupby('TransactionName')["elapsed"].mean()

        if sort:
            average_responseTimes = average_responseTimes.sort_values(ascending=False)

        average_responseTimes = average_responseTimes.to_frame()

        average_responseTimes.index.name = "Transaction"
        average_responseTimes.columns = ["Response Time (seconds)"]

        average_responseTimes["Response Time (seconds)"] = average_responseTimes["Response Time (seconds)"] / 1000

        average_responseTimes = average_responseTimes.round(decimals=2)

        average_responseTimes= average_responseTimes.transpose()

        return average_responseTimes

    def getTransactionCounts(self, decimals=2, filter="none", sort=True):

        if self.Debug :
            print("getTransactionCounts")
            print(self.df)

        if filter == "none":
            transaction_counts = self.df[self.df["TransactionName"].str.len() > 0].groupby('TransactionName')["elapsed"].count()
            if self.Debug :
                print("transaction_counts")
                print(transaction_counts)
        else:
            transaction_counts = self.df[self.df["TransactionName"].str.contains(filter)].groupby('TransactionName')["elapsed"].count()

        if sort : 
            transaction_counts = transaction_counts.sort_values(ascending=False)
        
        transaction_counts = transaction_counts.to_frame()

        if self.Debug :
            print("transaction_counts as Frame")
            print(transaction_counts)       

        transaction_counts.index.name = "Transaction"
        transaction_counts.columns = ["Count"]

        if self.Debug :
            print("Renamed columns etc")
            print(transaction_counts.round(decimals=decimals))  

        return transaction_counts.round(decimals=decimals)

    def TransactionsPerXSeconds(self, X=360):
        
        if self.Debug:
            print(self.df["responseMessage"])

        jmeter_results_transonly = self.df[self.df["responseMessage"].str.contains('Number of samples in transaction', na=False)]

        ##Get all of the unique Transaction Names from the dataset
        all_transactions = jmeter_results_transonly.TransactionName.unique()

        #trans_grouped_df=jmeter_results_transonly.groupby("TransactionName").count()

        jmeter_results_transonly = jmeter_results_transonly.set_index(pd.DatetimeIndex(jmeter_results_transonly.DateTime))
        time_grouped_trans_df = jmeter_results_transonly.groupby("TransactionName").resample(str(X) + 'S', on='DateTime').count() * 10
        return time_grouped_trans_df, all_transactions

    def FilterTransactionsPerX(self, transaction_filter):
        if transaction_filter == "none":
            single_transaction_results = self.df
        else:
            single_transaction_results = self.df.filter(like=transaction_filter, axis=0)

        single_transaction_results = single_transaction_results.drop(["TransactionName"], axis=1).reset_index().set_index("DateTime")
        #pass_only = single_transaction_results[single_transaction_results["TransactionName"] == transaction]
        #print(single_transaction_results.head(5))
        return single_transaction_results


        '''
        trans_grouped_df=jmeter_results_transonly.groupby("TransactionName").count()

if debug : print(trans_grouped_df)

jmeter_results_transonly = jmeter_results_transonly.set_index(pd.DatetimeIndex(jmeter_results_transonly.DateTime))
if debug : print (jmeter_results_transonly)
time_grouped_trans_df = jmeter_results_transonly.groupby("TransactionName").resample('360S', on='DateTime').count() * 10
if debug : print (time_grouped_trans_df)
        
        '''