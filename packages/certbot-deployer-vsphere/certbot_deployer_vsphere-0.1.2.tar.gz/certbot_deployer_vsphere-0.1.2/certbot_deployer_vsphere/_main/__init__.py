"""
main
"""

import sys

from certbot_deployer import main as framework_main
from ..certbot_deployer_vsphere import VsphereDeployer


def main(
    argv: list = sys.argv[1:],
) -> None:
    """
    main
    """
    new_argv = [VsphereDeployer.subcommand] + argv
    framework_main(deployers=[VsphereDeployer], argv=new_argv)
