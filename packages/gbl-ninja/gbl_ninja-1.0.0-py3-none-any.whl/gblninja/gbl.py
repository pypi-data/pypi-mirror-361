#!/usr/bin/env python3
"""
GBL (Gecko Bootloader) Library - Python Implementation
Converted from Kotlin with maintained functionality and structure.
"""

import struct
import zlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union, Set, Tuple, Any
import io


class GblType(Enum):
    HEADER_V3 = 0x03A617EB
    BOOTLOADER = 0xF50909F5
    APPLICATION = 0xF40A0AF4
    METADATA = 0xF60808F6
    PROG = 0xFE0101FE
    PROG_LZ4 = 0xFD0505FD
    PROG_LZMA = 0xFD0707FD
    ERASEPROG = 0xFD0303FD
    SE_UPGRADE = 0x5EA617EB
    END = 0xFC0404FC
    TAG = 0
    ENCRYPTION_DATA = 0xF90707F9
    ENCRYPTION_INIT = 0xFA0606FA
    SIGNATURE_ECDSA_P256 = 0xF70A0AF7
    CERTIFICATE_ECDSA_P256 = 0xF30B0BF3
    VERSION_DEPENDENCY = 0x76A617EB

    @classmethod
    def from_value(cls, value: int) -> Optional['GblType']:
        for item in cls:
            if item.value == value:
                return item
        return None


class ImageType(Enum):
    APPLICATION = 0x01
    BOOTLOADER = 0x02
    SE = 0x03


class ContainerErrorCode(Enum):
    CONTAINER_NOT_CREATED = "CONTAINER_NOT_CREATED"
    PROTECTED_TAG_VIOLATION = "PROTECTED_TAG_VIOLATION"
    TAG_NOT_FOUND = "TAG_NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"


@dataclass
class TagHeader:
    id: int
    length: int

    def content(self) -> bytes:
        return struct.pack('<II', self.id, self.length)


@dataclass
class ApplicationData:
    type: int
    version: int
    capabilities: int
    product_id: int

    APP_TYPE = 32
    APP_VERSION = 5
    APP_CAPABILITIES = 0
    APP_PRODUCT_ID = 54

    def content(self) -> bytes:
        return struct.pack('<IIIB', self.type, self.version, self.capabilities, self.product_id)


@dataclass
class ApplicationCertificate:
    struct_version: int
    flags: int
    key: int
    version: int
    signature: int


class ParseResult:
    pass


@dataclass
class ParseResultSuccess(ParseResult):
    result_list: List['Tag']


@dataclass
class ParseResultFatal(ParseResult):
    error: Any = None


class ParseTagResult:
    pass


@dataclass
class ParseTagResultSuccess(ParseTagResult):
    tag_header: TagHeader
    tag_data: bytes


@dataclass
class ParseTagResultFatal(ParseTagResult):
    error: Any = None


class ContainerResult:
    pass


@dataclass
class ContainerResultSuccess(ContainerResult):
    data: Any


@dataclass
class ContainerResultError(ContainerResult):
    message: str
    code: ContainerErrorCode


class Tag(ABC):
    def __init__(self, tag_type: GblType):
        self.tag_type = tag_type

    @abstractmethod
    def copy(self) -> 'Tag':
        pass

    def content(self) -> bytes:
        return self._generate_tag_data()

    def _generate_tag_data(self) -> bytes:
        return bytes()


class TagWithHeader(Tag):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, tag_data: bytes):
        super().__init__(tag_type)
        self.tag_header = tag_header
        self.tag_data = tag_data


class DefaultTag(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, tag_data: bytes):
        super().__init__(tag_header, tag_type, tag_data)

    def copy(self) -> 'DefaultTag':
        return DefaultTag(self.tag_header, self.tag_type, bytes())


class GblHeader(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, version: int, gbl_type: int, tag_data: bytes):
        super().__init__(tag_header, tag_type, tag_data)
        self.version = version
        self.gbl_type = gbl_type

    def copy(self) -> 'GblHeader':
        return GblHeader(self.tag_header, self.tag_type, self.version, self.gbl_type, bytes())

    def _generate_tag_data(self) -> bytes:
        return struct.pack('<II', self.version, self.gbl_type)


class GblBootloader(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, bootloader_version: int,
                 address: int, data: bytes, tag_data: bytes):
        super().__init__(tag_header, tag_type, tag_data)
        self.bootloader_version = bootloader_version
        self.address = address
        self.data = data

    def copy(self) -> 'GblBootloader':
        return GblBootloader(self.tag_header, self.tag_type, self.bootloader_version,
                             self.address, self.data, bytes())

    def _generate_tag_data(self) -> bytes:
        return struct.pack('<II', self.bootloader_version, self.address) + self.data


class GblApplication(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, application_data: ApplicationData, tag_data: bytes):
        super().__init__(tag_header, tag_type, tag_data)
        self.application_data = application_data

    def copy(self) -> 'GblApplication':
        return GblApplication(self.tag_header, self.tag_type, self.application_data, bytes())

    def _generate_tag_data(self) -> bytes:
        result = self.application_data.content()
        if self.tag_header.length > 13:
            remaining_data = self.tag_data[13:]
            result += remaining_data
        return result


class GblProg(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, flash_start_address: int,
                 data: bytes, tag_data: bytes):
        super().__init__(tag_header, tag_type, tag_data)
        self.flash_start_address = flash_start_address
        self.data = data

    def copy(self) -> 'GblProg':
        return GblProg(self.tag_header, self.tag_type, self.flash_start_address, self.data, bytes())

    def _generate_tag_data(self) -> bytes:
        return struct.pack('<I', self.flash_start_address) + self.data


class GblEraseProg(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, tag_data: bytes):
        super().__init__(tag_header, tag_type, tag_data)

    def copy(self) -> 'GblEraseProg':
        return GblEraseProg(self.tag_header, self.tag_type, bytes())


class GblEnd(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, gbl_crc: int, tag_data: bytes):
        super().__init__(tag_header, tag_type, tag_data)
        self.gbl_crc = gbl_crc

    def copy(self) -> 'GblEnd':
        return GblEnd(self.tag_header, self.tag_type, self.gbl_crc, bytes())

    def _generate_tag_data(self) -> bytes:
        return struct.pack('<I', self.gbl_crc)


class GblMetadata(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, meta_data: bytes, tag_data: bytes):
        super().__init__(tag_header, tag_type, tag_data)
        self.meta_data = meta_data

    def copy(self) -> 'GblMetadata':
        return GblMetadata(self.tag_header, self.tag_type, self.meta_data, bytes())

    def _generate_tag_data(self) -> bytes:
        return self.meta_data


class GblSeUpgrade(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, blob_size: int,
                 version: int, data: bytes, tag_data: bytes):
        super().__init__(tag_header, tag_type, tag_data)
        self.blob_size = blob_size
        self.version = version
        self.data = data

    def copy(self) -> 'GblSeUpgrade':
        return GblSeUpgrade(self.tag_header, self.tag_type, self.blob_size,
                            self.version, self.data, bytes())

    def _generate_tag_data(self) -> bytes:
        return struct.pack('<II', self.blob_size, self.version) + self.data


class GblProgLz4(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, tag_data: bytes):
        super().__init__(tag_header, tag_type, tag_data)

    def copy(self) -> 'GblProgLz4':
        return GblProgLz4(self.tag_header, self.tag_type, bytes())


class GblProgLzma(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, tag_data: bytes):
        super().__init__(tag_header, tag_type, tag_data)

    def copy(self) -> 'GblProgLzma':
        return GblProgLzma(self.tag_header, self.tag_type, bytes())


class GblCertificateEcdsaP256(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, tag_data: bytes,
                 certificate: ApplicationCertificate):
        super().__init__(tag_header, tag_type, tag_data)
        self.certificate = certificate

    def copy(self) -> 'GblCertificateEcdsaP256':
        return GblCertificateEcdsaP256(self.tag_header, self.tag_type, self.tag_data, self.certificate)

    def _generate_tag_data(self) -> bytes:
        return struct.pack('<BBBIB',
                           self.certificate.struct_version,
                           self.certificate.flags,
                           self.certificate.key,
                           self.certificate.version,
                           self.certificate.signature)


class GblSignatureEcdsaP256(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, tag_data: bytes, r: int, s: int):
        super().__init__(tag_header, tag_type, tag_data)
        self.r = r
        self.s = s

    def copy(self) -> 'GblSignatureEcdsaP256':
        return GblSignatureEcdsaP256(self.tag_header, self.tag_type, self.tag_data, self.r, self.s)

    def _generate_tag_data(self) -> bytes:
        return struct.pack('<BB', self.r, self.s)


class GblEncryptionData(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, tag_data: bytes,
                 encrypted_gbl_data: bytes):
        super().__init__(tag_header, tag_type, tag_data)
        self.encrypted_gbl_data = encrypted_gbl_data

    def copy(self) -> 'GblEncryptionData':
        return GblEncryptionData(self.tag_header, self.tag_type, self.tag_data, self.encrypted_gbl_data)

    def _generate_tag_data(self) -> bytes:
        return self.encrypted_gbl_data


class GblEncryptionInitAesCcm(TagWithHeader):
    def __init__(self, tag_header: TagHeader, tag_type: GblType, tag_data: bytes,
                 msg_len: int, nonce: int):
        super().__init__(tag_header, tag_type, tag_data)
        self.msg_len = msg_len
        self.nonce = nonce

    def copy(self) -> 'GblEncryptionInitAesCcm':
        return GblEncryptionInitAesCcm(self.tag_header, self.tag_type, bytes(), self.msg_len, self.nonce)

    def _generate_tag_data(self) -> bytes:
        return struct.pack('<IB', self.msg_len, self.nonce)


def parse_tag(byte_array: bytes, offset: int = 0) -> ParseTagResult:
    TAG_ID_SIZE = 4
    TAG_LENGTH_SIZE = 4

    if offset < 0 or offset + TAG_ID_SIZE + TAG_LENGTH_SIZE > len(byte_array):
        return ParseTagResultFatal(f"Invalid offset: {offset}")

    tag_id = struct.unpack('<I', byte_array[offset:offset + TAG_ID_SIZE])[0]
    tag_length = struct.unpack('<I', byte_array[offset + TAG_ID_SIZE:offset + TAG_ID_SIZE + TAG_LENGTH_SIZE])[0]

    if offset + TAG_ID_SIZE + TAG_LENGTH_SIZE + tag_length > len(byte_array):
        return ParseTagResultFatal(f"Invalid tag length: {tag_length}")

    tag_data = byte_array[offset + TAG_ID_SIZE + TAG_LENGTH_SIZE:offset + TAG_ID_SIZE + TAG_LENGTH_SIZE + tag_length]

    tag_header = TagHeader(id=tag_id, length=tag_length)

    return ParseTagResultSuccess(tag_header=tag_header, tag_data=tag_data)


def parse_tag_type(tag_id: int, length: int, byte_array: bytes) -> Tag:
    tag_type = GblType.from_value(tag_id)
    tag_header = TagHeader(id=tag_id, length=length)

    if tag_type == GblType.HEADER_V3:
        version = struct.unpack('<I', byte_array[0:4])[0]
        gbl_type = struct.unpack('<I', byte_array[4:8])[0]
        return GblHeader(tag_header, tag_type, version, gbl_type, byte_array)

    elif tag_type == GblType.BOOTLOADER:
        bootloader_version = struct.unpack('<I', byte_array[0:4])[0]
        address = struct.unpack('<I', byte_array[4:8])[0]
        data = byte_array[8:]
        return GblBootloader(tag_header, tag_type, bootloader_version, address, data, byte_array)

    elif tag_type == GblType.APPLICATION:
        app_type = struct.unpack('<I', byte_array[0:4])[0]
        version = struct.unpack('<I', byte_array[4:8])[0]
        capabilities = struct.unpack('<I', byte_array[8:12])[0]
        product_id = byte_array[12]
        app_data = ApplicationData(app_type, version, capabilities, product_id)
        return GblApplication(tag_header, tag_type, app_data, byte_array)

    elif tag_type == GblType.METADATA:
        return GblMetadata(tag_header, tag_type, byte_array, byte_array)

    elif tag_type == GblType.PROG:
        flash_start_address = struct.unpack('<I', byte_array[0:4])[0]
        data = byte_array[4:]
        return GblProg(tag_header, tag_type, flash_start_address, data, byte_array)

    elif tag_type == GblType.PROG_LZ4:
        return GblProgLz4(tag_header, tag_type, byte_array)

    elif tag_type == GblType.PROG_LZMA:
        return GblProgLzma(tag_header, tag_type, byte_array)

    elif tag_type == GblType.ERASEPROG:
        return GblEraseProg(tag_header, tag_type, byte_array)

    elif tag_type == GblType.SE_UPGRADE:
        blob_size = struct.unpack('<I', byte_array[0:4])[0]
        version = struct.unpack('<I', byte_array[4:8])[0]
        data = byte_array[8:]
        return GblSeUpgrade(tag_header, tag_type, blob_size, version, data, byte_array)

    elif tag_type == GblType.END:
        gbl_crc = struct.unpack('<I', byte_array[0:4])[0]
        return GblEnd(tag_header, tag_type, gbl_crc, byte_array)

    elif tag_type == GblType.ENCRYPTION_DATA:
        encrypted_data = byte_array[8:] if len(byte_array) > 8 else byte_array
        return GblEncryptionData(tag_header, tag_type, byte_array, encrypted_data)

    elif tag_type == GblType.ENCRYPTION_INIT:
        msg_len = struct.unpack('<I', byte_array[0:4])[0]
        nonce = byte_array[4]
        return GblEncryptionInitAesCcm(tag_header, tag_type, byte_array, msg_len, nonce)

    elif tag_type == GblType.SIGNATURE_ECDSA_P256:
        r = byte_array[0]
        s = byte_array[1]
        return GblSignatureEcdsaP256(tag_header, tag_type, byte_array, r, s)

    elif tag_type == GblType.CERTIFICATE_ECDSA_P256:
        cert = ApplicationCertificate(
            struct_version=byte_array[0],
            flags=byte_array[1],
            key=byte_array[2],
            version=struct.unpack('<I', byte_array[3:7])[0],
            signature=byte_array[7]
        )
        return GblCertificateEcdsaP256(tag_header, tag_type, byte_array, cert)

    else:
        return DefaultTag(tag_header, GblType.TAG, byte_array)


def generate_tag_data(tag: Tag) -> bytes:
    if hasattr(tag, '_generate_tag_data'):
        return tag._generate_tag_data()
    return bytes()


def encode_tags(tags: List[Tag]) -> bytes:
    TAG_ID_SIZE = 4
    TAG_LENGTH_SIZE = 4

    total_size = sum(TAG_ID_SIZE + TAG_LENGTH_SIZE + tag.tag_header.length
                     for tag in tags if isinstance(tag, TagWithHeader))

    buffer = io.BytesIO()

    for tag in tags:
        if not isinstance(tag, TagWithHeader):
            continue

        buffer.write(struct.pack('<I', tag.tag_header.id))
        buffer.write(struct.pack('<I', tag.tag_header.length))

        tag_data = generate_tag_data(tag)
        buffer.write(tag_data)

    return buffer.getvalue()


def create_end_tag_with_crc(tags: List[Tag]) -> GblEnd:
    TAG_ID_SIZE = 4
    TAG_LENGTH_SIZE = 4

    crc = zlib.crc32(b'')

    for tag in tags:
        if not isinstance(tag, TagWithHeader):
            continue

        tag_id_bytes = struct.pack('<I', tag.tag_header.id)
        tag_length_bytes = struct.pack('<I', tag.tag_header.length)
        tag_data = generate_tag_data(tag)

        crc = zlib.crc32(tag_id_bytes, crc)
        crc = zlib.crc32(tag_length_bytes, crc)
        crc = zlib.crc32(tag_data, crc)

    end_tag_id = GblType.END.value
    end_tag_length = TAG_LENGTH_SIZE

    end_tag_id_bytes = struct.pack('<I', end_tag_id)
    end_tag_length_bytes = struct.pack('<I', end_tag_length)

    crc = zlib.crc32(end_tag_id_bytes, crc)
    crc = zlib.crc32(end_tag_length_bytes, crc)

    crc_value = crc & 0xFFFFFFFF
    crc_bytes = struct.pack('<I', crc_value)

    return GblEnd(
        tag_header=TagHeader(id=GblType.END.value, length=TAG_LENGTH_SIZE),
        tag_type=GblType.END,
        gbl_crc=crc_value,
        tag_data=crc_bytes
    )


class Container(ABC):
    @abstractmethod
    def create(self) -> ContainerResult:
        pass

    @abstractmethod
    def add(self, tag: Tag) -> ContainerResult:
        pass

    @abstractmethod
    def remove(self, tag: Tag) -> ContainerResult:
        pass

    @abstractmethod
    def build(self) -> ContainerResult:
        pass

    @abstractmethod
    def content(self) -> ContainerResult:
        pass


class TagContainer(Container):
    GBL_TAG_ID_HEADER_V3 = 0x03A617EB
    HEADER_SIZE = 8
    HEADER_VERSION = 50331648
    HEADER_GBL_TYPE = 0
    PROTECTED_TAG_TYPES = {GblType.HEADER_V3, GblType.END}

    def __init__(self):
        self._content: Set[Tag] = set()
        self.is_created = False

    def create(self) -> ContainerResult:
        try:
            if self.is_created:
                return ContainerResultSuccess(None)

            self._content.clear()

            header_tag = self._create_header_tag()
            self._content.add(header_tag)

            end_tag = self._create_end_tag()
            self._content.add(end_tag)

            self.is_created = True
            return ContainerResultSuccess(None)

        except Exception as e:
            return ContainerResultError(
                f"Failed to create container: {str(e)}",
                ContainerErrorCode.INTERNAL_ERROR
            )

    def add(self, tag: Tag) -> ContainerResult:
        try:
            if not self.is_created:
                return ContainerResultError(
                    "Container must be created before adding tags. Call create() first.",
                    ContainerErrorCode.CONTAINER_NOT_CREATED
                )

            if self._is_protected_tag(tag):
                return ContainerResultError(
                    f"Cannot add protected tag: {tag.tag_type}. Protected tags are managed automatically.",
                    ContainerErrorCode.PROTECTED_TAG_VIOLATION
                )

            self._content.add(tag)
            return ContainerResultSuccess(None)

        except Exception as e:
            return ContainerResultError(
                f"Failed to add tag: {str(e)}",
                ContainerErrorCode.INTERNAL_ERROR
            )

    def remove(self, tag: Tag) -> ContainerResult:
        try:
            if not self.is_created:
                return ContainerResultError(
                    "Container must be created before removing tags. Call create() first.",
                    ContainerErrorCode.CONTAINER_NOT_CREATED
                )

            if self._is_protected_tag(tag):
                return ContainerResultError(
                    f"Cannot remove protected tag: {tag.tag_type}. Protected tags are managed automatically.",
                    ContainerErrorCode.PROTECTED_TAG_VIOLATION
                )

            if tag not in self._content:
                return ContainerResultError(
                    f"Tag not found in container: {tag.tag_type}",
                    ContainerErrorCode.TAG_NOT_FOUND
                )

            self._content.remove(tag)
            return ContainerResultSuccess(None)

        except Exception as e:
            return ContainerResultError(
                f"Failed to remove tag: {str(e)}",
                ContainerErrorCode.INTERNAL_ERROR
            )

    def build(self) -> ContainerResult:
        try:
            if not self.is_created:
                return ContainerResultError(
                    "Container must be created before building. Call create() first.",
                    ContainerErrorCode.CONTAINER_NOT_CREATED
                )

            sorted_tags = []

            for tag in self._content:
                if tag.tag_type == GblType.HEADER_V3:
                    sorted_tags.append(tag)
                    break

            other_tags = [tag for tag in self._content
                          if tag.tag_type not in self.PROTECTED_TAG_TYPES]
            other_tags.sort(key=lambda t: t.tag_type.value)
            sorted_tags.extend(other_tags)

            for tag in self._content:
                if tag.tag_type == GblType.END:
                    sorted_tags.append(tag)
                    break

            return ContainerResultSuccess(sorted_tags)

        except Exception as e:
            return ContainerResultError(
                f"Failed to build container: {str(e)}",
                ContainerErrorCode.INTERNAL_ERROR
            )

    def content(self) -> ContainerResult:
        try:
            if not self.is_created:
                return ContainerResultError(
                    "Container must be created before exporting content. Call create() first.",
                    ContainerErrorCode.CONTAINER_NOT_CREATED
                )

            tags_result = self.build()
            if isinstance(tags_result, ContainerResultSuccess):
                tags_without_end = [tag for tag in tags_result.data if not isinstance(tag, GblEnd)]
                end_tag = create_end_tag_with_crc(tags_without_end)
                final_tags = tags_without_end + [end_tag]

                byte_array = encode_tags(final_tags)
                return ContainerResultSuccess(byte_array)
            else:
                return ContainerResultError(
                    f"Failed to build tags for content export: {tags_result.message}",
                    tags_result.code
                )

        except Exception as e:
            return ContainerResultError(
                f"Failed to export container content: {str(e)}",
                ContainerErrorCode.INTERNAL_ERROR
            )

    def has_tag(self, tag_type: GblType) -> bool:
        if not self.is_created:
            return False
        return any(tag.tag_type == tag_type for tag in self._content)

    def get_tag(self, tag_type: GblType) -> Optional[Tag]:
        if not self.is_created:
            return None
        for tag in self._content:
            if tag.tag_type == tag_type:
                return tag
        return None

    def is_empty(self) -> bool:
        if not self.is_created:
            return True
        return len(self._content) == len(self.PROTECTED_TAG_TYPES)

    def size(self) -> int:
        if not self.is_created:
            return 0
        return len(self._content)

    def get_tag_types(self) -> Set[GblType]:
        if not self.is_created:
            return set()
        return {tag.tag_type for tag in self._content}

    def clear(self) -> ContainerResult:
        try:
            if not self.is_created:
                return ContainerResultError(
                    "Container must be created before clearing. Call create() first.",
                    ContainerErrorCode.CONTAINER_NOT_CREATED
                )

            self._content = {tag for tag in self._content if self._is_protected_tag(tag)}
            return ContainerResultSuccess(None)

        except Exception as e:
            return ContainerResultError(
                f"Failed to clear container: {str(e)}",
                ContainerErrorCode.INTERNAL_ERROR
            )

    def _is_protected_tag(self, tag: Tag) -> bool:
        return tag.tag_type in self.PROTECTED_TAG_TYPES

    def _create_header_tag(self) -> Tag:
        header = GblHeader(
            tag_header=TagHeader(id=self.GBL_TAG_ID_HEADER_V3, length=self.HEADER_SIZE),
            tag_type=GblType.HEADER_V3,
            version=self.HEADER_VERSION,
            gbl_type=self.HEADER_GBL_TYPE,
            tag_data=bytes()
        )

        header.tag_data = header.content()
        return header

    def _create_end_tag(self) -> Tag:
        return GblEnd(
            tag_header=TagHeader(id=GblType.END.value, length=0),
            tag_type=GblType.END,
            tag_data=bytes(),
            gbl_crc=0
        )


class GblBuilder:
    def __init__(self):
        self.container = TagContainer()

    @classmethod
    def create(cls) -> 'GblBuilder':
        builder = cls()
        builder.container.create()
        return builder

    @classmethod
    def empty(cls) -> 'GblBuilder':
        return cls()

    def encryption_data(self, encrypted_gbl_data: bytes) -> 'GblBuilder':
        tag = GblEncryptionData(
            tag_header=TagHeader(id=GblType.ENCRYPTION_DATA.value, length=len(encrypted_gbl_data)),
            tag_type=GblType.ENCRYPTION_DATA,
            tag_data=encrypted_gbl_data.copy(),
            encrypted_gbl_data=encrypted_gbl_data
        )
        self.container.add(tag)
        return self

    def encryption_init(self, msg_len: int, nonce: int) -> 'GblBuilder':
        tag = GblEncryptionInitAesCcm(
            tag_header=TagHeader(id=GblType.ENCRYPTION_INIT.value, length=5),
            tag_type=GblType.ENCRYPTION_INIT,
            tag_data=struct.pack('<IB', msg_len, nonce),
            msg_len=msg_len,
            nonce=nonce
        )
        self.container.add(tag)
        return self

    def signature_ecdsa_p256(self, r: int, s: int) -> 'GblBuilder':
        tag = GblSignatureEcdsaP256(
            tag_header=TagHeader(id=GblType.SIGNATURE_ECDSA_P256.value, length=2),
            tag_type=GblType.SIGNATURE_ECDSA_P256,
            tag_data=struct.pack('<BB', r, s),
            r=r,
            s=s
        )
        self.container.add(tag)
        return self

    def certificate_ecdsa_p256(self, certificate: ApplicationCertificate) -> 'GblBuilder':
        tag_data = struct.pack('<BBBIB',
                               certificate.struct_version,
                               certificate.flags,
                               certificate.key,
                               certificate.version,
                               certificate.signature)

        tag = GblCertificateEcdsaP256(
            tag_header=TagHeader(id=GblType.CERTIFICATE_ECDSA_P256.value, length=8),
            tag_type=GblType.CERTIFICATE_ECDSA_P256,
            tag_data=tag_data,
            certificate=certificate
        )
        self.container.add(tag)
        return self

    def version_dependency(self, dependency_data: bytes) -> 'GblBuilder':
        tag = DefaultTag(
            tag_header=TagHeader(id=GblType.VERSION_DEPENDENCY.value, length=len(dependency_data)),
            tag_type=GblType.VERSION_DEPENDENCY,
            tag_data=dependency_data.copy()
        )
        self.container.add(tag)
        return self

    def bootloader(self, bootloader_version: int, address: int, data: bytes) -> 'GblBuilder':
        tag_data = struct.pack('<II', bootloader_version, address) + data

        tag = GblBootloader(
            tag_header=TagHeader(id=GblType.BOOTLOADER.value, length=8 + len(data)),
            tag_type=GblType.BOOTLOADER,
            bootloader_version=bootloader_version,
            address=address,
            data=data,
            tag_data=tag_data
        )
        self.container.add(tag)
        return self

    def metadata(self, meta_data: bytes) -> 'GblBuilder':
        tag = GblMetadata(
            tag_header=TagHeader(id=GblType.METADATA.value, length=len(meta_data)),
            tag_type=GblType.METADATA,
            meta_data=meta_data,
            tag_data=meta_data.copy()
        )
        self.container.add(tag)
        return self

    def prog(self, flash_start_address: int, data: bytes) -> 'GblBuilder':
        tag_data = struct.pack('<I', flash_start_address) + data

        tag = GblProg(
            tag_header=TagHeader(id=GblType.PROG.value, length=4 + len(data)),
            tag_type=GblType.PROG,
            flash_start_address=flash_start_address,
            data=data,
            tag_data=tag_data
        )
        self.container.add(tag)
        return self

    def prog_lz4(self, flash_start_address: int, compressed_data: bytes, decompressed_size: int) -> 'GblBuilder':
        tag_data = struct.pack('<II', flash_start_address, decompressed_size) + compressed_data

        tag = GblProgLz4(
            tag_header=TagHeader(id=GblType.PROG_LZ4.value, length=8 + len(compressed_data)),
            tag_type=GblType.PROG_LZ4,
            tag_data=tag_data
        )
        self.container.add(tag)
        return self

    def prog_lzma(self, flash_start_address: int, compressed_data: bytes, decompressed_size: int) -> 'GblBuilder':
        tag_data = struct.pack('<II', flash_start_address, decompressed_size) + compressed_data

        tag = GblProgLzma(
            tag_header=TagHeader(id=GblType.PROG_LZMA.value, length=8 + len(compressed_data)),
            tag_type=GblType.PROG_LZMA,
            tag_data=tag_data
        )
        self.container.add(tag)
        return self

    def se_upgrade(self, version: int, data: bytes) -> 'GblBuilder':
        blob_size = len(data)
        tag_data = struct.pack('<II', blob_size, version) + data

        tag = GblSeUpgrade(
            tag_header=TagHeader(id=GblType.SE_UPGRADE.value, length=8 + blob_size),
            tag_type=GblType.SE_UPGRADE,
            blob_size=blob_size,
            version=version,
            data=data,
            tag_data=tag_data
        )
        self.container.add(tag)
        return self

    def application(self, type_val: int = ApplicationData.APP_TYPE,
                    version: int = ApplicationData.APP_VERSION,
                    capabilities: int = ApplicationData.APP_CAPABILITIES,
                    product_id: int = ApplicationData.APP_PRODUCT_ID,
                    additional_data: bytes = b'') -> 'GblBuilder':

        application_data = ApplicationData(type_val, version, capabilities, product_id)
        tag_data = application_data.content() + additional_data

        tag = GblApplication(
            tag_header=TagHeader(id=GblType.APPLICATION.value, length=len(tag_data)),
            tag_type=GblType.APPLICATION,
            application_data=application_data,
            tag_data=tag_data
        )
        self.container.add(tag)
        return self

    def erase_prog(self) -> 'GblBuilder':
        tag = GblEraseProg(
            tag_header=TagHeader(id=GblType.ERASEPROG.value, length=8),
            tag_type=GblType.ERASEPROG,
            tag_data=bytes(8)
        )
        self.container.add(tag)
        return self

    def get(self) -> List[Tag]:
        result = self.container.build()
        if isinstance(result, ContainerResultSuccess):
            return result.data
        return []

    def build_to_list(self) -> List[Tag]:
        tags = self._get_or_default([])
        tags_without_end = [tag for tag in tags if not isinstance(tag, GblEnd)]
        end_tag = create_end_tag_with_crc(tags_without_end)
        return tags_without_end + [end_tag]

    def build_to_byte_array(self) -> bytes:
        tags = self.build_to_list()
        return encode_tags(tags)

    def has_tag(self, tag_type: GblType) -> bool:
        return self.container.has_tag(tag_type)

    def get_tag(self, tag_type: GblType) -> Optional[Tag]:
        return self.container.get_tag(tag_type)

    def remove_tag(self, tag: Tag) -> ContainerResult:
        return self.container.remove(tag)

    def clear(self) -> ContainerResult:
        return self.container.clear()

    def size(self) -> int:
        return self.container.size()

    def is_empty(self) -> bool:
        return self.container.is_empty()

    def get_tag_types(self) -> Set[GblType]:
        return self.container.get_tag_types()

    def _get_or_default(self, default):
        result = self.container.build()
        if isinstance(result, ContainerResultSuccess):
            return result.data
        return default


class Gbl:
    HEADER_SIZE = 8
    TAG_ID_SIZE = 4
    TAG_LENGTH_SIZE = 4

    def parse_byte_array(self, byte_array: bytes) -> ParseResult:
        offset = 0
        size = len(byte_array)
        raw_tags = []

        if len(byte_array) < self.HEADER_SIZE:
            return ParseResultFatal(
                f"File is too small to be a valid gbl file. Expected at least {self.HEADER_SIZE} bytes, got {len(byte_array)} bytes."
            )

        while offset < size:
            result = parse_tag(byte_array, offset)

            if isinstance(result, ParseTagResultFatal):
                break

            if isinstance(result, ParseTagResultSuccess):
                header, data = result.tag_header, result.tag_data

                try:
                    parsed_tag = parse_tag_type(
                        tag_id=header.id,
                        length=header.length,
                        byte_array=data
                    )

                    raw_tags.append(parsed_tag)

                    offset += self.TAG_ID_SIZE + self.TAG_LENGTH_SIZE + header.length

                except Exception as e:
                    break

        return ParseResultSuccess(raw_tags)

    def encode(self, tags: List[Tag]) -> bytes:
        tags_without_end = [tag for tag in tags if not isinstance(tag, GblEnd)]
        end_tag = create_end_tag_with_crc(tags_without_end)
        final_tags = tags_without_end + [end_tag]
        return encode_tags(final_tags)

    @property
    def GblBuilder(self):
        return GblBuilder


def test_gbl_parsing():
    """
    Test function that instantiates the Gbl class, loads empty.gbl file, and parses it.
    Expected to return 4 tags: Header, application, erase_prog, and end.
    """
    print("Testing GBL Library...")

    gbl = Gbl()

    try:
        with open('n2k.gbl', 'rb') as f:
            gbl_data = f.read()

        print(f"Loaded empty.gbl: {len(gbl_data)} bytes")

        result = gbl.parse_byte_array(gbl_data)

        if isinstance(result, ParseResultSuccess):
            tags = result.result_list
            print(f"Successfully parsed {len(tags)} tags:")

            tag_types = []
            for tag in tags:
                tag_type_name = tag.tag_type.name if tag.tag_type else "UNKNOWN"
                tag_types.append(tag_type_name)
                print(f"  - {tag_type_name}: {type(tag).__name__}")

            expected_tags = {'HEADER_V3', 'APPLICATION', 'ERASEPROG', 'END'}
            found_tags = set(tag_types)

            if found_tags == expected_tags:
                print("✓ All expected tags found!")
            else:
                print(f"✗ Expected tags: {expected_tags}")
                print(f"✗ Found tags: {found_tags}")

        elif isinstance(result, ParseResultFatal):
            print(f"Parsing failed: {result.error}")

    except FileNotFoundError:
        print("empty.gbl file not found. Creating a test GBL file instead...")

        builder = Gbl().GblBuilder.create()
        builder.application(type_val=32, version=0x10000, capabilities=0, product_id=54)
        builder.erase_prog()

        test_gbl_data = builder.build_to_byte_array()

        with open('empty.gbl', 'wb') as f:
            f.write(test_gbl_data)

        print(f"Created empty.gbl with {len(test_gbl_data)} bytes")

        result = gbl.parse_byte_array(test_gbl_data)
        if isinstance(result, ParseResultSuccess):
            tags = result.result_list
            print(f"Successfully parsed {len(tags)} tags:")
            for tag in tags:
                tag_type_name = tag.tag_type.name if tag.tag_type else "UNKNOWN"
                print(f"  - {tag_type_name}: {type(tag).__name__}")


if __name__ == "__main__":
    test_gbl_parsing()