import asyncio
import threading
import tkinter as tk
from .dobotasync import DobotAsync as DobotAsync
from _typeshed import Incomplete

class DobotGUIApp:
    root: Incomplete
    loop: Incomplete
    dobot: Incomplete
    status_label: Incomplete
    connection_status_label: Incomplete
    def __init__(self, root: tk.Tk, loop: asyncio.AbstractEventLoop, dobot_instance: DobotAsync) -> None: ...

class DobotGUIController:
    dobot_async_instance: DobotAsync
    loop: asyncio.AbstractEventLoop | None
    async_thread: threading.Thread | None
    root: tk.Tk | None
    def __init__(self, dobot: DobotAsync) -> None: ...
    def initialize_gui(self) -> None: ...
