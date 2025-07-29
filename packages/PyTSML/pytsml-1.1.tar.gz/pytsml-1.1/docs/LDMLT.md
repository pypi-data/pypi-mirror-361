# LDMLT -  LogDet Divergence-Based Metric Learning With Triplet Constraints

This metod uses a metric learning algorithm with triplet constraints to build a Mahalanobis based DTW distance metric.

Reference work:  Mei, J., Liu, M., Karimi, H.R., & Gao, H. (2014). LogDet Divergence-Based Metric Learning With Triplet Constraints and Its Applications. IEEE Transactions on Image Processing, 23, 4920-4931.

# Relevant methods from LDMLT class

## LDMLT(triplets_factor = 20, cycles = 3, alpha_factor = 5)

Class constructor, used to set method parameters:

triplets_factor - value that controls triplet quality and quantity in each cycle;

cycles - number of algorithm iterations;

alpha_factor - can be described as learning rate of the method.

## fit(X, Y, M = None)

Used to initiate the learning process, doesn't return anything.

X - input train data (see docs/general.md for more);

Y - class labels;

M - a Mahalanobis array that can be imported from other pre-trained model. If provided, the method doesn't perform the metric learning algorithm and uses pre-trained array.

## predict(X, k = 3)

Used to predict unknown observation(s) using the KNN classifier used with learned metric. When there's a multiple nearest classes, the method chooses the class of a nearest neighbor. Returns a class label(or list of class labels). 

X - input test data (see docs/general.md for more);

k - number of nearest neighbors checked to determine the winner class.

## saveM(filename, delimiter = " ")

Used to export learned Mahalanobis matrix to a text file.

filename - target file name;

delimeter - a character or string which will separate values in each row in the file.

## static loadM(filename, delimeter = " ")

Used to load a Mahalanobis matrix from a text file. Returns a Mahalanobis array as a NumPy array.

filename - target file name;

delimeter - a character or string which will separate values in each row in the file.

# Notes
- This method tends to be really slow, especially on bigger datasets.


