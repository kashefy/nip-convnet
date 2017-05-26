import tensorflow as tf 

class CAE: 
	# convolutional autoencoder 

	def __init__(self, data, filter_dims, hidden_channels, strides = None, use_max_pooling = True, activation_function = 'sigmoid', store_model_walkthrough = False):

		# TODO:
		# 	- add assertion that test whether filter_dims, hidden_channels and strides have the right dimensions
		
		# 	- add possibility to store all intermediate values in a self.tensor_walkthrough list
		
		# 	- add the possibility of variable strides (currently only strides = [1,1,1,1] for all dimensions should work if use_max_pooling = True)
		# 	  (the upsampling_strides need to be adapted for the upsampling)
		# 	- verify the bias treatment (currently: the same bias for every pixel in a given feature map)

		self.data = data # we assume data in NHWC format 

		# filter_dims, out_channels and strides (if specified) are lists containing the specifications for each of the consecutive layers
		# the choice of mac pooling and activation function is used for the whole network (the last activation function is always a sigmoid)

		self.filter_dims 		= filter_dims 		# height and width of the conv kernels 	for each layer
		self.hidden_channels 	= hidden_channels	# number of feature maps 				for each layer
		if strides is None:
			self.strides = [[1,1,1,1] for filter in filter_dims]

		self.use_max_pooling 		= use_max_pooling
		self.activation_function	= activation_function

		# init lists that will store weights and biases for the convolution operations
		self.conv_weights 	= []
		self.conv_biases	= []
		self.reconst_biases = []

		# init list to store the shapes in the forward pass for the conv2d_transpose operations
		self.pre_conv_shapes = []

		self.store_model_walkthrough = store_model_walkthrough
		if self.store_model_walkthrough:
			# initialize list that stores all the intermediate tensors in a forward path (probably high memory consumption, set flag to False if any problems occur)
			self.model_walkthrough = []

		# private attributes used by the properties
		self._encoding 				= None
		self._optimize				= None
		self._logit_reconstruction 	= None
		self._reconstruction		= None
		self._error					= None


		print('Initializing conv autoencoder')
		with tf.name_scope('CAE'):
			self.optimize
			self.reconstruction

	@property
	def encoding(self):
		# returns the hidden layer representation (encoding) of the autoencoder

		if self._encoding is None:

			print('initialize encoding')

			tmp_tensor = self.data

			for layer in range(len(self.filter_dims)):

				# CONVOLUTION
				if layer == 0:
					in_channels = int(self.data.shape[3])
				else:

					if self.store_model_walkthrough:
						# store intermediate results
						self.model_walkthrough.append(tmp_tensor)

					in_channels = self.hidden_channels[layer - 1]
				out_channels = self.hidden_channels[layer]

				# initialize weights and biases:
				filter_shape = [self.filter_dims[layer][0], self.filter_dims[layer][1], in_channels, out_channels]

				W = tf.Variable(tf.truncated_normal(filter_shape, stddev=0.1), name='conv{}_weights'.format(layer))
				b = tf.Variable(tf.constant(0.1, shape=[out_channels]), name='conv{}_bias'.format(layer))

				self.conv_weights.append(W)
				self.conv_biases.append(b)

				self.pre_conv_shapes.append(tf.shape(tmp_tensor))

				# PREACTIVATION
				conv_preact = tf.add(tf.nn.conv2d(tmp_tensor, W, strides = self.strides[layer], padding='SAME'),  b, name='conv_{}_preactivation'.format(layer))

				# ACTIVATION
				if self.activation_function == 'relu':
					conv_act = tf.nn.relu(conv_preact, name='conv_{}_activation'.format(layer))

				else:
					conv_act = tf.nn.sigmoid(conv_preact, name='conv_{}_activation'.format(layer))

				# POOLING (2x2 max pooling)
				if self.use_max_pooling:
					pool_out = tf.nn.max_pool(conv_act, [1,2,2,1], [1,2,2,1], padding='SAME', name='max_pool_{}'.format(layer))
					tmp_tensor = pool_out

				else:
					tmp_tensor = conv_act

			self._encoding = tmp_tensor

		return self._encoding

	@property
	def error(self):
		# returns the training error node (cross-entropy) used for the training and testing

		if self._error is None:
			print('initialize error')

			self._error = tf.nn.sigmoid_cross_entropy_with_logits(labels=self.data, logits=self.logit_reconstruction, name='cross-entropy_error')

		return self._error

	@property
	def optimize(self):
		# returns the cross-entropy node we use for the optimization

		if self._optimize is None:
			print('initialize optimizer')

			# TODO: make step size modifiable
			step_size = 0.001

			self._optimize = tf.train.GradientDescentOptimizer(step_size).minimize(self.error)

		return self._optimize

	@property
	def logit_reconstruction(self):
		# returns the node containing the reconstruction before applying the sigmoid function 
		# the logit_reconstruction is separated to use the sigmoid_cross_entropy_with_logits function for the error

		if self._logit_reconstruction is None:
			print('initialize logit_reconstruction')

			tmp_tensor = self.encoding
			for layer in range(len(self.filter_dims))[::-1]:
				# go through the layers in reverse order to reconstruct the image

				if self.store_model_walkthrough:
					# store intermediate results
					self.model_walkthrough.append(tmp_tensor)

				# CONV_TRANSPOSE (AND UPSAMPLING)
				if layer == 0:
					channels = int(self.data.shape[3])
				else:
					channels = self.hidden_channels[layer - 1]

				# init reconstruction bias
				c = tf.Variable(tf.constant(0.1, shape=[channels]), name='reconstruction_bias_{}'.format(layer))
				self.reconst_biases.append(c)

				if self.use_max_pooling:
					# conv2d_transpose with upsampling
					upsampling_strides = [1,2,2,1]
					reconst_preact = tf.add( tf.nn.conv2d_transpose(tmp_tensor, self.conv_weights[layer], self.pre_conv_shapes[layer], upsampling_strides), c, name='reconstruction_preact_{}'.format(layer))

				else:
					# conv2d_transpose without upsampling 
					reconst_preact = tf.add( tf.nn.conv2d_transpose(tmp_tensor, self.conv_weights[layer], self.pre_conv_shapes[layer], self.strides[layer]), c, name='reconstruction_preact_{}'.format(layer))

				# ACTIVATION
				if layer > 0:
					# do not use the activation function in the last layer because we want the logits
					if self.activation_function == 'relu':
						reconst_act = tf.nn.relu(reconst_preact, name='reconst_act')
					else:
						reconst_act = tf.nn.sigmoid(reconst_preact ,name='reconst_act')

					tmp_tensor = reconst_act

				else:
					self._logit_reconstruction = reconst_preact

		return self._logit_reconstruction

	@property
	def reconstruction(self):
		# returns the reconstruction node that contains the reconstruction of the input

		if self._reconstruction is None:
			print('initialize reconstruction')

			self._reconstruction = tf.nn.sigmoid(self.logit_reconstruction, name='reconstruction')
		
		return self._reconstruction

	def store_model_to_file(self, sess, path_to_file):

		# TODO: add store / save function to the class
		saver = tf.train.Saver()
		save_path = saver.save(sess, path_to_file)

		print('Model was saved in {}'.format(save_path))

		return save_path

	def load_model_from_file(self, sess, path_to_file):

		saver = tf.train.Saver()
		saver.restore(sess, path_to_file)

		print('Restored model from {}'.format(path_to_file))
