import ast
import inspect
import itertools
import linecache
from typing import (
    Callable,
    ParamSpec,
    TypeVar,
    Generator,
    Iterable,
    Tuple,
    Literal,
    Any,
)
from types import FrameType

T = TypeVar("T")
P = ParamSpec("P")


class SpreadGeneratorError(RuntimeError):
    pass


def _up_frame(height: int) -> FrameType | None:
    """
    Get the frame `height` levels above the current frame, or None if it doesn't exist
    """
    frame = inspect.currentframe()
    for _ in range(height):
        if frame is None:
            return
        frame = frame.f_back
    return frame


def _num_unpack_names(node: ast.AST) -> int | None | Literal["all"]:
    """
    Get the number of unpacked names in an assignment in the form of `[a, b, c], rest = d`

    Returns None if the assignment cannot be meaningfully unpacked

    Returns "all" if the assignment is of the form `[a, *b, c], rest = d`, such that
    all elements of `d` are unpacked to the names

    Otherwise, returns the number of unpacked names in the assignment. For example,
    `[a, b, c], rest = d` returns 3
    """
    if not isinstance(node, ast.Assign):
        return None

    if len(node.targets) != 1:
        # Occurs in the case of `[a, b, *c] = d = [1, 2, 3, 4]`
        return None

    if not isinstance(node.targets[0], (ast.Tuple, ast.List)):
        # Occurs in the case of `a = [1, 2, 3, 4]`
        return None

    elts = node.targets[0].elts

    if len(elts) != 2:
        # Occurs in the case of `[a, b, c] = [1, 2, 3, 4]`
        return None

    if not isinstance(elts[0], (ast.Tuple, ast.List)):
        # Occurs in the case of `[a, b] = [1, 2, 3, 4]`
        return None

    name_elts = elts[0].elts

    for elt in name_elts:
        if isinstance(elt, ast.Starred):
            return "all"

    return len(name_elts)


def _empty_generator() -> Generator[Any, None, None]:
    """
    Produces an empty generator that does nothing
    """
    return
    yield None


def spread_generator(
    func: Callable[P, Generator[T, None, None]],
) -> Callable[P, Tuple[Iterable[T], Generator[T, None, None]]]:
    """
    Turn a function that returns a generator into a function that returns
    a tuple of an iterable and a generator, where the iterable is the first
    `n` elements of the generator, `n` being the number of unpacked names
    in the calling assignment from the form `[a, b, c], rest = d()`.
    """

    def wrapper(
        *args: P.args, **kwargs: P.kwargs
    ) -> Tuple[Iterable[T], Generator[T, None, None]]:
        executing_frame = _up_frame(2)

        if executing_frame is None:
            raise SpreadGeneratorError(
                "spread_generator must be used as a decorator, cannot find executing frame"
            )

        line_no: int = executing_frame.f_lineno
        file_name: str = executing_frame.f_code.co_filename

        line_content = linecache.getline(file_name, line_no)

        tree = ast.parse(line_content.strip())

        unpacked_names = _num_unpack_names(tree.body[0])

        if unpacked_names is None:
            raise SpreadGeneratorError(
                f"spread_generator cannot find unpacked names in line {line_no} of {file_name}. Is the assignment in the form `[a, b, c], rest = d`?"
            )

        if unpacked_names == "all":
            return func(*args, **kwargs), _empty_generator()

        func_gen = func(*args, **kwargs)

        return itertools.islice(func_gen, unpacked_names), func_gen

    return wrapper
