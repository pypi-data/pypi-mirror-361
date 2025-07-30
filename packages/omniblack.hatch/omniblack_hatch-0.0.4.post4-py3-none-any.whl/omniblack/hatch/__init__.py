import shlex
import sysconfig

from os import makedirs, path
from subprocess import run
from sysconfig import get_config_var
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.plugin import hookimpl
from msgspec import Struct
from msgspec.json import Encoder, format
from ruamel.yaml import YAML

# TODO this will have problems with multiple extensions in one project

class CompileCommand(Struct):
    arguments: list[str]
    directory: str
    output: str
    file: str

    def to_json(self) -> dict:
        return {
            'arguments': self.arguments,
            'command': shlex.join(self.arguments),
            'directory': self.directory,
            'output': self.output,
            'file': self.file,
        }

    def run(self):
        makedirs(path.dirname(self.output), exist_ok=True)
        print(f'Calling {self.arguments}')
        run(self.arguments, cwd=self.directory, check=True)


class LinkCommand(Struct):
    arguments: list[str]
    files: list[str]
    output: str
    directory: str

    def run(self):
        print(f'Calling {self.arguments}')
        return run(self.arguments, cwd=self.directory, check=True)


def replace_ext(p: str, ext: str):
    no_ext, _old_ext = path.splitext(p)
    return no_ext + ext



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

    so_name: str = ''

    out_path: str = ''

    cflags: list[str] = []

    ldflags: list[str] = []

    cc: str = None

    plugin: BuildHookInterface = None

    def __post_init__(self):
        self.module_name = self.name.split('.')[-1]
        self.so_name = f'{self.module_name}.so'
        self.out_path = path.join(self.plugin.native_out_dir, self.so_name)
        self.cflags = self.get_cflags()
        self.ldflags = self.get_ldflags()
        self.cc = sysconfig.get_config_var('CC')

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
            included_dir
            for included_dir in self.include_dirs
            if not path.isabs(included_dir)
        )

    def build_binary(self, build_data: dict[str, Any]):
        build_data['pure_python'] = False
        build_data['infer_tag'] = True

        final_so_path = self.name.replace('.', '/') + '.so'
        full_final_path = path.join(self.plugin.directory, final_so_path)

        makedirs(path.dirname(full_final_path), exist_ok=True)

        build_data['force_include'][self.out_path] = final_so_path


        object_compiles = self.compile_objects()
        link_objects = self.link_shared_object(object_compiles)

        for step in object_compiles:
            step.run()

        link_objects.run()

    def compile_objects(self) -> list[CompileCommand]:
        return [
            self.compile_object(src_file)
            for src_file in self.sources
        ]

    def get_cflags(self) -> list[str]:
        init_function = f'PyInit_{self.module_name}'
        flags = [
            *shlex.split(get_config_var('CFLAGS')),
            f'-I{get_config_var('INCLUDEPY')}',
            '-fvisibility=hidden',
            '-Xlinker', f'--export-dynamic-symbol={init_function}',
            *self.sources,
        ]
        flags.extend(
            f'-I{include_dir}'
            for include_dir in self.include_dirs
        )

        flags.extend(
            f'-D{name}={value}' if value is not None else f'-D{name}'
            for name, value in self.define_macros.items()
        )

        flags.extend(
            f'-U{name}'
            for name in self.undef_macros
        )

        return flags

    def get_ldflags(self) -> list[str]:
        init_function = f'PyInit_{self.module_name}'
        flags = [
            '-fPIC',
            '-shared',
            '-fvisibility=hidden',
            '-Xlinker', f'--export-dynamic-symbol={init_function}',
            *shlex.split(get_config_var('LDFLAGS')),
        ]

        flags.extend(
            f'-l{name}'
            for name in self.libraries
        )

        return flags

    def compile_object(self, src_file) -> CompileCommand:
        proj_rel = path.relpath(src_file, self.plugin.root)
        full_out = path.join(
            self.plugin.native_out_dir,
            replace_ext(proj_rel, '.o'),
        )
        cc_call = [
            self.cc,
            *self.cflags,
            src_file,
            f'-o{full_out}',
        ]

        return CompileCommand(
            arguments=cc_call,
            directory=self.plugin.root,
            output=full_out,
            file=src_file,
        )

    def link_shared_object(
            self,
            compilations: list[CompileCommand],
    ) -> LinkCommand:
        in_files = [
            compilation.output
            for compilation in compilations
        ]

        cc_call = [
            self.cc,
            *self.ldflags,
            *in_files,
            self.out_path,
        ]

        return LinkCommand(
            arguments=cc_call,
            files=in_files,
            output=self.out_path,
            directory=self.plugin.root,
        )



class OmniblackHatch(BuildHookInterface):
    PLUGIN_NAME = 'omniblack-hatch'

    def initialize(self,version: str, build_data: dict[str, Any]) -> None:
        self.dev_mode = self.target_name == 'wheel' and version == 'editable'
        self.out_dir = path.join(self.root, 'build')
        self.native_out_dir = path.join(self.out_dir, sysconfig.get_platform())
        makedirs(self.out_dir, exist_ok=True)

        self.build_package_config(build_data)

        exts = [
            CExtension(**ext, plugin=self)
            for ext in self.config['extensions']
        ]
        self.build_compile_commands(exts)

        for ext in exts:
            ext.build(build_data)

        self.build_external_requires(build_data, exts)


    def write_json(self, data, path):
        if not hasattr(self, '_encoding_buffer'):
            self._encoding_buffer = bytearray()

        if not hasattr(self, '_encoder'):
            self._encoder = Encoder(order='sorted')

        self._encoder.encode_into(data, self._encoding_buffer)
        out_pretty = format(self._encoding_buffer, indent=4)

        with open(path, 'wb') as file:
            file.write(out_pretty)


    def build_package_config(self, build_data):
        match self.target_name:
            case 'sdist':
                includes = build_data.setdefault('include', [])
                includes.append('package_config.yaml')
            case 'wheel':
                pkg_path = path.join(self.root, 'package_config.yaml')
                out_path = path.join(self.out_dir, 'package_config.json')

                with open(pkg_path) as in_file:
                    yaml = YAML()
                    config = yaml.load(in_file)
                    self.write_json(config, out_path)

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
        with open(out_path, 'w') as out_file:
            out_file.writelines(external_requires)

        build_data['extra_metadata'][out_path] = 'external_requires.txt'

    def build_compile_commands(self, exts: list[CExtension]):
        if not self.dev_mode:
            return

        compile_commands = [
            command
            for ext in exts
            for command in ext.compile_objects()
        ]

        self.write_json(
            compile_commands,
            path.join(self.root, 'compile_commands.json'),
        )


@hookimpl
def hatch_register_build_hook():
    return OmniblackHatch
