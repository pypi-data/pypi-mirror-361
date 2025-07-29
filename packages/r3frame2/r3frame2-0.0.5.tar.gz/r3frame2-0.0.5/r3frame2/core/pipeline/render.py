from ..atom import R3atom, R3private
from ..flags import R3flags
from ..log import R3logger
from ..globals import pg
from ..utils import draw_rect
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
    ) -> None:
        super().__init__()
        self.app: r3.app.R3app = app
        self.window: r3.app.R3window = app.window
        self.database: r3.resource.R3database = app.database

        self.blits: int = 0
        self.buffer_max: int = 2
        self.buffers: list[pg.Surface] = []
        self.calls: list[R3renderCall] = []

        for _ in range(self.buffer_max):
            surf = pg.Surface(app.window.size, pg.SRCALPHA)
            if _ == 1:
                surf.fill([255, 0, 0])
            else:
                surf.fill(app.window.color)
            self.buffers.append(surf)
        self.target: pg.Surface = self.buffers.pop()
        self._freeze()

    def queue(self, entity: "r3.resource.R3entity", surface: "r3.resource.R3surf" = None) -> None:
        if not self.target: return
        if not isinstance(entity, r3.resource.R3entity): return

        if isinstance(surface, r3.resource.R3surf):
            surf = surface.surface
        else: surf = entity.surface.surface
        pos = entity.pos

        self.calls.append(R3renderCall(pos, surf, entity.tag))

    def render(self, entity: "r3.resource.R3entity", surface: "r3.resource.R3surf" = None) -> None:
        if not self.target: return

        if isinstance(surface, r3.resource.R3surf):
            surf = surface.surface
        else: surf = entity.surface.surface
        pos = entity.pos

        self.target.blit(surf, pos)

        if self.get_flag(R3flags.renderer.SHOW_COLLIDERS):
            collider = self.database.query_aabb(f"{entity.tag}.aabb")
            if isinstance(collider, r3.resource.R3aabb):
                r3.utils.blit_rect(self.target, collider.rect, [0, 255, 0], 1)
                self.blits += 1

        self._unfreeze()
        self.blits += 1
        self._freeze()
    
    @R3private
    def flush(self) -> None:
        if not self.target: return
        self._unfreeze()
        for call in self.calls:
            self.target.blit(call.surf, call.pos)
            if isinstance(call.tag, str) and self.get_flag(R3flags.renderer.SHOW_COLLIDERS):
                collider = self.database.query_aabb(f"{call.tag}.aabb")
                if isinstance(collider, r3.resource.R3aabb):
                    r3.utils.blit_rect(self.target, collider.rect, [0, 255, 0], 1)
                    self.blits += 1
            self.blits += 1
        self.calls.clear()
        self._freeze()

    @R3private
    def swap_buffers(self) -> None:
        if not len(self.buffers): return

        self._unfreeze()
        self.blits = 0

        # TODO: post processing
        self.window.blit(self.target, [0, 0])
        self.buffers.insert(0, self.target)

        self.target = self.buffers.pop()
        self.target.fill(self.window.color)
        self._freeze()
