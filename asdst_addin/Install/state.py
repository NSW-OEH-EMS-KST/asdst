# state.py
from config import SystemConfig, MapConfig, UserConfig, AsdstDataConfig

# SEND_STATE_EVENT = None


# def send_state_event(event):
#
#     extension.state.on_event(event=event)
#
#     return


# Base state

class State(object):
    """
    A state object with some utility functions for the individual states within the state machine.
    """

    def __init__(self, machine):
        print 'Current state:', str(self)

        self.machine = machine

        return

    def on_event(self, event):
        """
        Handle events that are delegated to this State.
        """
        pass

    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.
        """
        return self.__str__()

    def __str__(self):
        """
        Returns the name of the State.
        """
        return self.__class__.__name__


# Start of our states

class InvalidSystem(State):
    """
    The state which indicates that the system is not correctly configured or installed.
    """

    def on_event(self, event):
        print "InvalidSystem.on_event {}".format(event)

        if event in ["startup", "newDocument", "openDocument"]:
            if self.machine.system_config.valid:
                return InvalidUserConfig(self.machine).on_event(event)

        return self


# class ValidSystem(State):
#     """
#     The state which indicates that there are limited device capabilities.
#     """
#
#     def on_event(self, event):
#         print "ValidSystem.on_event {}".format(event)
#
#         if event == "startup":
#             if self.machine.user_config.valid:
#                 return ValidUserConfig(self.machine).on_event("startup")
#         else:
#             return InvalidUserConfig(self.machine)
#
#         return self


class InvalidUserConfig(State):
    """
    The state which indicates that the system is not correctly configured or installed.
    """

    def on_event(self, event):
        print "InvalidUserData.on_event {}".format(event)

        if event in ["startup", "newDocument", "openDocument", "user_config_updated"]:
            self.machine.user_config.validate()
            if self.machine.user_config.valid:
                return InvalidMap(self.machine).on_event(event)

        return self


# class ValidUserConfig(State):
#     """
#     The state which indicates that there are limited device capabilities.
#     """
#
#     def on_event(self, event):
#         if event in ["startup", "newDocument", "openDocument"]:
#             self.machine.map_config.validate()
#             if self.machine.map_config.valid:
#                 return ValidMap(self.machine).on_event(event=event)
#             else:
#                 return InvalidMap(self.machine)
#
#         return self


class InvalidMap(State):
    """
    The state which indicates that there are limited device capabilities.
    """

    def on_event(self, event):
        if event in ["startup", "newDocument", "openDocument", "itemAdded"]:
            self.machine.map_config.validate()
            if self.machine.map_config.valid:
                return InvalidAsdstData(self.machine).on_event(event)

        return self


# class ValidMap(State):
#     """
#     The state which indicates that there are limited device capabilities.
#     """
#
#     def on_event(self, event):
#         if event in ["newDocument", "openDocument"]:
#             self.machine.map_config.validate()
#             if self.machine.map_config.valid:
#                 return self
#             else:
#                 return InvalidMap(self.machine)
#
#         if event == 'asdst_data_built':
#             self.machine.asdst_data_config.validate()
#             if self.machine.asdst_data_config.valid:
#                 return ValidAsdstData(self.machine)
#             else:
#                 return InvalidAsdstData(self.machine)
#
#         return self


class InvalidAsdstData(State):
    """
    The state which indicates that everything is in place for project ASDST data to be built
    """

    def on_event(self, event):
        if event == "itemDeleted":
            self.machine.map_config.validate()
            if not self.machine.map_config.valid:
                return InvalidMap(self.machine)

        if event in ["startup", "newDocument", "openDocument", "asdst_data_built"]:
            self.machine.asdst_data_config.validate()
            if self.machine.asdst_data_config.valid:
                return ValidAsdstData(self.machine)

        return self


class ValidAsdstData(State):
    """
    The state which indicates that evrything is ready to go for context calcs
    """

    def on_event(self, event):
        if event in ["newDocument", "openDocument"]:
            return InvalidMap(self.machine).on_event(event)

        return self

# End of our states.


# State Machine

class ProjectStateMachine(object):
    """
    A simple state machine that mimics the functionality of a device from a high level.
    """

    def __init__(self, extension):

        self.extension = extension
        self.system_config = SystemConfig()
        self.map_config = MapConfig()
        self.user_config = UserConfig()
        self.asdst_data_config = AsdstDataConfig(self.user_config.asdst_gdb)

        # Start with a default state.
        self.state = InvalidSystem(self)

        return

    def on_event(self, event):
        """
        This is the bread and butter of the state machine. Incoming events are delegated to the given states which then handle the event.
        The result is then assigned as the new state.
        """
        print "ProjectStateMachine.on_event {}".format(event)

        initial_state = str(self.state)

        if event == "startup":
            initial_state = "default"
            self.state = InvalidSystem(self)

        # The next state will be the result of the on_event function.
        self.state = self.state.on_event(event)

        if initial_state != str(self.state):
            print "state change: {} -> {}".format(initial_state, self.state)
            self.extension.enable_tools()

        return

        # if event == "user_config_update":
        #     self.user_config.validate()
        #     # self.state = InvalidSystem(self)
        #
        # if event in ["newDocument", "openDocument"] and self.system_config.valid:
        #     self.state = ValidSystem(self)

    def get_state_report(self):
        """
        Return a nicely formatted status report
        """

        return u"Current state: {}\n\n{}\n{}\n{}\n{}".format(self.state, self.system_config.get_status_pretty(),
                                                             self.user_config.get_status_pretty(),
                                                             self.map_config.get_status_pretty(),
                                                             self.asdst_data_config.get_status_pretty())
