import os
import re
import subprocess

from .svc import svc


# --------------------
## Operating System Abstraction Layer; provides functions to make cross-platform behavior similar
class Osal:
    # --------------------
    ## fix paths for cross-platforms
    #
    # @param path   the path to fix
    # @return the fixed path
    @classmethod
    def fix_path(cls, path):
        path = os.path.expanduser(path)
        if svc.gbl.os_name == 'win':
            # assumes there is only one ":" and it is for a drive letter
            m = re.search(r'(.*)(.):(.*)', path)
            if m:
                drive = m.group(2).lower()
                path = f'{m.group(1)}/{drive}/{m.group(3)}'
        path = path.replace('\\', '/')
        path = path.replace('//', '/')
        return path

    # --------------------
    ## get the homebrew link libraries root directory
    #
    # @return the homebrew link lib root dir
    @classmethod
    def homebrew_link_dirs(cls):
        return '/opt/homebrew/lib'

    # --------------------
    ## get the homebrew includes root directory
    #
    # @return the homebrew includes dir
    @classmethod
    def homebrew_inc_dirs(cls):
        return '/opt/homebrew/include'

    # --------------------
    ## get the root of the arduino cores, tools, etc.
    #
    # @return the root arduino directory
    @classmethod
    def arduino_root_dir(cls):
        if svc.gbl.os_name == 'macos':
            path = os.path.expanduser('~/Library/Arduino15')
        elif svc.gbl.os_name == 'win':
            path = os.path.expanduser('~/AppData/Local/Arduino15')
        else:
            path = '/usr/share/arduino'
        # do not fix_path()
        return path

    # --------------------
    ## get the library directory for arduino core source files
    #
    # @param arduino_root_dir   the root of the arduino directory system
    # @return the root libdir
    @classmethod
    def arduino_core_libdir(cls, arduino_root_dir):
        if svc.gbl.os_name == 'macos':
            path = f'{arduino_root_dir}/packages/arduino/hardware/avr/1.8.6/cores/arduino'
        elif svc.gbl.os_name == 'win':
            path = f'{arduino_root_dir}/packages/arduino/hardware/avr/1.8.6/cores/arduino'
        else:
            path = f'{arduino_root_dir}/hardware/arduino/avr/cores/arduino'
        # do not fix_path()
        return path

    # --------------------
    ## get the list of included directories for arduino core
    #
    # @param arduino_root_dir   the root of the arduino directory system
    # @return the list of include directories
    @classmethod
    def arduino_core_includes(cls, arduino_root_dir):
        if svc.gbl.os_name == 'macos':
            incs = [
                f'{arduino_root_dir}/packages/arduino/hardware/avr/1.8.6/cores/arduino',
                f'{arduino_root_dir}/packages/arduino/hardware/avr/1.8.6/variants/standard',
            ]
        elif svc.gbl.os_name == 'win':
            incs = [
                f'{arduino_root_dir}/packages/arduino/hardware/avr/1.8.6/cores/arduino',
                f'{arduino_root_dir}/packages/arduino/hardware/avr/1.8.6/variants/standard',
            ]
        else:
            incs = [
                f'{arduino_root_dir}/hardware/arduino/avr/cores/arduino',
                f'{arduino_root_dir}/hardware/arduino/avr/variants/standard',
            ]
        # do not fix_path()
        return incs

    # --------------------
    ## get the directory for avrdude.conf
    #
    # @param arduino_root_dir   the root of the arduino directory system
    # @return the avrdude directory
    @classmethod
    def avrdude_dir(cls, arduino_root_dir):
        if svc.gbl.os_name == 'macos':
            path = '/opt/homebrew/etc'
        elif svc.gbl.os_name == 'win':
            path = f'{arduino_root_dir}/packages/arduino/tools/avrdude/6.3.0-arduino17/etc'
            # TODO /c/Users/micro/AppData/Local/Arduino15/packages/arduino/tools/avrdude/6.3.0-arduino17/etc
        else:
            path = f'{arduino_root_dir}/hardware/tools'
        # do not fix_path()
        return path

    # --------------------
    ## return default gtest include directories
    #
    # @return the list of include directories
    @classmethod
    def gtest_includes(cls):
        incs = []
        if svc.gbl.os_name == 'win':
            incs.append('c:/msys64/mingw64/include')
        # do not fix_path()
        return incs

    # --------------------
    ## return default gtest link directories
    #
    # @return the list of link directories
    @classmethod
    def gtest_link_dirs(cls):
        dirs = []
        if svc.gbl.os_name == 'win':
            dirs.append('c:/msys64/mingw64/lib')
        # do not fix_path()
        return dirs

    # --------------------
    ## return default ruby include directories
    #
    # @return the list of include directories
    @classmethod
    def ruby_includes(cls):
        # TODO del; check if these work in msys2
        # incs = []
        # if svc.gbl.os_name == 'win':
        #     incs.append('C:/Ruby33-x64/include/ruby-3.3.0')
        #     incs.append('C:/Ruby33-x64/include/ruby-3.3.0/x64-mingw-ucrt')

        incs = [
            cls._get_ruby_inc1(),
            cls._get_ruby_inc2()
        ]
        # uncomment to debug
        # print(f'@@@DBG inc1:{incs[0]}')
        # print(f'@@@DBG inc2:{incs[1]}')

        # do not fix_path()
        return incs

    # --------------------
    ## get include directory1 using ruby utility
    #
    # @return path
    @classmethod
    def _get_ruby_inc1(cls):
        cmd = ['ruby', '-rrbconfig', '-e', 'puts RbConfig::CONFIG["rubyhdrdir"]']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=False)
        lines = result.stdout.strip().splitlines()
        if lines:
            inc1 = lines[0].strip()
        else:
            if svc.gbl.os_name == 'macos':
                inc1 = '/opt/homebrew/Cellar/ruby/3.3.5/include/ruby-3.3.0'
            elif svc.gbl.os_name == 'ubuntu':
                inc1 = '/usr/include/ruby-3.2.0'
            else:
                inc1 = 'unknown_inc1'
        return inc1

    # --------------------
    ## get include directory2 using ruby utility for ubuntu
    #
    # @return path
    @classmethod
    def _get_ruby_inc2(cls):
        cmd = ['ruby', '-rrbconfig', '-e', 'puts RbConfig::CONFIG["rubyarchhdrdir"]']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=False)
        lines = result.stdout.strip().splitlines()
        if lines:
            inc2 = lines[0].strip()
        else:
            if svc.gbl.os_name == 'macos':
                inc2 = '/opt/homebrew/Cellar/ruby/3.3.5/include/ruby-3.3.0'
            elif svc.gbl.os_name == 'ubuntu':
                inc2 = '/usr/include/x86_64-linux-gnu/ruby-3.2.0'
            else:
                inc2 = 'unknown_inc2'
        return inc2

    # --------------------
    ## return default ruby link directories
    #
    # @return the list of link directories
    @classmethod
    def ruby_link_dirs(cls):
        dirs = [cls._get_ruby_lib()]

        # uncomment to debug
        # print(f'@@@DBG link:{dirs[0]}')

        # do not fix_path()
        return dirs

    # --------------------
    ## get link library using ruby utility
    #
    # @return link library
    @classmethod
    def _get_ruby_lib(cls):
        # TODO check if this works in msys2
        cmd = ['ruby', '-rrbconfig', '-e', 'puts RbConfig::CONFIG["libdir"]']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=False)
        lines = result.stdout.strip().splitlines()
        if lines:
            lib = lines[0].strip()
        elif svc.gbl.os_name == 'macos':
            # best guess
            lib = '/opt/homebrew/Cellar/ruby/3.3.5/lib'
        elif svc.gbl.os_name == 'win':
            lib = 'C:/Ruby33-x64/lib'
        else:  # ubuntu
            lib = '/usr/lib'

        # uncomment to debug
        # print(f'@@@DBG lib:{lib}')
        return lib

    # --------------------
    ## return default link libraries needed for ruby
    #
    # @return the list of link libraries
    @classmethod
    def ruby_link_libs(cls):
        libs = []
        if svc.gbl.os_name == 'win':
            libs.append('x64-ucrt-ruby330.dll')
        # do not fix_path()
        return libs

    # --------------------
    ## return default python include directories
    #
    # @return the list of include directories
    @classmethod
    def python_includes(cls):
        # python3 -c "import sysconfig; print(sysconfig.get_path('include'))"
        import sysconfig
        incs = [sysconfig.get_path('include')]
        # do not fix_path()
        return incs

    # --------------------
    ## return default link libraries needed for ruby
    #
    # @return the list of link libraries
    @classmethod
    def python_link_libs(cls):
        import sysconfig
        libs = [sysconfig.get_config_var('LIBDIR')]

        # TODO del;
        # libs = []
        # if svc.gbl.os_name == 'macos':
        #     libs.append(
        #         '/opt/homebrew/Cellar/python@3.10/3.10.15/Frameworks/Python.framework/Versions/3.10/lib/python3.10/config-3.10-darwin')
        # do not fix_path()
        return libs
