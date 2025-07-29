import io
from collections.abc import Iterable
from pathlib import Path
from typing import Literal, Self

import pyzipper  # type: ignore[import-untyped]
import requests
from loguru import logger

from sample_finder.validators import verify_md5, verify_sha1, verify_sha224, verify_sha256, verify_sha384, verify_sha512

HASH_TYPE = Literal[
    "md5",
    "sha1",
    "sha224",
    "sha256",
    "sha384",
    "sha512",
]


class Source:
    """Abstract class for Source."""

    NAME: str | None = None
    SUPPORTED_HASHES: Iterable[HASH_TYPE] = (
        "md5",
        "sha1",
        "sha224",
        "sha256",
        "sha384",
        "sha512",
    )

    DEFAULT_ZIP_PASSWORD = b"infected"

    def __init__(self, config: dict[str, str]) -> None:
        """Construct a source."""
        self._session = requests.Session()
        self._config = config

    @classmethod
    def supported_hash(cls, h: str) -> bool:
        """Check if the hash matches one of the supported hashes."""
        return (
            ("md5" in cls.SUPPORTED_HASHES and verify_md5(h))
            or ("sha1" in cls.SUPPORTED_HASHES and verify_sha1(h))
            or ("sha224" in cls.SUPPORTED_HASHES and verify_sha224(h))
            or ("sha256" in cls.SUPPORTED_HASHES and verify_sha256(h))
            or ("sha384" in cls.SUPPORTED_HASHES and verify_sha384(h))
            or ("sha512" in cls.SUPPORTED_HASHES and verify_sha512(h))
        )

    def download_file(self, sample_hash: str, output_path: Path) -> bool:
        """
        Download a sample from a source.

        This should be implemented by each source.
        """
        raise NotImplementedError

    def _get(self, url: str, params: dict[str, str] | None = None) -> requests.Response | None:
        try:
            response = self._session.get(url, params=params)
        except requests.RequestException as e:
            logger.warning(f"Exception: {e}")
            return None

        logger.debug(f"Got response: {response.text[:20]!r}")

        return response

    def _post(self, url: str, data: dict[str, str] | None = None) -> requests.Response | None:
        try:
            response = self._session.post(url, data=data)
        except requests.RequestException as e:
            logger.warning(f"Exception: {e}")
            return None

        logger.debug(f"Got response: {response.text[:20]!r}")

        return response

    @classmethod
    def get_source(cls, name: str, config: dict[str, str]) -> Self:
        """Get source instance from a name and config dict."""
        for source in cls.__subclasses__():
            if name == source.NAME:
                return source(config)
        raise ValueError(f"Invalid source: '{name}'.")

    @staticmethod
    def _decrypt_zip(data: bytes, password: bytes = b"infected") -> bytes:
        """Decrypt a ZIP file with a given password."""
        if not data.startswith(b"PK\x03\x04"):
            raise ValueError(f"Data is not a valid ZIP file: {data[:20]!r}")

        zip_data = io.BytesIO(data)
        with pyzipper.AESZipFile(zip_data, encryption=pyzipper.WZ_AES) as h_zip:
            h_zip.setpassword(password)
            return bytes(h_zip.read(h_zip.filelist[0]))
