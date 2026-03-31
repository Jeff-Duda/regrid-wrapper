import argparse
from pathlib import Path

import yaml

from regrid_wrapper.app.verify.context import VerifyContext
from regrid_wrapper.app.verify.verify_cli import verify_cli


def test_happy_path(verify_ctx: VerifyContext, tmp_path: Path) -> None:
    yaml_data = {"rw-verify": verify_ctx.model_dump(mode="json")}
    yaml_path = tmp_path / "verify.yaml"
    yaml_path.write_text(yaml.safe_dump(yaml_data))
    print(yaml.safe_dump(yaml_data, sort_keys=False))

    args = argparse.Namespace(yaml_path=str(yaml_path), root_key="rw-verify")
    verify_cli(args)
