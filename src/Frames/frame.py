from __future__ import annotations
from typing import Callable, Any

import pygame
from abc import ABC, abstractmethod
from event_queue_manager import EventQueueManager, Event
from clock import Clock
from constants import R_ID
from Frames.frame_enums import FrameEnums
"""
Type definitions.
"""
type event_callback_result_t = int
type event_callback_t = Callable[ [pygame.event.Event, Any],  event_callback_result_t]

class Frame(EventQueueManager):

    """
    This class is the basic framework for a shown window instance.

    It has an internal rectangle defined as frame_dim, which
    specifies the rectangle in which it operates in (its window size).

    The internal rectangles x, y, width and height are separately stored as
    class varriables.

    IMPORTANT: Do not change a frames frame_dim by doing frame_dim.x = ...,
    because internal x, y, width and height and frame_dim are adjusted using setter
    methods.

    Each frame can also have a parent frame. If this class is discontinued using raise_exit_flag(),
    and the parent frames focus group is the same as this classes', the parent frame will receive the focus.

    About focus groups:

    A focus group is an identifier of the group the frame belongs to.
    Inside this group, only one frame can have the focus at one time.

    You can check if you have the focus using Frame.is_focused,
    and focus as well as unfocus using Frame.focus and Frame.unfocus().

    If you dont pass an argument for the focus group to the constructor,
    the frame will be assigned to a standard focus group.
    You should bind input received for the frame using bind_events().
    Whenever focus changes for an event, all event_callbacks are cleared,
    and Frame.bind_events is called. There you can bind callbacks depending on whether
    you have the focus or not.

    A frame handles pygame events by using Frame.manage_pygame_events in Frame.tick.
    You can register event callbacks using Frame.add_pygame_key_callback or
    Frame.add_pygame_event_callback.
    """

    STANDARD_FOCUS_GROUP: str = "STANDARD FOCUS GROUP"
    """
    The standard focus group.
    """
    FOCUS_GROUPS: dict[str, Frame] = {}
    """
    Class internal dict of focus groups.
    The keys are the names for the focus group,
    and each key has a frame as a value, being
    the reference to the frame that currently has the focus
    in this group (key).
    """

    class EventCallback(Event):

        """
        Class for a callback event.

        This class is callable, and executes the function
        with the data given to the constructor.

        The callback function receives two arguments:
        event: the pygame.event.Event reference,
        data: the data given to this class in the constructor.

        The callback function should return 1 of the following 3 enums:

        EventCallback.EXIT: signals to the frame processing the callback event
                            to call raise_exit_flag(), and this way end the frame's activity.
                            This will lead to the event being consumed.

        EventCallback.FAILURE:  Signals that the callback function was not able to
                                handle the event. This leads to the event not being consumed.

        EventCallback.SUCCESS:  Signals the event was successfully handled.
                                This will lead to the event being consumed.

        if EventCallback.putback == True, the event will be not consumed by this callback
        regardless of the return value
        """

        EXIT = R_ID()
        FAILURE = R_ID()
        SUCCESS = R_ID()

        def __init__(self, type: int, data: Any, putback: bool, func: event_callback_t):

            self.putback: bool = putback
            """
            If putback == True, this event callback won't consume the event.
            """
            self.func: event_callback_t = func
            """
            The function executed when this class is called.
            """
            super().__init__(type, data)

        def __call__(self, event: pygame.event.Event) -> event_callback_result_t:
            """
            Executes the callback function with the event and this classes' data.
            """
            return self.func(event, self.data)

    def __init__(       self,
                        frame_enum: FrameEnums,
                        data: Any = None,
                        frame_dim: pygame.Rect = None,
                        parent_frame: Frame = None,
                        max_parent_frames: int = 10,
                        focus_group: str = "",
                        has_focus: bool = True
                ):

        EventQueueManager.__init__(self)

        self.frame_enum: FrameEnums = frame_enum
        """
        Identifier for the Frame.
        """
        self.data: Any = (data if data is not None else {})
        """
        The internal data, meant to be passed on to other frames.
        """
        self._frame_dim: pygame.Rect = (frame_dim if frame_dim is not None else pygame.Rect(0, 0, 0, 0))
        """
        Protected frame dimension, changing the frame dimension adjust
        x, y, width and height.
        """
        self._x: int = self._frame_dim.x
        """
        x position of this frame.
        """
        self._y: int = self._frame_dim.y
        """
        y position of this frame.
        """
        self._width: int = self._frame_dim.width
        """
        width of this frame.
        """
        self._height: int = self._frame_dim.height
        """
        height of this frame.
        """
        self.focus_group: str = focus_group
        """
        The focus group this frame belongs to.
        """
        if not self.focus_group and self.focus_group is not None:
            self.focus_group = Frame.STANDARD_FOCUS_GROUP

        self.__event_callbacks: list[event_callback_t] = []
        """
        Private list of all event callbacks pertaining to this frame.
        """
        self.__exit_flag_raised: bool = False
        """
        If this flag is raised, the frame is set to exit and give control to another frame.
        """
        self.__disabled_keys: dict[int, bool] = {}
        """
        saves the keys that are currently disabled,
        meaning the event callbacks pertaining to the key x wont be called if
        self.__disabled_keys[x] = True
        """
        self.parent_frame: Frame = parent_frame
        """
        Reference to the frame that instantiated this frame, or is considered
        the higher frame in the hierarchy
        """
        self.max_parent_frames: int = max_parent_frames
        """
        Number of parent frames saved before the cutoff.
        This is done to free memory by discarding old frames.
        """
        self._parent_frame_list: list[Frame] = []
        """
        List of parent frames.
        """
        self.__prune_parent_frames()

        self.center: tuple[int, int] = (self.frame_dim.x + self.frame_dim.w // 2,
                        self.frame_dim.y + self.frame_dim.h // 2
                        )
        """
        The center of this frame.
        """
        self.__key_scancodes: dict[int, bool] = {}
        """
        Saves which keys are currently pressed.
        self.__key_scancodes[key] == True if the key is currently pressed.
        To check whether a key is pressed or not, use Frame.key_pressed(key),
        since not all scancodes might be contained as keys in __key_scancodes.
        """
        self._next_frame: Frame = None
        """
        The next frame returned by tick() after
        self.exit_flag_raised() == True.
        """

        self.bind_events()
        #binding events

        if has_focus:
            self.focus()
        """
        has_focus indicates if the frame receives the focus
        in its group upon instantiation.
        """



    @property
    def frame_dim(self):
        return self._frame_dim

    @frame_dim.setter
    def frame_dim(self, oframe):

        self._x = oframe.x
        self._y = oframe.y
        self._width = oframe.width
        self._height = oframe.height

        #those set the x, y, w, h

        self.center = (self._x + self._width // 2,
                        self._y + self._height // 2
                        )

        self._frame_dim = oframe.copy()

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        self.frame_dim = pygame.Rect(val, self.y, self.width, self.height)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self.frame_dim = pygame.Rect(self.x, val, self.width, self.height)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, val):
        pre_w = self.width
        self.frame_dim = pygame.Rect(self.x, self.y, val, self.height)
        if pre_w != self.width:
            self.rerender()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, val):
        pre_h = self.height
        self.frame_dim = pygame.Rect(self.x, self.y, self.width, val)
        if pre_h != self.height:
            self.rerender()


    def __prune_parent_frames(self) -> None:
        """
        This constructs the parent frame list.
        Then if the list is bigger that Frame.max_parent_frames,
        the oldest frames will be cutoff and cleaned up
        by the garbage collector.
        """
        if self.parent_frame is not None:
            self._parent_frame_list.insert(0, self.parent_frame)
            self._parent_frame_list.extend(self.parent_frame._parent_frame_list)

        if len(self._parent_frame_list) > self.max_parent_frames:
            self._parent_frame_list = self.__cutoff_parent_frames(self, self.max_parent_frames)

    def __cutoff_parent_frames(self, cframe: Frame, pindex: int) -> list[Frame]:
        """
        Cuts off the oldest frames, and removes them from memory.
        Returns the modified _parent_frame_list for the frame that called
        this function to adopt.
        """
        if cframe.parent_frame is None:
            return []
        if pindex == 0:
            cframe.parent_frame = None
            cframe._parent_frame_list = []
            return cframe._parent_frame_list.copy()
        else:
            back_list = self.__cutoff_parent_frames(cframe.parent_frame, pindex-1)
            cframe._parent_frame_list = [cframe.parent_frame] + back_list

            return cframe._parent_frame_list.copy()



    """
    The following 2 methods are callback functions,
    that are called when the own focus gets either lost or gained
    """

    def on_focus_gained(self) -> None:
        """
        Callback function for when this frame gains focus.
        """
        pass

    def on_focus_lost(self) -> None:
        """
        Callback function for when this frame looses focus.
        """
        pass


    def move_by(self, x: int = 0, y:int = 0, w: int = 0, h: int = 0) -> None:
        """
        Moves this frame by the given offsets.
        """
        #Moves the own frame dimension by the offsets
        nframe = pygame.Rect(self.x + x, self.y, self.width + w, self.height + h)
        self.frame_dim = nframe

    def offset_frame(self, frame_offsets: pygame.Rect) -> None:
        """
        Moves this frame by applying: self.frame_dim += frame_offsets.
        """

        nframe = pygame.Rect(self.x + frame_offsets.x, self.y + frame_offsets.y,
                            self.width + frame_offsets.width, self.height + frame_offsets.height
                            )

        self.frame_dim = nframe

    def move_to(self, x: int = None, y: int = None, w: int = None, h: int = None) -> None:
        """
        Sets the frame_dim to the provided values,
        if the value is None the old value is used.
        """
        r = pygame.Rect((x if x is not None else self.x),
                        (y if y is not None else self.y),
                        (w if w is not None else self.width),
                        (h if h is not None else self.height))

        self.frame_dim = r

    def _on_focus_changed(self) -> None:
        """
        Internal function, this function calls
        the on_focus_gained and on_focus_lost
        callback functions after clearing the event callbacks,
        and rebinding the events via self.bind_events().
        """

        self.clear_event_callbacks()
        self.bind_events()
        if self.is_focused():
            self.on_focus_gained()
        else:
            self.on_focus_lost()



    def focus(self) -> None:
        """
        Gives this frame the focus for its
        focus group.
        """
        if self.focus_group is None:
            return

        if self.focus_group not in Frame.FOCUS_GROUPS:
            Frame.FOCUS_GROUPS[self.focus_group] = None

        pre = Frame.FOCUS_GROUPS[self.focus_group]
        Frame.FOCUS_GROUPS[self.focus_group] = self

        if pre != self:
            if pre is not None:
                pre._on_focus_changed()
            self._on_focus_changed()


    def unfocus(self) -> None:
        """
        Takes the focus from this frame.
        If this frame had the focus, and the parent frame has the same focus group as this frame,
        the parent frame will receive the focus via parent_frame.focus().
        """
        if self.focus_group is not None and self.focus_group in Frame.FOCUS_GROUPS and Frame.FOCUS_GROUPS[self.focus_group] == self:
            pre = Frame.FOCUS_GROUPS[self.focus_group]
            Frame.FOCUS_GROUPS[self.focus_group] = None

            if pre == self:
                self._on_focus_changed()

            if self.parent_frame is not None and self.parent_frame.focus_group == self.focus_group:
                self.parent_frame.focus()

    def is_focused(self) -> bool:
        """
        Returns True if this frame currently has the focus in its group, else False.
        If self.focus_group is None, True is returned, since a frame not belonging
        to a focus group is always focused.
        """
        if self.focus_group is None:
            return None

        if self.focus_group not in Frame.FOCUS_GROUPS:
            return False

        return (Frame.FOCUS_GROUPS[self.focus_group] == self)

    def bind_events(self) -> None:
        """
        This is called in the constructor and every time this frames
        focus changes. Make event bindings dependent on self.is_focused().
        """
        pass

    def key_pressed(self, scancode: int) -> bool:
        """
        Returns if the key belonging to the scancode is currently pressed.
        If the key is disabled, this is always False.
        """
        if scancode not in self.__key_scancodes or self.pygame_key_is_disabled(scancode):
            return False
        else:
            return self.__key_scancodes[scancode]

    def add_default_escape_callback(self) -> None:
        """
        This adds a generic callback function, that returns EventCallback.EXIT
        on pressing enter.
        """
        self.add_pygame_key_callback(pygame.K_ESCAPE, {}, False, lambda e, d: Frame.EventCallback.EXIT, key_delay=0)

    def manage_pygame_events(self) -> None:
        """
        Manages the events, by going through all
        events in the pygame.event.Event queue.
        Should be called in tick().
        triggers the event_callbacks in self.__event_callbacks
        added via self.add_pygame_key_callback or self.add_pygame_event_callback
        if the callback has putback == True, the event stays in the queue
        for the next event check
        """

        putback_events = []

        for event in pygame.event.get():
            processed = True
            matched_any = False

            if event.type == pygame.KEYDOWN:

                if event.key not in self.__key_scancodes:
                    self.__key_scancodes[event.key] = True

                self.__key_scancodes[event.key] = True

            if event.type == pygame.KEYUP:

                if event.key not in self.__key_scancodes:
                    self.__key_scancodes[event.key] = False

                self.__key_scancodes[event.key] = False

            for ecallback in self.__event_callbacks:

                # First, always match the event type.
                if event.type != ecallback.type:
                    continue

                # Then, filter key-specific callbacks.
                if event.type == pygame.KEYDOWN:

                    if (
                        ecallback.data is not None
                        and "key" in ecallback.data
                        and event.key != ecallback.data["key"]
                    ):
                        continue

                matched_any = True

                res = ecallback(event)

                if res == Frame.EventCallback.EXIT:
                    #setting exit frame to None
                    self._exit_frame = None
                    self.raise_exit_flag()

                if res == Frame.EventCallback.FAILURE:
                    processed = False

                if ecallback.putback:
                    processed = False

            if not processed or not matched_any:
                putback_events.append(event)

        for event in putback_events:
            pygame.event.post(event)


    def clear_event_callbacks(self) -> None:
        """
        Clears the event callback functions.
        """
        #removes all event callbacks
        self.__event_callbacks = []

    def clear_pygame_events(self) -> None:
        """
        Empties the pygame.event queue.
        """
        #clears the pygame.event queue
        events = pygame.event.get()

    def get_event_callbacks(self) -> None:
        """
        Returns a copy of the stored event callbacks.
        The contents of the list are references of the store
        EventCallback classes, so changes to those references
        change the EventCallback instances in self.__event_callbacks.
        """
        return self.__event_callbacks.copy()

    def add_pygame_event_callback(self, type: int, data: Any, putback: bool, func: event_callback_t) -> Frame.EventCallback:
        """
        adds a EventCallback class into self.__event_callbacks.
        See Frame.EventCallback.
        Returns the created EventCallback.
        """

        cb = Frame.EventCallback(type, data, putback, func)
        self.__event_callbacks.append(cb)
        return cb

    def remove_pygame_event_callback(self, cb: Frame.EventCallback) -> bool:
        """
        Tries to remove the event callback from the event_callback queue.
        Returns True of the event callback was successfully removed, else False.
        """
        try:
            self.__event_callbacks.remove(cb)
            return True
        except:
            return False

    def pygame_key_is_disabled(self, key: int) -> bool:
        """
        returns if a key is currently disabled
        """
        if key not in self.__disabled_keys:
            return False
        else:
            return self.__disabled_keys[key]

    def disable_pygame_key(self, key: int) -> None:
        """
        Disables a key for the event callbacks
        """
        self.__disabled_keys[key] = True

    def enable_pygame_key(self, key) -> None:
        """
        enables the key for the event callbacks
        """
        self.__disabled_keys[key] = False

    def __key_callback_wrapper( self,
                                event: pygame.event.Event,
                                key: int,
                                data: Any,
                                putback: bool,
                                func: event_callback_t,
                                key_delay: float
                                ) -> event_callback_result_t:

        """
        Wrapper function for a event callback added using
        self.add_pygame_key_callback().
        """

        # This callback should only receive matching KEYDOWN events.
        if event.type != pygame.KEYDOWN or event.key != key:
            return Frame.EventCallback.FAILURE

        if self.pygame_key_is_disabled(key):
            #if the key is disabled, return SUCCESS for event consumption.
            return Frame.EventCallback.SUCCESS

        if data["clock"].elapsed() <= key_delay:
            #if not enough time elapsed for another keypress to be registered,
            #consume the event with a SUCCESS notification.
            return Frame.EventCallback.SUCCESS

        back = func(event, data)
        data["clock"].start()

        if back is None:
            return Frame.EventCallback.SUCCESS

        return back

    def add_pygame_key_callback(self, key: int, data: Any, putback: bool, func: event_callback_t, key_delay: float = 100) -> Frame.EventCallback:
        """
        Adds a callback for a pygame.KEYDOWN event with event.key == key.
        Returns the created EventCallback.

        key_delay is the time in milliseconds that needs to pass before this callback can be
        called again.
        """
        if data is None:
            data = {}
        else:
            data = data.copy()
        data["clock"] = Clock()
        data["clock"].start()
        data["key"] = key

        cb = Frame.EventCallback(pygame.KEYDOWN, data, putback, lambda event, d: self.__key_callback_wrapper(event, key, d, putback, func, key_delay))
        self.__event_callbacks.append(cb)
        return cb


    def raise_exit_flag(self) -> None:
        """
        Sets the exit flag, and gives the focus to
        self.parent_frame if self.parent frame is a Frame instance.
        """
        self.__exit_flag_raised = True
        self.unfocus()

    def reset_exit_flag(self) -> None:
        """
        Resets the exit flag, and makes this frame usable again.
        """
        self.__exit_flag_raised = False

    def exit_flag_raised(self) -> bool:
        """
        For checking if the exit flag is raised.
        """
        return self.__exit_flag_raised


    def tick(self) -> Frame:
        """
        This function is important, it should be called on every frame in the game.
        It returns a reference to the frame that should be the main frame rendered.
        If it returns None, this signals the frame is set to be deleted.
        """

        self.manage_pygame_events()

        if self.exit_flag_raised():
            if self._next_frame is not None:
                self._next_frame.focus()

            return None

        return self

    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """
        Renders this frame onto the given surface.
        Is called once per frame.
        """
        pass

    def rerender(self) -> None:
        """
        Can be called upon reentry into this frame.
        This function should prepare the frame and adopt changes
        made to it.
        This should e.g. cancel animations, reset the state...,
        and should also clear the exit flag.
        """
        pass
