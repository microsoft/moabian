# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass
from pymoab import get_joystick_btn, get_joystick_x, get_joystick_y, get_menu_btn


@dataclass
class Event:
    menu_btn: bool = False
    joy_btn: bool = False
    joy_x: float = 0.0
    joy_y: float = 0.0


class IEventListener:
    """
    Mix-in class describing the callback event interface.
    """

    def __init__(self):
        pass

    def on_menu_down(self, sender: object):
        pass

    def on_joy_down(self, sender: object):
        pass

    # continuous
    def on_joy_moved(self, sender: object, x: float, y: float):
        pass

    # discrete navigation flicks
    def on_flick_up(self, sender: object):
        pass

    def on_flick_down(self, sender: object):
        pass

    def on_flick_return(self, sender: object):
        pass


# constants for joystick flick direction
class FlickDir(Enum):
    Unset = 0
    Center = 0
    Up = 1
    Down = 2


class EventDispatcher:
    """
    Dispatches events to event to listeners
    in self.listeners.

    Call dispatch_event() in main loop.
    """

    def __init__(self):
        # ...are you listening?
        self.listeners: List[IEventListener] = []

        # previous event returned from get_next_event
        self.prev_event: Optional[Event] = None

        # last event scanned
        self._last_raw_event: Optional[Event] = None

        # tracked separately from the polled state
        self.flick_threshold = 0.8
        self.flick_dir = FlickDir.Unset

    def _raw_event(self) -> Event:
        return Event(
            get_menu_btn(), get_joystick_btn(), get_joystick_x(), get_joystick_y()
        )

    def get_next_event(self) -> Optional[Event]:
        """
        Watch for changes between current state
        and previous state.

        Returns the next event or None
        """
        # poll the current state of the hardware
        curr_event = self._raw_event()

        # first scan will set previous
        event = None
        if self._last_raw_event is None:
            self.prev_event = curr_event
            self._last_raw_event = curr_event

        # ...not the first event
        elif self._last_raw_event != curr_event:
            self.prev_event = self._last_raw_event
            event = curr_event

        # cache for next time
        self._last_raw_event = curr_event

        return event

    def dispatch_event(self, sender: object, event: Event):
        """
        Watch for changes between current state
        and previous state.

        Dispatch events to all listeners.
        """
        for listener in self.listeners:

            # menu btn press/release
            if event.menu_btn != self.prev_event.menu_btn:
                listener.on_menu_down(sender)

            # joy btn press/release
            if event.joy_btn != self.prev_event.joy_btn:
                listener.on_joy_down(sender)

            # joy moved
            if (
                event.joy_x != self.prev_event.joy_x
                or event.joy_y != self.prev_event.joy_y
            ):
                listener.on_joy_moved(sender, event.joy_x, event.joy_y)

            # dispatch joy flicked
            # flick up
            if event.joy_y > self.flick_threshold:
                if self.flick_dir != FlickDir.Up:
                    self.flick_dir = FlickDir.Up
                    listener.on_flick_up(sender)

            # flick down
            if event.joy_y < -self.flick_threshold:
                if self.flick_dir != FlickDir.Down:
                    self.flick_dir = FlickDir.Down
                    listener.on_flick_down(sender)

            # return to center?
            if (
                event.joy_y > -self.flick_threshold
                and event.joy_y < self.flick_threshold
            ):
                if self.flick_dir != FlickDir.Center:
                    self.flick_dir = FlickDir.Center
                    listener.on_flick_return(sender)
