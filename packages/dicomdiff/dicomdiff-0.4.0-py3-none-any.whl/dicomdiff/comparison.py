from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime
from tabulate import tabulate


@dataclass
class ComparisonConfig:
    """Configuration for pseudonymization comparison behavior.

    Attributes
    ----------
    strictness_levels: Dict
        Dict mapping status names to strictness levels
    phrases: Dict
        Dict of comparison result phrases
    """

    strictness_levels: Dict[str, int] = field(
        default_factory=lambda: {
            "Removed": 4,
            "Not Present": 3,
            "Changed": 2,
            "Created": 1,
            "Unchanged": 0,
        }
    )

    phrases: Dict[str, str] = field(
        default_factory=lambda: {
            "stricter": "{} is stricter",
            "more_lenient": "{} is more lenient",
            "both_equal": "Both methods are equal",
            "both_unchanged": "Both Unchanged",
            "both_not_present": "Both Not Present",
        }
    )

    generate_report: bool = False

    def get_comparison_result(
        self, status_a: str, status_b: str, pseudo_b_name: str
    ) -> str:
        """Compare two pseudonymization statuses and return a description.

        Args
        ----
        status_a: str
            Status from first pseudonymizer
        status_b: str
            Status from second pseudonymizer
        pseudo_b_name: str
            Name of the second pseudonymizer

        Returns
        -------
        str
            String describing the comparison result
        """
        # Handle None values
        status_a_val = status_a if status_a else "Not Present"
        status_b_val = status_b if status_b else "Not Present"

        # Check for special cases
        if status_a_val == "Not Present" and status_b_val == "Not Present":
            return self.phrases["both_not_present"]

        if status_a_val == "Unchanged" and status_b_val == "Unchanged":
            return self.phrases["both_unchanged"]

        # Get strictness levels
        m1_strict = self.strictness_levels.get(status_a_val, 0)
        m2_strict = self.strictness_levels.get(status_b_val, 0)

        # Special cases for Not Present vs Unchanged
        if status_a_val == "Not Present" and status_b_val == "Unchanged":
            return self.phrases["stricter"].format(pseudo_b_name)
        if status_a_val == "Unchanged" and status_b_val == "Not Present":
            return self.phrases["more_lenient"].format(pseudo_b_name)

        # Compare strictness levels
        if m1_strict == m2_strict:
            return self.phrases["both_equal"]
        elif m1_strict > m2_strict:
            return self.phrases["more_lenient"].format(pseudo_b_name)
        else:
            return self.phrases["stricter"].format(pseudo_b_name)


def get_dicomdiff_version() -> str:
    from importlib.metadata import version

    return version("dicomdiff")


@dataclass
class ComparisonReport:
    created_at: datetime
    pseudonymizer_a_name: str
    pseudonymizer_b_name: str
    comparison_results: Dict[str, Any]
    summary: str
    version: str = field(default_factory=get_dicomdiff_version)
    warnings: List[str] = field(default_factory=list)
    pseudonymizer_a_description: str = ""
    pseudonymizer_b_description: str = ""
    dataset_description: str = ""
    ignored_tags: List[Dict[str, str]] = field(default_factory=list)

    def _format_ignored_tags_section(self) -> str:
        if not self.ignored_tags:
            return ""

        ignored_tag_table = [
            [item["tag"], item["name"], item["reason"]] for item in self.ignored_tags
        ]

        headers = ["Tag", "Name", "Reason"]

        return f"""
Ignored Tags
------------
The following {len(self.ignored_tags)} tags were ignored in the analysis:

{tabulate(ignored_tag_table, headers=headers, tablefmt="rst")}
"""

    def _format_summary(self) -> str:
        """Format the summary dictionary into readable text."""
        if isinstance(self.summary, dict):
            return (
                f"**Answer**: {self.summary.get('answer', 'N/A')}\n\n"
                f"**Reason**: {self.summary.get('reason', 'N/A')}\n\n"
                f"**Details**: {self.summary.get('summary', 'N/A')}\n"
            )
        else:
            return str(self.summary)

    def to_rst(self) -> str:
        warnings_section = self._format_warnings_section()
        dataset_section = self.dataset_description or ""
        tag_differences = self._format_tag_differences()
        ignored_tags_section = self._format_ignored_tags_section()

        pseudonymizer_a_desc = (
            f" ({self.pseudonymizer_a_description})"
            if self.pseudonymizer_a_description
            else ""
        )
        pseudonymizer_b_desc = (
            f" ({self.pseudonymizer_b_description})"
            if self.pseudonymizer_b_description
            else ""
        )

        return f"""DICOM Pseudonymization Comparison Report
========================================
:Dicomdiff Version: {self.version}
:Date: {self.created_at.strftime('%d-%m-%Y %H:%M:%S')}
:Pseudonymizer A: {self.pseudonymizer_a_name}{pseudonymizer_a_desc}
:Pseudonymizer B: {self.pseudonymizer_b_name}{pseudonymizer_b_desc}
:Dataset Description: {dataset_section}

{warnings_section}
{self._format_summary()}
{tag_differences}
{ignored_tags_section}
"""

    def _format_warnings_section(self) -> str:
        if not self.warnings:
            return ""
        warnings_list = "\n".join(f"{str(warning)}" for warning in self.warnings)
        return f"""
Warnings
--------

{warnings_list}

"""

    def _format_tag_differences(self) -> str:
        if not self.comparison_results:
            return ""

        public_tags, private_tags = self._split_tags()

        result = ""

        different_public_tags = [
            r for r in public_tags if r.get("comparison") != "Both Unchanged"
        ]

        if different_public_tags:
            result += self._format_tag_table(different_public_tags, "public")

        different_private_tags = [
            r for r in private_tags if r.get("comparison") != "Both Unchanged"
        ]

        if different_private_tags:
            result += self._format_tag_table(different_private_tags, "private")
        return result

    def _split_tags(self):
        def is_private_tag(tag_str):
            try:
                group = int(tag_str.split(",")[0], 16)
                return group % 2 != 0
            except (ValueError, IndexError):
                return False

        public_tags = [
            r for r in self.comparison_results if not is_private_tag(r.get("tag", ""))
        ]
        private_tags = [
            r for r in self.comparison_results if is_private_tag(r.get("tag", ""))
        ]

        return public_tags, private_tags

    def _format_tag_table(self, tag_list, tag_type: str) -> str:
        headers = [
            "Tag",
            "Name",
            self.pseudonymizer_a_name,
            self.pseudonymizer_b_name,
            "Comparison",
        ]

        table_data = [
            [
                r.get("tag", ""),
                r.get("name", ""),
                r.get(self.pseudonymizer_a_name, ""),
                r.get(self.pseudonymizer_b_name, ""),
                r.get("comparison", ""),
            ]
            for r in tag_list
        ]

        title = (
            f"""
Tag Differences
---------------
Differences in public tags ({len(tag_list)}):
"""
            if tag_type == "public"
            else f"""

Differences in private tags ({len(tag_list)}):
"""
        )

        return f"""{title}

{tabulate(table_data, headers=headers, tablefmt="rst")}
"""
