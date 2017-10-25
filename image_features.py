
from PIL import Image as PIL_Image

import math

# TODO:
# 	- Add benchmarking for various image sizes
# 	- Add useful features

# ----------------------
# |  Helper Functions  |
# ----------------------

def toHSV(vs):
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
		return [self.width / self.height]

	def sumOfSizes(self):
		return [self.width + self.height]

	def size(self):
		return [self.width, self.height]

	# ----------------------
	# |    HSV Features    |
	# ----------------------

	def averageBrightness(self):
		return [sum(toHSV(self.pix[x, y])[2] for x in range(self.width) for y in range(self.height)) / float(self.width * self.height)]

	# Divides each dimension into 3 equal sections, and then averages the Hue of only the middle section
	def averageHueOfMiddle(self):
		ws, hs = self._getSections(3)
		return [sum(toHSV(self.pix[x, y])[0] for x in xrange(ws[1][0], ws[1][1]) for y in xrange(hs[1][0], hs[1][1])) / float(ws[1][1] - ws[1][0]) / float(hs[1][1] - hs[1][0])]

	# Divides each dimension into 3 equal sections, and then averages the Saturation of only the middle section
	def averageHueOfMiddle(self):
		ws, hs = self._getSections(3)
		return [sum(toHSV(self.pix[x, y])[1] for x in xrange(ws[1][0], ws[1][1]) for y in xrange(hs[1][0], hs[1][1])) / float(ws[1][1] - ws[1][0]) / float(hs[1][1] - hs[1][0])]

	# ----------------------
	# |    Bin Features    |
	# ----------------------

	# Divides each dimension into 3 equal sections. Then creates a histogram for each of the 9 sections using the provided number of bins.
	# Returns a 36 element list, where each element is the euclidean difference between two of the 9 histograms
	# TODO allow for different binning methods, and different difference methods.
	# TODO allow for pixel_type to be either 'rgb' or 'hsv'
	def binComparison(self, num_bins, pixel_type = 'rgb'):
		# Creates bins
		bins = []
		
		ws, hs = self._getSections(3)
		for wr in ws:
			for hr in hs:
				this_bin = [0] * num_bins

				for x in xrange(wr[0], wr[1]):
					for y in xrange(hr[0], hr[1]):
						v = self.pix[x, y]

						avg_v = float(sum(v)) / float(len(v))

						# TODO Consider better binning options
						b = int(math.floor(avg_v * num_bins / 255.0))

						this_bin[b] += 1
				bins.append(this_bin)
		# Compute differences of bins
		rv = []
		for i in range(num_bins):
			for j in range(num_bins):
				if j <= i:
					continue

				rv.append(math.sqrt(sum(pow(a - b, 2.0) for a, b in zip(bins[i], bins[j]))))
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
		w_sections = [(w_sections[i], (self.width  if i + 1 == num else h_sections[i + 1])) for i in range(num)]
		h_sections = [(h_sections[i], (self.height if i + 1 == num else h_sections[i + 1])) for i in range(num)]

		return w_sections, h_sections

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

	# TODO Test the size features

	# TODO Test the averageBrightness for images that are only one color

	# Test toHSV()
	print 'Testing toHSV()'
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
		comp_hsv = toHSV(test['rgb'])

		if comp_hsv[0] != test['hsv'][0] or \
				abs(comp_hsv[1] - test['hsv'][1]) > 0.001 or \
				abs(comp_hsv[2] - test['hsv'][2]) > 0.001:
			raise Exception('Error in toHSV(): got toHSV(' + str(test['rgb']) + ') = ' + str(comp_hsv) + '; expected ' + str(test['hsv']))
	print 'Passed toHSV() tests'