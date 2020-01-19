"""ProSafe OS support"""
import time
import re
from netmiko.cisco_base_connection import CiscoSSHConnection


class NetgearProSafeSSH(CiscoSSHConnection):
    """ProSafe OS support"""

    def __init__(self, **kwargs):
        if kwargs.get("default_enter") is None:
            kwargs["default_enter"] = "\r"
        return super().__init__(**kwargs)

    def session_preparation(self):
        """ProSafe OS requires enabe mode to disable paging."""
        self._test_channel_read()
        self.set_base_prompt()
        self.enable()
        self.disable_paging(command="terminal length 0")

        # Clear the read buffer
        time.sleep(0.3 * self.global_delay_factor)
        self.clear_buffer()

    def check_config_mode(self, check_string="(Config)#"):
        return super().check_config_mode(check_string=check_string)

    def config_mode(self, config_command="configure", pattern=""):
        output = ""
        if not self.check_config_mode():
            output = self.send_command_timing(
                config_command, strip_command=False, strip_prompt=False
            )
            if not self.check_config_mode():
                raise ValueError("Failed to enter configuration mode")
        return output

    def exit_config_mode(self, exit_config="exit", pattern="#"):
        return super().exit_config_mode(exit_config=exit_config, pattern=pattern)

    def save_config(self, save_cmd="write memory", confirm=True, confirm_response=""):
        self.enable()
        """ProSafe doesn't allow saving whilst within configuration mode"""
        if self.check_config_mode():
            self.exit_config_mode()

       """TODO: This operation may take a few minutes.
       Management interfaces will not be available during this time.

       Are you sure you want to save? (y/n)


       Configuration Not Saved!"""


        return super().save_config(
            cmd=save_cmd, confirm=confirm, confirm_response=confirm_response
        )
