from .solver import Solver
from ..parallel_tools import pt
from ..io.input import config
import numpy as np

try:
    from ..lib.scalapack_solver.scalapack import lstsq

    class ScaLAPACK(Solver):

        def __init__(self, name):
            super().__init__(name)

        def perform_fit(self):
            if pt.shared_arrays['configs_per_group'].testing_elements != 0:
                testing = -1*pt.shared_arrays['configs_per_group'].testing_elements
            else:
                testing = len(pt.shared_arrays['w'].array)
            if testing < 0:
                raise NotImplementedError("Testing w/ the ScaLAPACK solver is not implemented!")
            pt.split_by_node(pt.shared_arrays['w'])
            pt.split_by_node(pt.shared_arrays['a'])
            pt.split_by_node(pt.shared_arrays['b'])
            total_length = pt.shared_arrays['a'].get_total_length()
            node_length = pt.shared_arrays['a'].get_node_length()
            proc_length = pt.shared_arrays['a'].get_proc_length()
            scraped_length = pt.shared_arrays['a'].get_scraped_length()
            lengths = [total_length, node_length, proc_length, scraped_length]
            w = pt.shared_arrays['w'].array[:testing]
            aw, bw = w[:, np.newaxis] * pt.shared_arrays['a'].array[:testing], w * pt.shared_arrays['b'].array[:testing]

    #        Transpose method does not work with Quadratic SNAP (why?)
    #        We need to revisit this preconditioning of the linear problem, we can make this a bit more elegant.
    #        Since this breaks some examples this will stay as a 'secret' feature.
    #        Need to chat with some mathy people on how we can profile A and find good preconditioners.
    #        Will help when we want to try gradient based linear solvers as well.
            if config.sections['EXTRAS'].apply_transpose:
                bw = aw.T@bw
                aw = aw.T@aw
            self.fit = lstsq(aw, bw, lengths=lengths)
            self.fit = pt.allgather(self.fit)[0]
            # self.fit, residues, rank, s = lstsq(aw, bw, 1.0e-13)

        def _dump_a(self):
            np.savez_compressed('a.npz', a=pt.shared_arrays['a'].array)

        def _dump_x(self):
            np.savez_compressed('x.npz', x=self.fit)

        def _dump_b(self):
            b = pt.shared_arrays['a'].array @ self.fit
            np.savez_compressed('b.npz', b=b)

except ModuleNotFoundError:

    class ScaLAPACK(Solver):

        def __init__(self, name):
            super().__init__(name)
            raise ModuleNotFoundError("ScaLAPACK module not installed in lib")
