import logging
import os
from dataclasses import dataclass
from enum import StrEnum, unique
from pathlib import Path

from mpi4py import MPI


@unique
class Platform(StrEnum):
    URSA = "ursa"
    GAEAC6 = "gaeac6"


@dataclass
class Environment:
    REGRID_WRAPPER_LOG_DIR: Path = Path(".")
    REGRID_WRAPPER_LOG_PREFIX: str = "Regrid-Wrapper"
    REGRID_WRAPPER_LOG_LEVEL: int = logging.INFO
    REGRID_WRAPPER_PLATFORM: Platform = Platform.URSA
    REGRID_WRAPPER_TEST_TMPDIR: Path | None = None

    def create_log_file_path(self) -> Path:
        comm = MPI.COMM_WORLD
        return Path(self.REGRID_WRAPPER_LOG_DIR) / f"{self.REGRID_WRAPPER_LOG_PREFIX}-{str(comm.Get_rank()).zfill(4)}.log"

    def __post_init__(self) -> None:
        platform = os.environ.get("REGRID_WRAPPER_PLATFORM", "URSA")
        self.REGRID_WRAPPER_PLATFORM = Platform(platform.lower())

        key = "REGRID_WRAPPER_LOG_DIR"
        log_dir = os.environ.get(key, Path(".").resolve())
        self.REGRID_WRAPPER_LOG_DIR = Path(log_dir)

        test_tmpdir = os.environ.get("REGRID_WRAPPER_TEST_TMPDIR", None)
        if test_tmpdir is not None:
            self.REGRID_WRAPPER_TEST_TMPDIR = Path(test_tmpdir)
            assert self.REGRID_WRAPPER_TEST_TMPDIR.exists()
            assert self.REGRID_WRAPPER_TEST_TMPDIR.is_dir()


ENV = Environment()
