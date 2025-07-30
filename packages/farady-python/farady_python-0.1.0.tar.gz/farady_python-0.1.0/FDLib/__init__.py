import matplotlib.pyplot as plt

__all__ = [
    "FDLibrary", "FDLumpedElement",
    "Arc", "Path", "Polygon"
]


class FDBase:
    metalLayers = []
    Parameters = {}
    ParameterOrder = []
    chosen_parameters = {}
    pins = []

    def check_param(self):
        raise NotImplementedError()

    def reload(self):
        raise NotImplementedError()

    def show(self):
        raise NotImplementedError()

    def run(self):
        [setattr(self, k, v) for k, v in self.Parameters.items()]
        self.reload()
        self.show()


class FDLumpedElement(FDBase):
    def __init__(self):
        self.spice = []

    def show(self):
        for itr in self.spice:
            print(itr)


class FDLibrary(FDBase):
    def __init__(self):
        self.specifications = []

    @staticmethod
    def _extract(data):
        x, y = [], []
        for xi, yi in data:
            x.append(xi)
            y.append(yi)
        return x, y

    def show(self):
        fig, ax = plt.subplots()
        ax.set_title("Result")
        for one in self.specifications:
            x, y = self._extract(one.location)
            ax.plot(x, y)
            for pos in one.vias:
                c = plt.Circle(pos, radius=4, color="red")
                ax.add_patch(c)
        plt.show()


class Polygon:
    def __init__(
            self, location, pins, pins_location, metalLayer, vias, net
    ):
        self.location = location
        self.pins = pins
        self.pins_location = pins_location
        self.metalLayer = metalLayer
        self.vias = vias
        self.net = net

    def __repr__(self) -> "str":
        return (
            f"<Polygon:\n"
            f"  pins={self.pins}, pins_location={self.pins_location}\n"
            f"  metalLayer={self.metalLayer}, vias={self.vias}, net={self.net}\n"
            f"  location={self.location}\n"
            f">"
        )


class Arc(Polygon):
    def __init__(
            self, location, innerRadius, outerRadius, beginAngle, endAngle,
            pins, pins_location, clockwise, metalLayer, arc_type, vias, net
    ):
        super().__init__(location, pins, pins_location, metalLayer, vias, net)
        self.innerRadius = innerRadius
        self.outerRadius = outerRadius
        self.beginAngle = beginAngle
        self.endAngle = endAngle
        self.clockwise = clockwise
        self.arc_type = arc_type

    def __repr__(self) -> "str":
        return (
            f"<Arc:\n"
            f"  location={self.location}, pins={self.pins}, pins_location={self.pins_location}\n"
            f"  metalLayer={self.metalLayer}, vias={self.vias}, net={self.net}\n"
            f"  innerRadius={self.innerRadius}, outerRadius={self.outerRadius}\n"
            f"  beginAngle={self.beginAngle}, endAngle={self.endAngle}\n"
            f"  clockwise={self.clockwise}, arc_type={self.arc_type}\n"
            f">"
        )


class Path(Polygon):
    def __init__(
            self, location, width, metalLayer, pins,
            pins_location, path_type, corner_type, vias, net
    ):
        super().__init__(location, pins, pins_location, metalLayer, vias, net)
        self.width = width
        self.path_type = path_type
        self.corner_type = corner_type

    def __repr__(self) -> "str":
        return (
            f"<Path:\n"
            f"  pins={self.pins}, pins_location={self.pins_location}\n"
            f"  metalLayer={self.metalLayer}, vias={self.vias}, net={self.net}\n"
            f"  width={self.width}, path_type={self.path_type}, corner_type={self.corner_type}\n"
            f"  location={self.location}\n"
            f">"
        )
