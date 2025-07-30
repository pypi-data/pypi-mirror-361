# pymatchit

`pymatchit` is a high-performance Python binding for the [Rust `matchit`](https://github.com/ibraheemdev/matchit) routing library. It provides a fast and ergonomic way to match and manage URL routes in Python applications, leveraging the speed and safety of Rust under the hood.

> In fact, this module was created 90% with AI. _Fyi, I'm not a Rust developer and I'm just making Python bindings for fun._
> If you notice any issues with the implementation, your help would be greatly appreciated.

## Installation

We recommend using [uv](https://github.com/astral-sh/uv) for a fast and reliable installation experience.

```bash
uv add pymatchit
```

Or, if you prefer pip:

```bash
pip install pymatchit
```

## Usage

For usage examples and code samples, please refer to the [unit tests](tests/test_router.py). The tests demonstrate how to create a router, insert routes (with parameters and wildcards), perform lookups, remove routes, clear all routes, and handle conflicts. These examples provide practical guidance for integrating `pymatchit` into your own projects.
