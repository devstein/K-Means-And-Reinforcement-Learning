import sys
from PIL import Image
import numpy as np

class ImageSegmentation: 

	def __init__(self, k, inputFile, outputFile, numIters=100):
	    self.k = k
	    self.inputFile = inputFile
	    self.outputFile = outputFile
	    self.numIters = numIters


	def createFeatures(self):
		pixels = self.inputFile.load()

		numPixels = self.inputFile.size[0] * self.inputFile.size[1]
		self.features = np.zeros((numPixels, 5))

		# create feature vector
		index = 0
		for i in range(self.inputFile.size[0]):
			for j in range(self.inputFile.size[1]):
				#is a (R, G, B)
				RGB = pixels[i,j]
				self.features[index] = np.array([RGB[0], RGB[1], RGB[2], i ,j])
				index += 1
		self.mean = np.mean(self.features)
		self.std = np.std(self.features)
		#standardize self.features
		self.features = (self.features - self.mean) / self.std

	def nearestCentroid(self, point, centroids):
		nearestIndex = 0
		minDistance = np.inf
		#test np.inf
		for i in range(len(centroids)):
			distance = np.linalg.norm(point - centroids[i])
			if (distance < minDistance):
				minDistance = distance
				nearestIndex = i
		return nearestIndex

	def segmentFeatures(self, X, grouping, centroids):
		#for each X check its label and set it to the centroid (NOT i,j)
		n, d = X.shape
		for i in range(n):
			X[i, :3] = centroids[grouping[i], :3]
		return X

	def kMeans(self, k, X):
		n, d = X.shape
		#randomly choose k centroids
		randomPositions = np.random.choice(n, k, replace=False)
		centroids = np.zeros((k, 5))
		for i in range(k):
			centroids[i] = X[randomPositions[i]]

		# iteration number for debugging 
		# iters = 0
		
		#label vectors to assign centroids
		lastGrouping =  np.zeros(n, dtype=int)
		newGrouping =  np.ones(n, dtype=int)
		#loop until covergence 
		while (np.array_equal(lastGrouping, newGrouping) != True and self.numIters > iters):
			#save last grouping
			lastGrouping = np.copy(newGrouping)
			#assign eaach point to the cluster of the closest cetnroid
			for i in range(n):
				newGrouping[i] = self.nearestCentroid(X[i], centroids)


			#check for empty clusters 
			assignedClusters = np.unique(newGrouping)
			if (len(assignedClusters) != k):
				for i in range(k):
					if (np.any(assignedClusters != i)):
						newGrouping[np.random.randint(0,n)] = i 
			#re-estimate the cluter centroids based on the data assigned
			#to each cluster
			#zero centroids
			centroids = np.zeros((k, 5))
			#zero count matrix
			sumVector = np.zeros(k)
			#loop over newGrouping
			for i in range(n):
				index = newGrouping[i]
				#for newGroup value add that index of X to centroids index
				centroids[index] += X[i]
				#update corresponding count vector
				sumVector[index] += 1

			#multiply each centroid by 1/count 
			for i in range(k):
				centroids[i] *= 1/sumVector[i]

			# iters += 1
			# print iters 

		self.features = self.segmentFeatures(X, newGrouping, centroids)

	def inverseStandardization(self, X, mean, std):
		n, d = X.shape
		for i in range(n):
			if (std != 0):
				X[i] = X[i]*std + mean
			else:
				X[i] = X[i] + mean
		return np.rint(X)

	def createImage(self, X, fileName):
		#create new image same size as input 
		newImage = Image.new('RGB',(inputFile.size[0], inputFile.size[1]))
		newPixels = newImage.load()
		#undo standardization!
		X = self.inverseStandardization(X, self.mean, self.std)
		#fill in the color values of the new pixels
		index = 0
		for i in range(newImage.size[0]):
			for j in range(newImage.size[1]):
				newPixels[i,j] = tuple(X[index,:3].astype(int).tolist())
				index += 1

		newImage.save(fileName)

	def createSegmentedImage(self):
		self.createFeatures()
		self.kMeans(self.k, self.features)
		self.createImage(self.features, self.outputFile)


#do everything
if __name__ == '__main__':
	k = int(sys.argv[1])
	inputFile = Image.open(sys.argv[2])
	outputFile = sys.argv[3]
  	ImgSegmenter = ImageSegmentation(k, inputFile, outputFile)
  	ImgSegmenter.createSegmentedImage()