import atexit
import sys
import signal
import platform
import logging

from ctypes import CDLL, POINTER, cast, c_void_p, c_char_p, c_ubyte, c_uint16
from dataclasses import dataclass
from typing import Literal

from .downloader import fetch_config, download_library


__all__ = ["initialize", "load_library", "activate", "benchmark", "generate_contract", "Contract", "deactivate"]


log = logging.getLogger(__name__)


lib: CDLL | None = None
activated: bool = False


def initialize(
    environment: Literal["mainnet", "testnet", "local"],
    test_version: str | None = None,
):
    """
    Downloads the dataset library and loads it into the current process.
    """

    if lib:
        raise Exception("Library is already initialized")

    config = fetch_config()

    env_config = config.get(environment)
    if not env_config:
        raise Exception(f"Invalid environment: {environment}")

    version = test_version or env_config["version"]

    # There are multiple vulnerability libraries, and they are rotated
    # to avoid possibility of full extraction.
    # Server might decide to give any of them, or they might be rotated
    # automatically for everyone, but the downloaded file will have one of the following hashes.
    expected_hashes = set(env_config["hashes"])

    library_path = download_library(version, environment, expected_hashes)

    log.info(f"Loading dataset library for environment '{environment}' ({version})")

    load_library(library_path)


def load_library(library_path: str):
    """
    Loads the dataset library into the current process.
    """

    global lib

    if lib:
        raise Exception("Library is already loaded")
    
    if sys.platform != "linux" or platform.machine() != "x86_64":
        raise Exception("This library only supports Linux x86_64 platform")
    
    lib = CDLL(library_path)
    lib.do_the_thing.argtypes = (POINTER(c_ubyte),)
    lib.do_the_thing.restype = c_void_p

    request = (c_ubyte * 1)(0)

    result = lib.do_the_thing(request)
    assert not result, "Request 'null' always returns null"

    atexit.register(__handle_shutdown)
    signal.signal(signal.SIGINT, __handle_shutdown)
    signal.signal(signal.SIGTERM, __handle_shutdown)


def activate(activation_code: str):
    """
    Activates the library with your activation code.
    
    This is required before you can generate contracts.
    """

    global lib, activated

    if not lib:
        raise Exception("Library is not loaded")
    if activated:
        raise Exception("Already activated")

    log.debug(f"Activating dataset library...")

    request = (c_ubyte * (1 + len(activation_code) + 1))()
    request[0] = 4
    request[1:-1] = [c_ubyte(ord(c)) for c in activation_code]
    request[-1] = 0

    result = lib.do_the_thing(request)

    status = cast(result, POINTER(c_uint16)).contents.value
    if status:
        raise Exception(f"Activation failed with status code {status}")

    log.debug(f"Dataset library activated successfully")
    activated = True


def benchmark():
    global lib, activated

    if not activated:
        raise Exception("Library is not activated")

    request = (c_ubyte * 1)(13)

    result = lib.do_the_thing(request)
    assert result, "Contract pointer can not be null after activation"

    benchmark = cast(result, c_char_p).value.decode()

    log.info(f"Benchmark result:\n{benchmark}")


@dataclass
class Contract:
    vulnerability_class: str
    description: str
    code: str


def generate_contract() -> Contract:
    """
    Generates a new vulnerable contract template.
    
    The library must be initialized and activated before calling this function.
    """

    global lib, activated

    log.debug("Start contract generation...")

    if not activated:
        raise Exception("Library is not activated")

    request = (c_ubyte * 1)(12)

    result = lib.do_the_thing(request)
    assert result, "Contract pointer can not be null after activation"

    if cast(result, c_char_p).value == b"\x00":
        status = cast(result + 1, POINTER(c_uint16)).contents.value
        raise Exception(f"Generation failed with status code {status}")

    vuln_ptr = result
    vuln = cast(vuln_ptr, c_char_p).value.decode()

    desc_ptr = vuln_ptr + len(vuln) + 1
    desc = cast(desc_ptr, c_char_p).value.decode()

    code_ptr = desc_ptr + len(desc) + 1
    code = cast(code_ptr, c_char_p).value.decode()

    contract = Contract(vulnerability_class=vuln, description=desc, code=code)

    log.debug(f"Contract successfully generated: {contract}")

    return contract


def deactivate():
    """
    Deactivates the library.
    """

    global lib, activated

    if not activated:
        raise Exception("Library is not activated")

    log.debug("Deactivating dataset library...")
    
    request = (c_ubyte * 1)(6)
    lib.do_the_thing(request)

    log.debug(f"Dataset library deactivated successfully")
    activated = False

    del lib
    lib = None


def __handle_shutdown(signum = None, frame = None):
    try:
        deactivate()
    except Exception as e:
        pass
