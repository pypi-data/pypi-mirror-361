import pandas as pd
import pydicom
import json
import os

from typing import List, Optional, Dict, Set, Tuple, Union
from tqdm import tqdm

from dicomdiff.pseudonymizer import Pseudonymizer, InferredPseudonymizer
from dicomdiff.main import compare_dicom_datasets
from dicomdiff.comparison import ComparisonConfig, ComparisonReport
from dicomdiff.datamodel import DicomDifference
from dicomdiff.context import ComparisonContext


class InconsistentPseudoError(Exception):
    pass


def to_json(exception_list, filepath):
    def tag_sort_key(tag):
        group, element = tag.split(",")
        return (int(group, 16), int(element, 16))

    sorted_tags = dict(sorted(exception_list.items(), key=lambda x: tag_sort_key(x[0])))

    with open(filepath, "w") as f:
        json.dump(sorted_tags, f, indent=2)


def from_json(filepath):
    if not os.path.exists(filepath):
        return {}

    with open(filepath, "r") as f:
        return json.load(f)


def generate_pseudonymization_summary(
    file_paths: List[str],
    pseudonymizer_a: Pseudonymizer,
    pseudonymizer_b: Pseudonymizer,
    context: ComparisonContext = None,
    check_consistency: bool = True,
    config: ComparisonConfig = None,
) -> pd.DataFrame:
    """Generate a summary of pseudonymization differences between two pseudonymizers.

    Args
    ----
    file_paths: List[str]
        List of DICOM file paths to process
    pseudonymizer_a: Pseudonymizer
        First pseudonymizer instance
    pseudonymizer_b: Pseudonymizer
        Second pseudonymizer instance
    pseudonymizer_a_name: str, optional
        Display name for the first pseudonymizer. If None, will use class name or default
    pseudonymizer_b_name: str, optional
        Display name for the second pseudonymizer. If None, will use class name or default
    exception_path: str, optional
        Path to save exception configuration
    check_consistency: bool
        Whether to check for inconsistencies
    config: ComparisonConfig, optional
        Configuration for comparison behavior

    Returns
    -------
    pd.DataFrame
        DataFrame with pseudonymization comparison results
    """
    if config is None:
        config = ComparisonConfig()

    if context.pseudonymizer_a_name is None:
        context.pseudonymizer_a_name = get_pseudonymizer_name(
            pseudonymizer_a, "PseudonymizerA"
        )
    if context.pseudonymizer_b_name is None:
        context.pseudonymizer_b_name = get_pseudonymizer_name(
            pseudonymizer_b, "PseudonymizerB"
        )

    tag_data = initialize_tag_data(
        pseudonymizer_a,
        pseudonymizer_b,
        context.pseudonymizer_a_name,
        context.pseudonymizer_b_name,
    )
    tag_data = process_dicom_files(file_paths, tag_data, check_consistency)
    results = create_summary_results(tag_data)

    results, ignored_tags = _handle_exception_config(results, context.exception_path)

    results = sorted(
        results, key=lambda x: tuple(int(part, 16) for part in x["tag"].split(","))
    )

    df = pd.DataFrame(results)

    if df.empty:
        print("No tags found in the provided DICOM files.")
        return df

    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_columns", None)

    comparison_counts = _count_comparison_results(df)
    strictness_analysis = analyze_overall_strictness(
        df, context.pseudonymizer_a_name, context.pseudonymizer_b_name
    )

    if config.generate_report:
        from datetime import datetime

        report = ComparisonReport(
            created_at=datetime.now(),
            pseudonymizer_a_name=context.pseudonymizer_a_name,
            pseudonymizer_b_name=context.pseudonymizer_b_name,
            comparison_results=results,
            summary=strictness_analysis,
            warnings=tag_data.get("consistency_warnings", []),
            pseudonymizer_a_description=getattr(pseudonymizer_a, "description", "")
            or "",
            pseudonymizer_b_description=getattr(pseudonymizer_b, "description", "")
            or "",
            dataset_description=context.dataset_description,
            ignored_tags=ignored_tags,
        )

        report_filename = f"report_{datetime.now().strftime('%d-%m-%Y_%H%M%S')}.rst"
        with open(report_filename, "w") as f:
            f.write(report.to_rst())
        full_path = os.path.abspath(report_filename)
        print(f"RST report saved: {full_path}")
    else:
        print(f"\n{'=' * 60}")
        print("STRICTNESS ANALYSIS")
        print(f"{'=' * 60}")
        print(
            f"Is {context.pseudonymizer_a_name} more strict than or as strict as "
            f"{context.pseudonymizer_b_name}?"
        )
        print(f"Answer: {strictness_analysis['answer']}")
        print(f"Reason: {strictness_analysis['reason']}")
        print(f"Summary: {strictness_analysis['summary']}")
        print(f"{'=' * 60}\n")

        print("Comparison results (public tags only):")
        for comparison, count in sorted(comparison_counts.items()):
            print(f"{comparison:<55} {count:>3}")

        if ignored_tags:
            print(f"\n{'=' * 60}")
            print("IGNORED TAGS")
            print(f"{'=' * 60}")
            print(
                f"The following {len(ignored_tags)} tags were ignored in the analysis:"
            )
            for item in ignored_tags:
                print(f"  - {item['tag']} ({item['name']}): {item['reason']}")

    return df


def generate_exception_list(summary):
    exception_list = {}

    for result in summary:
        comparison = result.get("comparison", "")
        tag = result.get("tag", "")

        if "stricter" in comparison:
            exception_list[tag] = {"ignore": False, "reason": ""}
    return exception_list


def apply_exceptions_to_results(results, exception_config):
    ignored_tags = []

    for result in results:
        tag = result.get("tag", "")

        if tag in exception_config and exception_config[tag].get("ignore", False):
            reason = exception_config[tag].get("reason", "")
            comparison = result.get("comparison", "")
            name = result.get("name", "Unknown")

            result["comparison"] = f"{comparison} (Ignored)"

            ignored_tags.append(
                {
                    "tag": tag,
                    "name": name,
                    "reason": reason if reason else "No reason provided",
                }
            )

    return results, ignored_tags


def initialize_tag_data(
    pseudonymizer_a: Pseudonymizer,
    pseudonymizer_b: Pseudonymizer,
    pseudonymizer_a_name: str,
    pseudonymizer_b_name: str,
) -> Dict:
    """Initialize data structures for tracking tag information."""
    return {
        "tag_summary": {},
        "tag_methods": {},
        "all_tags": set(),
        "tag_existence": {},
        "pseudonymizers": {
            "a": pseudonymizer_a,
            "b": pseudonymizer_b,
        },
        "pseudonymizer_names": {
            "a": pseudonymizer_a_name,
            "b": pseudonymizer_b_name,
        },
    }


def process_dicom_files(
    file_paths: List[str], tag_data: Dict, check_consistency: bool
) -> Dict:
    """Process DICOM files and collect tag information."""
    for file_path in tqdm(file_paths, desc="Processing DICOM files"):
        try:
            source_ds = pydicom.dcmread(file_path, force=True)

            process_source_dataset(source_ds, tag_data, file_path)
            process_pseudonymization(source_ds, tag_data, file_path, "a")
            process_pseudonymization(source_ds, tag_data, file_path, "b")

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    tag_data["inconsistent_tags"] = set()

    if check_consistency:
        try:
            inconsistent_tags, error_msg = check_pseudonymization_consistency(
                tag_data["tag_methods"]
            )

            if error_msg:
                tag_data["inconsistent_tags"] = inconsistent_tags

                print("")
                print(f"\033[33;1mWARNING:\033[0m\033[33m {error_msg}\033[0m")
                print(
                    f"\nRemoving {len(inconsistent_tags)} inconsistent tags from results:"
                )
                for tag in inconsistent_tags:
                    tag_name = (
                        tag_data["tag_summary"].get(tag, {}).get("name", "Unknown")
                    )
                    print(f"  - {tag} ({tag_name})")
                print("\nContinuing with analysis despite inconsistencies.")

                tag_data["consistency_warnings"] = [error_msg]

        except InconsistentPseudoError as e:
            print(
                f"Warning: {str(e)}\nContinuing with analysis despite inconsistencies."
            )
            tag_data["consistency_warnings"] = [str(e)]

    return tag_data


def process_source_dataset(source_ds, tag_data, file_path):
    tag_existence = tag_data["tag_existence"]
    tag_summary = tag_data["tag_summary"]
    all_tags = tag_data["all_tags"]

    for elem in source_ds:
        tag = format_tag(elem.tag)

        if tag not in tag_existence:
            tag_existence[tag] = {}
        if file_path not in tag_existence[tag]:
            tag_existence[tag][file_path] = {
                "source": False,
                "a": False,
                "b": False,
            }
        tag_existence[tag][file_path]["source"] = True

        all_tags.add(tag)
        if tag not in tag_summary:
            tag_summary[tag] = {"name": elem.name}


def process_pseudonymization(source_ds, tag_data, file_path, method):
    """Process pseudonymization for a specific method and track changes.

    Args:
    ----
        source_ds: Source DICOM dataset
        tag_data: Tag tracking data structure
        file_path: Path to the file being processed
        method: "a" or "b" to specify which pseudonymizer to use
    """
    pseudo_name = tag_data["pseudonymizer_names"][method]
    pseudonymizer = tag_data["pseudonymizers"][method]

    try:
        pseudonymized_ds = pseudonymizer.pseudonimize(source_ds)
        diffs = compare_dicom_datasets(source_ds, pseudonymized_ds)

        process_differences(
            tag_data["tag_summary"],
            diffs,
            pseudo_name,
            tag_data["tag_methods"],
            file_path,
            file_tags=set(),
            all_tags=tag_data["all_tags"],
        )

        source_tags = set(format_tag(elem.tag) for elem in source_ds)
        track_tags_in_dataset(
            pseudonymized_ds, file_path, method, tag_data, source_tags=source_tags
        )

        if isinstance(pseudonymizer, InferredPseudonymizer):
            _handle_inferred_pseudonymizer_removals(
                source_ds, pseudonymized_ds, tag_data, file_path, method
            )

    except Exception as e:
        print(f"Error processing {file_path} with {pseudo_name}: {e}")


def _handle_inferred_pseudonymizer_removals(
    source_ds, pseudonymized_ds, tag_data, file_path, method
):
    """Handle explicit removal detection for InferredPseudonymizer."""
    source_tags = set(source_ds.keys())
    pseudo_tags = set(pseudonymized_ds.keys())

    # Find tags that were removed
    removed_tags = source_tags - pseudo_tags

    for tag in removed_tags:
        # Skip file meta tags
        if tag.group == 0x0002:
            continue

        try:
            name = source_ds[tag].name if hasattr(source_ds[tag], "name") else str(tag)
        except (KeyError, AttributeError):
            name = str(tag)

        pseudo_name = tag_data["pseudonymizer_names"][method]
        formatted_tag = format_tag(tag)

        # Only update if not already explicitly set by differences
        if (
            formatted_tag not in tag_data["tag_summary"]
            or pseudo_name not in tag_data["tag_summary"][formatted_tag]
        ):
            _update_tag_summary(
                tag_data["tag_summary"], formatted_tag, name, pseudo_name, "Removed"
            )
            _update_tag_methods(
                tag_data["tag_methods"],
                formatted_tag,
                pseudo_name,
                "Removed",
                file_path,
            )


def track_tags_in_dataset(ds, file_path, method, tag_data, source_tags=None):
    tag_existence = tag_data["tag_existence"]
    tag_summary = tag_data["tag_summary"]
    all_tags = tag_data["all_tags"]
    pseudo_name = tag_data["pseudonymizer_names"].get(method, method.upper())

    for elem in ds:
        tag = format_tag(elem.tag)
        if tag not in tag_existence:
            tag_existence[tag] = {}

        if file_path not in tag_existence[tag]:
            tag_existence[tag][file_path] = {
                "source": False,
                "a": False,
                "b": False,
            }
        tag_existence[tag][file_path][method] = True

        if source_tags is not None and tag not in source_tags:
            if tag not in tag_summary or pseudo_name not in tag_summary[tag]:
                if tag not in tag_summary:
                    tag_summary[tag] = {"name": elem.name}
                tag_summary[tag][pseudo_name] = "Created"

        all_tags.add(tag)


def create_summary_results(tag_data) -> List[Dict]:
    results = []
    all_tags = tag_data["all_tags"]
    tag_summary = tag_data["tag_summary"]
    tag_existence = tag_data["tag_existence"]
    inconsistent_tags = tag_data.get("inconsistent_tags", set())
    pseudo_a_name = tag_data["pseudonymizer_names"]["a"]
    pseudo_b_name = tag_data["pseudonymizer_names"]["b"]
    config = tag_data.get("config", ComparisonConfig())

    total_tags = len(all_tags)
    filtered_tags = all_tags - inconsistent_tags

    if inconsistent_tags:
        print(
            f"\nFiltering results: {len(filtered_tags)} of {total_tags} tags included"
        )
        print(f"Excluded {len(inconsistent_tags)} inconsistent tags")

    for tag in filtered_tags:
        info = tag_summary.get(tag, {})
        status_a, status_b = determine_tag_status(
            tag, info, tag_existence, pseudo_a_name, pseudo_b_name
        )

        result = {
            "tag": tag,
            "name": info.get("name", "Unknown"),
            pseudo_a_name: status_a,
            pseudo_b_name: status_b,
            "comparison": compare_methods(status_a, status_b, pseudo_b_name, config),
        }
        results.append(result)
    return results


def determine_tag_status(
    tag, info, tag_existence, pseudo_a_name, pseudo_b_name
) -> Tuple[str, str]:
    status_a = info.get(pseudo_a_name)
    status_b = info.get(pseudo_b_name)

    patterns = analyze_tag_existence_patterns(tag, tag_existence)

    patterns["current_tag"] = tag

    a_indicates_source = status_a in ["Changed", "Removed", "Unchanged"]
    b_indicates_source = status_b in ["Changed", "Removed", "Unchanged"]

    final_status_a = determine_pseudonymizer_status(
        status_a, patterns, "a", other_method_indicates_source=b_indicates_source
    )
    final_status_b = determine_pseudonymizer_status(
        status_b, patterns, "b", other_method_indicates_source=a_indicates_source
    )

    return final_status_a, final_status_b


def analyze_tag_existence_patterns(tag, tag_existence) -> Dict:
    patterns = {
        "tag_only_in_source": False,
        "tag_only_in_a": False,
        "tag_only_in_b": False,
        "tag_in_source_and_a": False,
        "tag_in_source_and_b": False,
    }

    for _, existence_dict in tag_existence.get(tag, {}).items():
        source = existence_dict.get("source", False)
        a = existence_dict.get("a", False)
        b = existence_dict.get("b", False)

        if source and not a and not b:
            patterns["tag_only_in_source"] = True
        if not source and a and not b:
            patterns["tag_only_in_a"] = True
        if not source and not a and b:
            patterns["tag_only_in_b"] = True
        if source and a:
            patterns["tag_in_source_and_a"] = True
        if source and b:
            patterns["tag_in_source_and_b"] = True

    return patterns


def _get_status_from_patterns_for_method(
    patterns: Dict[str, bool], method: str
) -> Optional[str]:
    """Helper function to determine status based on patterns for a specific method."""
    if method == "a":
        if patterns.get("tag_only_in_a", False):
            return "Created"
        elif patterns.get("tag_in_source_and_a", False):
            return "Unchanged"
        elif patterns.get("tag_only_in_source", False):
            return "Removed"
    else:  # method == "b"
        if patterns.get("tag_only_in_b", False):
            return "Created"
        elif patterns.get("tag_in_source_and_b", False):
            return "Unchanged"
        elif patterns.get("tag_only_in_source", False):
            return "Removed"

    return None


def _check_removed_by_comparison(
    patterns: Dict[str, bool], method: str
) -> Optional[str]:
    """Helper to determine if tag was removed by comparing with the other method."""
    if method == "a" and patterns.get("tag_in_source_and_b", False):
        return "Removed"
    elif method == "b" and patterns.get("tag_in_source_and_a", False):
        return "Removed"

    return None


def _check_if_removed_from_source(patterns: Dict[str, bool], method: str) -> bool:
    """Check if tag was in source but missing from this method's output."""
    if method == "a":
        return (
            patterns.get("tag_in_source_and_b", False)
            or patterns.get("tag_only_in_source", False)
        ) and not patterns.get("tag_in_source_and_a", False)
    else:  # method == "b"
        return (
            patterns.get("tag_in_source_and_a", False)
            or patterns.get("tag_only_in_source", False)
        ) and not patterns.get("tag_in_source_and_b", False)


def _check_cross_method_removal(patterns: Dict[str, bool], method: str) -> bool:
    """Check for cross-method removal cases."""
    if method == "a":
        return patterns.get("tag_in_source_and_b", False) and not patterns.get(
            "tag_in_source_and_a", False
        )
    else:  # method == "b"
        return patterns.get("tag_in_source_and_a", False) and not patterns.get(
            "tag_in_source_and_b", False
        )


def _check_tag_exists_in_source(
    patterns: Dict[str, bool], other_method_indicates_source: bool
) -> bool:
    """Check if there's evidence the tag existed in the source."""
    tag_exists_in_source = any(
        [
            patterns.get("tag_in_source_and_a", False),
            patterns.get("tag_in_source_and_b", False),
            patterns.get("tag_only_in_source", False),
        ]
    )

    if other_method_indicates_source:
        tag_exists_in_source = True

    return tag_exists_in_source


def determine_pseudonymizer_status(
    change_status: str,
    patterns: Dict[str, bool],
    method: str,
    other_method_indicates_source: bool = False,
) -> str:
    """Determine the status for a tag with a specific pseudonymizer."""

    # Use explicit change_status if available (highest priority)
    if change_status:
        return change_status

    # Check if tag was in source but missing from this method's output
    if _check_if_removed_from_source(patterns, method):
        return "Removed"

    # Direct check for tag that exists only in source (both methods removed it)
    if patterns.get("tag_only_in_source", False):
        return "Removed"

    # Cross-method removal checks
    if _check_cross_method_removal(patterns, method):
        return "Removed"

    # Use pattern-based status determination
    status = _get_status_from_patterns_for_method(patterns, method)
    if status:
        return status

    # Cross-comparison removal check
    status = _check_removed_by_comparison(patterns, method)
    if status:
        return status

    # Check if there's evidence the tag existed in SOURCE
    # This handles the InferredPseudonymizer case where one method has explicit
    # change_status but the other method has no patterns
    tag_exists_in_source = _check_tag_exists_in_source(
        patterns, other_method_indicates_source
    )

    # If tag existed in source but this method has no explicit status or patterns,
    # it means this method removed/doesn't include the tag
    if tag_exists_in_source:
        return "Removed"

    # If truly no evidence in source, then it's not present for this method
    return "Not Present"


def format_tag(tag):
    if isinstance(tag, int):
        group = tag >> 16
        element = tag & 0xFFFF
        return f"{group:04x},{element:04x}"
    return str(tag)


def _extract_diff_values(diff: DicomDifference) -> Tuple[Union[str, int], str, str]:
    """Extract key values from a DicomDifference object."""
    if isinstance(diff, dict):
        tag_value = diff.get("tag")
        name = diff.get("name")
        change_type = diff.get("change_type")
    else:
        tag_value = diff.tag
        name = diff.name
        change_type = (
            diff.change_type.value
            if hasattr(diff.change_type, "value")
            else str(diff.change_type)
        )
    return tag_value, name, change_type


def _update_tag_summary(tag_summary, tag, name, method, change_type):
    """Update the tag summary dictionary."""
    formatted_tag = format_tag(tag) if not isinstance(tag, str) else tag

    if formatted_tag not in tag_summary:
        tag_summary[formatted_tag] = {"name": name}

    tag_summary[formatted_tag][method] = change_type


def _update_tag_methods(tag_methods, tag, method, change_type, file_path):
    """Update the tag methods tracking."""
    formatted_tag = format_tag(tag) if not isinstance(tag, str) else tag

    if formatted_tag not in tag_methods:
        tag_methods[formatted_tag] = {}

    if method not in tag_methods[formatted_tag]:
        tag_methods[formatted_tag][method] = {}

    if change_type not in tag_methods[formatted_tag][method]:
        tag_methods[formatted_tag][method][change_type] = set()

    tag_methods[formatted_tag][method][change_type].add(file_path)


def process_differences(
    tag_summary: Dict[str, Dict[str, any]],
    differences: List[Union[DicomDifference, Dict[str, any]]],
    method: str,
    tag_methods: Dict[str, Dict[str, Dict[str, Set[str]]]] = None,
    file_path: str = None,
    file_tags: Set[str] = None,
    all_tags: Set[str] = None,
):
    """Process differences between datasets and update tracking structures."""
    for diff in differences:
        # Get normalized difference object and extract values
        tag_value, name, change_type = _extract_diff_values(diff)

        # Format the tag
        tag = format_tag(tag_value)

        # Update all_tags if provided
        if all_tags is not None:
            all_tags.add(tag)

        # Update tag summary
        _update_tag_summary(tag_summary, tag, name, method, change_type)

        # Update file_tags if provided
        if file_tags is not None:
            file_tags.add(tag)

        # Update tag_methods if provided
        if tag_methods is not None and file_path is not None:
            _update_tag_methods(tag_methods, tag, method, change_type, file_path)


def check_pseudonymization_consistency(tag_methods):
    """Check for inconsistencies in pseudonymization methods across files.

    Args
    ----§
    tag_methods: Dict
        Dict containing tag methods and change types

    Returns
    -------
    tuple
        (set of inconsistent tags, error message)
    """
    inconsistencies = []
    inconsistent_tags = set()

    for tag, methods in tag_methods.items():
        for method_name, change_types in methods.items():
            if isinstance(change_types, dict) and len(change_types) > 1:
                inconsistent_tags.add(tag)

                # Create inconsistency record
                inconsistency = {
                    "tag": tag,
                    "method": method_name,
                    "change_types": list(change_types.keys()),
                    "files": {},
                }
                for change_type, file_set in change_types.items():
                    inconsistency["files"][change_type] = list(file_set)

                inconsistencies.append(inconsistency)

    # Prepare error message if inconsistencies exist
    if inconsistencies:
        error_msg = "Inconsistent pseudonymization detected."
        for inc in inconsistencies:
            error_msg += (
                f"\nTag **{inc['tag']}** was handled "
                f"inconsistently by {inc['method']}:\n\n"
            )
            for change_type, files_list in inc["files"].items():
                file_examples = files_list[:3]
                file_count = len(files_list)
                error_msg += (
                    f"  - **{change_type}**: "
                    f"{file_count} files, e.g., {file_examples}\n"
                )

        return inconsistent_tags, error_msg

    return set(), None


def compare_methods(status_a, status_b, pseudo_b_name, config=None):
    """
    Compare pseudonymization methods to determine which is stricter.

    Args
    ----
    status_a: Status of tag in first pseudonymizer
    status_b: Status of tag in second pseudonymizer
    pseudo_b_name: Name of second pseudonymizer
    config: Optional ComparisonConfig to use

    Returns
    -------
    String describing the comparison result
    """
    if config is None:
        config = ComparisonConfig()

    return config.get_comparison_result(status_a, status_b, pseudo_b_name)


def analyze_overall_strictness(
    summary_df: pd.DataFrame,
    pseudonymizer_a_name: str = "PseudoA",
    pseudonymizer_b_name: str = "PseudoB",
) -> Dict[str, Union[str, List[str]]]:
    """Analyze overall strictness comparison between two pseudonymizers.

    Args
    ----
    summary_df: pd.DataFrame
        DataFrame with pseudonymization comparison results
    pseudonymizer_a_name: str
        Name of the first pseudonymizer
    pseudonymizer_b_name: str
        Name of the second pseudonymizer

    Returns
    -------
    Dict containing:
        - 'answer': 'YES' or 'NO' for whether pseudonymizer_a is as strict or
          stricter than pseudonymizer_b
        - 'reason': Explanation for the answer
        - 'stricter_tags': List of tags where pseudonymizer_a is stricter
        - 'less_strict_tags': List of tags where pseudonymizer_a is less strict
        - 'summary': Overall comparison summary
    """
    stricter_count = 0
    less_strict_count = 0
    equal_count = 0

    stricter_tags = []
    less_strict_tags = []

    for _, row in summary_df.iterrows():
        comparison = row.get("comparison", "")
        tag = row.get("tag", "Unknown")

        if "(Ignored" in comparison:
            continue

        if f"{pseudonymizer_b_name} is more lenient" in comparison:
            stricter_count += 1
            stricter_tags.append(tag)
        elif f"{pseudonymizer_b_name} is stricter" in comparison:
            less_strict_count += 1
            less_strict_tags.append(tag)
        elif (
            "Both methods are equal" in comparison
            or "Both Unchanged" in comparison
            or "Both Not Present" in comparison
        ):
            equal_count += 1

    if less_strict_count == 0:
        answer = "YES"
        if stricter_count > 0:
            reason = (
                f"{pseudonymizer_a_name} is more strict than or as strict as "
                f"{pseudonymizer_b_name}. {pseudonymizer_a_name} handles "
                f"{stricter_count} tags more strictly and no tags less strictly."
            )
        else:
            reason = (
                f"{pseudonymizer_a_name} is as strict as {pseudonymizer_b_name}. "
                f"Both pseudonymizers handle all tags equally."
            )
    else:
        answer = "NO"
        reason = (
            f"{pseudonymizer_a_name} is not as strict as {pseudonymizer_b_name}. "
            f"These {len(less_strict_tags)} tags were processed less strictly by "
            f"{pseudonymizer_a_name}: {', '.join(less_strict_tags[:5])}"
        )
        if len(less_strict_tags) > 5:
            reason += f" and {len(less_strict_tags) - 5} more"

    summary = (
        f"Comparison: {stricter_count} tags stricter, {less_strict_count} tags "
        f"less strict, {equal_count} tags equal"
    )

    return {
        "answer": answer,
        "reason": reason,
        "stricter_tags": stricter_tags,
        "less_strict_tags": less_strict_tags,
        "summary": summary,
        "comparison_counts": {
            "stricter": stricter_count,
            "less_strict": less_strict_count,
            "equal": equal_count,
        },
    }


def get_pseudonymizer_name(pseudonymizer: Pseudonymizer, default_name: str) -> str:
    """Get the name of a pseudonymizer, using class name if no name provided.

    Args
    ----
    pseudonymizer: Pseudonymizer
        The pseudonymizer instance
    default_name: str
        Default name to use if no specific name can be determined

    Returns
    -------
    str
        Name to use for the pseudonymizer
    """
    if hasattr(pseudonymizer, "name") and pseudonymizer.name:
        return pseudonymizer.name

    class_name = pseudonymizer.__class__.__name__
    if class_name and class_name != "Pseudonymizer":
        return class_name

    return default_name


def _count_comparison_results(df: pd.DataFrame) -> Dict[str, int]:
    """Count and group comparison results, combining ignored tags."""
    comparison_counts = {}
    ignored_counts = {}

    for _, row in df.iterrows():
        comp = row.get("comparison", "")

        if "(Ignored:" in comp or "(Ignored)" in comp:
            base_comp = comp.split(" (Ignored")[0]
            if base_comp not in ignored_counts:
                ignored_counts[base_comp] = 0
            ignored_counts[base_comp] += 1
        else:
            comparison_counts[comp] = comparison_counts.get(comp, 0) + 1

    for base_comp, count in ignored_counts.items():
        summary_key = f"{base_comp}, but ignored"
        comparison_counts[summary_key] = count

    return comparison_counts


def _handle_exception_config(results, exception_path: str):
    """Handle loading and applying exception configuration."""
    ignored_tags = []

    if not os.path.exists(exception_path):
        exception_list = generate_exception_list(results)
        to_json(exception_list, exception_path)
        exception_config = {}
    else:
        exception_config = from_json(exception_path)

    if exception_config:
        results, ignored_tags = apply_exceptions_to_results(results, exception_config)

    return results, ignored_tags
