"""CFNgin session caching."""

from __future__ import annotations

import logging

import boto3

from ..aws_sso_botocore.session import Session
from ..constants import BOTO3_CREDENTIAL_CACHE
from .ui import ui

LOGGER = logging.getLogger(__name__)

DEFAULT_PROFILE = None


def get_session(
    region: str | None = None,
    profile: str | None = None,
    access_key: str | None = None,
    secret_key: str | None = None,
    session_token: str | None = None,
) -> boto3.Session:
    """Create a thread-safe boto3 session.

    Args:
        region: The region for the session.
        profile: The profile for the session.
        access_key: AWS Access Key ID.
        secret_key: AWS secret Access Key.
        session_token: AWS session token.

    Returns:
        A thread-safe boto3 session.

    """
    if profile:
        LOGGER.debug(
            'building session using profile "%s" in region "%s"',
            profile,
            region or "default",
        )
    elif access_key:
        LOGGER.debug(
            'building session with Access Key "%s" in region "%s"',
            access_key,
            region or "default",
        )

    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token,
        botocore_session=Session(),
        region_name=region,
        profile_name=profile,
    )
    cred_provider = session._session.get_component("credential_provider")  # type: ignore
    provider = cred_provider.get_provider("assume-role")  # type: ignore
    provider.cache = BOTO3_CREDENTIAL_CACHE
    provider._prompter = ui.getpass  # noqa: SLF001
    return session
