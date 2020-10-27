"""
Action to resolve Python dependencies using PIP
"""

from aws_lambda_builders.actions import BaseAction, Purpose, ActionFailedError
from aws_lambda_builders.workflows.python_pip.utils import OSUtils
from .exceptions import MissingPipError
from .packager import PythonPipDependencyBuilder, PackagerError, DependencyBuilder, SubprocessPip, PipRunner


class PythonPipBuildAction(BaseAction):

    NAME = "ResolveDependencies"
    DESCRIPTION = "Installing dependencies from PIP"
    PURPOSE = Purpose.RESOLVE_DEPENDENCIES
    LANGUAGE = "python"

    def __init__(self, artifacts_dir, scratch_dir, manifest_path, runtime, binaries):
        self.artifacts_dir = artifacts_dir
        self.manifest_path = manifest_path
        self.scratch_dir = scratch_dir
        self.runtime = runtime
        self.binaries = binaries

    def execute(self):
        os_utils = OSUtils()
        python_path = self.binaries[self.LANGUAGE].binary_path
        try:
            pip = SubprocessPip(osutils=os_utils, python_exe=python_path)
        except MissingPipError as ex:
            raise ActionFailedError(str(ex)) from ex
        pip_runner = PipRunner(python_exe=python_path, pip=pip)
        dependency_builder = DependencyBuilder(osutils=os_utils, pip_runner=pip_runner, runtime=self.runtime)

        package_builder = PythonPipDependencyBuilder(
            osutils=os_utils, runtime=self.runtime, dependency_builder=dependency_builder
        )
        try:
            package_builder.build_dependencies(
                artifacts_dir_path=self.artifacts_dir,
                scratch_dir_path=self.scratch_dir,
                requirements_path=self.manifest_path,
            )
        except PackagerError as ex:
            raise ActionFailedError(str(ex)) from ex
