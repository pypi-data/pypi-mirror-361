#! /usr/bin/env python

from pathlib import Path

from solid2.core.utils import escape_openscad_identifier as escape
from solid2.libs.py_scadparser import scad_parser

headerTemplate = """\
from solid2.core.object_base import OpenSCADObject as _OpenSCADObject,\
                                    OpenSCADConstant as _OpenSCADConstant
from solid2.core.scad_import import extra_scad_include as _extra_scad_include
from pathlib import Path as _Path

_extra_scad_include(f"{{_Path(__file__).parent / _Path('../'*{parentCount}) / '{scadFile}'}}", use_not_include={use_not_include})

"""

constantTemplate = "{name} = _OpenSCADConstant('{name}')"

callableTemplate = """\
class {name}(_OpenSCADObject):
    def __init__({paramStr}):
       super().__init__({initStr})

"""

def generateStub(scadFile, outputDir, use_not_include,
                 headerTemplate=headerTemplate,
                 callableTemplate=callableTemplate,
                 parentCount=1):

    def generateHeader():
        return headerTemplate.format(__file__=__file__,
                                     scadFile=scadFile,
                                     use_not_include=use_not_include,
                                     parentCount=parentCount)

    def generateConstant(c):
        return constantTemplate.format(name=escape(c.name)) + "\n"

    def generateCallable(c):
        name = escape(c.name)
        paramNames = [escape(p.name) for p in c.parameters]
        paramNames = list(dict.fromkeys(paramNames))

        paramStr = ", ".join(["self"] +
                             [f"{p}=None" for p in paramNames] +
                             ["**kwargs"])
        initList = [f'"{p}" : {p}' for p in paramNames]
        initList.append("**kwargs")
        initStr = f'"{name}", {{{", ".join(initList)}}}'
        return callableTemplate.format(name=name, paramStr=paramStr, initStr=initStr)

    modules, functions, global_vars = scad_parser.parseFile(scadFile)

    escaped_filename = escape(scadFile.stem) + ".py"
    with open(outputDir / escaped_filename, "w") as f:
        f.write(generateHeader())

        for c in global_vars:
            f.write(generateConstant(c))

        for c in functions + modules:
            f.write(generateCallable(c))

def makePackage(directory):
    import os
    if not os.path.exists(directory):
        os.mkdir(directory)
    if not os.path.exists(directory / "__init__.py"):
        with open(directory / "__init__.py", "w") : pass


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="generates a solidpython2 extensions "
                                        "from a OpenSCAD library")
    parser.add_argument("scadInDir",
                        help="directory containing the scad (library) files")
    parser.add_argument("packageName",
                        help="name of the generated python package")
    parser.add_argument("-i", "--include", action='store_false', default=True,
                        help="use OpenSCADs 'include' to import the library. "
                             "Otherwiese OpenSCADs 'use' is used")

    args = parser.parse_args()

    def generatePackage(inDir, outDir, parentCount=1):
        for f in inDir.iterdir():
            if f.is_dir():
                makePackage(outDir)
                generatePackage(inDir / f.name, outDir / f.name, parentCount+1)
            elif f.suffix == ".scad":
                makePackage(outDir)
                generateStub(f, outDir, args.include, parentCount=parentCount)

    generatePackage(Path(args.scadInDir), Path(".") / args.packageName)
