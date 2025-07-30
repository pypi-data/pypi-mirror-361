"""Test"""

from __future__ import annotations

import argparse
from typing import Dict, List, Optional, Type

import pytest
from pytest_mock import MockerFixture

from certbot_deployer import CertificateBundle, Deployer
import certbot_deployer_vsphere._main as plugin_main
from certbot_deployer_vsphere.certbot_deployer_vsphere import (
    VsphereDeployer,
    put_certificate,
)


@pytest.mark.parametrize(
    "tls_no_verify",
    [False, True],
)
def test_put_certificate(
    # monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
    certbot_deployer_self_signed_certificate_bundle: CertificateBundle,
    tls_no_verify: bool,
) -> None:
    """
    Fake connection creation and cert upload and ensure that the expected host
    is targeted with the expected certificates

    Parameterize on whether to verify TLS
    """
    session_params: Dict[str, str | CertificateBundle] = {
        "host": "test_host",
        "user": "test_user",
        "password": "test_password",
        "certificate_bundle": certbot_deployer_self_signed_certificate_bundle,
    }

    mock_session_instance = mocker.MagicMock()
    mock_session_create = mocker.patch(
        "certbot_deployer_vsphere.certbot_deployer_vsphere.requests.session",
        return_value=mock_session_instance,
    )

    mock_client_instance = mocker.MagicMock()
    mock_create_vsphere_client = mocker.patch(
        "certbot_deployer_vsphere.certbot_deployer_vsphere.create_vsphere_client",
        return_value=mock_client_instance,
    )

    mock_tls_spec_instance = mocker.MagicMock()
    mock_tls_spec = mocker.patch(
        "certbot_deployer_vsphere.certbot_deployer_vsphere.Tls.Spec",
        return_value=mock_tls_spec_instance,
    )

    mock_client_tls_set = (
        mock_client_instance.vcenter.certificate_management.vcenter.Tls.set
    )

    put_certificate(
        host=str(session_params["host"]),
        user=str(session_params["user"]),
        password=str(session_params["password"]),
        certificate_bundle=session_params["certificate_bundle"],  # type:ignore
        tls_no_verify=tls_no_verify,
    )

    mock_session_create.assert_called_once()
    assert mock_session_instance.verify is not tls_no_verify

    mock_create_vsphere_client.assert_called_once_with(
        server=str(session_params["host"]),
        username=str(session_params["user"]),
        password=str(session_params["password"]),
        session=mock_session_instance,
    )

    mock_tls_spec.assert_called_once_with(
        cert=certbot_deployer_self_signed_certificate_bundle.cert.contents,
        key=certbot_deployer_self_signed_certificate_bundle.key.contents,
        root_cert=certbot_deployer_self_signed_certificate_bundle.intermediates.contents,
    )

    mock_client_tls_set.assert_called_once_with(mock_tls_spec_instance)


def test_args_valid() -> None:
    """
    Verify that the product of the register_args method is able to be processed by argparse
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title="Subcommands",
        description="test_subparser",
        dest="subcommand",
    )
    subparser = subparsers.add_parser("subcommand")
    VsphereDeployer.register_args(parser=subparser)


def test_main_delegation(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify that our `main()` hands control off to the framework when called
    directly by mocking the framework's `main()` and comparing the passed
    args/deployers
    """
    called_argv: list = []
    called_deployers: Optional[List[Type[Deployer]]]

    def fake_framework_main(
        argv: list, deployers: Optional[List[Type[Deployer]]] = None
    ) -> None:
        nonlocal called_argv
        nonlocal called_deployers
        called_argv = argv
        called_deployers = deployers

    argv: List[str] = ["-h"]
    expected_argv: List[str] = [VsphereDeployer.subcommand, "-h"]
    expected_deployers: Optional[List[Type[Deployer]]] = [VsphereDeployer]

    monkeypatch.setattr(
        plugin_main,
        "framework_main",
        fake_framework_main,
    )
    plugin_main.main(argv=argv)
    assert called_argv == expected_argv
    assert called_deployers == expected_deployers


def test_argparse_post() -> None:
    """
    Verify that the deployer subclass effectively requires all of its required
    args, both individually and collectively
    """
    required_args: Dict[str, str] = {
        k: "somevalue" for k in VsphereDeployer.required_args
    }
    # If this runs with no exception, we're happy
    VsphereDeployer.argparse_post(args=argparse.Namespace(**required_args))

    args: Dict[str, str]
    for arg in VsphereDeployer.required_args:
        args = dict(required_args)
        del args[arg]
        # Every call missing an arg should raise
        with pytest.raises(argparse.ArgumentTypeError):
            VsphereDeployer.argparse_post(args=argparse.Namespace(**args))
