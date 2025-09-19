from .points import SetPoints
from .geometricgraphs import GeometricGraph
from .proximitygraphs import (ProximityGraph, DelaunayG, Convex_Hull, MST,
                              Beta_Skeleton, RNG, GG, Stepping_Stone, NNG,
                              Sigma_Graph, Unit_Disk, SIG, Elliptic_GabrielG)


class Experiment:
    """
    A high-level API to define and run geometric graph experiments.

    An experiment consists of three main stages:
    1. Point Generation: A set of points is created using a specified generator.
    2. Transformations: A series of optional transformations (e.g., rotation,
       translation, perturbation) are applied to the points.
    3. Graph Construction: A geometric or proximity graph is built on the
       final set of points.

    The configuration for the experiment is provided at initialization, and
    the experiment is executed via the `run()` method.
    """
    def __init__(self, config):
        """
        Initializes the experiment with a given configuration.

        Parameters
        ----------
        config : dict
            A dictionary defining the experiment. It should have the following
            keys:
            - 'point_generator' (dict): Specifies the point generator.
              - 'name' (str): The name of the `SetPoints` class method to use
                (e.g., 'uniform_square').
              - 'params' (dict): The parameters for the generator method.
            - 'transformations' (list of dict, optional): A list of transformations
              to apply. Each dictionary should have:
              - 'name' (str): The name of the transformation method (e.g.,
                'rotation').
              - 'params' (dict): The parameters for the transformation.
            - 'graph' (dict): Specifies the graph to be constructed.
              - 'type' (str): The type of graph ('GeometricGraph' or
                'ProximityGraph').
              - 'name' (str): The name of the graph class (e.g., 'GG',
                'DelaunayG', 'complete').
              - 'params' (dict): The parameters for the graph constructor.
        """
        self.config = config
        self.points = None
        self.graph = None

    def run(self):
        """
        Executes the experiment based on the stored configuration.

        This method follows the three stages of the experiment:
        1. It calls the specified point generator from the `SetPoints` class.
        2. It applies each of the specified transformations in sequence to the
           generated points.
        3. It constructs the specified geometric or proximity graph using the
           final transformed points.

        The resulting `SetPoints` and graph objects are stored in the
        `self.points` and `self.graph` attributes, respectively.

        Returns
        -------
        GeometricGraph
            The final graph object constructed by the experiment.

        Raises
        ------
        ValueError
            If an unknown graph type or name is provided in the configuration.
        AttributeError
            If a specified point generator or transformation method does not exist.
        """
        # Step 1: Point Generation
        generator_config = self.config.get('point_generator', {})
        generator_name = generator_config.get('name')
        generator_params = generator_config.get('params', {})
        if not generator_name:
            raise ValueError("Point generator name must be specified in the configuration.")
        
        point_generator_method = getattr(SetPoints, generator_name)
        self.points = point_generator_method(**generator_params)

        # Step 2: Transformations
        if 'transformations' in self.config:
            for transform in self.config['transformations']:
                transform_name = transform.get('name')
                transform_params = transform.get('params', {})
                if not transform_name:
                    raise ValueError("Transformation name must be specified.")
                
                transform_method = getattr(self.points, transform_name)
                self.points = transform_method(**transform_params)
        
        # Step 3: Graph Construction
        graph_config = self.config.get('graph', {})
        graph_type_name = graph_config.get('type')
        graph_class_name = graph_config.get('name')
        graph_params = graph_config.get('params', {})
        if not graph_type_name or not graph_class_name:
            raise ValueError("Graph type and name must be specified in the configuration.")

        # Dynamically find and instantiate the graph class
        graph_class = None
        if graph_type_name == 'GeometricGraph':
            if hasattr(GeometricGraph, graph_class_name):
                graph_class = getattr(GeometricGraph, graph_class_name)
                # Classmethods like 'complete' or 'random_graph' need special handling
                if graph_class_name in ['complete', 'random_graph']:
                    self.graph = graph_class(self.points, **graph_params)
                else: # For a potential __init__ style constructor
                    self.graph = graph_class(self.points, **graph_params)
            else:
                raise ValueError(f"Unknown GeometricGraph name: {graph_class_name}")

        elif graph_type_name == 'ProximityGraph':
            # Proximity graph classes are imported into the current module's globals
            if graph_class_name in globals():
                graph_class = globals()[graph_class_name]
                self.graph = graph_class(self.points, **graph_params)
            else:
                raise ValueError(f"Unknown ProximityGraph name: {graph_class_name}")
        else:
            raise ValueError(f"Unknown graph type: {graph_type_name}")

        return self.points, self.graph