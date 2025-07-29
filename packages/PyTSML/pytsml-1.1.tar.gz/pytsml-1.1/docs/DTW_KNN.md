# DTW+KNN

A classic KNN classifier using DTW distance as its metric. It uses a fastDTW algorithm from fast_dtw package to efficently approximate DTW distance.

Reference work: https://pypi.org/project/fastdtw/


#Relevant methods from DTW_KNN class

##DTW_KNN()

Class constructor, initializes the model.

## fit(X, Y)

Used to load training data for the KNN classifier.

X - input train data (see docs/general.md for more);

Y - class labels;


## predict(k = 3)

Used to predict unknown observation(s) using the KNN classifier. When there's a multiple nearest classes, the method chooses the class of a nearest neighbor. Returns a class label(or list of class labels). 

X - input test data (see docs/general.md for more);

k - number of nearest neighbors checked to determine the winner class.


