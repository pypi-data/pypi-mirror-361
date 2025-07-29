from __future__ import annotations

from io import BytesIO

from tg_secret.raw.tl_object import SecretTLObject
from tg_secret.raw.vector import Vector
from tg_secret.raw.primitives import read_int, read_long, read_double, read_bytes, read_string
from tg_secret.raw.primitives import write_int, write_long, write_double, write_bytes, write_string
from tg_secret import raw

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

class DecryptedMessage_8(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``8``
        - ID: ``1F814F1F``

    """

    __slots__ = ("random_id", "random_bytes", "message", "media",)

    ID = 0x1f814f1f
    QUALNAME = "types.DecryptedMessage_8"

    def __init__(self, *, random_id: int, random_bytes: bytes, message: str, media: raw.base.DecryptedMessageMedia) -> None:
        self.random_id = random_id  # long
        self.random_bytes = random_bytes  # bytes
        self.message = message  # string
        self.media = media  # DecryptedMessageMedia

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessage_8:
        # No flags
        
        random_id = read_long(b)
        
        random_bytes = read_bytes(b)
        
        message = read_string(b)
        
        media = SecretTLObject.read(b)
        
        return DecryptedMessage_8(random_id=random_id, random_bytes=random_bytes, message=message, media=media)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_long(self.random_id))
        
        b.write(write_bytes(self.random_bytes))
        
        b.write(write_string(self.message))
        
        b.write(self.media.write())
        
        return b.getvalue()


class DecryptedMessageService_8(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``8``
        - ID: ``AA48327D``

    """

    __slots__ = ("random_id", "random_bytes", "action",)

    ID = 0xaa48327d
    QUALNAME = "types.DecryptedMessageService_8"

    def __init__(self, *, random_id: int, random_bytes: bytes, action: raw.base.DecryptedMessageAction) -> None:
        self.random_id = random_id  # long
        self.random_bytes = random_bytes  # bytes
        self.action = action  # DecryptedMessageAction

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageService_8:
        # No flags
        
        random_id = read_long(b)
        
        random_bytes = read_bytes(b)
        
        action = SecretTLObject.read(b)
        
        return DecryptedMessageService_8(random_id=random_id, random_bytes=random_bytes, action=action)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_long(self.random_id))
        
        b.write(write_bytes(self.random_bytes))
        
        b.write(self.action.write())
        
        return b.getvalue()


class DecryptedMessageMediaEmpty(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``8``
        - ID: ``89F5C4A``

    """

    __slots__ = ()

    ID = 0x89f5c4a
    QUALNAME = "types.DecryptedMessageMediaEmpty"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaEmpty:
        # No flags
        
        return DecryptedMessageMediaEmpty()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class DecryptedMessageMediaPhoto_8(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``8``
        - ID: ``32798A8C``

    """

    __slots__ = ("thumb", "thumb_w", "thumb_h", "w", "h", "size", "key", "iv",)

    ID = 0x32798a8c
    QUALNAME = "types.DecryptedMessageMediaPhoto_8"

    def __init__(self, *, thumb: bytes, thumb_w: int, thumb_h: int, w: int, h: int, size: int, key: bytes, iv: bytes) -> None:
        self.thumb = thumb  # bytes
        self.thumb_w = thumb_w  # int
        self.thumb_h = thumb_h  # int
        self.w = w  # int
        self.h = h  # int
        self.size = size  # int
        self.key = key  # bytes
        self.iv = iv  # bytes

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaPhoto_8:
        # No flags
        
        thumb = read_bytes(b)
        
        thumb_w = read_int(b)
        
        thumb_h = read_int(b)
        
        w = read_int(b)
        
        h = read_int(b)
        
        size = read_int(b)
        
        key = read_bytes(b)
        
        iv = read_bytes(b)
        
        return DecryptedMessageMediaPhoto_8(thumb=thumb, thumb_w=thumb_w, thumb_h=thumb_h, w=w, h=h, size=size, key=key, iv=iv)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_bytes(self.thumb))
        
        b.write(write_int(self.thumb_w))
        
        b.write(write_int(self.thumb_h))
        
        b.write(write_int(self.w))
        
        b.write(write_int(self.h))
        
        b.write(write_int(self.size))
        
        b.write(write_bytes(self.key))
        
        b.write(write_bytes(self.iv))
        
        return b.getvalue()


class DecryptedMessageMediaVideo_8(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``8``
        - ID: ``4CEE6EF3``

    """

    __slots__ = ("thumb", "thumb_w", "thumb_h", "duration", "w", "h", "size", "key", "iv",)

    ID = 0x4cee6ef3
    QUALNAME = "types.DecryptedMessageMediaVideo_8"

    def __init__(self, *, thumb: bytes, thumb_w: int, thumb_h: int, duration: int, w: int, h: int, size: int, key: bytes, iv: bytes) -> None:
        self.thumb = thumb  # bytes
        self.thumb_w = thumb_w  # int
        self.thumb_h = thumb_h  # int
        self.duration = duration  # int
        self.w = w  # int
        self.h = h  # int
        self.size = size  # int
        self.key = key  # bytes
        self.iv = iv  # bytes

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaVideo_8:
        # No flags
        
        thumb = read_bytes(b)
        
        thumb_w = read_int(b)
        
        thumb_h = read_int(b)
        
        duration = read_int(b)
        
        w = read_int(b)
        
        h = read_int(b)
        
        size = read_int(b)
        
        key = read_bytes(b)
        
        iv = read_bytes(b)
        
        return DecryptedMessageMediaVideo_8(thumb=thumb, thumb_w=thumb_w, thumb_h=thumb_h, duration=duration, w=w, h=h, size=size, key=key, iv=iv)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_bytes(self.thumb))
        
        b.write(write_int(self.thumb_w))
        
        b.write(write_int(self.thumb_h))
        
        b.write(write_int(self.duration))
        
        b.write(write_int(self.w))
        
        b.write(write_int(self.h))
        
        b.write(write_int(self.size))
        
        b.write(write_bytes(self.key))
        
        b.write(write_bytes(self.iv))
        
        return b.getvalue()


class DecryptedMessageMediaGeoPoint(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``8``
        - ID: ``35480A59``

    """

    __slots__ = ("lat", "long",)

    ID = 0x35480a59
    QUALNAME = "types.DecryptedMessageMediaGeoPoint"

    def __init__(self, *, lat: float, long: float) -> None:
        self.lat = lat  # double
        self.long = long  # double

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaGeoPoint:
        # No flags
        
        lat = read_double(b)
        
        long = read_double(b)
        
        return DecryptedMessageMediaGeoPoint(lat=lat, long=long)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_double(self.lat))
        
        b.write(write_double(self.long))
        
        return b.getvalue()


class DecryptedMessageMediaContact(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``8``
        - ID: ``588A0A97``

    """

    __slots__ = ("phone_number", "first_name", "last_name", "user_id",)

    ID = 0x588a0a97
    QUALNAME = "types.DecryptedMessageMediaContact"

    def __init__(self, *, phone_number: str, first_name: str, last_name: str, user_id: int) -> None:
        self.phone_number = phone_number  # string
        self.first_name = first_name  # string
        self.last_name = last_name  # string
        self.user_id = user_id  # int

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaContact:
        # No flags
        
        phone_number = read_string(b)
        
        first_name = read_string(b)
        
        last_name = read_string(b)
        
        user_id = read_int(b)
        
        return DecryptedMessageMediaContact(phone_number=phone_number, first_name=first_name, last_name=last_name, user_id=user_id)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_string(self.phone_number))
        
        b.write(write_string(self.first_name))
        
        b.write(write_string(self.last_name))
        
        b.write(write_int(self.user_id))
        
        return b.getvalue()


class DecryptedMessageActionSetMessageTTL(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``8``
        - ID: ``A1733AEC``

    """

    __slots__ = ("ttl_seconds",)

    ID = 0xa1733aec
    QUALNAME = "types.DecryptedMessageActionSetMessageTTL"

    def __init__(self, *, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds  # int

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageActionSetMessageTTL:
        # No flags
        
        ttl_seconds = read_int(b)
        
        return DecryptedMessageActionSetMessageTTL(ttl_seconds=ttl_seconds)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.ttl_seconds))
        
        return b.getvalue()


class DecryptedMessageMediaDocument_8(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``8``
        - ID: ``B095434B``

    """

    __slots__ = ("thumb", "thumb_w", "thumb_h", "file_name", "mime_type", "size", "key", "iv",)

    ID = 0xb095434b
    QUALNAME = "types.DecryptedMessageMediaDocument_8"

    def __init__(self, *, thumb: bytes, thumb_w: int, thumb_h: int, file_name: str, mime_type: str, size: int, key: bytes, iv: bytes) -> None:
        self.thumb = thumb  # bytes
        self.thumb_w = thumb_w  # int
        self.thumb_h = thumb_h  # int
        self.file_name = file_name  # string
        self.mime_type = mime_type  # string
        self.size = size  # int
        self.key = key  # bytes
        self.iv = iv  # bytes

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaDocument_8:
        # No flags
        
        thumb = read_bytes(b)
        
        thumb_w = read_int(b)
        
        thumb_h = read_int(b)
        
        file_name = read_string(b)
        
        mime_type = read_string(b)
        
        size = read_int(b)
        
        key = read_bytes(b)
        
        iv = read_bytes(b)
        
        return DecryptedMessageMediaDocument_8(thumb=thumb, thumb_w=thumb_w, thumb_h=thumb_h, file_name=file_name, mime_type=mime_type, size=size, key=key, iv=iv)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_bytes(self.thumb))
        
        b.write(write_int(self.thumb_w))
        
        b.write(write_int(self.thumb_h))
        
        b.write(write_string(self.file_name))
        
        b.write(write_string(self.mime_type))
        
        b.write(write_int(self.size))
        
        b.write(write_bytes(self.key))
        
        b.write(write_bytes(self.iv))
        
        return b.getvalue()


class DecryptedMessageMediaAudio_8(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``8``
        - ID: ``6080758F``

    """

    __slots__ = ("duration", "size", "key", "iv",)

    ID = 0x6080758f
    QUALNAME = "types.DecryptedMessageMediaAudio_8"

    def __init__(self, *, duration: int, size: int, key: bytes, iv: bytes) -> None:
        self.duration = duration  # int
        self.size = size  # int
        self.key = key  # bytes
        self.iv = iv  # bytes

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaAudio_8:
        # No flags
        
        duration = read_int(b)
        
        size = read_int(b)
        
        key = read_bytes(b)
        
        iv = read_bytes(b)
        
        return DecryptedMessageMediaAudio_8(duration=duration, size=size, key=key, iv=iv)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.duration))
        
        b.write(write_int(self.size))
        
        b.write(write_bytes(self.key))
        
        b.write(write_bytes(self.iv))
        
        return b.getvalue()


class DecryptedMessageActionReadMessages(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``8``
        - ID: ``C4F40BE``

    """

    __slots__ = ("random_ids",)

    ID = 0xc4f40be
    QUALNAME = "types.DecryptedMessageActionReadMessages"

    def __init__(self, *, random_ids: list[int]) -> None:
        self.random_ids = random_ids  # Vector<long>

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageActionReadMessages:
        # No flags
        
        random_ids = Vector.read(b, read_long)
        
        return DecryptedMessageActionReadMessages(random_ids=random_ids)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(Vector.write_primitive_list(self.random_ids, write_long))
        
        return b.getvalue()


class DecryptedMessageActionDeleteMessages(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``8``
        - ID: ``65614304``

    """

    __slots__ = ("random_ids",)

    ID = 0x65614304
    QUALNAME = "types.DecryptedMessageActionDeleteMessages"

    def __init__(self, *, random_ids: list[int]) -> None:
        self.random_ids = random_ids  # Vector<long>

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageActionDeleteMessages:
        # No flags
        
        random_ids = Vector.read(b, read_long)
        
        return DecryptedMessageActionDeleteMessages(random_ids=random_ids)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(Vector.write_primitive_list(self.random_ids, write_long))
        
        return b.getvalue()


class DecryptedMessageActionScreenshotMessages(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``8``
        - ID: ``8AC1F475``

    """

    __slots__ = ("random_ids",)

    ID = 0x8ac1f475
    QUALNAME = "types.DecryptedMessageActionScreenshotMessages"

    def __init__(self, *, random_ids: list[int]) -> None:
        self.random_ids = random_ids  # Vector<long>

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageActionScreenshotMessages:
        # No flags
        
        random_ids = Vector.read(b, read_long)
        
        return DecryptedMessageActionScreenshotMessages(random_ids=random_ids)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(Vector.write_primitive_list(self.random_ids, write_long))
        
        return b.getvalue()


class DecryptedMessageActionFlushHistory(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``8``
        - ID: ``6719E45C``

    """

    __slots__ = ()

    ID = 0x6719e45c
    QUALNAME = "types.DecryptedMessageActionFlushHistory"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageActionFlushHistory:
        # No flags
        
        return DecryptedMessageActionFlushHistory()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class DecryptedMessage_17(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``204D3878``

    """

    __slots__ = ("random_id", "ttl", "message", "media",)

    ID = 0x204d3878
    QUALNAME = "types.DecryptedMessage_17"

    def __init__(self, *, random_id: int, ttl: int, message: str, media: raw.base.DecryptedMessageMedia) -> None:
        self.random_id = random_id  # long
        self.ttl = ttl  # int
        self.message = message  # string
        self.media = media  # DecryptedMessageMedia

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessage_17:
        # No flags
        
        random_id = read_long(b)
        
        ttl = read_int(b)
        
        message = read_string(b)
        
        media = SecretTLObject.read(b)
        
        return DecryptedMessage_17(random_id=random_id, ttl=ttl, message=message, media=media)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_long(self.random_id))
        
        b.write(write_int(self.ttl))
        
        b.write(write_string(self.message))
        
        b.write(self.media.write())
        
        return b.getvalue()


class DecryptedMessageService_17(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``73164160``

    """

    __slots__ = ("random_id", "action",)

    ID = 0x73164160
    QUALNAME = "types.DecryptedMessageService_17"

    def __init__(self, *, random_id: int, action: raw.base.DecryptedMessageAction) -> None:
        self.random_id = random_id  # long
        self.action = action  # DecryptedMessageAction

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageService_17:
        # No flags
        
        random_id = read_long(b)
        
        action = SecretTLObject.read(b)
        
        return DecryptedMessageService_17(random_id=random_id, action=action)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_long(self.random_id))
        
        b.write(self.action.write())
        
        return b.getvalue()


class DecryptedMessageMediaVideo_17(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``524A415D``

    """

    __slots__ = ("thumb", "thumb_w", "thumb_h", "duration", "mime_type", "w", "h", "size", "key", "iv",)

    ID = 0x524a415d
    QUALNAME = "types.DecryptedMessageMediaVideo_17"

    def __init__(self, *, thumb: bytes, thumb_w: int, thumb_h: int, duration: int, mime_type: str, w: int, h: int, size: int, key: bytes, iv: bytes) -> None:
        self.thumb = thumb  # bytes
        self.thumb_w = thumb_w  # int
        self.thumb_h = thumb_h  # int
        self.duration = duration  # int
        self.mime_type = mime_type  # string
        self.w = w  # int
        self.h = h  # int
        self.size = size  # int
        self.key = key  # bytes
        self.iv = iv  # bytes

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaVideo_17:
        # No flags
        
        thumb = read_bytes(b)
        
        thumb_w = read_int(b)
        
        thumb_h = read_int(b)
        
        duration = read_int(b)
        
        mime_type = read_string(b)
        
        w = read_int(b)
        
        h = read_int(b)
        
        size = read_int(b)
        
        key = read_bytes(b)
        
        iv = read_bytes(b)
        
        return DecryptedMessageMediaVideo_17(thumb=thumb, thumb_w=thumb_w, thumb_h=thumb_h, duration=duration, mime_type=mime_type, w=w, h=h, size=size, key=key, iv=iv)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_bytes(self.thumb))
        
        b.write(write_int(self.thumb_w))
        
        b.write(write_int(self.thumb_h))
        
        b.write(write_int(self.duration))
        
        b.write(write_string(self.mime_type))
        
        b.write(write_int(self.w))
        
        b.write(write_int(self.h))
        
        b.write(write_int(self.size))
        
        b.write(write_bytes(self.key))
        
        b.write(write_bytes(self.iv))
        
        return b.getvalue()


class DecryptedMessageMediaAudio_17(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``57E0A9CB``

    """

    __slots__ = ("duration", "mime_type", "size", "key", "iv",)

    ID = 0x57e0a9cb
    QUALNAME = "types.DecryptedMessageMediaAudio_17"

    def __init__(self, *, duration: int, mime_type: str, size: int, key: bytes, iv: bytes) -> None:
        self.duration = duration  # int
        self.mime_type = mime_type  # string
        self.size = size  # int
        self.key = key  # bytes
        self.iv = iv  # bytes

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaAudio_17:
        # No flags
        
        duration = read_int(b)
        
        mime_type = read_string(b)
        
        size = read_int(b)
        
        key = read_bytes(b)
        
        iv = read_bytes(b)
        
        return DecryptedMessageMediaAudio_17(duration=duration, mime_type=mime_type, size=size, key=key, iv=iv)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.duration))
        
        b.write(write_string(self.mime_type))
        
        b.write(write_int(self.size))
        
        b.write(write_bytes(self.key))
        
        b.write(write_bytes(self.iv))
        
        return b.getvalue()


class DecryptedMessageLayer(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``1BE31789``

    """

    __slots__ = ("random_bytes", "layer", "in_seq_no", "out_seq_no", "message",)

    ID = 0x1be31789
    QUALNAME = "types.DecryptedMessageLayer"

    def __init__(self, *, random_bytes: bytes, layer: int, in_seq_no: int, out_seq_no: int, message: raw.base.DecryptedMessage) -> None:
        self.random_bytes = random_bytes  # bytes
        self.layer = layer  # int
        self.in_seq_no = in_seq_no  # int
        self.out_seq_no = out_seq_no  # int
        self.message = message  # DecryptedMessage

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageLayer:
        # No flags
        
        random_bytes = read_bytes(b)
        
        layer = read_int(b)
        
        in_seq_no = read_int(b)
        
        out_seq_no = read_int(b)
        
        message = SecretTLObject.read(b)
        
        return DecryptedMessageLayer(random_bytes=random_bytes, layer=layer, in_seq_no=in_seq_no, out_seq_no=out_seq_no, message=message)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_bytes(self.random_bytes))
        
        b.write(write_int(self.layer))
        
        b.write(write_int(self.in_seq_no))
        
        b.write(write_int(self.out_seq_no))
        
        b.write(self.message.write())
        
        return b.getvalue()


class SendMessageTypingAction(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``16BF744E``

    """

    __slots__ = ()

    ID = 0x16bf744e
    QUALNAME = "types.SendMessageTypingAction"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> SendMessageTypingAction:
        # No flags
        
        return SendMessageTypingAction()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class SendMessageCancelAction(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``FD5EC8F5``

    """

    __slots__ = ()

    ID = 0xfd5ec8f5
    QUALNAME = "types.SendMessageCancelAction"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> SendMessageCancelAction:
        # No flags
        
        return SendMessageCancelAction()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class SendMessageRecordVideoAction(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``A187D66F``

    """

    __slots__ = ()

    ID = 0xa187d66f
    QUALNAME = "types.SendMessageRecordVideoAction"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> SendMessageRecordVideoAction:
        # No flags
        
        return SendMessageRecordVideoAction()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class SendMessageUploadVideoAction(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``92042FF7``

    """

    __slots__ = ()

    ID = 0x92042ff7
    QUALNAME = "types.SendMessageUploadVideoAction"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> SendMessageUploadVideoAction:
        # No flags
        
        return SendMessageUploadVideoAction()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class SendMessageRecordAudioAction(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``D52F73F7``

    """

    __slots__ = ()

    ID = 0xd52f73f7
    QUALNAME = "types.SendMessageRecordAudioAction"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> SendMessageRecordAudioAction:
        # No flags
        
        return SendMessageRecordAudioAction()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class SendMessageUploadAudioAction(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``E6AC8A6F``

    """

    __slots__ = ()

    ID = 0xe6ac8a6f
    QUALNAME = "types.SendMessageUploadAudioAction"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> SendMessageUploadAudioAction:
        # No flags
        
        return SendMessageUploadAudioAction()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class SendMessageUploadPhotoAction(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``990A3C1A``

    """

    __slots__ = ()

    ID = 0x990a3c1a
    QUALNAME = "types.SendMessageUploadPhotoAction"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> SendMessageUploadPhotoAction:
        # No flags
        
        return SendMessageUploadPhotoAction()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class SendMessageUploadDocumentAction(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``8FAEE98E``

    """

    __slots__ = ()

    ID = 0x8faee98e
    QUALNAME = "types.SendMessageUploadDocumentAction"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> SendMessageUploadDocumentAction:
        # No flags
        
        return SendMessageUploadDocumentAction()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class SendMessageGeoLocationAction(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``176F8BA1``

    """

    __slots__ = ()

    ID = 0x176f8ba1
    QUALNAME = "types.SendMessageGeoLocationAction"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> SendMessageGeoLocationAction:
        # No flags
        
        return SendMessageGeoLocationAction()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class SendMessageChooseContactAction(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``628CBC6F``

    """

    __slots__ = ()

    ID = 0x628cbc6f
    QUALNAME = "types.SendMessageChooseContactAction"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> SendMessageChooseContactAction:
        # No flags
        
        return SendMessageChooseContactAction()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class DecryptedMessageActionResend(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``511110B0``

    """

    __slots__ = ("start_seq_no", "end_seq_no",)

    ID = 0x511110b0
    QUALNAME = "types.DecryptedMessageActionResend"

    def __init__(self, *, start_seq_no: int, end_seq_no: int) -> None:
        self.start_seq_no = start_seq_no  # int
        self.end_seq_no = end_seq_no  # int

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageActionResend:
        # No flags
        
        start_seq_no = read_int(b)
        
        end_seq_no = read_int(b)
        
        return DecryptedMessageActionResend(start_seq_no=start_seq_no, end_seq_no=end_seq_no)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.start_seq_no))
        
        b.write(write_int(self.end_seq_no))
        
        return b.getvalue()


class DecryptedMessageActionNotifyLayer(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``F3048883``

    """

    __slots__ = ("layer",)

    ID = 0xf3048883
    QUALNAME = "types.DecryptedMessageActionNotifyLayer"

    def __init__(self, *, layer: int) -> None:
        self.layer = layer  # int

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageActionNotifyLayer:
        # No flags
        
        layer = read_int(b)
        
        return DecryptedMessageActionNotifyLayer(layer=layer)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.layer))
        
        return b.getvalue()


class DecryptedMessageActionTyping(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``17``
        - ID: ``CCB27641``

    """

    __slots__ = ("action",)

    ID = 0xccb27641
    QUALNAME = "types.DecryptedMessageActionTyping"

    def __init__(self, *, action: raw.base.SendMessageAction) -> None:
        self.action = action  # SendMessageAction

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageActionTyping:
        # No flags
        
        action = SecretTLObject.read(b)
        
        return DecryptedMessageActionTyping(action=action)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(self.action.write())
        
        return b.getvalue()


class DecryptedMessageActionRequestKey(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``20``
        - ID: ``F3C9611B``

    """

    __slots__ = ("exchange_id", "g_a",)

    ID = 0xf3c9611b
    QUALNAME = "types.DecryptedMessageActionRequestKey"

    def __init__(self, *, exchange_id: int, g_a: bytes) -> None:
        self.exchange_id = exchange_id  # long
        self.g_a = g_a  # bytes

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageActionRequestKey:
        # No flags
        
        exchange_id = read_long(b)
        
        g_a = read_bytes(b)
        
        return DecryptedMessageActionRequestKey(exchange_id=exchange_id, g_a=g_a)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_long(self.exchange_id))
        
        b.write(write_bytes(self.g_a))
        
        return b.getvalue()


class DecryptedMessageActionAcceptKey(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``20``
        - ID: ``6FE1735B``

    """

    __slots__ = ("exchange_id", "g_b", "key_fingerprint",)

    ID = 0x6fe1735b
    QUALNAME = "types.DecryptedMessageActionAcceptKey"

    def __init__(self, *, exchange_id: int, g_b: bytes, key_fingerprint: int) -> None:
        self.exchange_id = exchange_id  # long
        self.g_b = g_b  # bytes
        self.key_fingerprint = key_fingerprint  # long

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageActionAcceptKey:
        # No flags
        
        exchange_id = read_long(b)
        
        g_b = read_bytes(b)
        
        key_fingerprint = read_long(b)
        
        return DecryptedMessageActionAcceptKey(exchange_id=exchange_id, g_b=g_b, key_fingerprint=key_fingerprint)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_long(self.exchange_id))
        
        b.write(write_bytes(self.g_b))
        
        b.write(write_long(self.key_fingerprint))
        
        return b.getvalue()


class DecryptedMessageActionAbortKey(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``20``
        - ID: ``DD05EC6B``

    """

    __slots__ = ("exchange_id",)

    ID = 0xdd05ec6b
    QUALNAME = "types.DecryptedMessageActionAbortKey"

    def __init__(self, *, exchange_id: int) -> None:
        self.exchange_id = exchange_id  # long

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageActionAbortKey:
        # No flags
        
        exchange_id = read_long(b)
        
        return DecryptedMessageActionAbortKey(exchange_id=exchange_id)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_long(self.exchange_id))
        
        return b.getvalue()


class DecryptedMessageActionCommitKey(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``20``
        - ID: ``EC2E0B9B``

    """

    __slots__ = ("exchange_id", "key_fingerprint",)

    ID = 0xec2e0b9b
    QUALNAME = "types.DecryptedMessageActionCommitKey"

    def __init__(self, *, exchange_id: int, key_fingerprint: int) -> None:
        self.exchange_id = exchange_id  # long
        self.key_fingerprint = key_fingerprint  # long

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageActionCommitKey:
        # No flags
        
        exchange_id = read_long(b)
        
        key_fingerprint = read_long(b)
        
        return DecryptedMessageActionCommitKey(exchange_id=exchange_id, key_fingerprint=key_fingerprint)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_long(self.exchange_id))
        
        b.write(write_long(self.key_fingerprint))
        
        return b.getvalue()


class DecryptedMessageActionNoop(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``20``
        - ID: ``A82FDD63``

    """

    __slots__ = ()

    ID = 0xa82fdd63
    QUALNAME = "types.DecryptedMessageActionNoop"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageActionNoop:
        # No flags
        
        return DecryptedMessageActionNoop()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class DocumentAttributeImageSize(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``23``
        - ID: ``6C37C15C``

    """

    __slots__ = ("w", "h",)

    ID = 0x6c37c15c
    QUALNAME = "types.DocumentAttributeImageSize"

    def __init__(self, *, w: int, h: int) -> None:
        self.w = w  # int
        self.h = h  # int

    @staticmethod
    def read(b: BytesIO, *args) -> DocumentAttributeImageSize:
        # No flags
        
        w = read_int(b)
        
        h = read_int(b)
        
        return DocumentAttributeImageSize(w=w, h=h)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.w))
        
        b.write(write_int(self.h))
        
        return b.getvalue()


class DocumentAttributeAnimated(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``23``
        - ID: ``11B58939``

    """

    __slots__ = ()

    ID = 0x11b58939
    QUALNAME = "types.DocumentAttributeAnimated"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> DocumentAttributeAnimated:
        # No flags
        
        return DocumentAttributeAnimated()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class DocumentAttributeSticker_23(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``23``
        - ID: ``FB0A5727``

    """

    __slots__ = ()

    ID = 0xfb0a5727
    QUALNAME = "types.DocumentAttributeSticker_23"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> DocumentAttributeSticker_23:
        # No flags
        
        return DocumentAttributeSticker_23()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class DocumentAttributeVideo_23(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``23``
        - ID: ``5910CCCB``

    """

    __slots__ = ("duration", "w", "h",)

    ID = 0x5910cccb
    QUALNAME = "types.DocumentAttributeVideo_23"

    def __init__(self, *, duration: int, w: int, h: int) -> None:
        self.duration = duration  # int
        self.w = w  # int
        self.h = h  # int

    @staticmethod
    def read(b: BytesIO, *args) -> DocumentAttributeVideo_23:
        # No flags
        
        duration = read_int(b)
        
        w = read_int(b)
        
        h = read_int(b)
        
        return DocumentAttributeVideo_23(duration=duration, w=w, h=h)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.duration))
        
        b.write(write_int(self.w))
        
        b.write(write_int(self.h))
        
        return b.getvalue()


class DocumentAttributeAudio_23(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``23``
        - ID: ``51448E5``

    """

    __slots__ = ("duration",)

    ID = 0x51448e5
    QUALNAME = "types.DocumentAttributeAudio_23"

    def __init__(self, *, duration: int) -> None:
        self.duration = duration  # int

    @staticmethod
    def read(b: BytesIO, *args) -> DocumentAttributeAudio_23:
        # No flags
        
        duration = read_int(b)
        
        return DocumentAttributeAudio_23(duration=duration)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.duration))
        
        return b.getvalue()


class DocumentAttributeFilename(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``23``
        - ID: ``15590068``

    """

    __slots__ = ("file_name",)

    ID = 0x15590068
    QUALNAME = "types.DocumentAttributeFilename"

    def __init__(self, *, file_name: str) -> None:
        self.file_name = file_name  # string

    @staticmethod
    def read(b: BytesIO, *args) -> DocumentAttributeFilename:
        # No flags
        
        file_name = read_string(b)
        
        return DocumentAttributeFilename(file_name=file_name)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_string(self.file_name))
        
        return b.getvalue()


class PhotoSizeEmpty(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``23``
        - ID: ``E17E23C``

    """

    __slots__ = ("type",)

    ID = 0xe17e23c
    QUALNAME = "types.PhotoSizeEmpty"

    def __init__(self, *, type: str) -> None:
        self.type = type  # string

    @staticmethod
    def read(b: BytesIO, *args) -> PhotoSizeEmpty:
        # No flags
        
        type = read_string(b)
        
        return PhotoSizeEmpty(type=type)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_string(self.type))
        
        return b.getvalue()


class PhotoSize(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``23``
        - ID: ``77BFB61B``

    """

    __slots__ = ("type", "location", "w", "h", "size",)

    ID = 0x77bfb61b
    QUALNAME = "types.PhotoSize"

    def __init__(self, *, type: str, location: raw.base.FileLocation, w: int, h: int, size: int) -> None:
        self.type = type  # string
        self.location = location  # FileLocation
        self.w = w  # int
        self.h = h  # int
        self.size = size  # int

    @staticmethod
    def read(b: BytesIO, *args) -> PhotoSize:
        # No flags
        
        type = read_string(b)
        
        location = SecretTLObject.read(b)
        
        w = read_int(b)
        
        h = read_int(b)
        
        size = read_int(b)
        
        return PhotoSize(type=type, location=location, w=w, h=h, size=size)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_string(self.type))
        
        b.write(self.location.write())
        
        b.write(write_int(self.w))
        
        b.write(write_int(self.h))
        
        b.write(write_int(self.size))
        
        return b.getvalue()


class PhotoCachedSize(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``23``
        - ID: ``E9A734FA``

    """

    __slots__ = ("type", "location", "w", "h", "bytes",)

    ID = 0xe9a734fa
    QUALNAME = "types.PhotoCachedSize"

    def __init__(self, *, type: str, location: raw.base.FileLocation, w: int, h: int, bytes: bytes) -> None:
        self.type = type  # string
        self.location = location  # FileLocation
        self.w = w  # int
        self.h = h  # int
        self.bytes = bytes  # bytes

    @staticmethod
    def read(b: BytesIO, *args) -> PhotoCachedSize:
        # No flags
        
        type = read_string(b)
        
        location = SecretTLObject.read(b)
        
        w = read_int(b)
        
        h = read_int(b)
        
        bytes = read_bytes(b)
        
        return PhotoCachedSize(type=type, location=location, w=w, h=h, bytes=bytes)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_string(self.type))
        
        b.write(self.location.write())
        
        b.write(write_int(self.w))
        
        b.write(write_int(self.h))
        
        b.write(write_bytes(self.bytes))
        
        return b.getvalue()


class FileLocationUnavailable(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``23``
        - ID: ``7C596B46``

    """

    __slots__ = ("volume_id", "local_id", "secret",)

    ID = 0x7c596b46
    QUALNAME = "types.FileLocationUnavailable"

    def __init__(self, *, volume_id: int, local_id: int, secret: int) -> None:
        self.volume_id = volume_id  # long
        self.local_id = local_id  # int
        self.secret = secret  # long

    @staticmethod
    def read(b: BytesIO, *args) -> FileLocationUnavailable:
        # No flags
        
        volume_id = read_long(b)
        
        local_id = read_int(b)
        
        secret = read_long(b)
        
        return FileLocationUnavailable(volume_id=volume_id, local_id=local_id, secret=secret)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_long(self.volume_id))
        
        b.write(write_int(self.local_id))
        
        b.write(write_long(self.secret))
        
        return b.getvalue()


class FileLocation(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``23``
        - ID: ``53D69076``

    """

    __slots__ = ("dc_id", "volume_id", "local_id", "secret",)

    ID = 0x53d69076
    QUALNAME = "types.FileLocation"

    def __init__(self, *, dc_id: int, volume_id: int, local_id: int, secret: int) -> None:
        self.dc_id = dc_id  # int
        self.volume_id = volume_id  # long
        self.local_id = local_id  # int
        self.secret = secret  # long

    @staticmethod
    def read(b: BytesIO, *args) -> FileLocation:
        # No flags
        
        dc_id = read_int(b)
        
        volume_id = read_long(b)
        
        local_id = read_int(b)
        
        secret = read_long(b)
        
        return FileLocation(dc_id=dc_id, volume_id=volume_id, local_id=local_id, secret=secret)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.dc_id))
        
        b.write(write_long(self.volume_id))
        
        b.write(write_int(self.local_id))
        
        b.write(write_long(self.secret))
        
        return b.getvalue()


class DecryptedMessageMediaExternalDocument(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``23``
        - ID: ``FA95B0DD``

    """

    __slots__ = ("id", "access_hash", "date", "mime_type", "size", "thumb", "dc_id", "attributes",)

    ID = 0xfa95b0dd
    QUALNAME = "types.DecryptedMessageMediaExternalDocument"

    def __init__(self, *, id: int, access_hash: int, date: int, mime_type: str, size: int, thumb: raw.base.PhotoSize, dc_id: int, attributes: list[raw.base.DocumentAttribute]) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.date = date  # int
        self.mime_type = mime_type  # string
        self.size = size  # int
        self.thumb = thumb  # PhotoSize
        self.dc_id = dc_id  # int
        self.attributes = attributes  # Vector<DocumentAttribute>

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaExternalDocument:
        # No flags
        
        id = read_long(b)
        
        access_hash = read_long(b)
        
        date = read_int(b)
        
        mime_type = read_string(b)
        
        size = read_int(b)
        
        thumb = SecretTLObject.read(b)
        
        dc_id = read_int(b)
        
        attributes = Vector.read(b, SecretTLObject.read)
        
        return DecryptedMessageMediaExternalDocument(id=id, access_hash=access_hash, date=date, mime_type=mime_type, size=size, thumb=thumb, dc_id=dc_id, attributes=attributes)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_long(self.id))
        
        b.write(write_long(self.access_hash))
        
        b.write(write_int(self.date))
        
        b.write(write_string(self.mime_type))
        
        b.write(write_int(self.size))
        
        b.write(self.thumb.write())
        
        b.write(write_int(self.dc_id))
        
        b.write(Vector.write_list(self.attributes))
        
        return b.getvalue()


class DecryptedMessage_45(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``36B091DE``

    """

    __slots__ = ("random_id", "ttl", "message", "media", "entities", "via_bot_name", "reply_to_random_id",)

    ID = 0x36b091de
    QUALNAME = "types.DecryptedMessage_45"

    def __init__(self, *, random_id: int, ttl: int, message: str, media: raw.base.DecryptedMessageMedia = None, entities: list[raw.base.MessageEntity] | None = None, via_bot_name: str | None = None, reply_to_random_id: int | None = None) -> None:
        self.random_id = random_id  # long
        self.ttl = ttl  # int
        self.message = message  # string
        self.media = media  # flags.9?DecryptedMessageMedia
        self.entities = entities  # flags.7?Vector<MessageEntity>
        self.via_bot_name = via_bot_name  # flags.11?string
        self.reply_to_random_id = reply_to_random_id  # flags.3?long

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessage_45:
        
        flags = read_int(b)
        
        random_id = read_long(b)
        
        ttl = read_int(b)
        
        message = read_string(b)
        
        media = SecretTLObject.read(b) if flags & (1 << 9) else None
        
        entities = SecretTLObject.read(b, SecretTLObject.read) if flags & (1 << 7) else []
        
        via_bot_name = read_string(b) if flags & (1 << 11) else None
        reply_to_random_id = read_long(b) if flags & (1 << 3) else None
        return DecryptedMessage_45(random_id=random_id, ttl=ttl, message=message, media=media, entities=entities, via_bot_name=via_bot_name, reply_to_random_id=reply_to_random_id)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        flags = 0
        flags |= (1 << 9) if self.media is not None else 0
        flags |= (1 << 7) if self.entities else 0
        flags |= (1 << 11) if self.via_bot_name is not None else 0
        flags |= (1 << 3) if self.reply_to_random_id is not None else 0
        b.write(write_int(flags))
        
        b.write(write_long(self.random_id))
        
        b.write(write_int(self.ttl))
        
        b.write(write_string(self.message))
        
        if self.media is not None:
            b.write(self.media.write())
        
        if self.entities is not None:
            b.write(Vector.write_list(self.entities))
        
        if self.via_bot_name is not None:
            b.write(write_string(self.via_bot_name))
        
        if self.reply_to_random_id is not None:
            b.write(write_long(self.reply_to_random_id))
        
        return b.getvalue()


class DecryptedMessageMediaPhoto_45(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``F1FA8D78``

    """

    __slots__ = ("thumb", "thumb_w", "thumb_h", "w", "h", "size", "key", "iv", "caption",)

    ID = 0xf1fa8d78
    QUALNAME = "types.DecryptedMessageMediaPhoto_45"

    def __init__(self, *, thumb: bytes, thumb_w: int, thumb_h: int, w: int, h: int, size: int, key: bytes, iv: bytes, caption: str) -> None:
        self.thumb = thumb  # bytes
        self.thumb_w = thumb_w  # int
        self.thumb_h = thumb_h  # int
        self.w = w  # int
        self.h = h  # int
        self.size = size  # int
        self.key = key  # bytes
        self.iv = iv  # bytes
        self.caption = caption  # string

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaPhoto_45:
        # No flags
        
        thumb = read_bytes(b)
        
        thumb_w = read_int(b)
        
        thumb_h = read_int(b)
        
        w = read_int(b)
        
        h = read_int(b)
        
        size = read_int(b)
        
        key = read_bytes(b)
        
        iv = read_bytes(b)
        
        caption = read_string(b)
        
        return DecryptedMessageMediaPhoto_45(thumb=thumb, thumb_w=thumb_w, thumb_h=thumb_h, w=w, h=h, size=size, key=key, iv=iv, caption=caption)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_bytes(self.thumb))
        
        b.write(write_int(self.thumb_w))
        
        b.write(write_int(self.thumb_h))
        
        b.write(write_int(self.w))
        
        b.write(write_int(self.h))
        
        b.write(write_int(self.size))
        
        b.write(write_bytes(self.key))
        
        b.write(write_bytes(self.iv))
        
        b.write(write_string(self.caption))
        
        return b.getvalue()


class DecryptedMessageMediaVideo_45(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``970C8C0E``

    """

    __slots__ = ("thumb", "thumb_w", "thumb_h", "duration", "mime_type", "w", "h", "size", "key", "iv", "caption",)

    ID = 0x970c8c0e
    QUALNAME = "types.DecryptedMessageMediaVideo_45"

    def __init__(self, *, thumb: bytes, thumb_w: int, thumb_h: int, duration: int, mime_type: str, w: int, h: int, size: int, key: bytes, iv: bytes, caption: str) -> None:
        self.thumb = thumb  # bytes
        self.thumb_w = thumb_w  # int
        self.thumb_h = thumb_h  # int
        self.duration = duration  # int
        self.mime_type = mime_type  # string
        self.w = w  # int
        self.h = h  # int
        self.size = size  # int
        self.key = key  # bytes
        self.iv = iv  # bytes
        self.caption = caption  # string

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaVideo_45:
        # No flags
        
        thumb = read_bytes(b)
        
        thumb_w = read_int(b)
        
        thumb_h = read_int(b)
        
        duration = read_int(b)
        
        mime_type = read_string(b)
        
        w = read_int(b)
        
        h = read_int(b)
        
        size = read_int(b)
        
        key = read_bytes(b)
        
        iv = read_bytes(b)
        
        caption = read_string(b)
        
        return DecryptedMessageMediaVideo_45(thumb=thumb, thumb_w=thumb_w, thumb_h=thumb_h, duration=duration, mime_type=mime_type, w=w, h=h, size=size, key=key, iv=iv, caption=caption)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_bytes(self.thumb))
        
        b.write(write_int(self.thumb_w))
        
        b.write(write_int(self.thumb_h))
        
        b.write(write_int(self.duration))
        
        b.write(write_string(self.mime_type))
        
        b.write(write_int(self.w))
        
        b.write(write_int(self.h))
        
        b.write(write_int(self.size))
        
        b.write(write_bytes(self.key))
        
        b.write(write_bytes(self.iv))
        
        b.write(write_string(self.caption))
        
        return b.getvalue()


class DecryptedMessageMediaDocument_45(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``7AFE8AE2``

    """

    __slots__ = ("thumb", "thumb_w", "thumb_h", "mime_type", "size", "key", "iv", "attributes", "caption",)

    ID = 0x7afe8ae2
    QUALNAME = "types.DecryptedMessageMediaDocument_45"

    def __init__(self, *, thumb: bytes, thumb_w: int, thumb_h: int, mime_type: str, size: int, key: bytes, iv: bytes, attributes: list[raw.base.DocumentAttribute], caption: str) -> None:
        self.thumb = thumb  # bytes
        self.thumb_w = thumb_w  # int
        self.thumb_h = thumb_h  # int
        self.mime_type = mime_type  # string
        self.size = size  # int
        self.key = key  # bytes
        self.iv = iv  # bytes
        self.attributes = attributes  # Vector<DocumentAttribute>
        self.caption = caption  # string

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaDocument_45:
        # No flags
        
        thumb = read_bytes(b)
        
        thumb_w = read_int(b)
        
        thumb_h = read_int(b)
        
        mime_type = read_string(b)
        
        size = read_int(b)
        
        key = read_bytes(b)
        
        iv = read_bytes(b)
        
        attributes = Vector.read(b, SecretTLObject.read)
        
        caption = read_string(b)
        
        return DecryptedMessageMediaDocument_45(thumb=thumb, thumb_w=thumb_w, thumb_h=thumb_h, mime_type=mime_type, size=size, key=key, iv=iv, attributes=attributes, caption=caption)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_bytes(self.thumb))
        
        b.write(write_int(self.thumb_w))
        
        b.write(write_int(self.thumb_h))
        
        b.write(write_string(self.mime_type))
        
        b.write(write_int(self.size))
        
        b.write(write_bytes(self.key))
        
        b.write(write_bytes(self.iv))
        
        b.write(Vector.write_list(self.attributes))
        
        b.write(write_string(self.caption))
        
        return b.getvalue()


class DocumentAttributeSticker_45(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``3A556302``

    """

    __slots__ = ("alt", "stickerset",)

    ID = 0x3a556302
    QUALNAME = "types.DocumentAttributeSticker_45"

    def __init__(self, *, alt: str, stickerset: raw.base.InputStickerSet) -> None:
        self.alt = alt  # string
        self.stickerset = stickerset  # InputStickerSet

    @staticmethod
    def read(b: BytesIO, *args) -> DocumentAttributeSticker_45:
        # No flags
        
        alt = read_string(b)
        
        stickerset = SecretTLObject.read(b)
        
        return DocumentAttributeSticker_45(alt=alt, stickerset=stickerset)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_string(self.alt))
        
        b.write(self.stickerset.write())
        
        return b.getvalue()


class DocumentAttributeAudio_45(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``DED218E0``

    """

    __slots__ = ("duration", "title", "performer",)

    ID = 0xded218e0
    QUALNAME = "types.DocumentAttributeAudio_45"

    def __init__(self, *, duration: int, title: str, performer: str) -> None:
        self.duration = duration  # int
        self.title = title  # string
        self.performer = performer  # string

    @staticmethod
    def read(b: BytesIO, *args) -> DocumentAttributeAudio_45:
        # No flags
        
        duration = read_int(b)
        
        title = read_string(b)
        
        performer = read_string(b)
        
        return DocumentAttributeAudio_45(duration=duration, title=title, performer=performer)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.duration))
        
        b.write(write_string(self.title))
        
        b.write(write_string(self.performer))
        
        return b.getvalue()


class MessageEntityUnknown(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``BB92BA95``

    """

    __slots__ = ("offset", "length",)

    ID = 0xbb92ba95
    QUALNAME = "types.MessageEntityUnknown"

    def __init__(self, *, offset: int, length: int) -> None:
        self.offset = offset  # int
        self.length = length  # int

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityUnknown:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        return MessageEntityUnknown(offset=offset, length=length)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        return b.getvalue()


class MessageEntityMention(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``FA04579D``

    """

    __slots__ = ("offset", "length",)

    ID = 0xfa04579d
    QUALNAME = "types.MessageEntityMention"

    def __init__(self, *, offset: int, length: int) -> None:
        self.offset = offset  # int
        self.length = length  # int

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityMention:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        return MessageEntityMention(offset=offset, length=length)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        return b.getvalue()


class MessageEntityHashtag(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``6F635B0D``

    """

    __slots__ = ("offset", "length",)

    ID = 0x6f635b0d
    QUALNAME = "types.MessageEntityHashtag"

    def __init__(self, *, offset: int, length: int) -> None:
        self.offset = offset  # int
        self.length = length  # int

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityHashtag:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        return MessageEntityHashtag(offset=offset, length=length)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        return b.getvalue()


class MessageEntityBotCommand(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``6CEF8AC7``

    """

    __slots__ = ("offset", "length",)

    ID = 0x6cef8ac7
    QUALNAME = "types.MessageEntityBotCommand"

    def __init__(self, *, offset: int, length: int) -> None:
        self.offset = offset  # int
        self.length = length  # int

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityBotCommand:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        return MessageEntityBotCommand(offset=offset, length=length)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        return b.getvalue()


class MessageEntityUrl(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``6ED02538``

    """

    __slots__ = ("offset", "length",)

    ID = 0x6ed02538
    QUALNAME = "types.MessageEntityUrl"

    def __init__(self, *, offset: int, length: int) -> None:
        self.offset = offset  # int
        self.length = length  # int

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityUrl:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        return MessageEntityUrl(offset=offset, length=length)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        return b.getvalue()


class MessageEntityEmail(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``64E475C2``

    """

    __slots__ = ("offset", "length",)

    ID = 0x64e475c2
    QUALNAME = "types.MessageEntityEmail"

    def __init__(self, *, offset: int, length: int) -> None:
        self.offset = offset  # int
        self.length = length  # int

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityEmail:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        return MessageEntityEmail(offset=offset, length=length)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        return b.getvalue()


class MessageEntityBold(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``BD610BC9``

    """

    __slots__ = ("offset", "length",)

    ID = 0xbd610bc9
    QUALNAME = "types.MessageEntityBold"

    def __init__(self, *, offset: int, length: int) -> None:
        self.offset = offset  # int
        self.length = length  # int

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityBold:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        return MessageEntityBold(offset=offset, length=length)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        return b.getvalue()


class MessageEntityItalic(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``826F8B60``

    """

    __slots__ = ("offset", "length",)

    ID = 0x826f8b60
    QUALNAME = "types.MessageEntityItalic"

    def __init__(self, *, offset: int, length: int) -> None:
        self.offset = offset  # int
        self.length = length  # int

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityItalic:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        return MessageEntityItalic(offset=offset, length=length)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        return b.getvalue()


class MessageEntityCode(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``28A20571``

    """

    __slots__ = ("offset", "length",)

    ID = 0x28a20571
    QUALNAME = "types.MessageEntityCode"

    def __init__(self, *, offset: int, length: int) -> None:
        self.offset = offset  # int
        self.length = length  # int

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityCode:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        return MessageEntityCode(offset=offset, length=length)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        return b.getvalue()


class MessageEntityPre(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``73924BE0``

    """

    __slots__ = ("offset", "length", "language",)

    ID = 0x73924be0
    QUALNAME = "types.MessageEntityPre"

    def __init__(self, *, offset: int, length: int, language: str) -> None:
        self.offset = offset  # int
        self.length = length  # int
        self.language = language  # string

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityPre:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        language = read_string(b)
        
        return MessageEntityPre(offset=offset, length=length, language=language)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        b.write(write_string(self.language))
        
        return b.getvalue()


class MessageEntityTextUrl(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``76A6D327``

    """

    __slots__ = ("offset", "length", "url",)

    ID = 0x76a6d327
    QUALNAME = "types.MessageEntityTextUrl"

    def __init__(self, *, offset: int, length: int, url: str) -> None:
        self.offset = offset  # int
        self.length = length  # int
        self.url = url  # string

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityTextUrl:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        url = read_string(b)
        
        return MessageEntityTextUrl(offset=offset, length=length, url=url)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        b.write(write_string(self.url))
        
        return b.getvalue()


class InputStickerSetShortName(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``861CC8A0``

    """

    __slots__ = ("short_name",)

    ID = 0x861cc8a0
    QUALNAME = "types.InputStickerSetShortName"

    def __init__(self, *, short_name: str) -> None:
        self.short_name = short_name  # string

    @staticmethod
    def read(b: BytesIO, *args) -> InputStickerSetShortName:
        # No flags
        
        short_name = read_string(b)
        
        return InputStickerSetShortName(short_name=short_name)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_string(self.short_name))
        
        return b.getvalue()


class InputStickerSetEmpty(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``FFB62B95``

    """

    __slots__ = ()

    ID = 0xffb62b95
    QUALNAME = "types.InputStickerSetEmpty"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> InputStickerSetEmpty:
        # No flags
        
        return InputStickerSetEmpty()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class DecryptedMessageMediaVenue(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``8A0DF56F``

    """

    __slots__ = ("lat", "long", "title", "address", "provider", "venue_id",)

    ID = 0x8a0df56f
    QUALNAME = "types.DecryptedMessageMediaVenue"

    def __init__(self, *, lat: float, long: float, title: str, address: str, provider: str, venue_id: str) -> None:
        self.lat = lat  # double
        self.long = long  # double
        self.title = title  # string
        self.address = address  # string
        self.provider = provider  # string
        self.venue_id = venue_id  # string

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaVenue:
        # No flags
        
        lat = read_double(b)
        
        long = read_double(b)
        
        title = read_string(b)
        
        address = read_string(b)
        
        provider = read_string(b)
        
        venue_id = read_string(b)
        
        return DecryptedMessageMediaVenue(lat=lat, long=long, title=title, address=address, provider=provider, venue_id=venue_id)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_double(self.lat))
        
        b.write(write_double(self.long))
        
        b.write(write_string(self.title))
        
        b.write(write_string(self.address))
        
        b.write(write_string(self.provider))
        
        b.write(write_string(self.venue_id))
        
        return b.getvalue()


class DecryptedMessageMediaWebPage(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``45``
        - ID: ``E50511D8``

    """

    __slots__ = ("url",)

    ID = 0xe50511d8
    QUALNAME = "types.DecryptedMessageMediaWebPage"

    def __init__(self, *, url: str) -> None:
        self.url = url  # string

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaWebPage:
        # No flags
        
        url = read_string(b)
        
        return DecryptedMessageMediaWebPage(url=url)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_string(self.url))
        
        return b.getvalue()


class DocumentAttributeAudio_46(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``46``
        - ID: ``9852F9C6``

    """

    __slots__ = ("duration", "voice", "title", "performer", "waveform",)

    ID = 0x9852f9c6
    QUALNAME = "types.DocumentAttributeAudio_46"

    def __init__(self, *, duration: int, voice: bool | None = None, title: str | None = None, performer: str | None = None, waveform: bytes | None = None) -> None:
        self.duration = duration  # int
        self.voice = voice  # flags.10?true
        self.title = title  # flags.0?string
        self.performer = performer  # flags.1?string
        self.waveform = waveform  # flags.2?bytes

    @staticmethod
    def read(b: BytesIO, *args) -> DocumentAttributeAudio_46:
        
        flags = read_int(b)
        
        voice = True if flags & (1 << 10) else False
        duration = read_int(b)
        
        title = read_string(b) if flags & (1 << 0) else None
        performer = read_string(b) if flags & (1 << 1) else None
        waveform = read_bytes(b) if flags & (1 << 2) else None
        return DocumentAttributeAudio_46(duration=duration, voice=voice, title=title, performer=performer, waveform=waveform)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        flags = 0
        flags |= (1 << 10) if self.voice else 0
        flags |= (1 << 0) if self.title is not None else 0
        flags |= (1 << 1) if self.performer is not None else 0
        flags |= (1 << 2) if self.waveform is not None else 0
        b.write(write_int(flags))
        
        b.write(write_int(self.duration))
        
        if self.title is not None:
            b.write(write_string(self.title))
        
        if self.performer is not None:
            b.write(write_string(self.performer))
        
        if self.waveform is not None:
            b.write(write_bytes(self.waveform))
        
        return b.getvalue()


class DocumentAttributeVideo_66(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``66``
        - ID: ``EF02CE6``

    """

    __slots__ = ("duration", "w", "h", "round_message",)

    ID = 0xef02ce6
    QUALNAME = "types.DocumentAttributeVideo_66"

    def __init__(self, *, duration: int, w: int, h: int, round_message: bool | None = None) -> None:
        self.duration = duration  # int
        self.w = w  # int
        self.h = h  # int
        self.round_message = round_message  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args) -> DocumentAttributeVideo_66:
        
        flags = read_int(b)
        
        round_message = True if flags & (1 << 0) else False
        duration = read_int(b)
        
        w = read_int(b)
        
        h = read_int(b)
        
        return DocumentAttributeVideo_66(duration=duration, w=w, h=h, round_message=round_message)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.round_message else 0
        b.write(write_int(flags))
        
        b.write(write_int(self.duration))
        
        b.write(write_int(self.w))
        
        b.write(write_int(self.h))
        
        return b.getvalue()


class SendMessageRecordRoundAction(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``66``
        - ID: ``88F27FBC``

    """

    __slots__ = ()

    ID = 0x88f27fbc
    QUALNAME = "types.SendMessageRecordRoundAction"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> SendMessageRecordRoundAction:
        # No flags
        
        return SendMessageRecordRoundAction()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class SendMessageUploadRoundAction(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``66``
        - ID: ``BB718624``

    """

    __slots__ = ()

    ID = 0xbb718624
    QUALNAME = "types.SendMessageUploadRoundAction"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(b: BytesIO, *args) -> SendMessageUploadRoundAction:
        # No flags
        
        return SendMessageUploadRoundAction()

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        return b.getvalue()


class DecryptedMessage_73(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``73``
        - ID: ``91CC4674``

    """

    __slots__ = ("random_id", "ttl", "message", "no_webpage", "silent", "media", "entities", "via_bot_name", "reply_to_random_id", "grouped_id",)

    ID = 0x91cc4674
    QUALNAME = "types.DecryptedMessage_73"

    def __init__(self, *, random_id: int, ttl: int, message: str, no_webpage: bool | None = None, silent: bool | None = None, media: raw.base.DecryptedMessageMedia = None, entities: list[raw.base.MessageEntity] | None = None, via_bot_name: str | None = None, reply_to_random_id: int | None = None, grouped_id: int | None = None) -> None:
        self.random_id = random_id  # long
        self.ttl = ttl  # int
        self.message = message  # string
        self.no_webpage = no_webpage  # flags.1?true
        self.silent = silent  # flags.5?true
        self.media = media  # flags.9?DecryptedMessageMedia
        self.entities = entities  # flags.7?Vector<MessageEntity>
        self.via_bot_name = via_bot_name  # flags.11?string
        self.reply_to_random_id = reply_to_random_id  # flags.3?long
        self.grouped_id = grouped_id  # flags.17?long

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessage_73:
        
        flags = read_int(b)
        
        no_webpage = True if flags & (1 << 1) else False
        silent = True if flags & (1 << 5) else False
        random_id = read_long(b)
        
        ttl = read_int(b)
        
        message = read_string(b)
        
        media = SecretTLObject.read(b) if flags & (1 << 9) else None
        
        entities = SecretTLObject.read(b, SecretTLObject.read) if flags & (1 << 7) else []
        
        via_bot_name = read_string(b) if flags & (1 << 11) else None
        reply_to_random_id = read_long(b) if flags & (1 << 3) else None
        grouped_id = read_long(b) if flags & (1 << 17) else None
        return DecryptedMessage_73(random_id=random_id, ttl=ttl, message=message, no_webpage=no_webpage, silent=silent, media=media, entities=entities, via_bot_name=via_bot_name, reply_to_random_id=reply_to_random_id, grouped_id=grouped_id)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.no_webpage else 0
        flags |= (1 << 5) if self.silent else 0
        flags |= (1 << 9) if self.media is not None else 0
        flags |= (1 << 7) if self.entities else 0
        flags |= (1 << 11) if self.via_bot_name is not None else 0
        flags |= (1 << 3) if self.reply_to_random_id is not None else 0
        flags |= (1 << 17) if self.grouped_id is not None else 0
        b.write(write_int(flags))
        
        b.write(write_long(self.random_id))
        
        b.write(write_int(self.ttl))
        
        b.write(write_string(self.message))
        
        if self.media is not None:
            b.write(self.media.write())
        
        if self.entities is not None:
            b.write(Vector.write_list(self.entities))
        
        if self.via_bot_name is not None:
            b.write(write_string(self.via_bot_name))
        
        if self.reply_to_random_id is not None:
            b.write(write_long(self.reply_to_random_id))
        
        if self.grouped_id is not None:
            b.write(write_long(self.grouped_id))
        
        return b.getvalue()


class MessageEntityUnderline(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``101``
        - ID: ``9C4E7E8B``

    """

    __slots__ = ("offset", "length",)

    ID = 0x9c4e7e8b
    QUALNAME = "types.MessageEntityUnderline"

    def __init__(self, *, offset: int, length: int) -> None:
        self.offset = offset  # int
        self.length = length  # int

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityUnderline:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        return MessageEntityUnderline(offset=offset, length=length)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        return b.getvalue()


class MessageEntityStrike(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``101``
        - ID: ``BF0693D4``

    """

    __slots__ = ("offset", "length",)

    ID = 0xbf0693d4
    QUALNAME = "types.MessageEntityStrike"

    def __init__(self, *, offset: int, length: int) -> None:
        self.offset = offset  # int
        self.length = length  # int

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityStrike:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        return MessageEntityStrike(offset=offset, length=length)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        return b.getvalue()


class MessageEntityBlockquote(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``101``
        - ID: ``20DF5D0``

    """

    __slots__ = ("offset", "length",)

    ID = 0x20df5d0
    QUALNAME = "types.MessageEntityBlockquote"

    def __init__(self, *, offset: int, length: int) -> None:
        self.offset = offset  # int
        self.length = length  # int

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityBlockquote:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        return MessageEntityBlockquote(offset=offset, length=length)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        return b.getvalue()


class DecryptedMessageMediaDocument_143(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``143``
        - ID: ``6ABD9782``

    """

    __slots__ = ("thumb", "thumb_w", "thumb_h", "mime_type", "size", "key", "iv", "attributes", "caption",)

    ID = 0x6abd9782
    QUALNAME = "types.DecryptedMessageMediaDocument_143"

    def __init__(self, *, thumb: bytes, thumb_w: int, thumb_h: int, mime_type: str, size: int, key: bytes, iv: bytes, attributes: list[raw.base.DocumentAttribute], caption: str) -> None:
        self.thumb = thumb  # bytes
        self.thumb_w = thumb_w  # int
        self.thumb_h = thumb_h  # int
        self.mime_type = mime_type  # string
        self.size = size  # long
        self.key = key  # bytes
        self.iv = iv  # bytes
        self.attributes = attributes  # Vector<DocumentAttribute>
        self.caption = caption  # string

    @staticmethod
    def read(b: BytesIO, *args) -> DecryptedMessageMediaDocument_143:
        # No flags
        
        thumb = read_bytes(b)
        
        thumb_w = read_int(b)
        
        thumb_h = read_int(b)
        
        mime_type = read_string(b)
        
        size = read_long(b)
        
        key = read_bytes(b)
        
        iv = read_bytes(b)
        
        attributes = Vector.read(b, SecretTLObject.read)
        
        caption = read_string(b)
        
        return DecryptedMessageMediaDocument_143(thumb=thumb, thumb_w=thumb_w, thumb_h=thumb_h, mime_type=mime_type, size=size, key=key, iv=iv, attributes=attributes, caption=caption)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_bytes(self.thumb))
        
        b.write(write_int(self.thumb_w))
        
        b.write(write_int(self.thumb_h))
        
        b.write(write_string(self.mime_type))
        
        b.write(write_long(self.size))
        
        b.write(write_bytes(self.key))
        
        b.write(write_bytes(self.iv))
        
        b.write(Vector.write_list(self.attributes))
        
        b.write(write_string(self.caption))
        
        return b.getvalue()


class MessageEntitySpoiler(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``144``
        - ID: ``32CA960F``

    """

    __slots__ = ("offset", "length",)

    ID = 0x32ca960f
    QUALNAME = "types.MessageEntitySpoiler"

    def __init__(self, *, offset: int, length: int) -> None:
        self.offset = offset  # int
        self.length = length  # int

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntitySpoiler:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        return MessageEntitySpoiler(offset=offset, length=length)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        return b.getvalue()


class MessageEntityCustomEmoji(SecretTLObject):  # type: ignore
    """Telegram API type.

    Details:
        - Layer: ``144``
        - ID: ``C8CF05F8``

    """

    __slots__ = ("offset", "length", "document_id",)

    ID = 0xc8cf05f8
    QUALNAME = "types.MessageEntityCustomEmoji"

    def __init__(self, *, offset: int, length: int, document_id: int) -> None:
        self.offset = offset  # int
        self.length = length  # int
        self.document_id = document_id  # long

    @staticmethod
    def read(b: BytesIO, *args) -> MessageEntityCustomEmoji:
        # No flags
        
        offset = read_int(b)
        
        length = read_int(b)
        
        document_id = read_long(b)
        
        return MessageEntityCustomEmoji(offset=offset, length=length, document_id=document_id)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(write_int(self.ID, False))

        # No flags
        
        b.write(write_int(self.offset))
        
        b.write(write_int(self.length))
        
        b.write(write_long(self.document_id))
        
        return b.getvalue()


