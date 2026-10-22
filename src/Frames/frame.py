import pygame
from abc import ABC, abstractmethod
from constants import FrameDataID
from event_queue_manager import EventQueueManager, Event
from clock import Clock

class Frame(EventQueueManager):

    STANDARD_FOCUS_GROUP = "STANDARD FOCUS GROUP"
    FOCUS_GROUPS = {}

    class SlideHandler:

        def __init__(self, x_offset, y_offset, slide_positions, slide_duration=800):

            #x offset is the amount to slide horizontally,
            #y offset the amount to slide vertically
            #x_offset, y_offset = target_pos - current_pos
            self.x_offset = x_offset
            self.y_offset = y_offset

            #positions is a list of p(x, y),
            #each representing the position of an object.
            #each index in self.current_slide_positions
            #corresponds to the position in the same index in slide_positions
            self.slide_start_positions = slide_positions.copy()
            self.current_slide_positions = slide_positions.copy()

            #slide duration is in ms
            self.slide_duration = slide_duration
            self.clock = Clock()

            #for saving time that has passed when the slide is paused.
            self.time_passed = 0

            #status, if it is sliding or not
            self.is_sliding = False

            #slide needs to be started using start_slide()

        def reset_slide(self):
            #resets the slide
            self.is_sliding = False
            self.time_passed = 0

        def start_slide(self):

            #needs to be called to start, at the beginning or after a pause
            self.clock.start()
            self.is_sliding = True

        def stop_slide(self):

            #stops the slide, but keeps the progress
            self.time_passed += self.clock.elapsed()
            self.is_sliding = False

        def tick(self):

            #needs to be called in another frame tick function

            if self.is_sliding:
                percentage = (self.clock.elapsed() + self.time_passed) / self.slide_duration

                new_pos = []

                for x, y in self.slide_start_positions:

                    new_pos.append((x + int(self.x_offset * percentage), y + int(self.y_offset * percentage)))

                self.current_slide_positions = new_pos

        def positions(self):
            #returns the adjusted positions
            return self.current_slide_positions.copy()



    class CallbackEvent(Event):

        EXIT = 0
        FAILURE = 1
        SUCCESS = 2

        def __init__(self, type, data, putback, func):
            #type is a pygame event.type enum, like pygame.KEYDOWN or pygame.TEXT_INPUT
            #data is the data given to the function
            #if putback == True, the pygame event gets but back into the event queue
            #func is the function that is called. The function gets the pygame event and the data
            self.putback = putback
            self.func = func
            super().__init__(type, data)

        def __call__(self, event):
            return self.func(event, self.data)

    class EventTypes:
        #event types
        EXIT_FRAME = 0 #signal to exit the current frame
        EXIT_PARENT_FRAME = 1

    def __init__(self,
                        frame_enum, #the identifier for the frame, typically specified in frame_enums.py
                        data=None, #the data passed from other frames
                        frame_dim=None, #the pygame.Rect that describes the area in which the frame operates
                        parent_frame=None, #the frame that instantiated this frame. If the previous frame wont be used, None is apt.
                        max_parent_frames=10,   #since each parent_frame also keeps its parent_frame in memory,
                                                #the frames in memory keep piling up.
                                                #if max_parent_frames in memory is reached,
                                                #the oldest frame is deleted by cutting it off in the follow up frame
                                                #that has it as its parent_frame

                        focus_group="",       #a string identifying the focus group this frame belongs to.
                                                #there can only be one frame that has the focus in each focus group

                        has_focus=True          #if the frame should start out with focus after being created.
                                                #this takes the focus from the currently focused frame in the same
                                                #focus group away
                ):


        #identifier
        self.frame_enum = frame_enum
        #passed on data
        self.data = (data if data is not None else {})
        #frame dimensions. if this variable is changed, x, y, width and height are as well
        self._frame_dim = (frame_dim if frame_dim is not None else pygame.Rect(0, 0, 0, 0))
        #changing any of the following variables changes self._frame_dim as well
        self._x = self.frame_dim.x
        self._y = self.frame_dim.y
        self._width = self.frame_dim.width
        self._height = self.frame_dim.height

        #the focus group this frame is assigned to
        self.focus_group = focus_group
        if not self.focus_group:
            self.focus_group = Frame.STANDARD_FOCUS_GROUP

        #indicates if the frame has the focus in its group
        #this variable should be changed using
        #self.has_focus = x
        #or self.focus(), self.unfocus()
        #since this class handles the focus group
        self._has_focus = not has_focus
        self.has_focus = has_focus

        #the event callbacks that used in self.manage_pygame_events()
        self.__event_callbacks = []
        #if this flag is raised, the frame should return None in the tick method
        #to indicate the frame should be deleted
        self.__exit_flag_raised = False
        #saves the keys that are currently enabled,
        #meaning the event callbacks pertaining to the key x wont be called if
        #self.__disabled_keys[x] = False
        self.__disabled_keys = {}

        #reference to the frame that instantiated this frame
        self.parent_frame = parent_frame
        #frame cutoff
        self.max_parent_frames = max_parent_frames
        #getting the list of parent frames
        self._parent_frame_list = []

        self.__prune_parent_frames()

        #the event queue containing the events from event_queue_manager this frame posts
        self.event_queue = []

        #own center, gets adjusted when x, y, width, height or frame_dim are changed
        self.center = (self.frame_dim.x + self.frame_dim.w // 2,
                        self.frame_dim.y + self.frame_dim.h // 2
                        )

        #saves scancode: is_pressed, so you can ask via key_pressed(scancode) if the key
        #belonging to scancode is currently pressed
        self.__key_scancodes = {}

        #list of own widgets, or subframes
        self.widgets = [] #own widgets

        #adding escape key
        self.add_pygame_key_callback(pygame.K_ESCAPE, {}, False, lambda e, d: Frame.CallbackEvent.EXIT, key_delay=0)

        self.bind_events()

    def __del__(self):
        self.raise_exit_flag()

        #removing from exit group
        if self.focus_group in Frame.FOCUS_GROUPS and Frame.FOCUS_GROUPS[self.focus_group] == self:
            #even if parent is None, its ok
            Frame.FOCUS_GROUPS[self.focus_group] = self.parent_frame



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
        #if the focus changes:
        #
        #if focus is gained:
        #the current frame reference owning the focus in the focus group
        #loses the focus, then this frame gains the focus and inserts
        #itself as the active reference in the focus group
        #After that, on_focus_gained is called
        #
        #if focus is lost:
        #if this frame is the frame currently owning the focus,
        #the focus reference is set to None
        #if this was triggered by another frame gaining focus, the focus
        #wont stay None, but instead will be overwritten.
        #After that on_focus_lost is called
        if x != self._has_focus:
            self._has_focus = x

            if self.focus_group is not None:

                if self.focus_group not in Frame.FOCUS_GROUPS:
                    Frame.FOCUS_GROUPS[self.focus_group] = None

                fd = Frame.FOCUS_GROUPS[self.focus_group]

                if not x:
                    if fd == self:
                        Frame.FOCUS_GROUPS[self.focus_group] = None
                else:

                    if fd is not None:
                        fd.has_focus = False

                    Frame.FOCUS_GROUPS[self.focus_group] = self


            self.clear_event_callbacks()
            self.add_pygame_key_callback(pygame.K_ESCAPE, {}, False, lambda e, d: Frame.CallbackEvent.EXIT, key_delay=0)
            self.bind_events()
            if self._has_focus:
                self.on_focus_gained()
            else:
                self.on_focus_lost()

    def __prune_parent_frames(self):

        if self.parent_frame is not None:
            self._parent_frame_list.insert(0, self.parent_frame)
            self._parent_frame_list.extend(self.parent_frame._parent_frame_list)

        if len(self._parent_frame_list) > self.max_parent_frames:
            self._parent_frame_list = self.__cutoff_parent_frames(self, self.max_parent_frames)

    def __cutoff_parent_frames(self, cframe, pindex):

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

    def on_focus_gained(self):
        pass

    def on_focus_lost(self):
        pass


    def move_by(self, x=0, y=0, w=0, h=0):
        #Moves the own frame dimension by the offsets
        nframe = pygame.Rect(self.x + x, self.y, self.width + w, self.height + h)
        self.frame_dim = nframe

    def offset_frame(self, frame_offsets):
        #takes a pygame.Rect and does self.frame_dim += frame_offsets

        nframe = pygame.Rect(self.x + frame_offsets.x, self.y + frame_offsets.y,
                            self.width + frame_offsets.width, self.height + frame_offsets.height
                            )

        self.frame_dim = nframe

    def move_to(self, x=None, y=None, w=None, h=None):
        #sets the frame_dim to the provdided values,
        #if the value is None the old value is used
        r = pygame.Rect((x if x is not None else self.x),
                        (y if y is not None else self.y),
                        (w if w is not None else self.width),
                        (h if h is not None else self.height))

        self.frame_dim = r


    def focus(self):
        #sets the focus
        self.has_focus = True

    def unfocus(self):
        #takes the focus away
        self.has_focus = False

    def is_focused(self):
        #just for style
        return self.has_focus

    def bind_events(self):
        #This is called in the constructor and every time this frames
        #focus changes. Make event bindings dependent on self._has_focus
        pass

    def key_pressed(self, scancode):
        #returns if the key belonging to the scancode is currently pressed
        if scancode not in self.__key_scancodes:
            return False
        else:
            return self.__key_scancodes[scancode]

    def manage_pygame_events(self):

        #Manages the events, by going through all
        #events in the pygame event queue.
        #Should be called in tick().
        #triggers the event_callbacks in self.__event_callbacks
        #added via self.add_pygame_key_callback or self.add_pygame_event_callback
        #if the callback has putback == True, the event stays in the queue
        #for the next event check

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

                if res == Frame.CallbackEvent.EXIT:
                    self.raise_exit_flag()

                if res == Frame.CallbackEvent.FAILURE:
                    processed = False

                if ecallback.putback:
                    processed = False

            if not processed or not matched_any:
                putback_events.append(event)

        for event in putback_events:
            pygame.event.post(event)


    def clear_event_callbacks(self):
        #removes all event callbacks
        self.__event_callbacks = []

    def clear_pygame_events(self):
        #clears the pygame event queue
        events = pygame.event.get()

    def get_event_callbacks(self):
        #gets the event callback list
        return self.__event_callbacks.copy()

    def add_pygame_event_callback(self, type, data, putback, func):

        #adds a CallbackEvent class into self.__event_callbacks
        cb = Frame.CallbackEvent(type, data, putback, func)
        self.__event_callbacks.append(cb)
        return cb

    def remove_pygame_event_callback(self, cb):

        #if the CallbackEvent class is in self.__event_callbacks it gets removed
        try:
            self.__event_callbacks.remove(cb)
            return True
        except:
            return False

    def pygame_key_is_disabled(self, key):
        #returns if a key is currently disabled
        if key not in self.__disabled_keys:
            return False
        else:
            return self.__disabled_keys[key]

    def disable_pygame_key(self, key):
        #disables a key for the event callbacks
        self.__disabled_keys[key] = True

    def enable_pygame_key(self, key):
        #enables the key for the event callbacks
        self.__disabled_keys[key] = False

    def __key_callback_wrapper(self, event, key, data, putback, func, key_delay):

        #wrapper for the keycallbacks, adds a delay between key_down detection

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
        #adds a callback for a pygame.KEYDOWN event with event.key == key
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


    def raise_exit_flag(self):
        #sets the exit flag, and gives the focus to next_focused_frame,
        #or the parent frame if the variable is None.
        #The focus can only be given if the next focused frame is in the same
        #focus group, and only if this frame has the focus
        self.__exit_flag_raised = True

    def reset_exit_flag(self):

        self.__exit_flag_raised = False



    def exit_flag_raised(self):
        return self.__exit_flag_raised

    def set_parent_frame(self, pframe):
        self.parent_frame = pframe

    def widgets_tick(self):
        #calls the tick function in all widgets/subframes
        #should be called in self.tick()
        for w in self.widgets:
            w.tick()

    def render_widgets(self, screen):
        #renders the widgets/subframes onto the screen.
        #should be called in self.render
        for widget in self.widgets:
            widget.render(screen)

    def rerender(self):
        #called every time either this frames
        #width or this frames height changes
        pass

    def tick(self):
        #This function is important, it should be called on every frame in the game.
        #It returns a reference to the frame that should be the main frame rendered.
        #If it returns None, this signals the frame was deleted

        self.manage_pygame_events()
        self.widgets_tick()

        if self.exit_flag_raised():
            return None

        return self

    @abstractmethod
    def render(self, screen):
        #draws the frame onto the screen
        #it should call self.render_widgets(screen)
        pass
