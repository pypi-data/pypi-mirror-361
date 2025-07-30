r"""**torchdensityratio** is a package for density ratio estimation based on PyTorch.

==================== =======================================================
**Download**             https://pypi.python.org/pypi/torchdensityratio/

**Source code**          https://github.com/FilippoAiraldi/torch-density-ratio/

**Report issues**        https://github.com/FilippoAiraldi/torch-density-ratio/issues
==================== =======================================================


It implements the Relative unconstrained Least-Squares Importance Fitting (RuLSIF)
method for density ratio estimation [1,2,3].

References
----------
.. [1] Yamada, M., Suzuki, T., Kanamori, T., Hachiya, H. and Sugiyama, M., 2013.
       Relative density-ratio estimation for robust distribution comparison. Neural
       computation, 25(5), pp.1324-1370.
.. [2] Liu, S., Yamada, M., Collier, N. and Sugiyama, M., 2013. Change-point detection
       in time-series data by relative density-ratio estimation. Neural Networks, 43,
       pp.72-83.
.. [3] Kanamori, T., Hido, S. and Sugiyama, M., 2009. A least-squares approach to direct
       importance estimation. The Journal of Machine Learning Research, 10,
       pp.1391-1445.
"""

__version__ = "1.0.1"

__all__ = ["rulsif_fit", "rulsif_predict"]

from .rulsif import rulsif_fit, rulsif_predict
