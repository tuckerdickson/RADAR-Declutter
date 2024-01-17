# RADAR Declutter
## How to Run:
To run the program:
1. Navigate to the src directory.
2. Open a terminal and run main.py

   2.1 To evaluate the currently deployed model: ```python main.py evaluate```
   
   2.2 To train a new model: ```python main.py train```
   
   2.3 To make an inference: ```python main.py inference <path-to-input> <path-to-output>```

      For now, use /data/combined/combined_unlabeled.csv as the input file. The model currently being used to generate predictions (initial_noFF.sav) makes predictions using the fields present in this file (Range To Contact, Bearing To Contact, EL, ...). We will need to come up with a good location to output the results...
