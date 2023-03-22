****JMeter Results Analysis With Python

This project is to help analyse JTL files (or groups of JTL files) and produce some basic graphs and logs.

The project is built in python and should run file with Python 3.10 and 3.11.  It makes extensive use of Pandas and Matplotlib which you will need to install via PIP.

It is focused on Transactions rather than individual samplers so use of Transaction Controllers to delinate Transactions is required.

The file that drives the code is file_reader.py in the root directory.  You will need to update the load_test_folders[] list with one or more folders that contain your test results.  You can also directly add the path of a single JTL file.

NOTE: If you have multiple JTLs in the same folder, its assumed these are from the same test and will be merged together - this is a feature and not a bug as it helps to merge results from mutliple injectors into one result set without having to use jmeters remote_hosts feature.

Other values that should be checked and updated:

debug=True                  #this being true outputs lots of info to the console and helps understand what is happening
group_trans_by_x_secs=60    #This controls the grouping of transaction - you may want Transaction Per Second (TPS) or any   other value that makes sense

no_filter=False             #If this is true than all transactions are a single group and reported together - this can be messy to understand what is going on if you have lots of transactions.  Set to True if you want to break your transactions up into smaller groups with seperate graphs

transaction_grouping = ["Process_One", "Process_Two", "Process_Three", "Process_Four"]
#Set the names of your transactions group - for this to work correctly this must be the prefix for the relavent transactions so they can be filtered accordingly

Enjoy and Good Luck!