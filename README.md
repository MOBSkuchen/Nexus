# Nexus
Nexus is a shell built in python. It is easily extendable using PEx and the NXPY API.

For its high-performance tasks, Nexus uses NTL (NexusTools library), which is made in rust usinng maturin and pyo3.

### Nexus provides:
- A PackageManager, which also has its own project filetype (.ypp)
- SSH and SFTP connection managers (Nexus-SSH and Nexus-SFTP [*still in progress*])
- Path and content search using NTL
- Extensive documentation with manuals (.man)
- Its own argument parser
- NXPY (Nexus-Python) API for extending Nexus and using nexus core functions in extensions

For a list of all implemented commands do:
```nexus -h``` or ```nexus --help```

### Extending Nexus
Developing an extension is very easy. Just use ```pex --new example``` in Nexus to create a new extension file (example.py).

#### Using NXPY
In the file that has been created, you should find a ``main`` function.

Main uses ``ctx.getlib()`` to load a NXPY library ``io_pack`` to print "Hello World" in the Nexus way.

Please note that your extension must implement main the following way:

```python
def main(args):
    ...  # Your code
```
[SEE : ``man NXPY``]
### Limitations
- Nexus currently has only relatively minimal error handling
- The logging is not very good
- Not all commands are *[fully]* implemented
- Most commands do not gave a manual
