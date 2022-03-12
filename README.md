# Formula1Analytics

Data:
The data in this page have been retrieved from fastf1 python package. 
Races where containing at least one tyre or intermediate compound have 
been excluded.
Laps where the car in front is less than 1.1 seconds have been 
excluded.
Laps before and after pit stop have been exluded.
Laps where there is a red flag or VSC or SC have been excluded.
Lap Times have been cleaned based on IQR.Any lap time lower than
Q1-1.5*IQR or higher than  Q3+1.5*IQR have been excluded. 
Laps where the compound is na have been excluded
The number in the Compound  _1,_2,_3,_4 explain the number of set.For 
example if there are two sets of soft  tyres in a race the first
set of tyres is SOFT_1 


Data fields Description:
lapinseconds= Lap Times in seconds. 
tyredelta= difference lap by lap for lapinseconds


