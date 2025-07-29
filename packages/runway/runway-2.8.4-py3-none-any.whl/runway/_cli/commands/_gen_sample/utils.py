"""Utilities for gen-sample commands."""

import logging
import shutil
from pathlib import Path

import click
from cfn_flip import to_yaml  # pyright: ignore[reportUnknownVariableType]
from typing_extensions import Literal

from ....blueprints.tf_state import TfState
from ....context import CfnginContext

LOGGER = logging.getLogger(__name__.replace("._", "."))
ROOT = Path(__file__).parent.parent.parent.parent
TEMPLATES = ROOT / "templates"


def convert_gitignore(src: Path) -> Path:
    """Rename a gitignore template.

    Keyword Args:
        src: Path object for source file.

    Returns:
        The renamed file if it was created.

    """
    gitignore = src.parent / ".gitignore"
    LOGGER.debug('renaming "%s" to "%s"', src, gitignore)
    src.rename(gitignore)
    return gitignore


def copy_sample(ctx: click.Context, src: Path, dest: Path) -> None:
    """Copy a sample directory.

    Args:
        ctx: Click context object.
        src: Source path.
        dest: Destination path.

    """
    if dest.exists():
        LOGGER.error("Directory %s already exists!", dest)
        ctx.exit(1)
    LOGGER.debug('copying "%s" to "%s"', src, dest)
    shutil.copytree(src, dest)


def write_tfstate_template(
    dest: Path, *, bucket_deletion_policy: Literal["Delete", "Retain"] = "Retain"
) -> None:
    """Write TfState blueprint as a YAML CFN template.

    Args:
        dest: File to be written to.
        bucket_deletion_policy: CloudFormation deletion policy for S3 Bucket.

    """
    LOGGER.debug('writing TfState as a YAML template to "%s"', dest)
    dest.write_text(
        to_yaml(
            TfState("test", CfnginContext(environment={"namespace": "test"})).to_json(
                {"BucketDeletionPolicy": bucket_deletion_policy}
            )
        )
    )
