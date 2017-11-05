#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Alin Panaitiu
# Copyright (c) 2017 Alin Panaitiu
#
# License: MIT
#
"""This module exports the Clippy plugin class."""

import os
import json

from SublimeLinter.lint import Linter, util

from .addict import Dict


class Rust(Linter):
    """Provides an interface to Rust linting."""

    defaults = {'cargo-command': 'clippy'}
    syntax = ('rust', 'rustenhanced')
    regex = r'^\{.*\}$'
    executable = 'cargo'

    def get_chdir(self, settings):
        """Find the chdir to use with the linter."""
        current_dir = os.path.dirname(self.filename)
        cargo_config = util.find_file(current_dir, 'Cargo.toml')

        if not cargo_config:
            raise Exception('No Cargo.toml found')

        return os.path.dirname(cargo_config)

    def cmd(self):
        cmd = self.get_view_settings().get('cargo-command', self.defaults['cargo-command'])

        return ['cargo', cmd, '--message-format', 'json']

    def error(self, line, col, message, error_type):
        if isinstance(message, (list, set, tuple)):
            for m in message:
                super().error(line, col, m, error_type)
        else:
            super().error(line, col, message, error_type)

    def split_match(self, match):
        if not match:
            return match, None, None, None, None, '', None

        output = Dict(json.loads(match.group()))

        if not os.path.samefile(output.target.src_path, self.filename):
            return match, None, None, None, None, '', None

        output = output.message
        error = output.level == 'error'
        warning = not error
        messages = [output.message, '']
        if output.spans[0].label:
            messages.append(('\t' * 2) + output.spans[0].label)
        messages += [('\t' * 4) + c.message for c in output.children if c.message]

        line = output.spans[0].line_start or None
        if line:
            line -= 1

        col = output.spans[0].column_start or None
        if col:
            col -= 1

        near = output.spans[0].text[0]
        near = near.text[near.highlight_start:near.highlight_end]

        return match, line, col, error, warning, messages, near
