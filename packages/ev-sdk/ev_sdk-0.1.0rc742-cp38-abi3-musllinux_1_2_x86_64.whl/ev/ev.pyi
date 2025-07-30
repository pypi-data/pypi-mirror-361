from __future__ import annotations

from typing import Callable

def main(): ...

class _Client:
    #
    @staticmethod
    def default() -> _Client: ...
    #
    async def run(self, job: _Job, args: dict[str, str]): ...

class _Function:
    #
    @staticmethod
    def from_code(py_name: str, py_code: str): ...
    #
    @staticmethod
    def from_callable(py_name: str, py_callable: Callable): ...

class _Job:
    #
    @staticmethod
    def new(name: str) -> _Job: ...

class _Env:
    #
    @staticmethod
    def new(python_version: str) -> _Env: ...
    #
    @property
    def environ(self): ...
    #
    def include(self, paths: list[str]): ...
    #
    def pip_install(self, requirements: list[str]): ...
    #
    def dump(self) -> dict[str, str]: ...
