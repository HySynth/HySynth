""" This module is just a binding module which helps reference submodules more easily """

from .multi_dim import two_states as ND_two_states

from .single_dim import single_state as SD_single_state
from .single_dim import two_states as SD_two_states
from .single_dim import three_states as SD_three_states
from .single_dim import four_states as SD_four_states

__all__ = ["ND_two_states",
           "SD_single_state",
           "SD_two_states",
           "SD_three_states",
           "SD_four_states", ]

if __name__ == "__main__":
    raise RuntimeError("This module should only be imported and not run directly")
