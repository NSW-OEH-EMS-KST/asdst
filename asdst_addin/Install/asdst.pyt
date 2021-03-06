# -*- coding: utf-8 -*-

from configure import ConfigureTool
from project import CreateProjectTool
from context import ContextCalculationTool
from build import BuildDataTool


class Toolbox(object):
    def __init__(self):
        self.label = u'Aboriginal Site Decision Support Tools'
        self.alias = u'ASDST'
        self.tools = [ConfigureTool, CreateProjectTool, BuildDataTool, ContextCalculationTool]


