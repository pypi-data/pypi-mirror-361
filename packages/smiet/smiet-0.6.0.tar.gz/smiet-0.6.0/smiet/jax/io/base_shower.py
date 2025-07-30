import logging
from typing_extensions import Self

import jax
import jax.numpy as jnp
import numpy as np

from smiet import units
from jax_radio_tools import spherical_to_cartesian
from ..utilities.geometry import angle_between
from ..utilities.jax_utils import ModelMeta

logger = logging.getLogger("smiet.jax.io")


class BaseShower(metaclass=ModelMeta):
    """
    Base class to contain the shower parameters.

    The Shower class is used to hold the geometric information for a shower, like the zenith/azimuth,
    as well as the longitudinal profile. It can be used to specify the target parameters for a shower
    in template synthesis.
    """

    __parameter_names = ("xmax", "nmax", "zenith", "azimuth", "magnetic_field")

    def __init__(self: Self) -> None:
        self.logger = logging.getLogger("smiet.jax.io.Shower")

        # shower parameters
        self.__xmax = None
        self.__nmax = None
        self.__x0 = None
        self.__lmbda_params = None
        self.__grammages = None
        self.__long_profile = None

        # observational parameters
        self.__zenith = None
        self.__azimuth = None
        self.__geometry = None  # not used, there for backwards compatibility
        self.__magnetic_field_vector = None
        self.__simulation_core = jnp.array([0, 0, 0])  # Currently fixed

    @property
    def xmax(self: Self) -> float:
        """The $X_{max}$ of the shower, from fitting a GH to the longitudinal profile."""
        if self.__xmax is not None:
            return self.__xmax
        else:
            self.logger.error("Xmax has not been set")

    @property
    def nmax(self: Self) -> float:
        """The $N_{max}$ of the shower, from fitting a GH to the longitudinal profile."""
        if self.__nmax is not None:
            return self.__nmax
        else:
            self.logger.error("Nmax has not been set")

    @property
    def lmbda_params(self: Self) -> np.ndarray:
        r"""
        The $p_0$, $p_1$, and $p_2$ corresponding to the calculation of lambda from the
        fittting to a GH to the longitudinal profile.
        """
        if self.__lmbda_params is not None:
            return self.__lmbda_params
        else:
            self.logger.error("lambda polynomial parameters has not been set")

    @property
    def x0(self: Self) -> float:
        """The $X_0$ of the shower, from fitting a GH to the longitudinal profile."""
        if self.__x0 is not None:
            return self.__x0
        else:
            self.logger.error("x0 has not been set")

    @property
    def grammages(self: Self) -> jax.Array:
        """Array of atmospheric slices in g/cm^2."""
        if self.__grammages is not None:
            return self.__grammages
        else:
            self.logger.error("The grammage has not been set")

    @property
    def slice_grammage(self: Self) -> float:
        """The spacing between each grammage in g/cm^2."""
        if self.__grammages is not None:
            return self.__grammages[1] - self.__grammages[0]
        else:
            self.logger.error(
                "Longitudinal profile has not been set yet, cannot calculate slicing thickness"
            )

    @property
    def long_profile(self: Self) -> float:
        """The longitudinal profile of electrons and positrons in each atmospheric slice."""
        if self.__long_profile is not None:
            # ensure that the length of grammages and ___long_profile is the same
            assert len(self.__long_profile) == len(
                self.__grammages
            ), "Length not same as grammages!"
            return self.__long_profile
        else:
            self.logger.error("Set the longitudinal parameters first.")

    @property
    def nr_slices(self: Self) -> int:
        """The number of slices in the array."""
        if self.__long_profile is not None or self.__grammages is not None:
            # ensure that the length of grammages and __long_profile is the same
            assert len(self.__long_profile) == len(
                self.__grammages
            ), "Length not same as grammages!"
            return len(self.__long_profile)
        else:
            self.logger.error("Set the longitudinal parameters first.")

    @property
    def geometry(self: Self) -> jax.Array:
        """Store the zenith and azimuth. These must be provided in the internal units system."""
        if self.__geometry is not None:
            return self.__geometry
        else:
            self.logger.error("Geometry has not been set")

    @property
    def zenith(self: Self) -> float:
        """The zenith angle in radians."""
        if self.__zenith is not None:
            return self.__zenith
        else:
            self.logger.error("Geometry has not been set")

    @property
    def azimuth(self: Self) -> float:
        """The azimuthal angle in radians."""
        if self.__azimuth is not None:
            return self.__azimuth
        else:
            self.logger.error("Geometry has not been set")

    @property
    def core(self: Self) -> jax.Array:
        """The core (x, y, z in NRR CS) where the EAS hit in the simulation."""
        if self.__simulation_core is not None:
            return self.__simulation_core
        else:
            self.logger.error("The simulation core is not known")

    @property
    def magnetic_field_vector(self: Self) -> float:
        """Magnetic field vector in the NRR coordinate system."""
        if self.__magnetic_field_vector is not None:
            return self.__magnetic_field_vector
        else:
            self.logger.error("The magnetic field vector has not been set")

    @property
    def geomagnetic_angle(self: Self) -> float:
        """The angle between the magnetic field vector and the shower axis."""
        shower_axis = spherical_to_cartesian(self.__zenith / units.rad, self.__azimuth / units.rad)

        return angle_between(self.__magnetic_field_vector, shower_axis)
    
    @xmax.setter
    def xmax(self: Self, xmax: float) -> None:
        self.__xmax = xmax

    @nmax.setter
    def nmax(self: Self, nmax: float) -> None:
        self.__nmax = nmax

    @x0.setter
    def x0(self: Self, x0: float) -> None:
        self.__x0 = x0

    @lmbda_params.setter
    def lmbda_params(self: Self, lmbda_params: np.ndarray) -> None:
        self.__lmbda_params = lmbda_params
    
    @zenith.setter
    def zenith(self: Self, zenith : float) -> None:
        self.__zenith = zenith

    @azimuth.setter
    def azimuth(self: Self, azimuth : float) -> None:
        self.__azimuth = azimuth

    @geometry.setter
    def geometry(self: Self, geo: jax.typing.ArrayLike) -> None:
        assert (
            len(geo) == 2
        ), "Please provide zenith and azimuth components in internal units"

        self.__geometry = jnp.array(geo)

    @grammages.setter
    def grammages(self: Self, grammages: jax.typing.ArrayLike) -> None:
        self.__grammages = grammages

    @long_profile.setter
    def long_profile(self: Self, long_profile: jax.typing.ArrayLike) -> None:
        self.__long_profile = long_profile

    @magnetic_field_vector.setter
    def magnetic_field_vector(self: Self, magnet_field_vector: jax.typing.ArrayLike) -> None:
        assert (
            len(magnet_field_vector) == 3
        ), "B-field vector must contain three components"

        self.__magnetic_field_vector = magnet_field_vector
    
    @core.setter
    def core(self: Self, core: jax.typing.ArrayLike) -> None:
        self.__simulation_core = core

    def set_parameters(
        self: Self, grammages: jax.typing.ArrayLike, params: dict
    ) -> None:
        """
        Set the parameters of the shower model from a dictionary of parameters.

        Parameters
        ----------
        grammages : jax.typing.ArrayLike
            an array of atmospheric depth in g/cm^2
        params : dict
            a dictionary containing values of all parameters.
            this includes:

            - Xmax in g/cm^2 (key: "xmax")
            - Nmax (key: "nmax")
            - zenith angle in radians (key : "zenith")
            - azimuthal angle in radians (key : "azimuth")
            - magnetic field vector in jax.typing.ArrayLike (key : "magnetic_field_vector")

            The function will raise an error if any of these parameters are
            not contained in the dictionary with the specific key.
        """
        # assert list(params.keys()) != list(
        #     self.__parameter_names
        # ), "Parameter names (dict keys) are not assigned correctly."

        self.grammages = grammages

        self.xmax = params["xmax"]
        self.nmax = params["nmax"]
        
        self.geometry = np.array([params["zenith"], params["azimuth"]])
        self.zenith = params["zenith"]
        self.azimuth = params["azimuth"]
        self.magnetic_field_vector = params["magnetic_field_vector"]
        self.core = params["core"]

        # NOTE: we simply ignore storing the parameters themselves for now
        # since they are anyways never used in the tempalte synthesis for scaling
        # (only xmax and nmax are used)
        # self.x0 = params["x0"]
        # self.lmbda_params = jnp.array([params['lmbda_p0'], params['lmbda_p1'], params['lmbda_p2']])
        # self.L = params["L"]
        # self.R = params["R"]

    def set_longitudinal_profile(
        self: Self,
        long_profile: jax.typing.ArrayLike,
    ) -> None:
        """Set the longitudinal profile of the shower."""
        self.__long_profile = long_profile