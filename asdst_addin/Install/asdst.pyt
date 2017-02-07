# -*- coding: utf-8 -*-

from configure import ConfigureTool
from context_calculation import ContextCalculationTool
from create_project import CreateProjectTool


class Toolbox(object):
    def __init__(self):
        self.label = u'Aboriginal Site Decision Support Tools'
        self.alias = u'ASDST'
        self.tools = [ConfigureTool, CreateProjectTool, ContextCalculationTool]


def main():
    pass


if __name__ == "__main__":
    main()
