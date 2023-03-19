import re
import sys
import enum
import argparse

from abc import ABC
from typing import Callable, Type
from dataclasses import dataclass


class AutoHelpParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = None
        self.command = None

    def error(self, message):
        if self.command:
            message = re.sub(r"__command_\d+", self.command, message)
        else:
            message = re.sub(r"argument __command_\d+: ", "", message)
        print(f"ERROR: {message}\n")

        if self.parent:
            # print help of child command looking at each parent command
            # to reconstruct the command chain
            prog = list()
            cur = self
            while cur and cur.command:
                prog.insert(0, cur.command)
                cur = cur.parent

            if prog:
                prog_name = self.prog.split(" ")[0]
                prog.insert(0, prog_name)

                self.prog = self.prog.split(" ")[0] + " " + " ".join(prog)

            self.print_help()
        else:
            # the root parser has triggered an error. try to find which child parser's help
            # should be invoked by looping trough argv and each parser's command
            parser = getattr(self, "auto_parser")
            prog = [self.prog]
            argv = sys.argv[1:]
            while argv and argv[0] and hasattr(parser, "commands") and argv[0] in parser.commands:
                parser = parser.commands[argv[0]]
                prog.append(argv.pop(0))

            parser.parser.prog = " ".join(prog)
            parser.parser.print_help()

        sys.exit(1)


@dataclass
class ParserCommand(ABC):
    parser: argparse.ArgumentParser
    main: Callable

    def __call__(self, *args, **kwargs):
        self.main(args)


class AutoParser(ABC):
    description: "str | None" = None

    commands: "dict[str, ParserCommand | AutoParser]" = {}

    _command_counter = 0

    def __init__(self):
        self.parser = AutoHelpParser(description=self.description)
        self.parent = None
        self.command = None
        self.parser.auto_parser = self  # pyright: ignore[reportGeneralTypeIssues]

        self._command_attr_name = f"__command_{AutoParser._command_counter}"
        AutoParser._command_counter += 1

        subparsers = self.parser.add_subparsers(dest=self._command_attr_name)

        for command, parser_command in self.commands.items():
            subparser = parser_command.parser
            subparsers.add_parser(
                command,
                parents=[subparser],  # pyright: ignore[reportGeneralTypeIssues]
                add_help=False,
                help=subparser.description,
                description=subparser.description,
            )

            subparser.parent = self  # pyright: ignore[reportGeneralTypeIssues]
            subparser.command = command  # pyright: ignore[reportGeneralTypeIssues]

            subparsers.choices[command].parent = self.parser  # pyright: ignore[reportGeneralTypeIssues]
            subparsers.choices[command].command = command  # pyright: ignore[reportGeneralTypeIssues]

    def __call__(self, *args, **kwargs):
        argv = sys.argv[1:] if not args else args
        args = self.parser.parse_args(argv or None)

        command = getattr(args, self._command_attr_name)

        if not command:
            self.parser.print_help()
            sys.exit(0)

        self.commands[command](*argv[1:])


class ArgEnum:
    def __init__(self, enum_type: Type[enum.Enum]):
        self.enum_type = enum_type

    @property
    def options(self):
        return tuple(p.name for p in self.enum_type)

    @property
    def default(self):
        return tuple(self.enum_type)[0].name

    @property
    def option_str(self):
        return ",".join(self.options)

    def from_string(self, name: str):
        try:
            return next(p for p in self.enum_type if p.name == name.upper())
        except StopIteration:
            options = self.option_str
            raise ValueError(f'"{name}" is not a valid option. must be one of {{{options}}}')

    def __call__(self, arg: str):
        try:
            return self.from_string(arg)
        except ValueError as ve:
            raise argparse.ArgumentTypeError(str(ve))
