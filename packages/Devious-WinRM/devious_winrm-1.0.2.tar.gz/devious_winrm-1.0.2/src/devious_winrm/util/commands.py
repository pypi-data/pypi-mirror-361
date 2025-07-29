"""File to define commands."""
from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import psrp

from devious_winrm.util.printers import print_error, print_ft, print_info

if TYPE_CHECKING:
    from devious_winrm.app import Terminal
import pathlib
from typing import Callable

commands = {}

def command(func: Callable) -> Callable:
    """Automatically registers a command using its docstring.

    This decorator adds the decorated function to the `commands` dictionary,
    using the function's name as the key. The value is a dictionary containing
    the function's docstring as the description and the function itself as the action.

    Args:
        func (Callable): The function to be registered as a command.

    Returns:
        Callable: The original function, unmodified.

    """
    commands[func.__name__] = {
        "description": func.__doc__,
        "action": func,
    }
    return func

def run_command(self: Terminal, user_input: str) -> None:
    """Run a command by looking it up in the dictionary and invoking its action.

    Args:
        self (Terminal): The terminal instance on which the command is executed.
        user_input (str): The command to execute.

    Raises:
        KeyError: If the specified command is not found in the commands dictionary.

    Notes:
        If the command is not found, a message is printed to inform
        the user and suggest typing 'help' for a list of available commands.

    """
    input_array: list[str] = user_input.split(" ")
    if len(input_array) == 0:
         return
    cmd: str = user_input.split(" ")[0]
    args: list[str] = input_array[1:] if len(input_array) > 1 else []
    try:
        commands[cmd]["action"](self, args)
    except KeyError:
        print_error(
            f"Command '{cmd}' not found. Type 'help' for a list of commands.",
        )


@command
def exit(_self: Terminal, _args: str) -> None:  # noqa: A001
    """Exit the application."""
    sys.exit(0)

@command
def help(_self: Terminal, _args: str) -> None:  # noqa: A001
    """Show help information."""
    print_info("Available commands:")
    for cmd, details in commands.items():
        print_info(f"{cmd}: {details['description']}")

@command
def upload(self: Terminal, args: list[str]) -> None:
    """Upload a file.

    Usage: upload <local_path> <remote_path>.

    Large files may struggle to transfer.
    """
    if len(args) < 1:
        print_ft("Usage: upload <local_path> [remote_path]")
        return
    local_path = pathlib.Path(args[0])
    remote_path = args[1] if len(args) > 1 else local_path.name
    try:
        final_path = psrp.copy_file(self.conn, local_path, remote_path)
        print_ft(f"Uploaded {local_path} to {final_path}")
    except FileNotFoundError:
        print_error(f"No such file or directory: {local_path}")
    except psrp.PSRPError as e:
        print_error(f"Failed to upload file: {e}")

@command
def download(self: Terminal, args: list[str]) -> None:
    """Download a file.

    Usage: download <remote_path> [local_path].

    Large files may struggle to transfer.
    """
    if len(args) < 1:
        print_ft("Usage: download <remote_path> [local_path]")
        return
    remote_path = args[0]
    local_path = args[1] if len(args) > 1 else remote_path.split("\\")[-1] # Filename
    try:
        final_path = psrp.fetch_file(self.conn, remote_path, local_path)
        print_ft(f"Downloaded {remote_path} to {final_path}")
    except psrp.PSRPError as e:
        print_error(f"Failed to download file: {e}")
