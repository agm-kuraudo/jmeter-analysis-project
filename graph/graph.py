import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.ticker import AutoMinorLocator
import glob
from datetime import datetime

class Graph:

    def __init__(self):
        self.Debug=False
        pass

    def setDebugOption(self, option):
        self.Debug = option

    def TransactionResponseTimes(self, averageResponseTimes, fileName, chart_title="Transaction Response Times"):

        fig, ax = plt.subplots(dpi=300, figsize=(24,6))

        ax.set_ylabel("Response Time Seconds")

        #print(averageResponseTimes)
        
        if self.Debug : 
            print(fileName)
            print(averageResponseTimes)

        averageResponseTimes.plot.bar(ax=ax)

        for container in ax.containers:
            ax.bar_label(container)

        ax.axes.get_xaxis().set_visible(False)

        ax.set_title(chart_title)

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                fancybox=True, shadow=True, ncol=3)

        fig.savefig(fileName, bbox_inches="tight")

    def TransactionsPerX(self, df, filename, chart_title="Transactions Per X"):

        print(filename)
        
        fig, ax = plt.subplots(dpi=300, figsize=(24,12))
        
        ind_transactions = df.TransactionName.unique()

        for ind_transaction in ind_transactions:
            if "- PASS" in ind_transaction:
                #print(ind_transaction)
                #print(df[df["TransactionName"].str.contains(ind_transaction)]["label"].to_frame().head(10))
                ax.plot(df[df["TransactionName"].str.contains(ind_transaction)]["label"].to_frame(), label=ind_transaction[:len(ind_transaction)-7])

        ax.xaxis.set_major_formatter(md.DateFormatter("%H:%M"))
        ax.xaxis.set_major_locator(md.MinuteLocator(interval=15))
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
        fancybox=True, shadow=True, ncol=3)

        ax.set_title(chart_title)

        fig.savefig(filename, bbox_inches="tight")