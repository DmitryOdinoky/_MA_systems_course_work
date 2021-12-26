import cherrypy
from cherrypy.process.plugins import Monitor
import os
import random
import simplejson
import sys
import numpy as np




x = np.array([3, 1, 2, np.NaN])
y = np.array([4, 5, 6, np.NaN])

z = [x, y]

z = np.array(z)

# print(np.argsort(x))