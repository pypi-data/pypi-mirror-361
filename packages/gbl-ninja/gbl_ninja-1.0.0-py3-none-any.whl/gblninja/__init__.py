"""
GBL Ninja - Python library for parsing and creating GBL (Gecko Bootloader) files.

This library provides functionality to:
- Parse GBL files into structured tag objects
- Create new GBL files using a builder pattern
- Encode tag objects back to binary format
- Validate GBL files with CRC checking
"""

from .gbl import (
    Gbl,
    ParseResultSuccess,
    ParseResultFatal,
    GblType,
    Tag,
    TagHeader,
    TagWithHeader,
    DefaultTag,
    GblHeader,
    GblApplication,
    GblBootloader,
    GblProg,
    GblProgLz4,
    GblProgLzma,
    GblEnd,
    GblMetadata,
    GblEraseProg,
    GblEncryptionData,
    GblEncryptionInitAesCcm,
    GblCertificateEcdsaP256,
    GblSignatureEcdsaP256,
    GblSeUpgrade,
    GblVersionDependency,
    ImageType,
    ApplicationData,
    ApplicationCertificate,
)

__version__ = "1.0.0"
__author__ = "GBL Ninja"
__email__ = "contact@gblninja.com"
__description__ = "Python library for parsing and creating GBL (Gecko Bootloader) files"

__all__ = [
    "Gbl",
    "ParseResultSuccess", 
    "ParseResultFatal",
    "GblType",
    "Tag",
    "TagHeader",
    "TagWithHeader",
    "DefaultTag",
    "GblHeader",
    "GblApplication",
    "GblBootloader",
    "GblProg",
    "GblProgLz4",
    "GblProgLzma",
    "GblEnd",
    "GblMetadata",
    "GblEraseProg",
    "GblEncryptionData",
    "GblEncryptionInitAesCcm",
    "GblCertificateEcdsaP256",
    "GblSignatureEcdsaP256",
    "GblSeUpgrade",
    "GblVersionDependency",
    "ImageType",
    "ApplicationData",
    "ApplicationCertificate",
]