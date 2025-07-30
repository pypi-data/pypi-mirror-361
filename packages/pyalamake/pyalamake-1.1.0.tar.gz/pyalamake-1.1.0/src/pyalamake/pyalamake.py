import json
import os
import re
import subprocess

from falcon_logger import FalconLogger

from .arduino_shared import ArduinoShared
from .constants_version import ConstantsVersion
from .gbl import Gbl
from .osal import Osal
from .package_cpip import PackageCpip
from .package_opengl import PackageOpengl
from .svc import svc


# --------------------
## class to generate a makefile using a set of rules defined in python
class AlaMake:

    # --------------------
    ## constructor
    def __init__(self):
        svc.log = FalconLogger()
        svc.log.set_format('prefix')
        svc.gbl = Gbl()
        svc.osal = Osal  # not an instance, it is the class

        svc.log.line(f'OS name: {svc.gbl.os_name}')

        ## list of targets
        self._targets = []

        ## the file pointer to the makefile
        self._fp = None
        ## the current target
        self._tgt = None
        ## the list of rules
        self._rules = {}
        ## the list of help info
        self._help = {}
        svc.log.highlight('creating targets...')

    # --------------------
    ## return True if OS is RPI
    @property
    def is_rpi(self):
        return svc.gbl.os_name == 'rpi'

    # --------------------
    ## return True if OS is Windows/Msys2
    @property
    def is_win(self):
        return svc.gbl.os_name == 'win'

    # --------------------
    ## return True if OS is macoOS
    @property
    def is_macos(self):
        return svc.gbl.os_name == 'macos'

    # --------------------
    ## return True if OS is Ubuntu
    @property
    def is_ubuntu(self):
        return svc.gbl.os_name == 'ubuntu'

    # --------------------
    ## return the version string for pyalamake
    @property
    def version(self):
        return ConstantsVersion.version

    # --------------------
    ## return ref to svc global
    # @return svc.gbl
    @property
    def gbl(self):
        return svc.gbl

    # --------------------
    ## return ref to svc log
    # @return svc.log
    @property
    def log(self):
        return svc.log

    # --------------------
    ## return ref to svc OSAL
    # @return svc.osal
    @property
    def osal(self):
        return svc.osal

    # --------------------
    ## for UT only
    # @return ref to svc
    @property
    def ut_svc(self):
        return svc

    # === cfg related

    # --------------------
    ## generate quiet rm for clean command
    #
    # @param val (bool) set cfg value to True to run quiet, or False to be verbose
    # @return None
    def cfg_quiet_clean(self, val=True):
        svc.gbl.quiet_clean = val

    # --------------------
    ## crate an arduino shared target
    #
    # @return reference to arduino shared object
    def create_arduino_shared(self):
        return ArduinoShared()

    # --------------------
    ## create a target with the given name and type.
    # The current recognized target types:
    #  * arduino - an arduino app
    #  * arduino-core - an arduino core
    #  * cpp - a C++ app or library
    #  * gtest - a unit test app for test C++
    #
    # @param target_name   the name of the new target
    # @param target_type   the type of the target
    # @param shared        whether this is a shared target (e.g. Arduino Core)
    def create(self, target_name, target_type, shared=None):
        valid_types = [
            # do not put arduino_core here
            'arduino',
            'cpp',
            'gtest',
        ]

        for tgt in self._targets:
            if target_name == tgt.target:
                svc.abort(f'target name is already in use: {target_name}')
                return None  # pragma: no cover

        if target_type == 'cpp':
            from .target_cpp import TargetCpp
            svc.log.line(f'create: {target_name}')
            impl = TargetCpp.create(self._targets, target_name)
        elif target_type == 'cpp-lib':
            from .target_cpp_lib import TargetCppLib
            svc.log.line(f'create: {target_name}')
            impl = TargetCppLib.create(self._targets, target_name)
        elif target_type == 'gtest':
            from .target_gtest import TargetGtest
            svc.log.line(f'create: {target_name}')
            impl = TargetGtest.create(self._targets, target_name)
        elif target_type == 'arduino':
            svc.log.line(f'create: {target_name}')
            from .target_arduino import TargetArduino
            impl = TargetArduino.create(self._targets, target_name, shared=shared)
        elif target_type == 'arduino-core':
            svc.log.line(f'create: {target_name}')
            from .target_arduino_core import TargetArduinoCore
            impl = TargetArduinoCore.create(self._targets, target_name, shared=shared)
        elif target_type == 'swig':
            from .target_swig import TargetSwig
            svc.log.line(f'create: {target_name}')
            impl = TargetSwig.create(self._targets, target_name)
        elif target_type == 'manual':
            from .target_manual import TargetManual
            svc.log.line(f'create: {target_name}')
            impl = TargetManual.create(self._targets, target_name)
        else:
            svc.log.err(f'unknown target type: {target_type}')
            svc.abort(f'valid target types: {" ".join(valid_types)} ')
            return None  # pragma: no cover

        return impl

    # --------------------
    ## find a package to add to this target.
    # Current packages recognized:
    #  cpip.* - see CPIP for available packages
    #  opengl - OpenGL package for graphics
    #
    # @param pkgname  the package name to search for
    # @return package info
    def find_package(self, pkgname):
        if pkgname.startswith('cpip.'):
            pkg = PackageCpip()
        elif pkgname == 'opengl':
            pkg = PackageOpengl()
        else:
            svc.log.err(f'unknown package: {pkgname}')
            svc.abort()
            return 'unknown'  # not needed, but stops IDE and pylint warnings

        return pkg.find(pkgname)

    # -------------------
    ## get the cross-platform port (e.g. COM3) based on the vid-pid of the USB port.
    #
    # @param vid_pid   the USB VID/PID value
    # @return the port with the VID/PID value in it, or None if not found
    def get_port(self, vid_pid):
        try:
            import serial
        except ModuleNotFoundError:
            svc.log.warn(f'{"get_port": <15}: module pyserial is not installed')
            return None

        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            if vid_pid in hwid:
                svc.log.ok(f'{"get_port": <15}: found port {port}: {desc} [{hwid}]')
                return port
            # svc.log.dbg(f'port {port}: {desc} [{hwid}]')
        svc.log.err(f'{"get_port": <15}: vid-pid not found: "{vid_pid}"')
        svc.log.err(f'{"get_port": <15}: check USB is connected and powered on')
        return None

    # === makefile related

    # --------------------
    ## generate makefile
    #
    # @param path  the path to the makefile to generate; default: Makefile
    # @return None
    def makefile(self, path='Makefile'):
        with open(path, 'w', encoding='utf-8') as self._fp:
            svc.log.highlight('generating targets...')
            self._gather_targets()
            svc.log.highlight('generating makefile...')
            self._gen_rules()
            self._gen_targets()
            self._gen_clean()
            self._gen_help()
        svc.log.line('done')

    # --------------------
    ## gather all targets
    #
    # @return None
    def _gather_targets(self):
        self._rules = {}
        for tgt in self._targets:
            # uncomment to debug
            # svc.log.dbg(f'   source   : {tgt.sources}')

            tgt.check()
            tgt.gen_target()
            tgt.gen_clean()
            self._rules[tgt.target] = tgt.rules

    # --------------------
    ## generate all rules
    #
    # @return None
    def _gen_rules(self):
        # gen rule for all
        rule = 'all'
        rules_str = ''
        for tgt, rules in self._rules.items():
            rules_str += f' {tgt} '
            rules_str += ' '.join(rules)
        self._writeln(f'.PHONY : all clean help {rules_str}')

        # has to be first target found otherwise clion can't parse it
        self._gen_rule(rule, rules_str, f'build {rule}')

        # generate a single rule to build each target in total
        for rule, rules_deps in self._rules.items():
            rules_str = ' '.join(rules_deps)
            self._gen_rule(rule, rules_str, f'build {rule}')

        self._writeln('')

    # --------------------
    # TODO move to separate file
    class CompileCmdJson:
        # --------------------
        def __init__(self):
            self._found_it = False
            self._count = 0
            self._compile_cmds = []
            self._curr_cmd = {}

        # --------------------
        def init(self):
            self._found_it = False

        # --------------------
        def get_info(self, line):
            if self._found_it:
                self._handle_line2(line)
                self._found_it = False
                self._curr_cmd = {}
                return

            m = re.search(r'(.*\.o):\s+(.*)', line)
            if not m:
                return

            obj_file = m.group(1)
            src_file = m.group(2)
            if src_file.startswith('/usr'):
                # exclude system includes/files
                return

            self._count += 1
            self._curr_cmd = {}
            self._compile_cmds.append(self._curr_cmd)
            self._handle_line1(obj_file, src_file)
            self._found_it = True

        # --------------------
        def _handle_line1(self, obj_file, src_file):
            # print(f'@@ DBG line1 {self._count: >2}: {obj_file} {src_file}')
            root_path = os.getcwd()
            self._curr_cmd['directory'] = root_path
            if src_file.startswith('/'):
                self._curr_cmd['file'] = src_file
            else:
                self._curr_cmd['file'] = os.path.join(root_path, src_file)

            if obj_file.startswith('/'):
                self._curr_cmd['output'] = obj_file
            else:
                self._curr_cmd['output'] = os.path.join(root_path, obj_file)

        # --------------------
        def _handle_line2(self, line):
            tokens = []
            for token in line.strip().split():
                token = token.strip('"')
                if token in ['-MMD']:
                    continue

                if not tokens:
                    # first token is the command
                    token = self._get_full_path(token)

                tokens.append(token)
            # print(f'@@ DBG line2 {self._count: >2}: {tokens}')
            self._curr_cmd['arguments'] = tokens

        # --------------------
        def _get_full_path(self, cmd):
            result = subprocess.run(f'which {cmd}',
                                    shell=True,  # Execute via shell
                                    capture_output=True,  # Capture stdout and stderr
                                    text=True,  # Decode output as string
                                    check=True)  # Raise error for non-zero exit codes
            return result.stdout.strip()

        # --------------------
        def save(self):
            print(f'@@ DBG found: {self._count}')
            with open('compile_commands.json', 'w', encoding='utf-8') as fp:
                json.dump(self._compile_cmds, fp, indent=2, sort_keys=True)

    # --------------------
    ## generate all targets
    #
    # @return None
    def _gen_targets(self):
        ccj = AlaMake.CompileCmdJson()
        for tgt in self._targets:
            ccj.init()
            self._writeln(f'# ==== {tgt.target}')
            for line in tgt.lines:
                ccj.get_info(line)
                self._writeln(line)

        ccj.save()

    # --------------------
    ## generate help info
    #
    # @return None
    def _gen_help(self):
        bslash = '\\'
        self._add_help('help', 'this help info')

        # gather all the help
        all_help = {}
        all_help.update(self._help)
        for tgt in self._targets:
            all_help.update(tgt.help)

        self._writeln('help:')
        self._writeln(f'\t@printf "Available targets:{bslash}n"')
        lastrule = 'help'
        for rule, desc in sorted(all_help.items()):
            if rule.startswith(f'{lastrule}-'):
                rulepfx = '  '
            else:
                lastrule = rule
                rulepfx = ''
            desc2 = desc.replace('"', f'{bslash}"')
            self._writeln(f'\t@printf "  {rulepfx}\x1b[32;01m{rule: <35}\x1b[0m {desc2}{bslash}n"')
        self._writeln(f'\t@printf "{bslash}n"')

    # --------------------
    ## generate lines to clean all generated files
    #
    # @return None
    def _gen_clean(self):
        rule = 'clean'
        clean_tgts = ''
        for tgt in self._targets:
            clean_tgts += f'{tgt.target}-clean '

        self._gen_rule(rule, clean_tgts, 'clean files')
        self._writeln('')

    # --------------------
    ## write a line to the makefile
    #
    # @param line  the line to write
    # @return None
    def _writeln(self, line):
        self._fp.write(line + '\n')

    # --------------------
    ## add a line for target help
    #
    # @param target   the target
    # @param desc     the help line
    # @return None
    def _add_help(self, target, desc):
        # TODO duplicate of function in target_base
        if target in self._help:
            svc.log.warn(f'add_help: target "{target}" already has description')
            svc.log.warn(f'   prev: {self._help[target]}')
            svc.log.warn(f'   curr: {desc}')
            svc.log.warn('   replacing...')
        self._help[target] = desc

    # --------------------
    ## generate a rule
    #
    # @param rule   the rule to generate
    # @param deps   the dependencies for this rule
    # @param desc   the help line
    # @return None
    def _gen_rule(self, rule, deps, desc):
        self._writeln(f'#-- {desc}')
        self._add_help(rule, desc)
        if deps:
            self._writeln(f'{rule}: {deps}')
        else:
            self._writeln(f'{rule}:')
