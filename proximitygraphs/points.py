# https://hpaulkeeler.com/ para point process

import numpy as np

from matplotlib.pyplot import figure
from scipy.stats import poisson, uniform
from scipy.optimize import minimize
from matplotlib.pyplot import savefig, close

from .utils import points_on_sphere

class SetPoints:
    """
    Represent an ordered collection of points in the plane.

    Attributes:
        n (int): The number of points in the collection.
        points (numpy.ndarray): An 2-dimensional numpy array the points.
    """

    # ATTRIBUTES

    @property
    def n(self):
        return self.__n
    
    @property
    def dim(self):
        return self.__dim

    @property
    def points(self):
        return self.__points

    @property
    def pos(self):
        return dict(enumerate(self.__points))

    @property
    def centroid(self):
        return np.mean(self.__points, axis=0)

    # CONSTRUCTORS

    def __init__(self, points):
        self.__points = points
        self.__n, self.__dim= np.shape(points)

    def __add__(self, other):
        new_points = np.concatenate((self.points, other.points), axis=0)
        return SetPoints(new_points)

    def copy(self):
        return SetPoints(self.points)

    @classmethod
    def uniform_square(cls, n=10, dims=2):
        points = np.random.rand(n, dims)
        return cls(points)
    
    @classmethod
    def uniform_over_sphere(cls, n=10, dims=2):
        points = points_on_sphere(n, dims)
        return cls(points)
    
    
    @classmethod
    def uniform_sphere(cls, n=10, dims=2):
        # Referencia
        radius = np.random.rand(n, 1)**(1/dims)
        unit_sphere_surface = points_on_sphere(n, dims)
        points = radius * unit_sphere_surface
        return cls(points)

    @classmethod
    def normal_distr(cls, n=10, dims=2):
        """Generates a sample from a multivariate standard normal distribution"""
        mean = np.zeros(dims)
        cov = np.eye(dims)
        points = np.random.multivariate_normal(mean, cov, n)
        return cls(points)

    @classmethod
    def grid(cls, shape=(3, 3)):
        axes = [np.arange(0, n_points + 1) for n_points in shape]
        mesh = np.meshgrid(*axes, indexing="ij")
        points = np.array(list(zip(*(axis.flat for axis in mesh)))) 
        return cls(points)

    @classmethod
    def hexagonal(cls, n_x=3, n_y=3):
        x = np.cumsum(np.array([1, 2]*n_x))
        x = np.insert(x, 0, 0)
        y = np.cumsum(np.array([np.sqrt(3)]*2*n_y))
        y = np.insert(y, 0, 0)
        xv, yv = np.meshgrid(x, y)
        grid_1 = np.array(list(zip(xv.flat, yv.flat)))
        x = np.cumsum(np.array([2, 1] * n_x))
        x = np.insert(x, 0, 0) - 0.5
        y = np.cumsum(np.array([np.sqrt(3)]*2*n_y))
        y = np.insert(y, 0, 0)
        y = y + 0.5*np.sqrt(3)
        xv, yv = np.meshgrid(x, y)
        grid_2 = np.array(list(zip(xv.flat, yv.flat)))
        points = np.concatenate((grid_1, grid_2))
        return cls(points)

    @classmethod
    def triangular(cls, n_x=3, n_y=3):
        x = np.arange(0, n_x+1)
        y = np.arange(0, np.sqrt(3) * np.floor(n_y/2)+1, np.sqrt(3))
        xv, yv = np.meshgrid(x, y)
        grid_1 = np.array(list(zip(xv.flat, yv.flat)))
        x = x+0.5
        y = np.arange(np.sqrt(3)/2, np.sqrt(3) * np.ceil(n_y/2), np.sqrt(3))
        xv, yv = np.meshgrid(x, y)
        grid_2 = np.array(list(zip(xv.flat, yv.flat)))
        points = np.concatenate((grid_1, grid_2))
        return cls(points)

    @classmethod
    def poissonprocess_square(cls, intensity=10, limit=1):
        limits = ((0, limit),
                  (0, limit))
        # Simulation window parameters
        xmin, xmax = limits[0]
        ymin, ymax = limits[1]
        xdelta = xmax-xmin
        ydelta = ymax-ymin
        area = xdelta*ydelta
        n_points = poisson(intensity*area).rvs()
        x = xdelta*uniform.rvs(0, 1, ((n_points, 1)))+xmin
        y = ydelta*uniform.rvs(0, 1, ((n_points, 1)))+ymin
        points = np.hstack((x, y))
        return cls(points)

    @classmethod
    def poissonprocess_circle(cls, intensity=10, radius=1):
        length = 2*np.pi*radius
        n_points = np.random.poisson(intensity*length)
        theta = 2*np.pi*np.random.uniform(0, 1, n_points)
        x = radius*np.cos(theta)
        y = radius*np.sin(theta)
        points = np.stack((x, y), axis=1)
        return cls(points)

    @classmethod
    def poissonprocess_inhomogeneus(cls, fun_lambda = lambda x, y: x+y,
                                    n_sim=1,
                                    limit=1):
        limits = ((0, limit),
                  (0, limit))
        # fun_lambda = lambda x,y: np.cos(2*x)+np.cos(2*y)
        xmin, xmax = limits[0]
        ymin, ymax = limits[1]
        xdelta = xmax - xmin
        ydelta = ymax - ymin
        area = xdelta*ydelta
        # Find maximum lambda
        fun_neg = lambda x: -fun_lambda(x[0], x[1])
        xy0 = [(xmin + xmax) / 2, (ymin + ymax) / 2]
        results_opt = minimize(fun_neg, xy0,
                               bounds=((xmin, xmax), (ymin, ymax)))
        lambda_neg_min = results_opt.fun
        lambda_max = -lambda_neg_min
        # define thinning probability function
        fun_p = lambda x, y: fun_lambda(x, y)/lambda_max
        # Simulate a Poisson point process
        n_poins = np.random.poisson(area*lambda_max)
        x = np.random.uniform(0, xdelta, ((n_poins, 1)))+xmin
        y = np.random.uniform(0, ydelta, ((n_poins, 1)))+ymin
        # calculate spatially-dependent thinning probabilities
        p = fun_p(x, y)
        # Generate Bernoulli variables (ie coin flips) for thinning
        retained = np.random.uniform(0, 1, ((n_poins, 1))) < p
        # x/y locations of retained points
        x_retained = x[retained]
        y_retained = y[retained]
        points = np.stack((x_retained, y_retained), axis=1)
        return cls(points)

    @classmethod
    def cluster_square(cls, intensity=(10, 10),
                       cluster={"name": "Matern", "param": 0.1},  
                       limit=1):
        limits = ((0, limit),
                  (0, limit))
        # intensity[0] - density of parent Poisson point process
        # indensity[1] - mean number of points in each cluster
        # Extended simulation window parameters
        xmin, xmax = limits[0]
        ymin, ymax = limits[1]
        if cluster["name"] == "Matern":
            radius = cluster["param"]
        elif cluster["name"] == "Thomas":
            radius = 5*cluster["param"]
        xmin_ext = xmin-radius
        xmax_ext = xmax+radius
        ymin_ext = ymin-radius
        ymax_ext = ymax+radius
        xdelta = xmax_ext-xmin_ext
        ydelta = ymax_ext-ymin_ext
        area = xdelta*ydelta
        # Simulated Poisson points process for the parents
        n_points_parent = np.random.poisson(area*intensity[0])
        x_parent = xmin_ext+xdelta*np.random.uniform(0, 1, n_points_parent)
        y_parent = ymin_ext+ydelta*np.random.uniform(0, 1, n_points_parent)
        # Simulate Poisson point process for the daughters
        n_points_daughter = np.random.poisson(intensity[1], n_points_parent)
        n_points = sum(n_points_daughter)
        if cluster["name"] == "Matern":
            # Generate the (relative) locations in polar coordinates
            theta = 2*np.pi*np.random.uniform(0, 1, n_points)
            rho = radius*np.sqrt(np.random.uniform(0, 1, n_points))
            # Convert from polar to Cartesian coordinates
            x_aux = rho*np.cos(theta)
            y_aux = rho*np.sin(theta)
        elif cluster["name"] == "Thomas":
            # Generate the (relative) locations in Cartesian coordinates
            x_aux = np.random.normal(0, cluster["param"], n_points)
            y_aux = np.random.normal(0, cluster["param"], n_points)
        # replicate parent points (ie centres of disks/clusters)
        x = np.repeat(x_parent, n_points_daughter)
        y = np.repeat(y_parent, n_points_daughter)
        x = x+x_aux
        y = y+y_aux
        # thin points if outside the simulation window
        inside = ((x >= xmin) & (x <= xmax) & (y >= ymin) & (y <= ymax))
        # retain points inside simulation window
        x = x[inside]
        y = y[inside]
        points = np.stack((x, y), axis=1)
        return cls(points)

    # METHODS

    def __draw_points(self, fig, figsize, plot_axes, 
                      size, color, axis, position=111,
                      ):
        ax = fig.add_subplot(position)
        ax.scatter(x=self.points[:, plot_axes[0]],
                   y=self.points[:, plot_axes[1]],
                   s=size,
                   color=color,
                   edgecolors=color,
                   linewidths=1)
        ax.set_aspect("equal", adjustable="box")
        ax.tick_params(left=True, bottom=True,
                       labelleft=True, labelbottom=True)
        if axis:
            ax.set_axis_on()
        else:
            ax.set_axis_off()
        return ax

    def draw(self, figsize=(15, 15), 
             plot_axes = (0, 1),
             size=30, color="black",
             axis=True, save=None):
        fig = figure(figsize=figsize)
        ax = self.__draw_points(fig = fig,
                                figsize = figsize,
                                plot_axes = plot_axes,
                                size = size,
                                color = color,
                                axis = axis)
        if save is None:
            return fig, ax
        else:
            savefig(save+".png", bbox_inches='tight')
            close()
        return fig, ax

    def __affin_transformation(self,
                               matrix = None,
                               c = None):
        if matrix is None:
            matrix=np.eye(self.dim)
        if c is None:
            c=np.zeros(self.dim)
        return SetPoints(self.points @ matrix + c)

    def rotation(self, angle, degree=False):
        ###### ERROR #################
        if degree:
            angle = np.radians(angle)
        cos = np.cos(angle)
        sin = np.sin(angle)
        matrix = np.matrix([[cos, sin],
                            [-sin, cos]])
        return self.__affin_transformation(matrix)

    def scaling(self, scales):
        matrix = np.diag(scales)
        return self.__affin_transformation(matrix)

    def traslation(self, c):
        return self.__affin_transformation(c=c)
    
    def perturb(self,  radius):
        ###### ERROR #################
        r = np.random.uniform(0, radius, self.n)**(1/self.dim)
        unit_sphere_surface = points_on_sphere(self.n, self.dim)
        perturbations = r.reshape(-1,1) * unit_sphere_surface
        return SetPoints(self.points+perturbations)
