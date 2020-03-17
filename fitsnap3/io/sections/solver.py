from fitsnap3.io.sections.sections import Section
# TODO: Update examples to use SOLVER section instead of MODEL section


class Solver(Section):

    def __init__(self, name, config, args):
        super().__init__(name, config, args)
        self.solver = self.get_value("SOLVER", "solver", "SVD")
        self.normalweight = self.get_value("SOLVER", "normalweight", "-12", "float")
        self.normratio = self.get_value("SOLVER", "normratio", "0.5", "float")
        self.compute_dbvb = self.get_value("SOLVER", "compute_dbvb", "0", "bool")
        self.compute_testerrs = self.get_value("SOLVER", "compute_testerrs", "0", "bool")
        self.delete()
