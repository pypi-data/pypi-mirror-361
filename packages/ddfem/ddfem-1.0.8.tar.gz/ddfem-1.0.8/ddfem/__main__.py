import sys, os
try:
    import dune
except ImportError:
    dune = None
import ddfem

from importlib.metadata import version

def getVersion():
    femVersion = version("dune.fem")
    while True:
        dataPath = os.path.join(ddfem.__path__[0],"data",femVersion)
        if os.path.exists(dataPath):
            return femVersion
        ver = femVersion.split(".")
        if "dev" in ver[-1]:
            ver[-1] = 100 # try to find the largest matching release version
        lower = int(ver[-1])-1
        if lower < 0:
            raise RuntimeError(f"no suitable data for {version("dune.fem")} found")
        ver[-1] = str(lower)
        femVersion = ".".join(ver)

def main():
    if dune:
        from dune.fem.utility import FemThreadPoolExecutor
        from dune.generator import builder

        module = "intro"
        workers = 8
        if len(sys.argv)>1:
            workers = int(sys.argv[1])
            if len(sys.argv)>2:
                module = sys.argv[2]

        builder.initialize()

        femVersion = getVersion()
        dataPath = os.path.join(ddfem.__path__[0],"data",femVersion)
        print(f"obtaining data from {dataPath}")
        onlyCompile = []
        if not module == "all":
            filename = os.path.join(dataPath,module+".modules")
            with open(filename,"r") as f:
                onlyCompile = f.readlines()
            onlyCompile = set([c.strip()+".cc" for c in onlyCompile])
        else:
            onlyCompile = os.listdir(dataPath)
        with FemThreadPoolExecutor(max_workers=workers) as executor:
            for file in onlyCompile:
                filename = os.path.join(dataPath,os.fsdecode(file))
                if ( not filename.endswith(".cc") or
                     not os.path.exists(filename) ):
                    continue
                with open(filename,"r") as f:
                    executor.submit( builder.load, file.replace(".cc",""), f.read(), None )

if __name__ == "__main__":
    main()
