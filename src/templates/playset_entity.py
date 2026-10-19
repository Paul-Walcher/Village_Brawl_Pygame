from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
import constants

class PlaysetEntity(Frame):

    @staticmethod
    def info():
        pass

    def __init__(self, modules, entity_type, frame_enum=FrameEnums.PLAYSET_ENTITY, data=None,
                        frame_dim=constants.FULLSCREEN, parent_frame=None):

        super().__init__(frame_enum, data, frame_dim, parent_frame)

        self.modules = modules
        self.mappings = modules.mappings
        self.enums = modules.enums
        self.tags = modules.tags

        self.prev_phase = None

        self.entity_type = entity_type

        self.phase_change_functions = {}

    def tick(self, phaseinfo):
        self.execute_phase_change(phaseinfo)

    #default is drawing nothing
    def render(self, screen):
        pass

    def execute_phase_change(self, phaseinfo):

        cphase = phaseinfo.phase

        if self.prev_phase != cphase:

            if self.prev_phase in self.phase_change_functions:
                for func in self.phase_change_functions[self.prev_phase]:
                    func(self.prev_phase, cphase)


        if cphase in self.phase_change_functions:
            for func in self.phase_change_functions[cphase]:
                func(self.prev_phase, cphase)

        self.prev_phase = cphase

    def add_on_phase_change(self, new_phase, func):

        if new_phase not in self.phase_change_functions:
            self.phase_change_functions[new_phase] = []

        self.phase_change_functions[new_phase].append(func)

    def remove_on_phase_change(self, new_phase, func):

        if new_phase in self.phase_change_functions:
            if func in self.phase_change_functions[new_phase]:
                self.phase_change_functions[new_phase].remove(func)
                return True

        return False
