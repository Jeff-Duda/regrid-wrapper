import logging
import os
from dataclasses import dataclass

from pathlib import Path
from mpi4py import MPI


@dataclass
class Environment:
    REGRID_WRAPPER_LOG_DIR: Path
    REGRID_WRAPPER_LOG_PREFIX: str = "Regrid-Wrapper"
    REGRID_WRAPPER_LOG_LEVEL: int = logging.DEBUG

    def create_log_file_path(self) -> Path:
        comm = MPI.COMM_WORLD
        return (
            Path(self.REGRID_WRAPPER_LOG_DIR)
            / f"{self.REGRID_WRAPPER_LOG_PREFIX}-{str(comm.Get_rank()).zfill(4)}.log"
        )


def _get_log_dir_path() -> Path:
    key = "REGRID_WRAPPER_LOG_DIR"
    log_dir = os.environ.get(key, Path(".").resolve())
    return Path(log_dir)


ENV = Environment(REGRID_WRAPPER_LOG_DIR=_get_log_dir_path())  # type: ignore[call-arg]
