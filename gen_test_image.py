
from PIL import Image as PIL_Image

import argparse
import random
import math

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = 'Create a image that can be used to test image_features.py')

	# Size of the image
	parser.add_argument('-s', '--size', metavar = 'V', type = int, nargs = 2, default = [90, 90], help = 'Width and Height of the image in terms of pixels')
	
	# Colors of the 9 quadrants
	parser.add_argument('-q1', '--quad1', metavar = 'COLOR', type = int, nargs = 3, default = [0, 0, 0], help = 'RGB color of quadrant 1')
	parser.add_argument('-q2', '--quad2', metavar = 'COLOR', type = int, nargs = 3, default = [0, 0, 0], help = 'RGB color of quadrant 2')
	parser.add_argument('-q3', '--quad3', metavar = 'COLOR', type = int, nargs = 3, default = [0, 0, 0], help = 'RGB color of quadrant 3')
	parser.add_argument('-q4', '--quad4', metavar = 'COLOR', type = int, nargs = 3, default = [0, 0, 0], help = 'RGB color of quadrant 4')
	parser.add_argument('-q5', '--quad5', metavar = 'COLOR', type = int, nargs = 3, default = [0, 0, 0], help = 'RGB color of quadrant 5')
	parser.add_argument('-q6', '--quad6', metavar = 'COLOR', type = int, nargs = 3, default = [0, 0, 0], help = 'RGB color of quadrant 6')
	parser.add_argument('-q7', '--quad7', metavar = 'COLOR', type = int, nargs = 3, default = [0, 0, 0], help = 'RGB color of quadrant 7')
	parser.add_argument('-q8', '--quad8', metavar = 'COLOR', type = int, nargs = 3, default = [0, 0, 0], help = 'RGB color of quadrant 8')
	parser.add_argument('-q9', '--quad9', metavar = 'COLOR', type = int, nargs = 3, default = [0, 0, 0], help = 'RGB color of quadrant 9')

	parser.add_argument('-rand','--rand_color', help = 'If given, all quadrants will have random colors', action = 'store_true')

	# Output
	parser.add_argument('-f', '--out_file', metavar = 'FILENAME', type = str, nargs = 1, default = [None], help = 'File to save the image to')
 
	args = parser.parse_args()

	width = args.size[0]
	height = args.size[1]

	colors = map(tuple,[args.quad1, args.quad2, args.quad3,
						args.quad4, args.quad5, args.quad6,
						args.quad7, args.quad8, args.quad9])

	if args.rand_color:
		for i in range(len(colors)):
			colors[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

	im = PIL_Image.new("RGB", (width, height), "black")

	wsecs = [int(math.ceil(float(width)  / 3.0 * v)) for v in range(3)]
	hsecs = [int(math.ceil(float(height) / 3.0 * v)) for v in range(3)]

	wsecs = [(wsecs[0], wsecs[1]), (wsecs[1], wsecs[2]), (wsecs[2], width)]
	hsecs = [(hsecs[0], hsecs[1]), (hsecs[1], hsecs[2]), (hsecs[2], height)]

	pix = im.load()

	q = 0
	for ws in wsecs:
		for hs in hsecs:
			for w in xrange(*ws):
				for h in xrange(*hs):
					pix[w, h] = colors[q]
			q += 1

	out_file = args.out_file[0]
	if out_file != None:
		im.save(out_file)
