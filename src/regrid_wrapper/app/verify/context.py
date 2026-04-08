from pathlib import Path
from typing import Iterator

from pydantic import BaseModel, Field


class VerifyPair(BaseModel):
    actual: Path
    expected: Path
    variables: tuple[str, ...] | None = None


class VerifyContext(BaseModel):
    verify_pairs: tuple[VerifyPair, ...] = Field(min_length=1)
    baseline_dir: Path | None = None
    expt_dir: Path | None = None
    tolerance: float = 1e-12
    verbose: bool = True
    fail_fast: bool = False

    @property
    def verify_pairs_full_path(self) -> tuple[VerifyPair, ...]:
        ret = []
        for verify_pair in self.verify_pairs:
            actual = verify_pair.actual
            if not actual.exists():
                if self.expt_dir is None:
                    raise ValueError(f"expt_dir must be set if actual path does not exist. {actual=}")
                actual = self.expt_dir / actual
            expected = verify_pair.expected
            if not expected.exists():
                if self.baseline_dir is None:
                    raise ValueError(f"baseline_dir must be set if expected path does not exist. {expected=}")
                expected = self.baseline_dir / expected
            ret.append(VerifyPair(actual=actual, expected=expected, variables=verify_pair.variables))
        return tuple(ret)

    def iter_nccmp_cmds(self) -> Iterator[tuple[str, ...]]:
        for verify_pair in self.verify_pairs_full_path:
            cmd = ["nccmp"]
            if self.verbose:
                cmd.append("--verbose")
            if verify_pair.variables is not None:
                v = ",".join(verify_pair.variables)
                cmd += ["-v", v]
            cmd += ["-d", "-m", "-t", str(self.tolerance), str(verify_pair.actual), str(verify_pair.expected)]
            yield tuple(cmd)
