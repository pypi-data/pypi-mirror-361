import shlex
from sysconfig import get_config_vars
from os import path, makedirs
from subprocess import run
from typing import Any
from ruamel.yaml import YAML
from json import dump

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.plugin import hookimpl
from msgspec import Struct


class CExtension(Struct):

    # the full name of the extension, including any packages
    # – ie. not a filename or pathname, but Python dotted name
    name: str

    # list of source filenames, relative to the distribution root
    # (where the setup script lives), in Unix form (slash-separated)
    # for portability.
    sources: tuple[str]

    # list of directories to search for C/C++ header files
    # (in Unix form for portability)
    include_dirs: tuple[str] = ()

    # list of library names (not filenames or paths) to link against
    libraries: tuple[str] = ()

    #  list of macros to define; each macro is defined using a 2-tuple:
    # the first item corresponding to the name of the macro and the second item
    # either a string with its value or None to define it without a particular
    # value (equivalent of “#define FOO” in source or -DFOO on Unix C compiler
    # command line)
    define_macros: dict[str, str | None] = {}

    #  list of macros to undefine explicitly
    undef_macros: tuple[str] = ()

    module_name: str = ''

    plugin: BuildHookInterface = None

    def __post_init__(self):
        self.module_name = self.name.split('.')[-1]

    def build(self, build_data: dict[str, Any]):
        match self.plugin.target_name:
            case 'sdist':
                self.build_source(build_data)
            case 'wheel':
                self.build_binary(build_data)

    def build_source(self, build_data: dict[str, Any]):
        build_data.setdefault('sources', [])
        build_data['sources'] = [*self.sources]

        build_data.setdefault('include', [])
        build_data['include'].extend(
            dir
            for dir in self.include_dirs
            if not path.isabs(dir)
        )

    def build_binary(self, build_data: dict[str, Any]):
        build_data['pure_python'] = False
        build_data['infer_tag'] = True
        init_function = f'PyInit_{self.module_name}'

        config_vars = get_config_vars()

        gcc_call = [
            config_vars['CC'],
            *self.sources,
            '-fPIC',
            '-shared',
            '-fvisibility=hidden',
            *shlex.split(config_vars['CFLAGS']),
            f'-I{config_vars['INCLUDEPY']}',
            '-Xlinker', f'--export-dynamic-symbol={init_function}',
            *shlex.split(config_vars['LDFLAGS']),
        ]

        gcc_call.extend(
            f'-I{include_dir}'
            for include_dir in self.include_dirs
        )

        gcc_call.extend(
            f'-D{name}={value}' if value is not None else f'-D{name}'
            for name, value in self.define_macros.items()
        )

        gcc_call.extend(
            f'-U{name}'
            for name in self.undef_macros
        )

        gcc_call.extend(
            f'-l{name}'
            for name in self.libraries
        )

        out_path = path.join(
            self.plugin.out_dir,
            f'{self.module_name}.so',
        )
        gcc_call.append(f'-o{out_path}')

        final_so_path = self.name.replace('.', '/') + '.so'
        full_final_path = path.join(self.plugin.directory, final_so_path)

        makedirs(path.dirname(full_final_path), exist_ok=True)

        build_data['force_include'][out_path] = final_so_path

        run(gcc_call, cwd=self.plugin.root, check=True)


class OmniblackHatch(BuildHookInterface):
    PLUGIN_NAME = 'omniblack-hatch'

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        self.out_dir = path.join(self.root, 'build')
        makedirs(self.out_dir, exist_ok=True)

        self.build_package_config(build_data)

        exts = [
            CExtension(**ext, plugin=self)
            for ext in self.config['extensions']
        ]

        for ext in exts:
            ext.build(build_data)

        self.build_external_requires(build_data, exts)

    def build_package_config(self, build_data):
        match self.target_name:
            case 'sdist':
                includes = build_data.setdefault('include', [])
                includes.append('package_config.yaml')
            case 'wheel':
                pkg_path = path.join(self.root, 'package_config.yaml')
                out_path = path.join(self.out_dir, 'package_config.json')

                with (
                    open(pkg_path) as in_file,
                    open(out_path, 'x') as out_file,
                ):
                    yaml = YAML()
                    config = yaml.load(in_file)
                    dump(config, out_file, ensure_ascii=False, sort_keys=True)

                build_data['extra_metadata'][out_path] = 'package_config.json'

    def build_external_requires(self, build_data, exts):
        if self.target_name != 'wheel':
            return

        libraries = {
            lib
            for ext in exts
            for lib in ext.libraries
        }

        if not libraries:
            return

        external_requires = (
            f'lib{name}\n'
            for name in libraries
        )

        out_path = path.join(self.out_dir, 'external_requires.txt')
        with open(out_path, 'x') as out_file:
            out_file.writelines(external_requires)

        build_data['extra_metadata'][out_path] = 'external_requires.txt'


@hookimpl
def hatch_register_build_hook():
    return OmniblackHatch
