
from PIL import Image as PIL_Image

import math
import os

# TODO:
# 	- Add benchmarking for various image sizes
# 	- Add useful features

# ----------------------
# |  Helper Functions  |
# ----------------------

# Input: RGB color as a 3-tuple
# Output: HSV representation of the inputted color as a 3-tuple
def RGBtoHSV(vs):
	r = float(vs[0]) / 255.0
	g = float(vs[1]) / 255.0
	b = float(vs[2]) / 255.0

	cmax = max(r, g, b)
	cmin = min(r, g, b)

	delta = cmax - cmin

	if delta == 0.0:
		h = 0.0
	elif cmax == r:
		h = (g - b) / delta
	elif cmax == g:
		h = (b - r) / delta + 2
	elif cmax == b:
		h = (r - g) / delta + 4
	h = h * 60
	if h < 0:
		h += 360
	
	s = (0.0 if cmax == 0.0 else delta / cmax)
	v = cmax

	return (int(h), s, v)

# Input: RGB pixel as 3-tuple.
# Output: Same exact RGP pixel.
def RGBtoRGB(v):
	return v

# Creates a new image_feature.Image object from the given file.
# Input:
#   filename - path to an image file. JPG and PNG file formats are tested and confirmed, but aany file format supported by PIL should work
# Output:
#   image_features.Image object
def newImage(filename):
	return Image(PIL_Image.open(filename))

class Image:
	# Input:
	#   pil_image - PIL.Image object.
	def __init__(self, pil_image):
		self.image = pil_image

		# TODO only load pixel data as necessary
		self.pix = pil_image.load()

		self.width, self.height = self.image.size

	# ---------------------
	# |   Size Features   |
	# ---------------------

	def aspectRatio(self):
		return [float(self.width) / float(self.height)]

	def sumOfSizes(self):
		return [self.width + self.height]

	def size(self):
		return [self.width, self.height]

	# ----------------------
	# |    RGB Features    |
	# ----------------------

	# Averages the R of the RGB representation of each pixel for each of the nine sections.
	def averageRedOfEachSection(self):
		return self._averageChannelOfEachSection(RGBtoRGB, 0)

	# Averages the G of the RGB representation of each pixel for each of the nine sections.
	def averageGreenOfEachSection(self):
		return self._averageChannelOfEachSection(RGBtoRGB, 1)

	# Averages the B of the RGB representation of each pixel for each of the nine sections.
	def averageBlueOfEachSection(self):
		return self._averageChannelOfEachSection(RGBtoRGB, 2)

	# ----------------------
	# |    HSV Features    |
	# ----------------------

	# Averages the V of the HSV represenation of each pixel over the entire image
	def averageBrightness(self):
		return [sum(RGBtoHSV(self.pix[x, y])[2] for x in range(self.width) for y in range(self.height)) / float(self.width * self.height)]

	# Divides each dimension into 3 equal sections, and then averages the Hue of only the middle section
	def averageHueOfMiddle(self):
		ws, hs = self._getSections(3)
		return [sum(RGBtoHSV(self.pix[x, y])[0] for x in xrange(*ws[1]) for y in xrange(*hs[1])) / float(ws[1][1] - ws[1][0]) / float(hs[1][1] - hs[1][0])]

	# Divides each dimension into 3 equal sections, and then averages the Saturation of only the middle section
	def averageSaturationOfMiddle(self):
		ws, hs = self._getSections(3)
		return [sum(RGBtoHSV(self.pix[x, y])[1] for x in xrange(*ws[1]) for y in xrange(*hs[1])) / float(ws[1][1] - ws[1][0]) / float(hs[1][1] - hs[1][0])]

	# Averages the H of the HSV representation of each pixel for each of the nine sections.
	def averageHueOfEachSection(self):
		return self._averageChannelOfEachSection(RGBtoRGB, 0)

	# Averages the S of the HSV representation of each pixel for each of the nine sections.
	def averageSaturationOfEachSection(self):
		return self._averageChannelOfEachSection(RGBtoRGB, 1)

	# Averages the V of the HSV representation of each pixel for each of the nine sections.
	def averageValueOfEachSection(self):
		return self._averageChannelOfEachSection(RGBtoRGB, 2)

	# ----------------------
	# |    Bin Features    |
	# ----------------------

	# Divides each dimension into 3 equal sections. Then creates a histogram for each of the 9 sections using the provided number of bins.
	# Returns a 36 element list, where each element is the euclidean difference between two of the 9 histograms
	# Optional Paramters:
	# 	bin_type - Method to bin pixels
	# 		'avg' - Bins pixels based on the average of the three channels.
	# 		'3d' - Divides the pixel space into num_bins^3 equal-sized bins
	# 	dif_type - Method to compute the difference between section's histograms
	# 		'sum_of_abs' - Sums up the abosulte difference between each element of the histogram
	# 		'euclidean' - Computes the euclidean distance between two histograms
	# 		'earth_mover' - Computes the earth mover distance between two histograms
	# 	norm_type - Method to normalize the histograms
	# 		'sum_to_one' - Divides each element of the histogram by the number of pixels in the section
	# 		'euclidean' - Makes the magnitude of each histogram one
	# 		'none' - No normalization is done
	# 	pixel_type - Format of each pixel: ['rgb']
	# TODO allow for different binning methods, different difference methods, and normalization methods.
	# TODO allow for pixel_type to be either 'rgb' or 'hsv'

	binComparison_bin_types = ['avg', '3d']
	binComparison_norm_types = ['sum_to_one', 'none']
	binComparison_dif_types = ['sum_of_abs']
	binComparison_pixel_types = 'rgb'

	def binComparison(self, num_bins,
							bin_type = 'avg',
							norm_type = 'sum_to_one',
							dif_type = 'sum_of_abs',
							pixel_type = 'rgb'):
		if bin_type not in Image.binComparison_bin_types:
			raise Exception('Invalid bin_type in binComparison: got ' + str(bin_type) + ', but must be in ' + str(Image.binComparison_bin_types))
		if norm_type not in Image.binComparison_norm_types:
			raise Exception('Invalid norm_type in binComparison: got ' + str(norm_type) + ', but must be in ' + str(Image.binComparison_norm_types))
		if dif_type not in Image.binComparison_dif_types:
			raise Exception('Invalid dif_type in binComparison: got ' + str(dif_type) + ', but must be in ' + str(Image.binComparison_dif_types))
		if pixel_type not in Image.binComparison_pixel_types:
			raise Exception('Invalid pixel_type in binComparison: got ' + str(pixel_type) + ', but must be in ' + str(Image.binComparison_pixel_types))

		# Creates bins
		bins = []
		
		ws, hs = self._getSections(3)
		for wr in ws:
			for hr in hs:
				if bin_type == 'avg':
					this_bin = [0] * num_bins
				if bin_type == '3d':
					this_bin = [0] * pow(num_bins, 3)

				for x in xrange(wr[0], wr[1]):
					for y in xrange(hr[0], hr[1]):
						v = self.pix[x, y]

						if bin_type == 'avg':
							avg_v = float(sum(v)) / float(len(v))
							b = int(math.floor(avg_v * num_bins / 256.0))
						if bin_type == '3d':
							r = int(math.floor(v[0] * num_bins / 256.0))
							g = int(math.floor(v[1] * num_bins / 256.0))
							b = int(math.floor(v[2] * num_bins / 256.0))

							b = r + g * num_bins + b * num_bins * num_bins

						this_bin[b] += 1
				bins.append(this_bin)

		if norm_type == 'sum_to_one':
			# Normalize bins so the sum of them is 1.0
			for i in range(9):
				sum_bin = float(sum(bins[i]))
				bins[i] = [v / sum_bin for v in bins[i]]
		elif norm_type == 'none':
			pass

		# Compute differences of bins
		rv = []
		for i in range(9):
			for j in range(9):
				if j <= i:
					continue
				if dif_type == 'sum_of_abs':
					rv.append(sum(abs(a - b) for a, b in zip(bins[i], bins[j])))
		return rv


	# ---------------------
	# |  Helper Fuctions  |
	# ---------------------

	# Input: num - number of times to divide each dimension. Ex. providing a value of 3 creates 9 sections.
	# Output: two lists of 2-tuples. Each tuple is a range (inclusive lower-bound exclusive upper bound) of indices for a section.
	#         The first list is for the X/width dimension and the second list is for the Y/height dimension.
	def _getSections(self, num):
		# Compute the lower bounds of each section
		w_sections = [int(math.ceil(float(self.width  / float(num) * v))) for v in range(num)]
		h_sections = [int(math.ceil(float(self.height / float(num) * v))) for v in range(num)]

		# Add the upper bound of each section
		w_sections = [(w_sections[i], (self.width  if i + 1 == num else w_sections[i + 1])) for i in range(num)]
		h_sections = [(h_sections[i], (self.height if i + 1 == num else h_sections[i + 1])) for i in range(num)]

		return w_sections, h_sections

	# Input:
	#         f - function that takes a single 3-tuple RGB pixel and outputs a 3-tuple.
	#         chan - the index of the 3-tuple outputted by f to be averaged.
	# Output: A list of length 9, where each element is the average the desired pixel channel for a section of the image.
	def _averageChannelOfEachSection(self, f, chan):
		ws, hs = self._getSections(3)
		return [sum(f(self.pix[x, y])[chan]
						for x in xrange(wr[0], wr[1]) for y in xrange(hr[0], hr[1]))
				/ float((wr[1] - wr[0]) * (hr[1] - hr[0]))
					for wr in ws for hr in hs]

	# ----------------------
	# | Debugging Fuctions |
	# ----------------------

	# Displays the Image
	def show(self):
		# TODO figure out why not working
		self.image.show()

	# Prints all Pixel data
	def printAll(self):
		for x in range(self.width):
			for y in range(self.height):
				print x, y, '->', self.pix[x, y]
		print self.width, self.height

if __name__ == '__main__':
	# Runs debugging unit tests for the Image class

	# Test RGBtoHSV()
	print 'Testing RGBtoHSV()'
	tests = [{'rgb': (0,0,0), 'hsv':(0, 0.0, 0.0)},
				{'rgb': (255, 0, 0), 'hsv': (0, 1.0, 1.0)},
				{'rgb': (0, 255, 0), 'hsv': (120, 1.0, 1.0)},
				{'rgb': (0, 0, 255), 'hsv': (240, 1.0, 1.0)},
				{'rgb': (100, 0, 0), 'hsv': (0, 1.0, 0.392)},
				{'rgb': (0, 100, 0), 'hsv': (120, 1.0, 0.392)},
				{'rgb': (0, 0, 100), 'hsv': (240, 1.0, 0.392)},
				{'rgb': (255, 255, 0), 'hsv': (60, 1.0, 1.0)},
				{'rgb': (255, 0, 255), 'hsv': (300, 1.0, 1.0)},
				{'rgb': (0, 255, 255), 'hsv': (180, 1.0, 1.0)},
				{'rgb': (150, 100, 100), 'hsv': (0, 0.333, 0.588)},
				{'rgb': (100, 150, 100), 'hsv': (120, 0.333, 0.588)},
				{'rgb': (100, 100, 150), 'hsv': (240, 0.333, 0.588)}]

	for test in tests:
		comp_hsv = RGBtoHSV(test['rgb'])

		if comp_hsv[0] != test['hsv'][0] or \
				abs(comp_hsv[1] - test['hsv'][1]) > 0.001 or \
				abs(comp_hsv[2] - test['hsv'][2]) > 0.001:
			raise Exception('Error in RGBtoHSV(): got RGBtoHSV(' + str(test['rgb']) + ') = ' + str(comp_hsv) + '; expected ' + str(test['hsv']))
	print 'Passed RGBtoHSV() tests'

	# List of test images with known outputted values
	test_images = [{'filename': 'test_images/all_color.png',
						'im': newImage('test_images/all_color.png'),
						'aspectRatio': 0.5,
						'sumOfSizes': 270,
						'size': (90, 180),
						'averageBrightness': 7.0 / 9.0,
						'averageHueOfMiddle': 60,
						'averageSaturationOfMiddle': 1.0,
						'binComparison_avg': (2, 2, 2, 2, 2, 2, 2, 0,
											  0, 0, 2, 2, 2, 2, 2,
											  0, 2, 2, 2, 2, 2,
											  2, 2, 2, 2, 2,
											  0, 0, 2, 2,
											  0, 2, 2,
											  2, 2,
											  2),
						'binComparison_3d': (2, 2, 2, 2, 2, 2, 2, 0,
											 2, 2, 2, 2, 2, 2, 2,
											 2, 2, 2, 2, 2, 2,
											 2, 2, 2, 2, 2,
											 2, 2, 2, 2,
											 2, 2, 2,
											 2, 2,
											 2)},
					{'filename': 'test_images/horizontal_stripes.png',
						'im': newImage('test_images/horizontal_stripes.png'),
						'aspectRatio': 2.0,
						'sumOfSizes': 270,
						'size': (180, 90),
						'averageBrightness': 1.0,
						'averageHueOfMiddle': 120,
						'averageSaturationOfMiddle': 1.0,
						'binComparison_avg': (0, 0, 0, 0, 0, 0, 0, 0,
											  0, 0, 0, 0, 0, 0, 0,
											  0, 0, 0, 0, 0, 0,
											  0, 0, 0, 0, 0,
											  0, 0, 0, 0,
											  0, 0, 0,
											  0, 0,
											  0),
						'binComparison_3d': (0, 0, 2, 2, 2, 2, 2, 2,
											 0, 2, 2, 2, 2, 2, 2,
											 2, 2, 2, 2, 2, 2,
											 0, 0, 2, 2, 2,
											 0, 2, 2, 2,
											 2, 2, 2,
											 0, 0,
											 0)}]

	# List of features to test
	features =[{'name': 'aspectRatio',
					'func': Image.aspectRatio,
					'args': (),
					'good_out': lambda out, exp: abs(out[0] - exp) < 0.0001},
				{'name': 'sumOfSizes',
					'func': Image.sumOfSizes,
					'args': (),
					'good_out': lambda out, exp: out[0] == exp},
				{'name': 'size',
					'func': Image.size,
					'args': (),
					'good_out': lambda out, exp: out[0] == exp[0] and out[1] == exp[1]},
				{'name': 'averageBrightness',
					'func': Image.averageBrightness,
					'args': (),
					'good_out': lambda out, exp: abs(out[0] - exp) < 0.0001},
				{'name': 'averageHueOfMiddle',
					'func': Image.averageHueOfMiddle,
					'args': (),
					'good_out': lambda out, exp: out[0] == exp},
				{'name': 'averageSaturationOfMiddle',
					'func': Image.averageSaturationOfMiddle,
					'args': (),
					'good_out': lambda out, exp: abs(out[0] - exp) < 0.0001},
				{'name': 'binComparison_avg',
					'func': Image.binComparison,
					'args': (10, 'avg', 'sum_to_one', 'sum_of_abs', 'rgb'),
					'good_out': lambda out, exp: all(abs(o - e) <= 0.0001 for o, e in zip(out, exp))},
				{'name': 'binComparison_3d',
					'func': Image.binComparison,
					'args': (3, '3d', 'sum_to_one', 'sum_of_abs', 'rgb'),
					'good_out': lambda out, exp: all(abs(o - e) <= 0.0001 for o, e in zip(out, exp))}]

	for feature in features:
		short_name = feature['name'].split('_')[0]
		print 'Testing', short_name + '()'

		for test_image in test_images:
			rv = feature['func'](test_image['im'], *feature['args'])
			if not feature['good_out'](rv, test_image[feature['name']]):
				raise Exception('Error in ' + short_name + '(): got ' + short_name + '(' + ', '.join([test_image['filename']] + list(map(str, feature['args']))) + ') = ' + str((rv if len(rv) != 1 else rv[0])) + '; expected ' + str(test_image[feature['name']]))

		print 'Passed', short_name + '()', 'tests'


	# Tests all images in folder sample_images to ensure that there are no crashes
	sample_images = os.listdir('sample_images/')

	for sample_image in sample_images:
		im = newImage('sample_images/' + sample_image)
		for feature in features:
			feature['func'](im, *feature['args'])



