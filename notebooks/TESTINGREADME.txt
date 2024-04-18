What is the purpose of this testing procedure?

Create an optimal model based on the sets of biological and man-made data we currently have available, assess what are the impacts of different datasets on the overall performance of the model and understand the impacts of potentially risky features on the accuracy of the model for different datasets.

Training Procedure:
 - Using the different datasets that we currently have available, create a variety of training sets that span the current csv datasets we have (ECCO, Marked, Contacts, 20230914).
 - Current Ideas for training dataset splits:
   1. ECCO, Marked
   2. ECCO, Marked, Contacts
   3. ECCO, Marked, Contacts, 20230914 Manmades
   4. ECCO, Marked, 20230914 Manmades
 - Feature vectors should also be partially cycled along with MDI graphic outputs to show the reliance of the model and the impacts of risky features (avg_speed, avg_rcs)
 - Current Ideas for Feature Sets:
   1. Full List (all flight characteristics + smoothness)
   2. All - avg_rcs
   3. All - avg_speed
   4. All - avg_speed - avg_rcs

Testing Procudure:
 - Testing should record the following metrics on models trained and tested from the training procedure dataset splits:
   1. F-1/Accuracy
   2. Confidence (overall avg and avg for incorrect)
   3. Speed to make inference for different tracklengths through full pipeline (calculating full feature vector and then making prediction, no network processing)
