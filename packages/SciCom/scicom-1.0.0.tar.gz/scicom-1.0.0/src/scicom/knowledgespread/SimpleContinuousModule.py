import mesa


class SimpleCanvas(mesa.visualization.VisualizationElement):
    """Display agents on a map background. No coordinates."""
    local_includes = ["knowledgespread/simple_continuous_canvas.js"]
    portrayal_method = None
    canvas_height = 720
    canvas_width = 1280

    def __init__(self, portrayal_method, canvas_height=720, canvas_width=1280):
        """
        Instantiate a new SimpleCanvas
        """
        self.portrayal_method = portrayal_method
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        new_element = "new Simple_Continuous_Module({}, {})".format(
            self.canvas_width, self.canvas_height
        )
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        """Draw agents."""
        space_state = []
        for obj in model.schedule.agents:
            portrayal = self.portrayal_method(obj)
            x, y = obj.pos
            x = (x - model.space.x_min) / (model.space.x_max - model.space.x_min)
            y = (y - model.space.y_min) / (model.space.y_max - model.space.y_min)
            portrayal["x"] = x
            portrayal["y"] = y
            space_state.append(portrayal)
        return space_state
