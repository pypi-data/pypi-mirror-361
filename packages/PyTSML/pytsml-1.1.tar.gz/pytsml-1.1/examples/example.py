# Import assumes that the package is installed through pip
from PyTSML import PyTSML
# Generate 240 observations distributed among 5 classes with length varied from 3 do 10
x_train, y_train = PyTSML.generate_example_data(3,10,240,5)
# Initiate model
model = PyTSML.DTW_KNN()
# Fit training data
model.fit(x_train,y_train)
# Generate 20 instances of test data
x_test,y_test = PyTSML.generate_example_data(3,10,20,5)
# Make predictions
y_predicted = model.predict(x_test)
# Calculate and print classification accuracy
acc = PyTSML.accuracy(y_predicted, y_test)
print(acc)


