# -*- coding: utf-8 -*-

from config import ConfigureTool
from manage_layers import ManageLayersTool
from project import CreateProjectTool
from context import ContextCalculationTool
from build import BuildDataTool


class Toolbox(object):
    def __init__(self):
        self.label = u'Aboriginal Site Decision Support Tools'
        self.alias = u'ASDST'
        self.tools = [ConfigureTool, ManageLayersTool,CreateProjectTool, BuildDataTool, ContextCalculationTool]


