#       config.py
#
#       Copyright 2017 Daniel Mende <mail@c0decafe.de>
#

#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are
#       met:
#
#       * Redistributions of source code must retain the above copyright
#         notice, this list of conditions and the following disclaimer.
#       * Redistributions in binary form must reproduce the above
#         copyright notice, this list of conditions and the following disclaimer
#         in the documentation and/or other materials provided with the
#         distribution.
#       * Neither the name of the  nor the names of its
#         contributors may be used to endorse or promote products derived from
#         this software without specific prior written permission.
#
#       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#       "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#       LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#       A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#       OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#       SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#       LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#       DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#       THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#       OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from configparser import ConfigParser
from pathlib import Path
from platform import system
from random import seed
from sys import prefix

from dizzy import DizzyParseException
from dizzy.log import print_dizzy, pprint_dizzy, VERBOSE_1, VERBOSE_2, DEBUG
from dizzy.module import DizzyModule
from dizzy.library import DizzyLibrary

CONFIG = { "GLOBALS" :
               { "VERSION" : "2.0rc3",
                 "PLATFORM" : system(),
                 "RANDOM_SEED" : "1l0v3D1zzYc4us31tsR4nd0m1sr3Pr0duc4bl3!",
                 "CODEC" : "utf-8",
                 "DEFAULT_STR_LIB_NAME" : "std_string_lib.txt",
                 "INTERACTION_GLOBALS" : {},
                 "GLOBAL_LIBRARY" : DizzyLibrary(),
                 "ROOTDIR" : "~/.local/share/dizzy",
                 "CONFIGFILE" : "dizzy.conf",
                 "SESSION" : None,
                },
        }

def init_config():
    try:
        #read main config
        global CONFIG
        cfg = ConfigParser(allow_no_value=True)
        root = Path(CONFIG["GLOBALS"]["ROOTDIR"]).expanduser()
        str_lib_path = root / CONFIG["GLOBALS"]["DEFAULT_STR_LIB_NAME"]
        CONFIG["GLOBALS"]["DEFAULT_STR_LIB"] = str(str_lib_path)
        if not root.exists():
            Path.mkdir(root)
        if (root / CONFIG["GLOBALS"]["CONFIGFILE"]).exists():
            cfg.read(str(root / CONFIG["GLOBALS"]["CONFIGFILE"]))
        else:
            print_dizzy("config/init: no config file found, creating default config.")
            cfg['dizzy'] = {'module_path' : '%s/modules' % CONFIG["GLOBALS"]["ROOTDIR"],
                            'overwrite_path' : '%s/local' % CONFIG["GLOBALS"]["ROOTDIR"]}
            with (root / CONFIG["GLOBALS"]["CONFIGFILE"]).open('x') as cfile:
                cfg.write(cfile)
            Path.mkdir(root / "modules", exist_ok=True)
            Path.mkdir(root / "local", exist_ok=True)

        if not str_lib_path.exists():
            if str_lib_path.is_symlink():
                str_lib_path.unlink()
            dflt_str_lib_path = Path(prefix + CONFIG["GLOBALS"]["DEFAULT_STR_LIB_NAME"])
            if dflt_str_lib_path.exists():
                print_dizzy("config/init: creating symlink to std_lib.")
                str_lib_path.symlink_to(dflt_str_lib_path.resolve())
            dflt_str_lib_path = Path("./lib/" + CONFIG["GLOBALS"]["DEFAULT_STR_LIB_NAME"])
            if dflt_str_lib_path.exists():
                print_dizzy("config/init: creating symlink to std_lib.")
                str_lib_path.symlink_to(dflt_str_lib_path.resolve())

        CONFIG.update(dict(cfg))
        modp = CONFIG['dizzy'].get("module_path")
        if modp is None:
            print_dizzy("config/init: no module_path in config file.")
            exit(1)
        print_dizzy("config/init: using module path '%s'." % modp, VERBOSE_1)
        
        #check dependencies
        CONFIG["DEPS"] = {}
        try:
            import exrex
        except:
            CONFIG["DEPS"]["exrex"] = False
        else:
            CONFIG["DEPS"]["exrex"] = True

        try:
            import Crypto
        except:
            CONFIG["DEPS"]["Crypto"] = False
        else:
            CONFIG["DEPS"]["Crypto"] = True
        
        #load modules
        CONFIG["DIZZ"] = {}
        CONFIG["ACT"] = {}
        CONFIG["JOB"] = {}
        CONFIG["MODULES"] = {}
        CONFIG["PROBE"] = {}
        CONFIG["SESSION"] = {}
        module_path = Path(modp).expanduser()
        for f in module_path.glob("*.zip"):
            if f.is_dir():
                continue
            print_dizzy("config/init: trying to load module '%s'." % f, VERBOSE_2)
            try:
                mod = DizzyModule(str(f), CONFIG)
            except Exception as e:
                print_dizzy("config/init: can't init module '%s'." % f)
                print_dizzy(e, DEBUG)

            load = True
            #check module dependencies
            for d in mod.dependencies:
                if d in CONFIG["DEPS"]:
                    if not CONFIG["DEPS"][d]:
                        print_dizzy("config/init: can't load module '%s', dependency '%s' not found." % (mod.name, d), VERBOSE_1)
                        load = False
                        continue
                else:
                    try:
                        __import__(d)
                    except:
                        CONFIG["DEPS"][d] = False
                        print_dizzy("config/init: can't load module '%s', dependency '%s' not found." % (mod.name, d), VERBOSE_1)
                        load = False
                        continue
                CONFIG["DEPS"][d] = True
            if load:
                try:
                    mod.load()
                except Exception as e:
                    print_dizzy("config/init: can't load module '%s'." % f)
                    print_dizzy(e, DEBUG)
                    continue

                CONFIG["MODULES"][mod.name] = mod
                if mod.name in CONFIG["MODULES"]:
                    print_dizzy("config/init: module %s loaded successfully." % mod.name, VERBOSE_1)

        #load default sessions
        sessions = __import__("dizzy.session").session.__all__
        for i in sessions:
            CONFIG["SESSION"]["session." + i] = getattr(__import__('dizzy.session.' + i).session, i)

        #load default probes
        probes = __import__("dizzy.probe").probe.__all__
        for i in probes:
            CONFIG["PROBE"]["probe." + i] = getattr(__import__('dizzy.probe.' + i).probe, i)

        #look for overwrite folder
        overwritep = CONFIG["dizzy"].get("overwrite_path")
        if not overwritep is None:
            overwrite_path = Path(overwritep).expanduser()
            if not overwrite_path.is_dir():
                print_dizzy("config/init: overwrite_path is not a directory.", VERBOSE_1)
            else:
                for module in overwrite_path.iterdir():
                    if not module.is_dir():
                        print_dizzy("config/init: %s is not a directory, skipping." % module, VERBOSE_2)
                        continue
                    for component in module.iterdir():
                        if not component.is_dir():
                            print_dizzy("config/init: %s is not a directory, skipping." % component, VERBOSE_2)
                            continue
                        if component.stem == "act":
                            for act in component.iterdir():
                                if not act.is_file():
                                    print_dizzy("config/init: %s is not a file, skipping." % act, VERBOSE_2)
                                    continue
                                with act.open() as input:
                                    name = "%s/%s/%s" % (module.stem, component.stem, act.name)
                                    CONFIG["ACT"][name] = input.read()
                        elif component.stem == "dizz":
                            for dizz in component.iterdir():
                                if not dizz.is_file():
                                    print_dizzy("config/init: %s is not a file, skipping." % dizz, VERBOSE_2)
                                    continue
                                with dizz.open() as input:
                                    name = "%s/%s/%s" % (module.stem, component.stem, dizz.name)
                                    CONFIG["DIZZ"][name] = input.read()
                        elif component.stem == "job":
                            for job in component.iterdir():
                                if not job.is_file():
                                    print_dizzy("config/init: %s is not a file, skipping." % job, VERBOSE_2)
                                    continue
                                with job.open() as input:
                                    name = "%s/%s/%s" % (module.stem, component.stem, job.name)
                                    CONFIG["JOB"][name] = input.read()
                        elif component.stem == "probe":
                            for probe in component.iterdir():
                                if not probe.is_file():
                                    print_dizzy("config/init: %s is not a file, skipping." % probe, VERBOSE_2)
                                    continue
                            name = "%s.%s.probe.%s" % (overwrite_path.stem, module.stem, probe.stem)
                            obj = getattr(getattr(__import__(name), module.stem).probe, probe.stem)
                            name = "%s.probe.%s" % (module.stem, probe.stem)
                            CONFIG["PROBE"][name] = obj
                        elif component.stem == "session":
                            for session in component.iterdir():
                                if not session.is_file():
                                    print_dizzy("config/init: %s is not a file, skipping." % session, VERBOSE_2)
                                    continue
                                name = "%s.%s.session.%s" % (overwrite_path.stem, module.stem, session.stem)
                                obj = getattr(getattr(__import__(name), module.stem).session, session.stem)
                                name = "%s.session.%s" % (module.stem, session.stem)
                                CONFIG["SESSION"][name] = obj
                    if not module.stem in CONFIG["MODULES"]:
                        class Object(object):
                            pass
                        obj = Object()
                        obj.path = "%s" % module
                        obj.version = 0
                        name = "%s" % module.stem
                        CONFIG["MODULES"][name] = obj

        print_dizzy("config/init: init finished, config:", DEBUG)
        #pprint_dizzy(CONFIG, DEBUG)
    except Exception as e:
        raise DizzyParseException("Can't read config file %s: %s" % (CONFIG["GLOBALS"]["CONFIGFILE"], e))

def print_config():
    print_dizzy("### global sessions ###")
    for i in CONFIG["SESSION"]:
        if i.startswith("session."):
            print_dizzy("  - %s" % i)
    print_dizzy("### global probes ###")
    for i in CONFIG["PROBE"]:
        if i.startswith("probe."):
            print_dizzy("  - %s" % i)
    for i in CONFIG["MODULES"]:
        print_dizzy("### module '%s' loaded from '%s' v%s ###" % (i, CONFIG["MODULES"][i].path, CONFIG["MODULES"][i].version))
        for j in CONFIG["DIZZ"]:
            if j.startswith("%s/" % i):
                print_dizzy("  - %s" % j)
        for j in CONFIG["ACT"]:
            if j.startswith("%s/" % i):
                print_dizzy("  - %s" % j)
        for j in CONFIG["JOB"]:
            if j.startswith("%s/" % i):
                print_dizzy("  - %s" % j)
        for j in CONFIG["SESSION"]:
            if j.startswith("%s." % i):
                print_dizzy("  - %s" % j)
        for j in CONFIG["PROBE"]:
            if j.startswith("%s." % i):
                print_dizzy("  - %s" % j)

seed(CONFIG["GLOBALS"]["RANDOM_SEED"])
init_config()
