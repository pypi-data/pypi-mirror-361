# DDE -  Derivative Delay Embedding

This uses a mathematical concept of Delay Embedding to find similarities between time series and performs classification based on them.

Reference work:  Zhang, Z., Song, Y., Wang, W., & Qi, H. (2016). Derivative Delay Embedding: Online Modeling of Streaming Time Series. Proceedings of the 25th ACM International on Conference on Information and Knowledge Management.

# Relevant methods from DDE class

## DDE(DE_step = 3, DE_dim = 2, DE_slid = 2, alpha = 2, beta = 3, grid_size = 0.1, filter_param = 0.5)

Class constructor, used to set method parameters:

DE_step - value that represents the step used in delay embedding;

DE_dim - dimensionality of the delay embedding space;

DE_slid - value that represents the shift(slid) that takes place during embedding an observation to the embedding space;

alpha - distance relationship weight used in distance metric;

beta - angular relationship weight used in distance metric;

grid_size - size of a single grid in cell (DDE method splits the embedding space into equally sized cells and then approximates every point to the nearest cell). When grid_size = 0, then no approximations are being made;

filter_param - low pass filter threshold, used to perform noise filtering in the input data.

## fit(X, Y, M = None)

Used to initiate the learning process, doesn't return anything.

X - input train data (see docs/general.md for more);

Y - class labels;

## predict(X, k = 3)

Used to predict unknown observation(s) based on the learned delay embeddings. Returns a class label(or list of class labels). 

X - input test data (see docs/general.md for more);




