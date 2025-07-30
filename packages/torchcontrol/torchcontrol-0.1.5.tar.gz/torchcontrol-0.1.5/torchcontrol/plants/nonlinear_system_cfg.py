"""
nonlinear_system_cfg.py
Configuration for NonlinearSystem plant (general nonlinear system).
"""
from __future__ import annotations

import torch
from ..system import Parameters
from .plant_cfg import PlantCfg, configclass
from .nonlinear_system import NonlinearSystem

@configclass
class NonlinearSystemCfg(PlantCfg):
    """Configuration for NonlinearSystem plant."""
    
    class_type: type = NonlinearSystem
    
    dynamics: callable = None
    """Callable for system dynamics: `dx/dt = f(x, u, t, params)`
    ```
    def dynamics(x: Tensor, u: Tensor, t: float, params: Parameters) -> Tensor:
        # x: state, shape=(num_envs, state_dim)
        # u: input, shape=(num_envs, action_dim)
        # t: time, float
        # params: parameters
        return dx/dt # shape=(num_envs, state_dim)
    ```
    """
    
    output: callable = None
    """Optional callable for system output: `y = g(x, u, t, params)`. If None, `y = x`.
    ```
    def output(x: Tensor, u: Tensor, t: float, params: Parameters) -> Tensor:
        # x: state, shape=(num_envs, state_dim)
        # u: input, shape=(num_envs, action_dim)
        # t: time, float
        # params: parameters
        return y # shape=(num_envs, output_dim)
    ```
    """
    
    params: Parameters = None
    """Parameters dataclass for the dynamics/output functions."""

    def __repr__(self):
        return f"{super().__repr__()}dynamics: {self.dynamics}\noutput: {self.output}\nparams: {self.params}\n"

    def __post_init__(self):
        """Post-initialization"""
        # dynamics and output must be callable functions
        assert callable(self.dynamics), "dynamics must be a callable function"
        if self.output is not None:
            assert callable(self.output), "output must be a callable function if provided"
        else:
            self.output = lambda x, u, t, params: x # all state feedback if output is None
        # Parameters shape assert
        if self.params is None:
            self.params = Parameters()
        else:
            # If force_batch is true, add a batch dimension to the parameters when there is a confused shape
            force_batch = self.params.force_batch
            for k, v in self.params.__dict__.items():
                if not isinstance(v, torch.Tensor):
                    continue
                # Only allow scalar, 1D, 2D or 3D tensors, and 3D tensors must have first dimension equal to num_envs
                assert v.dim() <= 3, f"Parameter '{k}' must be a scalar, 1D, 2D or 3D tensor, but got {v.shape}"
                # 3D tensors must have first dimension equal to num_envs
                if v.dim() == 3:
                    assert v.shape[0] == self.num_envs, f"Parameter '{k}' with dim=3 must have shape[0]==num_envs, got {v.shape}"
        # Call the parent post_init
        super().__post_init__()