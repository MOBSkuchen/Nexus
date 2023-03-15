loaded = False


def safe_import():
    global ntl, __version__, loaded
    if loaded:
        return
    from logger import logger
    import errors as xsErrors

    try:
        import ntllib as ntl
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
    import ntllib as ntl
    __version__ = ntl.version()
    loaded = True


if __name__ == '__main__':
    unsafe_import()
else:
    safe_import()
