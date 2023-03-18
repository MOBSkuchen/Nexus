loaded = False


def _import():
    import ntllib
    return ntllib


def safe_import():
    global ntl, __version__, loaded
    if loaded:
        return
    from logger import logger
    import errors as xsErrors

    try:
        ntl = _import()
        __version__ = ntl.version()
        loaded = True
    except Exception as ex:
        if xsErrors.debug:
            raise ex
        logger.add(f"NTL failed to load : {str(ex)}")
        xsErrors.internal_error("Nexustools library load failed, this is NOT fixable!", -3)
    logger.add(f"NTL loaded V{__version__}")


def unsafe_import():
    global ntl, __version__, loaded
    if loaded:
        return
    ntl = _import()
    __version__ = ntl.version()
    loaded = True


if __name__ == '__main__':
    unsafe_import()
else:
    safe_import()

x = ntl.file_get("main.py")
print(x)
print(type(x))
