# -*- coding: utf-8 -*-

import contextlib
import os
import sys

import arcpy

# You can ignore/delete this code; these are basic utility functions to
# streamline porting

# @contextlib.contextmanager
# def script_run_as(filename, args=None):
#     oldpath = sys.path[:]
#     oldargv = sys.argv[:]
#     newdir = os.path.dirname(filename)
#     sys.path = oldpath + [newdir]
#     sys.argv = [filename] + [arg.valueAsText for arg in (args or [])]
#     oldcwd = os.getcwdu()
#     os.chdir(newdir)
#
#     try:
#         # Actually run
#         yield filename
#     finally:
#         # Restore old settings
#         sys.path = oldpath
#         sys.argv = oldargv
#         os.chdir(oldcwd)


from tools.configure import ConfigureTool
from tools.create_project import CreateProject
from tools.context_calculation import ContextCalculation


class Toolbox(object):
    def __init__(self):
        self.label = u'ASDST'
        self.alias = u'ASDST'
        self.tools = [ConfigureTool, CreateProject, ContextCalculation]


def main():
    pass


if __name__ == "__main__":
    main()
