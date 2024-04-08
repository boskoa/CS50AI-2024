## Smaller data set

With lesson notes configuration it achieves accuracy of 0,99 - 1,00.
If we set the pool size to (3, 3) - accuracy decreases slightly.
Changing activation to "sigmoid" varies the result greatly.
Reducing dropuot rate to 0.2 increases overfitting.

## Larger data set

With lesson notes configuration it achieves accuracy of 0,005.
Increased number of neurons in the hidden layer to 256 - accuracy 0,75.
Adding another hidden layer (128 neurons) with dropout before flattening; reduces accuracy.
Moving hidden layer (64 neurons, dropout - 0.01) in between convolution and maxpooling - no improvement.
Adding another round of convolution and maxpooling - timing improved, accuracy up to 0.95.
Increasing number of filters on the second convolution to 64 - same accuracy.
Adding Dense layer (128 neurons) in between conv - pooling rounds - no good.
Adding dropout after that layer - 0,90 accuracy. Back to just another round of convolution and maxpooling.
Adding third round of convolution and maxpooling - less than without it.
Increasing number of filters on the first convolution to 128 - 0.05 accuracy.