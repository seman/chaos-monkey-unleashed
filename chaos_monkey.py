# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.
from chaos import (
    kill,
    net
)

__metaclass__ = type


class ChaosMonkey:
    """Runs chaos monkey commands."""

    def __init__(self, chaos, factory_obj):
        self.chaos = chaos
        self.factory_obj = factory_obj

    @classmethod
    def factory(cls):
        all_chaos, factory_obj = ChaosMonkey.get_all_chaos()
        return cls([], factory_obj)

    @staticmethod
    def get_all_chaos():
        """Get all Chaos Monkey available commands."""
        all_chaos = []
        all_factory_obj = []
        factories = [net.Net.factory, kill.Kill.factory]
        for factory in factories:
            factory_obj = factory()
            all_factory_obj.append(factory_obj)
            all_chaos.extend(factory_obj.get_chaos())
        return all_chaos, all_factory_obj

    def include_group(self, groups):
        """Select the specified groups from all available groups."""
        if not groups:
            return
        all_chaos, _ = ChaosMonkey.get_all_chaos()
        if groups == 'all':
            self.chaos = all_chaos
            return
        self.chaos = self.get_groups(groups, all_chaos)

    def exclude_group(self, groups):
        """Exclude the specified groups from the selected groups."""
        excluded_groups = self.get_groups(groups, self.chaos)
        for group in excluded_groups:
            self.chaos.remove(group)

    @staticmethod
    def get_all_groups():
        """Return all available groups."""
        return list(set(c.group for c in ChaosMonkey.get_all_chaos()[0]))

    @staticmethod
    def get_all_commands():
        """Return all available command."""
        return [c.command_str for c in ChaosMonkey.get_all_chaos()[0]]

    @staticmethod
    def get_groups(groups, chaos):
        """Return selected group from available groups."""
        ret_groups = []
        for group in groups:
            ret_groups.extend([c for c in chaos if c.group == group])
        return ret_groups

    def include_command(self, commands):
        """Select the specified commands from all available commands."""
        all_chaos, _ = ChaosMonkey.get_all_chaos()
        included_commands = [x for x in all_chaos if x.command_str in commands]
        for cmd in included_commands:
            if not self._find_command(self.chaos, cmd.command_str):
                self.chaos.extend(included_commands)

    def exclude_command(self, commands):
        """Exclude the specified commands from the selected commands."""
        excluded_commands = (
            [x for x in self.chaos if x.command_str in commands])
        for cmd in excluded_commands:
            self.chaos.remove(cmd)

    @staticmethod
    def _find_command(chaos, command_str):
        """Find a chaos by command string."""
        for item in chaos:
            if item.command_str == command_str:
                return item
        return None

    def reset_command_selection(self):
        self.chaos = []
