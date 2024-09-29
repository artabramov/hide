import os
import importlib.util
import inspect
from app.context import get_context
from app.config import get_config
from app.log import get_log

log = get_log()
ctx = get_context()
cfg = get_config()


async def load_hooks():
    ctx.hooks = {}

    # Load and register functions from extension modules.
    filenames = [file + ".py" for file in cfg.EXTENSIONS_ENABLED]
    for filename in filenames:
        module_name = filename.split(".")[0]
        module_path = os.path.join(cfg.EXTENSIONS_BASE_PATH, filename)

        try:
            # Load the module from the specified file path.
            spec = importlib.util.spec_from_file_location(
                module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Register functions from the module as hooks.
            func_names = [attr for attr in dir(module)
                          if inspect.isfunction(getattr(module, attr))]
            for func_name in func_names:
                func = getattr(module, func_name)
                if func_name not in ctx.hooks:
                    ctx.hooks[func_name] = [func]
                else:
                    ctx.hooks[func_name].append(func)

        except Exception as e:
            log.debug("Hook error; filename=%s; e=%s;" % (filename, str(e)))
            raise e
