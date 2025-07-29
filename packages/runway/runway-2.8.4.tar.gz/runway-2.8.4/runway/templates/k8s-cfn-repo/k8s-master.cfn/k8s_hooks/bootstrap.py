"""Execute the AWS CLI update-kubeconfig command."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any

from runway.config import RunwayConfig

if TYPE_CHECKING:
    from runway.context import CfnginContext

LOGGER = logging.getLogger(__name__)


def copy_template_to_env(path: Path, env: str, region: str) -> None:
    """Copy k8s module template into new environment directory."""
    overlays_dir = path / "overlays"
    template_dir = overlays_dir / "template"
    env_dir = overlays_dir / env
    if template_dir.is_dir():
        if env_dir.is_dir() or (Path(f"{env_dir}-{region}").is_dir()):
            LOGGER.info(
                'Bootstrap of k8s module at "%s" skipped; module '
                "already has a config for this environment",
                path,
            )
        else:
            LOGGER.info(
                'Copying overlay template at "%s" to new environment directory "%s"',
                template_dir,
                env_dir,
            )
            shutil.copytree(template_dir, env_dir, symlinks=True)
            # Update templated environment name in files
            for i in [
                "kustomization.yaml",
                # namespace files can't be directly kustomized
                "namespace.yaml",
            ]:
                templated_file_path = env_dir / i
                if templated_file_path.is_file():
                    filedata = templated_file_path.read_text()
                    if "REPLACE_ME_ENV" in filedata:
                        templated_file_path.write_text(filedata.replace("REPLACE_ME_ENV", env))
    else:
        LOGGER.info(
            'Skipping bootstrap of k8s module at "%s"; no template directory present',
            path,
        )


def create_runway_environments(*, context: CfnginContext, namespace: str, **_: Any) -> bool:
    """Copy k8s module templates into new environment directories.

    Args:
        context: CFNgin context.
        namespace: Current CFNgin namespace.

    Returns: boolean for whether or not the hook succeeded.

    """
    LOGGER.info("Bootstrapping runway k8s modules, looking for unconfigured environments...")

    environment = namespace

    runway_config_path = RunwayConfig.find_config_file(Path.cwd().parent)
    if not runway_config_path.is_file():
        LOGGER.warning("could not find RUNWAYCONFIG=%s", runway_config_path)
        return False

    runway_config = RunwayConfig.parse_file(file_path=runway_config_path)

    for deployment in runway_config.deployments:
        for module in deployment.modules:
            if isinstance(module.path, Path):
                path = module.path.name
            elif isinstance(module.path, str):
                path = module.path
            else:
                path = ""
            if path.endswith(".k8s"):
                copy_template_to_env(
                    runway_config_path.parent / path,
                    environment,
                    context.env.aws_region,
                )
    return True
