
import time
from functools import wraps
import numpy as np


def timethis(func):
    '''
    Decorator that reports the execution time.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end - start)
        return result

    return wrapper


def gen_rgbStr(**kwargs):
    r = np.random.randint(256)
    g = np.random.randint(256)
    b = np.random.randint(256)

    return 'rgb(%3d,%3d,%3d)' % (r, g, b)


def circle_ngon_L(r, n, aofs=0.0):
    '''
    Generate a list of points for a regular n-gon.
    Parameters:
    r -> radius of circumscribed circle (center: 0,0)
    n -> number of edges
    aofs -> offset angle for first edges
    '''
    p_L = []
    ap = 2 * np.pi / n
# - adjust angle to North == 0° == 0.0 rad - #
    aofs -= np.pi / 2

    for p in range(n):
        a = p * ap + aofs
        x = np.cos(a) * r
        y = np.sin(a) * r
        p_L.append((x, y))

    return p_L



class GraphCubicBezier:
    '''
    This class holds the points of a cubic bezier curve graph/path/svg d attr
    in a Numpy array
    '''
    def __init__(self, p_L, p_ofs=(0.0,0.0), closed='True'):
        self.P = np.array(p_L, dtype=float)
        self.P_OFS = np.array(p_ofs, dtype=float)
        self.prec = 2
        self.closed = closed
        self.P += self.P_OFS


    def repr(self, format='svg'):
        '''
        Return the points as SVG path d string
        '''
        s = ''
        sfs = 'M%.' + str(self.prec) + 'f,%.' + str(self.prec) + 'f'
        s += sfs % (tuple(self.P[0].flatten()))

        s += 'C'
        sfs = (len(self.P[1:])) * ('%.' + str(self.prec) + 'f,%.' + str(self.prec) + 'f ')
        s += sfs % (tuple(self.P[1:].flatten()))

        if self.closed:
            s += 'z'

        return s



class SVGPathC:
    def __init__(self, p_L, ofs, **kwargs):
        self.graph = GraphCubicBezier(p_L, ofs)
        self.attr_D = { 'fill': 'rgb(128,128,128)', 'stroke': 'rgb(0,0,0)' }
        for k in kwargs.keys():
            self.attr_D[k] = kwargs[k]


    def attr(self, **kwargs):
        if len(kwargs):
            for k in kwargs.keys():
                self.attr_D[k] = kwargs[k]
        else:
            self.attr_D['d'] = self.graph.repr()
            return self.attr_D



class Corolla:
    def __init__(self, n, r, ros_r, petN=12, **kwargs):
        self.n = n
        self.r = r
        self.ros_r = ros_r
        self.petN = petN
        self.petA = 2 * np.pi / self.petN
        self.rv_D = {
            'p0':   0.0
        ,   'a1':   0.1 + np.random.random() * 0.4
        ,   'a2':   0.6 + np.random.random() * 0.4
        ,   'p1':   0.95
        ,   'a3':   0.6 + np.random.random() * 0.4
        ,   'a4':   0.1 + np.random.random() * 0.4
        }
        self.ao_D = {
            'p0':   0.0
        ,   'a1':   (0.1 + np.random.random() * 0.4) * -1
        ,   'a2':   (0.8 + np.random.random() * 0.4) * -1
        ,   'p1':   np.random.random() * 1.0 - 0.5
        ,   'a3':   0.8 + np.random.random() * 0.4
        ,   'a4':   0.1 + np.random.random() * 0.4
        }
        self.shape_D = {}
        self.create()


    @timethis
    def create(self):
        p0_L = circle_ngon_L(self.r * self.rv_D['p0'],  self.petN,  self.petA * self.ao_D['p0'])
        a1_L = circle_ngon_L(self.r * self.rv_D['a1'],  self.petN,  self.petA * self.ao_D['a1'])
        a2_L = circle_ngon_L(self.r * self.rv_D['a2'],  self.petN,  self.petA * self.ao_D['a2'])
        p1_L = circle_ngon_L(self.r * self.rv_D['p1'],  self.petN,  self.petA * self.ao_D['p1'])
        a3_L = circle_ngon_L(self.r * self.rv_D['a3'],  self.petN,  self.petA * self.ao_D['a3'])
        a4_L = circle_ngon_L(self.r * self.rv_D['a4'],  self.petN,  self.petA * self.ao_D['a4'])
        fill_s = gen_rgbStr()

        for i, shape in enumerate(zip(p0_L, a1_L, a2_L, p1_L, a3_L, a4_L, p0_L)):
            self.shape_D["s%02d%04d" % (self.n, i)] = SVGPathC(list(shape), (self.ros_r, self.ros_r)
                                        ,   stroke='rgb(0,0,0)'
                                        ,   strokeWidth=0
                                        ,   fill=fill_s
                                        ,   opacity=0.3
                                        )



class Rosace:
    def __init__(self, r, corN=1, petN=24):
        self.r = r
        self.cor_L = []
        self.corN = corN
# rc -> radius corolla
        rc_min = int(self.r) * 0.3
        rc_L = [ np.random.randint(rc_min, self.r) for i in range(corN - 1)]
        rc_L.append(self.r)
        rc_L.sort(reverse=True)
#logger
        for n, rc in enumerate(rc_L):
            pN = petN - 2 * n
            if pN < 6:
                pN = 6
            self.cor_L.append(Corolla(n + 1, rc, self.r, pN ))


    def morph(self):
# color
        for n, cor in enumerate(self.cor_L):
            rgb_s = gen_rgbStr()
            for i, k in enumerate(cor.shape_D.keys()):
                if k[2] == str(n + 1):
                    cor.shape_D[k].attr(fill=rgb_s)
# shape
        for cor in self.cor_L:
            cor.rv_D = {
                'p0':   0.0
            ,   'a1':   0.1 + np.random.random() * 0.4
            ,   'a2':   0.5 + np.random.random() * 0.5
            ,   'p1':   0.95
            ,   'a3':   0.5 + np.random.random() * 0.5
            ,   'a4':   0.1 + np.random.random() * 0.4
            }
            cor.ao_D = {
                'p0':   0.0
            ,   'a1':   -1.5 + np.random.random()
            ,   'a2':   -1.5 + np.random.random()
            ,   'p1':   -0.5 + np.random.random()
            ,   'a3':   0.5 + np.random.random()
            ,   'a4':   0.5 + np.random.random()
            }
            cor.create()


    @timethis
    def repr(self):
        r = { 'shapes': {} }

        for cor in self.cor_L:
            for k in cor.shape_D.keys():
                r['shapes'][k] = cor.shape_D[k].attr().copy()

        return r
