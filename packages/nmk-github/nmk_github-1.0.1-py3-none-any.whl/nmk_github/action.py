"""
Github actions handling module
"""

from nmk.model.resolver import NmkListConfigResolver
from nmk.utils import is_condition_set
from nmk_base.common import TemplateBuilder

# Conditional steps keys
_KEY_IF = "__if__"
_KEY_UNLESS = "__unless__"
_KEY_NAME = "name"


class ActionFileBuilder(TemplateBuilder):
    """
    Builder used to handle github workflow generation
    """

    def _filter_steps(self, steps: list[dict[str, str]]) -> list[dict[str, str]]:
        # Browse steps
        out = []
        for step in steps:
            added_step = dict(step)

            # Check conditions
            ok_to_add = True
            for key, expected in [(_KEY_IF, True), (_KEY_UNLESS, False)]:
                if key in added_step:
                    if is_condition_set(added_step[key]) != expected:
                        self.logger.debug(f"'{key}' condition not met for build step '{added_step[_KEY_NAME]}': {added_step[key]}")  # NOQA: B028
                        ok_to_add = False
                        break
                    del added_step[key]

            # No filter, add it
            if ok_to_add:
                out.append(added_step)

        return out

    def build(self, python_versions: list[str], images: list[str], build_steps: list[dict[str, str]], publish_steps: list[dict[str, str]]):
        """
        Called by the **gh.actions** to generate the Github workflow file.

        :param python_versions: List of used python versions
        :param images: List of used Github images
        :param build_steps: List of extra build steps to be generated
        :param publish_steps: List of extra publish steps to be generated
        """

        # Create directory and build from template
        self.main_output.parent.mkdir(parents=True, exist_ok=True)
        self.build_from_template(
            self.main_input,
            self.main_output,
            {
                "pythonVersions": python_versions,
                "images": images,
                "buildExtraSteps": self._filter_steps(build_steps),
                "publishExtraSteps": self._filter_steps(publish_steps),
            },
        )


class PythonVersionsResolver(NmkListConfigResolver):
    """
    Resolution logic for **githubDetectedPythonVersions**
    """

    def get_value(self, name: str) -> list[str]:
        """
        Resolves python version to be used in generated workflow file.

        Returns:

        * **githubPythonVersions** item value if not empty
        * otherwise **pythonSupportedVersions** item value if **nmk-python** plugin is used
        * otherwise an empty list

        :param name: item name
        :returns: resolved python versions list
        """

        # If "manual" configuration is provided
        gh_versions = self.model.config["githubPythonVersions"].value
        if len(gh_versions):
            return gh_versions

        # If python plugin is present
        if "pythonSupportedVersions" in self.model.config:
            return self.model.config["pythonSupportedVersions"].value

        # Default: no version
        return []
