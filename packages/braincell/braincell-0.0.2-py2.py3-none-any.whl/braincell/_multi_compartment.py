# Copyright 2024 BDP Ecosystem Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from typing import Optional, Callable, Sequence, Tuple

import brainstate
import brainunit as u
import numpy as np

from ._base import HHTypedNeuron, IonChannel
from ._integrator import get_integrator
from ._morphology import Morphology
from ._morphology_utils import diffusive_coupling
from ._protocol import DiffEqState
from ._typing import Initializer

__all__ = [
    'MultiCompartment',
]


class MultiCompartment(HHTypedNeuron):
    r"""
    A multi-compartment neuronal model that simulates spatially extended neurons.

    This class implements a detailed neuron model with multiple connected compartments
    that can represent complex dendritic arbors and axons. Each compartment has its own
    membrane potential dynamics and can contain different ion channel distributions.
    The compartments are electrically coupled through axial resistances.

    Parameters
    ----------
    size : brainstate.typing.Size
        Shape of the neuron population.
    connection : Sequence[Tuple[int, int, int]] or numpy.ndarray
        Connectivity information between compartments. Each entry is a tuple of
        (child_idx, parent_idx, connection_site) where connection_site is either
        0.5 (middle) or 1 (end) of the parent compartment.
    Ra : brainstate.typing.ArrayLike, optional
        Axial resistivity in ohm·cm. Default is 100 ohm·cm.
    cm : brainstate.typing.ArrayLike, optional
        Specific membrane capacitance in μF/cm². Default is 1.0 μF/cm².
    diam : brainstate.typing.ArrayLike, optional
        Diameter of compartments in μm. Default is 1.0 μm.
    L : brainstate.typing.ArrayLike, optional
        Length of compartments in μm. Default is 10.0 μm.
    V_th : Union[brainstate.typing.ArrayLike, Callable], optional
        Threshold potential for spike detection in mV. Default is 0.0 mV.
    V_initializer : Union[brainstate.typing.ArrayLike, Callable], optional
        Initial membrane potential or initializer function. Default is uniform random between -70mV and -60mV.
    spk_fun : Callable, optional
        Surrogate gradient function for spike generation. Default is ReluGrad.
    solver : str or Callable, optional
        Numerical integration method. Default is 'exp_euler'.
    name : str, optional
        Name identifier for the neuron model.
    Gl : brainstate.typing.ArrayLike, optional
        Leak conductance in mS/cm². Default is 0 mS/cm².
    El : brainstate.typing.ArrayLike, optional
        Leak reversal potential in mV. Default is -65 mV.
    **ion_channels
        Additional keyword arguments for ion channels to be added to the neuron model.

    Attributes
    ----------
    Ra : Quantity
        Axial resistivity.
    cm : Quantity
        Specific membrane capacitance.
    diam : Quantity
        Compartment diameters.
    L : Quantity
        Compartment lengths.
    A : Quantity
        Surface areas of compartments.
    connection : ndarray
        Connectivity matrix between compartments.
    resistances : Quantity
        Axial resistances between connected compartments.
    V_th : Quantity or Callable
        Threshold potential for spike detection.
    V_initializer : Quantity or Callable
        Initial membrane potential values or initializer.
    spk_fun : Callable
        Surrogate gradient function used for spike generation.
    solver : Callable
        Numerical integration solver function.

    Notes
    -----
    This class is subclassed from :class:`braincell.HHTypedNeuron`.
    The multi-compartment model simulates the spatial properties of neurons by dividing
    the neuron into electrically connected compartments. Currents can flow between compartments
    based on the voltage differences and axial resistances, allowing for a more accurate
    representation of dendritic integration, action potential propagation, and other
    spatially-dependent phenomena.
    """

    __module__ = 'braincell'

    def __init__(
        self,
        size: brainstate.typing.Size,

        # morphology parameters
        connection: Sequence[Tuple[int, int, float]] | np.ndarray,

        # neuron parameters
        Ra: Initializer = 100. * (u.ohm * u.cm),  # resistivity
        cm: Initializer = 1.0 * (u.uF / u.cm ** 2),  # membrane capacitance
        diam: Initializer = 1. * u.um,  # diameter
        L: Initializer = 10. * u.um,  # length

        # membrane potentials
        V_th: Initializer = 0. * u.mV,
        V_initializer: Initializer = brainstate.init.Uniform(-70 * u.mV, -60. * u.mV),
        spk_fun: Callable = brainstate.surrogate.ReluGrad(),

        # others
        solver: str | Callable = 'exp_euler',
        name: Optional[str] = None,

        Gl: Initializer = 0 * (u.mS / u.cm ** 2),  # for splitting
        El: Initializer = -65 * u.mV,  # for splitting

        **ion_channels
    ):
        super().__init__(size, name=name, **ion_channels)

        # for splitting linear term
        self.Gl = brainstate.init.param(Gl, self.varshape)
        self.El = brainstate.init.param(El, self.varshape)

        # parameters for morphology
        self.Ra = brainstate.init.param(Ra, self.varshape)
        self.cm = brainstate.init.param(cm, self.varshape)
        self.diam = brainstate.init.param(diam, self.varshape)
        self.L = brainstate.init.param(L, self.varshape)
        self.A = np.pi * self.diam * self.L  # surface area

        # connections between compartments
        connection = np.asarray(connection)
        assert connection.shape[1] == 3, (
            'The connection should be a sequence of tuples with three elements. '
            'The first element is the children node, '
            'the second element is the parent node, '
            'the third element is the connection position in the parent node, only for 0.5(middle) and 1(end)'
        )
        self.connection = connection
        if self.connection.max() >= self.n_compartment:
            raise ValueError('The connection should be within the range of compartments. '
                             f'But we got {self.connection.max()} >= {self.n_compartment}.')
        self.resistances = init_coupling_weight(self.n_compartment, connection, self.diam, self.L, self.Ra)

        # parameters for membrane potentials
        self.V_th = brainstate.init.param(V_th, self.varshape)
        self.V_initializer = V_initializer
        self.spk_fun = spk_fun

        # numerical solver
        self.solver = get_integrator(solver)

    @property
    def pop_size(self) -> Tuple[int, ...]:
        """
        Returns the shape of the neuron population, excluding the compartment dimension.

        Returns
        -------
        Tuple[int, ...]
            The shape of the neuron population (all dimensions except the last, which
            corresponds to the number of compartments).
        """
        return self.varshape[:-1]

    @property
    def n_compartment(self) -> int:
        """
        Returns the number of compartments in the neuron model.

        Returns
        -------
        int
            The number of compartments, corresponding to the last dimension of the neuron's variable shape.
        """
        return self.varshape[-1]

    def init_state(self, batch_size=None):
        self.V = DiffEqState(brainstate.init.param(self.V_initializer, self.varshape, batch_size))
        super().init_state(batch_size)

    def reset_state(self, batch_size=None):
        self.V.value = brainstate.init.param(self.V_initializer, self.varshape, batch_size)
        super().reset_state(batch_size)

    def pre_integral(self, *args):
        """
        Perform pre-integration operations on the neuron's ion channels.

        This method is called before the integration step to prepare the ion channels
        for the upcoming computation. It iterates through all ion channels associated
        with this neuron and calls their respective pre_integral methods.

        Parameters
        -----------
        *args : tuple
            Variable length argument list. Not used in the current implementation
            but allows for future extensibility.

        Returns
        --------
        None
            This method doesn't return any value but updates the internal state
            of the ion channels.
        """
        for key, node in self.nodes(IonChannel, allowed_hierarchy=(1, 1)).items():
            node.pre_integral(self.V.value)

    def compute_derivative(self, I_ext=0. * u.nA):
        """
        Compute the derivative of the membrane potential for the multi-compartment neuron model.

        This method calculates the derivative of the membrane potential by considering
        external currents, axial currents between compartments, synaptic currents,
        and ion channel currents. It also computes the derivatives for all ion channels.

        Parameters
        -----------
        I_ext : Quantity, optional
            External current input to the neuron. Default is 0 nanoamperes.

        Returns
        --------
        None
            This method doesn't return a value but updates the internal state of the neuron,
            specifically the derivative of the membrane potential (self.V.derivative).

        Notes
        ------
        The method performs the following steps:
        1. Normalizes external currents by the compartment surface area.
        2. Calculates axial currents between compartments.
        3. Computes synaptic currents.
        4. Sums up all ion channel currents.
        5. Calculates the final derivative of the membrane potential.
        6. Computes derivatives for all associated ion channels.
        """

        # [ Compute the derivative of membrane potential ]
        # 1. external currents
        I_ext = I_ext / self.A

        # 2.axial currents
        _compute_axial_current = brainstate.environ.get('compute_axial_current', True)
        if _compute_axial_current:
            I_axial = diffusive_coupling(self.V.value, self.connection, self.resistances) / self.A
        else:
            I_axial = self.Gl * self.El  # u.Quantity(0., unit=u.get_unit(I_ext))

        # 3. synapse currents
        I_syn = self.sum_current_inputs(0. * u.nA / u.cm ** 2, self.V.value)

        # 4. channel currents
        I_channel = None
        for key, ch in self.nodes(IonChannel, allowed_hierarchy=(1, 1)).items():
            I_channel = ch.current(self.V.value) if I_channel is None else (I_channel + ch.current(self.V.value))

        # 5. derivatives
        self.V.derivative = (I_ext + I_axial + I_syn + I_channel) / self.cm

        # [ integrate dynamics of ion and ion channel ]
        # check whether the children channel have the correct parents.
        for key, node in self.nodes(IonChannel, allowed_hierarchy=(1, 1)).items():
            node.compute_derivative(self.V.value)

    def post_integral(self, I_ext=0. * u.nA):
        """
        Perform post-integration operations on the neuron's state.

        This method is called after the integration step to update the membrane potential
        and perform any necessary post-integration operations on ion channels.

        Parameters
        -----------
        I_ext : Quantity, optional
            External current input to the neuron. Default is 0 nanoamperes.
            Note: This parameter is not used in the current implementation but is
            included for consistency with other methods.

        Returns
        --------
        None
            This method doesn't return any value but updates the neuron's internal state.
        """
        self.V.value = self.sum_delta_inputs(init=self.V.value)
        for key, node in self.nodes(IonChannel, allowed_hierarchy=(1, 1)).items():
            node.post_integral(self.V.value)

    def update(self, I_ext=0. * u.nA):
        """
        Update the neuron's state and compute spike occurrences.

        This function performs a single update step for the neuron, solving its
        differential equations and determining if a spike has occurred.

        Parameters
        -----------
        I_ext : Quantity, optional
            External current input to the neuron. Default is 0 nanoamperes.

        Returns
        --------
        Quantity
            A binary value indicating whether a spike has occurred (1) or not (0)
            for each compartment of the neuron.
        """
        last_V = self.V.value
        t = brainstate.environ.get('t')
        dt = brainstate.environ.get('dt')
        self.solver(self, t, dt, I_ext)
        return self.get_spike(last_V, self.V.value)

    def get_spike(self, last_V, next_V):
        """
        Determine if a spike has occurred based on the membrane potential change.

        This function calculates whether a spike has occurred by comparing the previous
        and current membrane potentials to the threshold potential.

        Parameters
        -----------
        last_V : Quantity
            The membrane potential at the previous time step.
        next_V : Quantity
            The membrane potential at the current time step.

        Returns
        --------
        Quantity
            A value between 0 and 1 indicating the likelihood of a spike occurrence.
            A value closer to 1 suggests a higher probability of a spike.

        Notes
        ------
        The function uses a surrogate gradient function (self.spk_fun) to approximate
        the non-differentiable spike event, allowing for backpropagation in learning algorithms.
        """
        denom = 20.0 * u.mV
        return (
            self.spk_fun((next_V - self.V_th) / denom) *
            self.spk_fun((self.V_th - last_V) / denom)
        )


class MorphologicalCell(MultiCompartment):
    def __init__(
        self,
        size: brainstate.typing.Size,
        morphology: Morphology,
        V_th: Initializer = 0. * u.mV,
        V_initializer: Initializer = brainstate.init.Uniform(-70 * u.mV, -60. * u.mV),
        spk_fun: Callable = brainstate.surrogate.ReluGrad(),
        solver: str | Callable = 'exp_euler',
        name: Optional[str] = None,
        **ion_channels
    ):
        super().__init__(
            size=size,
            V_th=V_th,
            V_initializer=V_initializer,
            spk_fun=spk_fun,
            solver=solver,
            name=name,
            **ion_channels
        )
