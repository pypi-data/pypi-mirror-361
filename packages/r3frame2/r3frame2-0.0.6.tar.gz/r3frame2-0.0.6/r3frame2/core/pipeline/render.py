from ..atom import R3atom, R3private
from ..flags import R3flags
from ..log import R3logger
from ..globals import pg, math
from ..utils import draw_rect, blit_rect, sub_v2
import r3frame2 as r3

class R3renderCall(R3atom):
    def __init__(self, pos: list[float], surf: pg.Surface, tag: str = None) -> None:
        super().__init__()
        self.tag: str = tag
        self.pos: list[float] = pos
        self.surf: pg.Surface = surf
        self._freeze()

class R3renderer(R3atom):
    def __init__(
            self,
            app: "r3.app.R3app",
            camera: "r3.pipeline.R3camera"
    ) -> None:
        super().__init__()
        self.app: r3.app.R3app = app
        self.window: r3.app.R3window = app.window
        self.camera: r3.pipeline.R3camera = camera
        self.database: r3.resource.R3database = app.database

        self.blits: int = 0
        self.calls: list[R3renderCall] = []
        
        self.buffers: list[pg.Surface] = [pg.Surface(camera.viewport_size, pg.SRCALPHA) for _ in range(2)]
        self.target: pg.Surface = self.buffers.pop()

        self._freeze()

    def visible(self, pos: list[float], size: list[int]) -> bool:
        x, y = pos
        w, h = size
        vx, vy = self.camera.viewport_pos
        vw, vh = self.camera.viewport_size
        return (x + w >= vx and x <= vx + vw and y + h >= vy and y <= vy + vh)

    def queue(self, entity: "r3.resource.R3entity", surface: "r3.resource.R3surf" = None) -> None:
        if not self.target: return
        if not isinstance(entity, r3.resource.R3entity): return

        if isinstance(surface, r3.resource.R3surf):
            surf = surface.surface
        else: surf = entity.surface.surface
        
        if not self.visible(entity.pos, surf.size): return

        self.calls.append(R3renderCall(self.camera.project(entity.pos), surf, entity.tag))

    def render(self, entity: "r3.resource.R3entity", surface: "r3.resource.R3surf" = None) -> None:
        if not self.target: return
        if not isinstance(entity, r3.resource.R3entity): return

        if isinstance(surface, r3.resource.R3surf):
            surf = surface.surface
        else: surf = entity.surface.surface
        
        if not self.visible(entity.pos, surf.size): return
        
        self.target.blit(surf, [*map(math.floor, self.camera.project(entity.pos))])

        self._unfreeze()
        self.blits += 1
        self._freeze()


    @R3private
    def flush(self) -> None:
        if not self.target: return
        self._unfreeze()
        
        if self.get_flag(R3flags.renderer.Y_SORT):
            self.calls.sort(key=lambda call: call.pos[1])
        
        for call in self.calls:
            self.target.blit(call.surf, [*map(math.floor, call.pos)])
            self.blits += 1
        self.calls.clear()
        
        self._freeze()

    @R3private
    def swap_buffers(self) -> None:
        if not len(self.buffers): return

        self._unfreeze()
        self.blits = 0

        self.window.blit(pg.transform.scale(self.target, self.window.size), [0, 0])
        
        if self.camera.get_flag(R3flags.renderer.DIRTY_CAMERA):
            self.buffers = [pg.Surface(self.camera.viewport_size, pg.SRCALPHA) for _ in range(2)]
            self.camera.rem_flag(R3flags.renderer.DIRTY_CAMERA)
        else:
            self.buffers.insert(0, self.target)

        self.target = self.buffers.pop()
        self.target.fill(self.window.color)
        self._freeze()
