from TBM_RezManager import utils
import os

class Build(utils.Build):
    def pre_build(self):
        pass

    def post_build(self):
        dest_bin = os.path.join(self.build_path, "bin")
        utils.make_dir(dest_bin)

        #launchers
        for ext in ["exe", "bat"]:
            self.create_launcher(data=[self.project], 
                                path=dest_bin, 
                                name="%s_creator"%self.project, 
                                cmd = "python -c \"from qargparser.uiCreator import show;show()\"",
                                ext=ext,
                                icon=None)

        #Package info file
        self.create_package_info(
            os.path.join(self.build_path, "qargparser", '__version__.py'))

if __name__ == "__main__":
    Build(exclude_patterns=["*.py", "__pycache__"], 
          keep_roots=["qargparser", "resources", "README.md", "examples"])
