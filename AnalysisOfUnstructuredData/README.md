To run the program:

   1. Proceed to a directory containing folder
   
   **AnalysisOfUnstructuredData**
   2. From command line run the following for help message:
   
   `python -m AnalysisOfUnstructuredData -h / --help`
   3. To see help message for specific list please use:
    
   `python -m AnalysisOfUnstructuredData LIST -h / --help`
    
   where LIST is an english word for the list number i.e
    one, two,...
    
    
LIST 1 HELP:

**List one is implemented as a general interface for creating
three types of plots, namely pie charts, scatter plots and histograms.
Unfortunately I did not yet find a way of creating nested subparsers,
so the plots are invoked as a flag instead of subparser. (Keeping the whole
project organised in a way that each list is a subfunctionality is more
valuable to me).**

Flags specification are available through command:

`python -m AnalysisOfUnstructuredData one -h`

Scripts are available in 

AnalysisOfUnstructuredData/lists/list1

Few selected Results are saved in 

AnalysisOfUnstructuredData/Results

Basic plots are presented there, but also some more advanced plots can be seen,
as a show of possibilities made with interface.