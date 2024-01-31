# RADAR Declutter
## How to Run:
To run the program:
1. Navigate to the src directory.
2. Open a terminal and run main.py (```python main.py```). You should now see a ```>```, prompting you to enter a command.

   2.1 To retrain the currently deployed model, type: ```train```
   
   2.2 To make an inference with the currently deployed model, type: ```inference <path-to-input> <path-to-output>```
   
   2.3 To stop the program, type: ```quit```

For now, use /data/combined/combined_unlabeled.csv as the input file. The currently deployed model (initial_noFF.sav) makes predictions using the fields present in this file (Range To Contact, Bearing To Contact, EL, ...). We will need to come up with a good location to output the results...
