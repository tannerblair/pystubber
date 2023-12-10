import shutil
import black
import clr
import pathlib

import logging

from black import InvalidInput

logging.basicConfig()
logging.root.setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

from dotnetwrapper.pywriter import PyWriter
from System.Reflection import Assembly
from System import BadImageFormatException

if __name__ == "__main__":
    root_dir = pathlib.Path("C:/Program Files/National Instruments/VeriStand 2021")
    out_dir = pathlib.Path(__file__).parent.parent / "output"

    dll_paths = root_dir.glob('NationalInstruments.VeriStand.SystemDef*.dll')
    for dll_path in dll_paths:
        try:

            out_path = '/'.join(str(dll_path.stem.lower()).split('.'))
            out_path = out_dir / out_path
            if out_path.exists():
                shutil.rmtree(out_path)
            out_path.mkdir(parents=True)

            assembly = Assembly.LoadFrom(str(dll_path))
            [print(m) for m in assembly.GetModules()]
            python_code = PyWriter().write_assembly(assembly)
            mode = black.FileMode()
            mode.is_pyi = True
            try:
                python_code = black.format_file_contents(python_code, fast=True, mode=mode)
            except InvalidInput as e:
                logging.warning(e)
            with (out_path / "__init__.pyi").open('w') as f:
                f.write(python_code)

            with (out_path / "__init__.py").open('w') as f:
                f.write("import clr\n\r")
                sanitized_path = str(dll_path).replace("\\", "/")
                f.write(f'clr.AddReference("{sanitized_path}")\n\r')
                f.write(f'from {dll_path.stem} import *')

            logger.info(f"Success: {dll_path}")
        except BadImageFormatException:
            logger.warning(f"Bad Image: {dll_path}")
