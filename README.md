# nip-convnet

## execution of current version
Dependencies:
* tensorflow (tested with 1.1.0 )
* python 2.7 (tested with 2.7.12)
* matplotlib (tested with 1.5.1 )

To train and test a simple single-layer autoencoder on the MNIST dataset, simply call 'python train_and_test_simple_mnist_autoencoder.py'

## project description
We want to train a neural network to classify images. Before we do that, an Autoencoder is trained for the network to pertain information of its input. The weights obtained from training the autoencoder are used for initializing a neural network for image classification. It has been shown that this pre-training of the network allows for obtaining higher generalization performance than when starting from a random weight initialization. This project will be about using a convolutional architecture for the Autoencoder that is well suited for visual data in obtaining said improved weight initialization. Initially we will reproduce the experiment of following paper:

Masci, J., Meier, U., Cireşan, D., & Schmidhuber, J. (2011). Stacked convolutional auto-encoders for hierarchical feature extraction. Artificial Neural Networks and Machine Learning–ICANN 2011, 52-59. 

Other Relevant Papers:
* Bengio et al. Representation Learning: A Review and New Perspectives

* Bengio, Y., Lamblin, P., Popovici, D., & Larochelle, H. (2007). Greedy layer-wise training of deep networks. Advances in neural information processing systems, 19, 153.

* Makhzani, A., & Frey, B. (2014, September). A winner-take-all method for training sparse convolutional autoencoders. In NIPS Deep Learning Workshop.

* D. Hamester, P. Barros and S. Wermter, Face expression recognition with a 2-channel Convolutional Neural Network, 2015 International Joint Conference on Neural Networks (IJCNN), Killarney, 2015, pp. 1-8.

Datasets:
* http://www.pitt.edu/~emotion/ck-spread.htm

Tutorials: 
* https://www.tensorflow.org/tutorials/

# Planning

What do we have so far?
	*  simple fully-connected autoencoder (unclear whether it needs regularization)
	*  simple conv autoencoder  (desperately needs regularization)

next steps:
	*  transfer weights to (convolutional) neural network
	 	** get setup that lets us train a (convolutional) neural network 
		** make it possible to load weights stored by the autoencoder if the architecture is fitting
		** make it possible to set enable/disable the learning of these wheigts in the training
		** architecture should be generic, the simplest way to test would be to add a fully-connected layer after the encoding layers of the autoencoder
		** it would probably be good to start with the fully-connected autoencoder for the sake of simplicity

	* regularizing the conv autoencoder

		** sparsity constraint? (probably not needed if we have maxpool layers and this doesn't reflect a convnet structure)

		** maxpool layer (important!)
			-> question: how to do upsampling? (there seems to be a way to do it with conv2d_transpose, working on it)

	* train deeper autoencoders
		** make the autoencoder classes more generic so that we're able to add as many layers as we want
		** implement layerwise training? 
			*** the stacked conv autoencoder paper also suggests a layerwise training, unclear if absolutely needed
			*** in order to implement this, we need to find a way to fix some variables during the training (there seems to be a flag to set weights trainable, otherwise we would maybe need to choose an adaptive learning rate of 0 or sth like that)

Discussion with Youssef today (23.5.17):
	* plot L2 norm during training instead of aggregated cross-entropy

general questions:
	* activation functions to use
		** sigmoid 	(our first autoencoder versions use it and it needs to be used in the last layer)
		** tanh		(needs to be scaled to [0,1]? as described in stacked ae paper)
		** rect 		(often used in practise, i think we should use this)