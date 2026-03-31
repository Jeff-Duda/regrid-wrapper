import subprocess

from regrid_wrapper.app.verify.context import VerifyContext
from regrid_wrapper.context.logging import LOGGER


class NccmpError(Exception): ...


def run_verify(ctx: VerifyContext) -> None:
    LOGGER.info(ctx.model_dump_json(indent=2))
    error_ctr = 0
    for cmd in ctx.iter_nccmp_cmds():
        LOGGER.info(str(cmd))
        try:
            subprocess.check_call(cmd)
            LOGGER.info("verify successful")
        except subprocess.CalledProcessError:
            error_ctr += 1
            if ctx.fail_fast:
                msg = "verify failed, see above for error info"
                LOGGER.error(msg)
                raise NccmpError(msg)
            else:
                LOGGER.warning("verify failed, but fail_fast is False so continuing")
    if error_ctr > 0:
        msg = f"verify failed with {error_ctr=}, see above for error info"
        LOGGER.error(msg)
        raise NccmpError(msg)
