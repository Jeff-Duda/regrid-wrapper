from enum import IntEnum, unique
from typing import Any


from mpi4py import MPI


@unique
class Tag(IntEnum):
    SET_VARIABLE_DATA = 1


class Comm:
    MPI = MPI

    def __init__(self) -> None:
        self._comm = MPI.COMM_WORLD

    @property
    def rank(self) -> int:
        return self._comm.Get_rank()

    @property
    def size(self) -> int:
        return self._comm.Get_size()

    def barrier(self) -> None:
        self._comm.barrier()

    def bcast(self, value: dict, root: int = 0) -> dict:
        return self._comm.bcast(value, root=root)

    def allgather(self, target: Any) -> Any:
        return self._comm.allgather(target)

    def send(self, *args, **kwargs) -> None:
        self._comm.send(*args, **kwargs)

    def recv(self, *args, **kwargs) -> Any:
        return self._comm.recv(*args, **kwargs)


COMM = Comm()


def reconcile_bounds(bounds: tuple[int, int]) -> tuple[int, int]:
    from regrid_wrapper.context.logging import LOGGER

    LOGGER.debug(f"{bounds=}")
    all_bounds = COMM.allgather(bounds)
    LOGGER.debug(f"{all_bounds=}")
    reconciled_bounds = [[0, 0] for _ in range(len(all_bounds))]
    for idx in range(len(all_bounds)):
        if idx == 0:
            reconciled_bounds[idx] = list(all_bounds[idx])
        else:
            reconciled_bounds[idx][0] = reconciled_bounds[idx - 1][1]
            reconciled_bounds[idx][1] = reconciled_bounds[idx - 1][1] + (
                all_bounds[idx][1] - all_bounds[idx][0]
            )
    LOGGER.debug(f"{reconciled_bounds=}")
    return tuple(reconciled_bounds[COMM.rank])
