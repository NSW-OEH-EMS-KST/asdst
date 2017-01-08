from tools.configure import ConfigureTool
from tools.create_project import CreateProject
from tools.context_calculation import ContextCalculation


class Toolbox(object):
    def __init__(self):
        self.label = u'ASDST'
        self.alias = u'ASDST'
        self.tools = [CreateProject, ConfigureTool, ContextCalculation]


def main():
    tbx = Toolbox()

    for tool_class in tbx.tools:
        try:
            print "Creating '{0}'".format(tool_class.__name__)
            tool = tool_class()
            print "Building blank parameters for '{0}'".format(tool.label)
            z = tool.getParameterInfo()
            print "Executing '{0}'".format(tool.label)
            tool.execute(z, None)
        except Exception as e:
            print e


if __name__ == "__main__":
    main()
