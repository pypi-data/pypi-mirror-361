# Data format

For training (fit() methods), all training datasets should be in one container - a list or a numpy array. Each element in this container represents a single obervation and should be in a form of a MxN matrix (nested lists or numpy array), where M is a length of the time series and N is number of features. In other words, each row of that matrix represents values of all the features in a specific point in time. Every observation in dataset must have equal N.

For classification (predict() methods), data format is the same, but now the input can be in form of a single matrix, without a container. When providing a number of observations, the result is a numpy array containing class labels.

# Test data

The package contains a function for generating random time series data for testing purposes. Classes for each instance are generated randomly so it is possible to have less number of classes in resulting dataset than the number provided with function parameter.

## generate_example_data(min_len, max_len, n_instances, n_classes)

min_len - minimum time series length;

max_len - maximum time series length;

n_instances - number of observations to generate;

n_classes - number of classes.

The function returns a tuple (X, Y), where X contains data features in form of a nested list and Y is a list of class labels.

For example use see examples/example.py


