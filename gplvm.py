# Copyright (c) 2012, GPy authors (see AUTHORS.txt).
# Licensed under the BSD 3-clause license (see LICENSE.txt)
import numpy as _np
default_seed = _np.random.seed(123344)
SAVEDFILE_TRAIN='jabongRep_Train.npy'
SAVEDFILE_TEST='jabongRep_Test.npy'
DIM=30
def gplvm(SAVEDFILE,optimize=True, verbose=True):
    import GPy
    X= np.load(SAVEDFILE)
    Xn = X - X.mean()
    Xn /= Xn.std()
    print Xn.shape
    m = GPy.models.GPLVM(Xn, DIM)
    if optimize: m.optimize('scg', messages=verbose, max_iters=1000)
    np.save('jabong_'+DIM+'.npy', m)

gplvm(SAVEDFILE_TRAIN)