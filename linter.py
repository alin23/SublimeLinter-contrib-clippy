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

    defaults = {
        'cargo-command': 'clippy',
    }
    syntax = ('rust', 'rustenhanced')
    regex = r'.*'

    cargo_command = 'clippy'

    def get_chdir(self, settings):
        """Find the chdir to use with the linter."""
        current_dir = os.path.dirname(self.filename)
        cargo_config = util.find_file(current_dir, 'Cargo.toml')

        if not cargo_config:
            raise Exception('No Cargo.toml found')

        return os.path.dirname(cargo_config)

    def cmd(self, cmd, code):
        cmd = self.get_view_settings().get('cargo-command', self.cargo_command)

        return ['cargo'] + cmd + ['--message-format', 'json']

    def split_match(self, match):
        output = Dict(json.loads(match.group()))

        if not os.path.samefile(output.target.src_path, self.filename):
            return match, None, None, None, None, '', None

        error = output.level == 'error'
        warning = not error
        message = output.message + '\n\t' + '\n\t'.join(c.message for c in output.children if c.message)
        line = output.spans[0].line_start
        col = output.spans[0].column_start
        near = '\n'.join(c.text for c in output.spans[0].text)

        return match, line, col, error, warning, message, near
