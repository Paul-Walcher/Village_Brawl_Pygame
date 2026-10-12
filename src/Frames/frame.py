import pygame
from abc import ABC, abstractmethod
from constants import FrameDataID
from event_queue_manager import EventQueueManager, Event
from widgets.widget import Widget
from clock import Clock

class Frame(EventQueueManager):

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
        self.x = self.frame_dim.x
        self.y = self.frame_dim.y
        self.width = self.frame_dim.width
        self.height = self.frame_dim.height

        self.__event_callbacks = [Frame.CallbackEvent(pygame.QUIT, None, False, lambda e, d: Frame.CallbackEvent.EXIT)]
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

    @property
    def frame_dim(self):
        return self._frame_dim

    @frame_dim.setter
    def frame_dim(self, oframe):

        self.x = oframe.x
        self.y = oframe.y
        self.width = oframe.width
        self.height = oframe.height
        self.center = (self.x + self.width // 2,
                        self.y + self.height // 2
                        )
        self._frame_dim = oframe


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
            for w, pos in widget.get_surfaces_with_position():
                screen.blit(w, pos)


    @abstractmethod
    def tick(self):
        pass

    @abstractmethod
    def render(self, screen):
        pass
