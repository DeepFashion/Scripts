import numpy as np
np.random.seed(23423478) # random seed for consistency
from PIL import Image
from sklearn import random_projection
import scipy.io
import pylab as pylab

FILENAME_TRAIN='/home/siddhantmanocha/Projects/neural/caffe-cvprw15/examples/deepFashion/train.txt'
FILENAME_TEST='/home/siddhantmanocha/Projects/neural/caffe-cvprw15/examples/deepFashion/test.txt'
DIRNAME='/home/siddhantmanocha/Projects/jabongImages/'
SAVEDFILE_TRAIN='jabongRep_Train.npy'
SAVEDFILE_TEST='jabongRep_Test.npy'
WIDTH=150
HEIGHT=205

# im2 = im.resize((width, height), Image.NEAREST)  # use nearest neighbour
# im3 = im.resize((width, height), Image.BILINEAR) # linear interpolation in a 2x2 environment
# im4 = im.resize((width, height), Image.BICUBIC)  # cubic spline interpolation in a 4x4 environment
# im5 = im.resize((width, height), Image.ANTIALIAS)# best down-sizing filter

def main(FILENAME,SAVEDFILE):
	with open(FILENAME,'r') as f:
		data=f.readlines()

	print FILENAME,SAVEDFILE,len(data)
	
	for i in range(0,len(data)):
		fname=data[i].split(' ')[0]
		loc=DIRNAME+fname.split('/')[1]
		data[i]=loc

	imlist=data[:25000]
	im = np.array(Image.open(imlist[0])) # open one image to get size
	m,n = im.shape[0:2] # get the size of the images
	imnbr = len(imlist) # get the number of images

	# create matrix to store all flattened images
	immatrix = np.array([np.array((Image.open(im)).resize((WIDTH, HEIGHT), Image.BILINEAR)).flatten() for im in imlist],'f')
	np.save(SAVEDFILE, immatrix)
	print immatrix.shape
	# imm1=np.load(SAVEDFILE)
	# print imm1.shape

main(FILENAME_TRAIN,SAVEDFILE_TRAIN)
main(FILENAME_TEST,SAVEDFILE_TEST)
