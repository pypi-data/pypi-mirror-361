"""Connectivity test."""

import os
import sys
from re import search

from dns.exception import DNSException
from requests import RequestException

from procustodibus_agent import DOCS_URL
from procustodibus_agent.api import (
    get_health_info,
    get_host_info,
    raise_unless_has_cnf,
    setup_api,
)
from procustodibus_agent.resolve_hostname import is_likely_ip, lookup_ip
from procustodibus_agent.wg import parse_wg_show, run_wg_show, update_socket_mark
from procustodibus_agent.wg_cnf import load_all_from_wg_cnf


def check_connectivity(cnf, output=None):
    """Runs all connectivity checks and outputs issues.

    Arguments:
        cnf (Config): Config object.
        output (IOBase): Output stream to write issues to (defaults to stdout).

    Returns:
        int: 0 if no issues, positive number if issues.
    """
    if not output:
        output = sys.stdout

    try:
        raise_unless_has_cnf(cnf)
    except ValueError as e:
        print(str(e), file=output)
        return 1

    exit_code = (
        check_wg(cnf, output)
        + check_dns(cnf, output)
        + check_health(cnf, output)
        + check_host(cnf, output)
    )

    if exit_code:
        print(
            f"Issues encountered; see {DOCS_URL}/guide/agents/troubleshoot/ to fix",
            file=output,
        )
    else:
        print("All systems go :)", file=output)

    return exit_code


def check_wg(cnf, output):
    """Checks that wireguard is available and configured with at least one interface.

    Arguments:
        cnf (Config): Config object.
        output (IOBase): Output stream to write issues to.

    Returns:
        int: 0 if no issues, positive number if issues.
    """
    if cnf.wiresock:
        try:
            interfaces = load_all_from_wg_cnf(cnf)
        except Exception as e:  # noqa: BLE001
            _bad(f"cannot open interface conf files ({e})", output)
            return 2
    else:
        try:
            interfaces = parse_wg_show(run_wg_show(cnf))
            update_socket_mark(interfaces, cnf)
        except OSError as e:
            _bad(f"no wg executable found ({e})", output)
            return 2

    if interfaces:
        _good(f"{len(interfaces)} wireguard interfaces found", output)
        return 0
    _bad("no wireguard interfaces found", output)
    return 0


def check_dns(cnf, output):
    """Checks that the local DNS resolver can resolve api.procustodib.us.

    Arguments:
        cnf (Config): Config object.
        output (IOBase): Output stream to write issues to.

    Returns:
        int: 0 if no issues, positive number if issues.
    """
    hostname = _get_hostname(cnf.api)
    try:
        address = hostname if is_likely_ip(hostname) else lookup_ip(cnf, hostname)
        _good(f"{address} is pro custodibus ip address", output)
    except DNSException as e:
        _bad(e, output)
        return 4
    else:
        return 0


def check_health(cnf, output):
    """Checks connectivity to and the health of the Pro Custodibus API.

    Arguments:
        cnf (Config): Config object.
        output (IOBase): Output stream to write issues to.

    Returns:
        int: 0 if no issues, positive number if issues.
    """
    try:
        errors = [x["error"] for x in get_health_info(cnf) if not x["healthy"]]
    except (DNSException, RequestException) as e:
        errors = [f"server unavailable ({e})"]

    if errors:
        for error in errors:
            _bad(f"unhealthy pro custodibus api: {error}", output)
        return 8
    _good("healthy pro custodibus api", output)
    return 0


def check_host(cnf, output):
    """Checks that the agent can access the configured host through the API.

    Arguments:
        cnf (Config): Config object.
        output (IOBase): Output stream to write issues to.

    Returns:
        int: 0 if no issues, positive number if issues.
    """
    try:
        _setup_if_available(cnf)
    except (DNSException, RequestException, ValueError) as e:
        _bad(f"cannot set up access to api ({e})", output)
        return 16

    try:
        host = get_host_info(cnf)
        name = host["data"][0]["attributes"]["name"]
        _good(f"can access host record on api for {name}", output)
    except (DNSException, RequestException, ValueError) as e:
        _bad(f"cannot access host record on api ({e})", output)
        return 16
    else:
        return 0


def _setup_if_available(cnf):
    """Sets up new agent credentials if setup code is available.

    Arguments:
        cnf (Config): Config object.
    """
    if type(cnf.setup) is dict or os.path.exists(cnf.setup):
        setup_api(cnf)


def _good(message, output):
    """Prints the specified "good" message to the specified output stream.

    Arguments:
        message (str): Message to print.
        output (IOBase): Output stream to write to.
    """
    print(f"... {message} ...", file=output)


def _bad(message, output):
    """Prints the specified "bad" message to the specified output stream.

    Arguments:
        message (str): Message to print.
        output (IOBase): Output stream to write to.
    """
    print(f"!!! {message} !!!", file=output)


def _get_hostname(url):
    """Extracts the hostname from the specified URL.

    Arguments:
        url (str): URL (eg 'http://test.example.com:8080').

    Returns:
        str: Hostname (eg 'test.example.com').
    """
    match = search(r"(?<=://)[^:/]+", url)
    return match.group(0) if match else None
