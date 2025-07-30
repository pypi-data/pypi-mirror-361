#!/usr/bin/env python3

# Copyright © 2023-2024, Meheret Tesfaye Batu <meherett.batu@gmail.com>
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit

from typing import (
    Union, Tuple, Type
)

from .libs.base58 import (
    encode, decode
)
from .cryptocurrencies import (
    ICryptocurrency, Bitcoin
)
from .const import (
    COMPRESSED_PRIVATE_KEY_PREFIX, WIF_TYPES
)
from .crypto import get_checksum
from .exceptions import (
    WIFError, Secp256k1Error
)
from .utils import (
    get_bytes, integer_to_bytes, bytes_to_string
)


def encode_wif(
    private_key: Union[str, bytes], wif_prefix: int = Bitcoin.NETWORKS["mainnet"]["wif_prefix"]
) -> Tuple[str, str]:
    """
    Encode a private key to Wallet Import Format (WIF).

    :param private_key: The private key to encode, as a 32-byte string or bytes.
    :type private_key: Union[str, bytes]
    :param wif_prefix: The prefix to use for the WIF format (default is Bitcoin mainnet prefix).
    :type wif_prefix: int

    :returns: A tuple containing the WIF and WIF-compressed formats.
    :rtype: Tuple[str, str]
    """

    if len(get_bytes(private_key)) != 32:
        raise Secp256k1Error("Invalid private key length", expected=64, got=len(private_key))

    wif_payload: bytes = (
        integer_to_bytes(wif_prefix) + get_bytes(private_key)
    )
    wif_compressed_payload: bytes = (
        integer_to_bytes(wif_prefix) + get_bytes(private_key) + integer_to_bytes(COMPRESSED_PRIVATE_KEY_PREFIX)
    )
    return (
        encode(wif_payload + get_checksum(wif_payload)),
        encode(wif_compressed_payload + get_checksum(wif_compressed_payload))
    )


def decode_wif(
    wif: str, wif_prefix: int = Bitcoin.NETWORKS["mainnet"]["wif_prefix"]
) -> Tuple[bytes, str, bytes]:
    """
    Decode a Wallet Import Format (WIF) string to a private key.

    :param wif: The WIF string to decode.
    :type wif: str
    :param wif_prefix: The prefix to use for the WIF format (default is Bitcoin mainnet prefix).
    :type wif_prefix: int

    :returns: A tuple containing the private key, the WIF type ('wif' or 'wif-compressed'), and the checksum.
    :rtype: Tuple[bytes, str, bytes]
    """

    raw: bytes = decode(wif)
    if not raw.startswith(integer_to_bytes(wif_prefix)):
        raise WIFError(f"Invalid Wallet Import Format (WIF)")

    prefix_length: int = len(integer_to_bytes(wif_prefix))
    prefix_got: bytes = raw[:prefix_length]
    if integer_to_bytes(wif_prefix) != prefix_got:
        raise WIFError("Invalid WIF prefix", expected=prefix_length, got=prefix_got)

    raw_without_prefix: bytes = raw[prefix_length:]
    checksum: bytes = raw_without_prefix[-1 * 4:]
    private_key: bytes = raw_without_prefix[:-1 * 4]
    wif_type: str = "wif"

    if len(private_key) not in [33, 32]:
        raise WIFError(f"Invalid Wallet Import Format (WIF)")
    elif len(private_key) == 33:
        private_key = private_key[:-len(integer_to_bytes(COMPRESSED_PRIVATE_KEY_PREFIX))]
        wif_type = "wif-compressed"

    return private_key, wif_type, checksum


def private_key_to_wif(
    private_key: Union[str, bytes],
    wif_type: str = "wif-compressed",
    cryptocurrency: Type[ICryptocurrency] = Bitcoin,
    network: str = "mainnet"
) -> str:
    """
    Convert a private key to Wallet Import Format (WIF).

    :param private_key: The private key to convert, as a 32-byte string or bytes.
    :type private_key: Union[str, bytes]
    :param wif_type: The WIF type, either 'wif' or 'wif-compressed' (default is 'wif-compressed').
    :type wif_type: str
    :param cryptocurrency: The cryptocurrency class (default is Bitcoin).
    :type cryptocurrency: Type[ICryptocurrency]
    :param network: The network type (default is 'mainnet').
    :type network: str

    :returns: The private key in WIF format.
    :rtype: str
    """

    if wif_type not in WIF_TYPES:
        raise WIFError("Wrong WIF type", expected=WIF_TYPES, got=wif_type)
    wif, wif_compressed = encode_wif(
        private_key=private_key, wif_prefix=cryptocurrency.NETWORKS[network]["wif_prefix"]
    )
    return wif if wif_type == "wif" else wif_compressed


def wif_to_private_key(
    wif: str, cryptocurrency: Type[ICryptocurrency] = Bitcoin, network: str = "mainnet"
) -> str:
    """
    Convert a Wallet Import Format (WIF) string to a private key.

    :param wif: The WIF string to decode.
    :type wif: str
    :param cryptocurrency: The cryptocurrency class (default is Bitcoin).
    :type cryptocurrency: Type[ICryptocurrency]
    :param network: The network type (default is 'mainnet').
    :type network: str

    :returns: The private key as a string.
    :rtype: str
    """

    return bytes_to_string(decode_wif(
        wif=wif, wif_prefix=cryptocurrency.NETWORKS[network]["wif_prefix"]
    )[0])


def get_wif_type(
    wif: str, cryptocurrency: Type[ICryptocurrency] = Bitcoin, network: str = "mainnet"
) -> str:
    """
    Get the type of Wallet Import Format (WIF) string ('wif' or 'wif-compressed').

    :param wif: The WIF string to inspect.
    :type wif: str
    :param cryptocurrency: The cryptocurrency class (default is Bitcoin).
    :type cryptocurrency: Type[ICryptocurrency]
    :param network: The network type (default is 'mainnet').
    :type network: str

    :returns: The WIF type ('wif' or 'wif-compressed').
    :rtype: str
    """

    return decode_wif(
        wif=wif, wif_prefix=cryptocurrency.NETWORKS[network]["wif_prefix"]
    )[1]


def get_wif_checksum(
    wif: str, cryptocurrency: Type[ICryptocurrency] = Bitcoin, network: str = "mainnet"
) -> str:
    """
    Get the checksum of a Wallet Import Format (WIF) string.

    :param wif: The WIF string to inspect.
    :type wif: str
    :param cryptocurrency: The cryptocurrency class (default is Bitcoin).
    :type cryptocurrency: Type[ICryptocurrency]
    :param network: The network type (default is 'mainnet').
    :type network: str

    :returns: The checksum as a string.
    :rtype: str
    """

    return bytes_to_string(decode_wif(
        wif=wif, wif_prefix=cryptocurrency.NETWORKS[network]["wif_prefix"]
    )[2])
