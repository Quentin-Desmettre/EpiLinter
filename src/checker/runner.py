import importlib
import sys
import os

module_source_folder = os.path.dirname(sys.argv[0])
os.chdir(module_source_folder)

import vera

vera.loadTokens(open(sys.argv[1]).read(), sys.argv[2])
vera.setSourceFileNames([sys.argv[2]])

modules = sys.argv[3:]
for module in modules:
    if module[-1] == '\n':
        module = module[:-1]
    # if module != "C-L3" and module != "C-L4":
    #     continue
    importlib.import_module(module)
vera.logReports()