import pygame
from abc import ABC, abstractmethod
from constants import FrameDataID
from event_queue_manager import EventQueueManager, Event
from clock import Clock

class Frame(EventQueueManager):

    class SlideHandler:

        def __init__(self, x_offset, y_offset, slide_positions, slide_duration=800):

            self.x_offset = x_offset
            self.y_offset = y_offset

            self.slide_start_positions = slide_positions.copy()
            self.current_slide_positions = slide_positions.copy()

            self.slide_duration = slide_duration
            self.clock = Clock()

            self.time_passed = 0

            self.is_sliding = False

        def reset_slide(self):
            self.is_sliding = False
            self.time_passed = 0

        def start_slide(self):

            self.clock.start()
            self.is_sliding = True

        def stop_slide(self):

            self.time_passed += self.clock.elapsed()
            self.is_sliding = False

        def tick(self):

            if self.is_sliding:
                percentage = (self.clock.elapsed() + self.time_passed) / self.slide_duration

                new_pos = []

                for x, y in self.slide_start_positions:

                    new_pos.append((x + int(self.x_offset * percentage), y + int(self.y_offset * percentage)))

                self.current_slide_positions = new_pos

        def positions(self):
            return self.current_slide_positions.copy()



    class CallbackEvent(Event):

        EXIT = 0
        FAILURE = 1
        SUCCESS = 2

        def __init__(self, type, data, putback, func):
            self.putback = putback
            self.func = func
            super().__init__(type, data)

        def __call__(self, event):
            return self.func(event, self.data)

    class EventTypes:
        #event types
        EXIT_FRAME = 0 #signal to exit the current frame
        EXIT_PARENT_FRAME = 1

    def __init__(self, frame_enum, data=None, frame_dim=None, parent_frame=None, max_parent_frames=10):

        self.frame_enum = frame_enum
        self.data = (data if data is not None else {})
        if self.data is not None:
            self.data[FrameDataID.CURRENT_FRAME] = self
        self._frame_dim = (frame_dim if frame_dim is not None else pygame.Rect(0, 0, 0, 0))
        self._x = self.frame_dim.x
        self._y = self.frame_dim.y
        self._width = self.frame_dim.width
        self._height = self.frame_dim.height

        self.slide_endpos = None
        self.slide_startpos = None

        self._has_focus = True

        self.__event_callbacks = []
        self.__exit_flag_raised = False
        self.__disabled_keys = {}

        self.parent_frame = parent_frame
        self.max_parent_frames = max_parent_frames
        self.parent_frame_list = []
        if self.parent_frame is not None:
            self.parent_frame_list.insert(0, self.parent_frame)
            self.parent_frame_list.extend(self.parent_frame.parent_frame_list)

        if len(self.parent_frame_list) > self.max_parent_frames:
            self.__cutoff_parent_frames(self, self.max_parent_frames)
            self.parent_frame_list = self.parent_frame_list[:self.max_parent_frames]

        self.event_queue = []

        self.center = (self.frame_dim.x + self.frame_dim.w // 2,
                        self.frame_dim.y + self.frame_dim.h // 2
                        )

        self.widgets = [] #own widgets

        #adding escape key
        self.add_pygame_key_callback(pygame.K_ESCAPE, {}, False, lambda e, d: Frame.CallbackEvent.EXIT, key_delay=0)

        self.bind_events()

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



    @property
    def has_focus(self):
        return self._has_focus

    @has_focus.setter
    def has_focus(self, x):
        if x != self._has_focus:
            self._has_focus = x
            self.clear_event_callbacks()
            self.add_pygame_key_callback(pygame.K_ESCAPE, {}, False, lambda e, d: Frame.CallbackEvent.EXIT, key_delay=0)
            self.bind_events()
            if self._has_focus:
                self.on_focus_gained()
            else:
                self.on_focus_lost()

    def on_focus_gained(self):
        pass

    def on_focus_lost(self):
        pass

    def move_by(self, x=0, y=0, w=0, h=0):

        nframe = pygame.Rect(self.x + x, self.y, self.width + w, self.height + h)
        self.frame_dim = nframe

    def move_to(self, x=None, y=None, w=None, h=None):

        r = pygame.Rect((x if x is not None else self.x),
                        (y if y is not None else self.y),
                        (w if w is not None else self.width),
                        (h if h is not None else self.height))

        self.frame_dim = r

    def focus(self):
        self.has_focus = True

    def unfocus(self):
        self.has_focus = False

    def bind_events(self):
        pass

    def manage_pygame_events(self):

        putback_events = []

        for event in pygame.event.get():
            processed = True
            matched_any = False

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

                if res == Frame.CallbackEvent.EXIT:
                    self.__exit_flag_raised = True

                if res == Frame.CallbackEvent.FAILURE:
                    processed = False

                if ecallback.putback:
                    processed = False

            if not processed or not matched_any:
                putback_events.append(event)

        for event in putback_events:
            pygame.event.post(event)


    def clear_event_callbacks(self):
        self.__event_callbacks = []

    def clear_pygame_events(self):
        events = pygame.event.get()

    def get_event_callbacks(self):
        return self.__event_callbacks.copy()

    def add_pygame_event_callback(self, type, data, putback, func):

        cb = Frame.CallbackEvent(type, data, putback, func)
        self.__event_callbacks.append(cb)
        return cb

    def remove_pygame_event_callback(self, cb):

        try:
            self.__event_callbacks.remove(cb)
            return True
        except:
            return False

    def pygame_key_is_disabled(self, key):
        if key not in self.__disabled_keys:
            return False
        else:
            return self.__disabled_keys[key]

    def disable_pygame_key(self, key):
        self.__disabled_keys[key] = True

    def enable_pygame_key(self, key):
        self.__disabled_keys[key] = False

    def __key_callback_wrapper(self, event, key, data, putback, func, key_delay):

        if event.type == pygame.KEYDOWN and data["clock"].elapsed() > key_delay and event.key == key and not self.pygame_key_is_disabled(key):
            back = func(event, data)
            data["clock"].start()
            if back is None:
                return Frame.CallbackEvent.SUCCESS
            else:
                return back

        else:
            return Frame.CallbackEvent.FAILURE

    def add_pygame_key_callback(self, key, data, putback, func, key_delay=300):#ms
        if data is None:
            data = {}
        else:
            data = data.copy()
        data["clock"] = Clock()
        data["clock"].start()
        data["key"] = key

        cb = Frame.CallbackEvent(pygame.KEYDOWN, data, putback, lambda event, d: self.__key_callback_wrapper(event, key, d, putback, func, key_delay))
        self.__event_callbacks.append(cb)
        return cb


    def exit_flag_raised(self):
        return self.__exit_flag_raised


    def __cutoff_parent_frames(self, pindex):

        if self.parent_frame is None:
            return
        if pindex == 0:
            self.parent_frame = None
        else:
            self.__cutoff_parent_frames(self.parent_frame, pindex-1)

    def set_parent_frame(self, pframe):
        self.parent_frame = pframe

    def offset_frame(self, frame_offsets):

        nframe = pygame.Rect(self.x + frame_offsets.x, self.y + frame_offsets.y,
                            self.width + frame_offsets.width, self.height + frame_offsets.height
                            )

        self.frame_dim = nframe

    def widgets_tick(self):
        for w in self.widgets:
            w.tick()

    def render_widgets(self, screen):
        for widget in self.widgets:
            widget.render(screen)

    #called when the image size changes
    def rerender(self):
        pass

    @abstractmethod
    def tick(self):
        pass

    @abstractmethod
    def render(self, screen):
        pass
