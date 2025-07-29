# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains the main entrypoint for running performance tests"""

from performance.command import run_test

if __name__ == "__main__":
    import typer

    app = typer.Typer()
    app.command()(run_test)
    app()
