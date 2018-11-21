from numpy import *
from numpy.linalg import *


def principal_component_analysis(data, n=2):
    means = mean(data, axis=0)
    data = data - means

    # Covariance matrix
    covar = cov(data, rowvar=False)

    # eigvalues
    eigvalues, eigvectors = eig(covar)

    # sort it from big to small
    index = argsort(eigvalues)
    index = index[:-(n + 1):-1]
    eigvector_sorted = eigvectors[:, index]

    # summary it transfer into low Dimensions
    newdata = data * eigvector_sorted

    return newdata
