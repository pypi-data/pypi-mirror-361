# mcpm

a tool for managing minecraft servers

not very polished. knocked together in a weekend.

initialize a `mcpm.toml` file (in the current directory):

```sh
mcpm init
```

install a plugin:

```sh
mcpm add viaversion
```

mcpm operations like `add`, `remove`, and `upgrade` all cause a file called `mcpm.lock` to be generated or updated. this file is stored alongside `mcpm.toml`. this is similar to package managers like `uv`, `poetry`, `npm`, `cargo`, etc.

the lockfile describes exactly which version of a given jarfile should be installed. once a jarfile is locked, it will not be moved to a new version unless you explicitly upgrade.

you can explictly perform a lock, with:

```sh
mcpm lock
```

finally, you can provision a server from the lockfile:

```sh
mcpm provision
```

this downloads all the jars into the correct place.
