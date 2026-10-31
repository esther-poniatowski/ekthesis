"""
Validator of a SARIF log against the findings profile of Elenchos, written from the profile text.

The profile places two sets of requirements on a log:

- the rejected input of its section 5.6: the rules on which the identity or the verdict of the gate
  depends, which the gate enforces on every log;
- the requirements of its sections 3 and 4 on a producer, which include the rejected input and add
  the objects that the gate does not check, such as the complete list of rules.

Each function reports every violation as a string naming the object at fault. The module imports no
package of Elenchos, as the profile requires of a producer.

Functions
---------
rejections(log) -> list of str
    Violations of section 5.6, for which the gate rejects a log.
profile_violations(log) -> list of str
    Violations of sections 3 and 4 by the log of a producer, section 5.6 included.
"""

import re
from collections.abc import Mapping
from urllib.parse import unquote

SARIF_SCHEMA = (
    "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json"
)
GATE_DRIVER = "elenchos"
DRIVER_NAME = re.compile(r"[a-z][a-z0-9-]*\Z")
RULE_ID = re.compile(r"[a-z0-9][a-z0-9._-]*(/[a-z0-9][a-z0-9._-]*)*\Z")
VERSIONED_KEY = re.compile(r"([^/]+/)*v(0|[1-9][0-9]*)\Z")
LEVELS = {"error", "warning", "note"}
NOTIFICATION_LEVELS = {"none", "note", "warning", "error"}
COLUMN_KINDS = {"unicodeCodePoints", "utf16CodeUnits"}
LOCUS_TYPES = {"link", "task", "slot", "term", "symbol"}
ABSENT = ("kind", "baselineState")


def rejections(log: object) -> list[str]:
    """Return the violations of section 5.6 by `log`, empty when the gate accepts the log."""
    return _log_violations(log, producer=False)


def profile_violations(log: object) -> list[str]:
    """Return the violations of sections 3 and 4 by the log of a producer, empty if it conforms."""
    return _log_violations(log, producer=True)


def _log_violations(log: object, producer: bool) -> list[str]:
    """Return the violations by a log: section 5.6, and sections 3 and 4 when `producer` is set."""
    if not isinstance(log, Mapping):
        return ["the log is no object"]
    problems = []
    if log.get("version") != "2.1.0":
        problems.append("sarifLog.version is not 2.1.0")
    if producer and log.get("$schema", SARIF_SCHEMA) != SARIF_SCHEMA:
        problems.append("sarifLog.$schema is not the schema URI of errata 01")
    runs = log.get("runs")
    if not isinstance(runs, list) or not runs:
        return [*problems, "sarifLog.runs holds no run"]
    for index, run in enumerate(runs):
        problems.extend(f"runs[{index}]: {problem}" for problem in _run_violations(run, producer))
    return problems


def _run_violations(run: object, producer: bool) -> list[str]:
    """Return the violations of section 3, and of section 4 by the results of one run."""
    if not isinstance(run, Mapping):
        return ["the run is no object"]
    problems = []
    tool = run.get("tool")
    driver = tool.get("driver") if isinstance(tool, Mapping) else None
    if not isinstance(driver, Mapping):
        return ["tool.driver is absent"]
    name = driver.get("name")
    if not isinstance(name, str) or not DRIVER_NAME.match(name):
        problems.append(f"tool.driver.name {name!r} breaks [a-z][a-z0-9-]*")
        name = ""
    elif name == GATE_DRIVER:
        problems.append(f"tool.driver.name is {GATE_DRIVER}, the driver of the gate")
    described = None
    if producer:
        if not any(isinstance(driver.get(key), str) for key in ("version", "semanticVersion")):
            problems.append("tool.driver holds neither version nor semanticVersion")
        described = _rule_descriptors(driver.get("rules"), problems)
        if driver.get("isComprehensive", True) is not True:
            problems.append("tool.driver.isComprehensive is written, and is not true")
    incomplete = _invocation_violations(run.get("invocations"), producer, problems)
    if "results" not in run and incomplete:
        return problems
    results = run.get("results")
    if not isinstance(results, list):
        return [*problems, "results is no array, and the run declares no incomplete analysis"]
    if producer and results and run.get("columnKind") not in COLUMN_KINDS:
        problems.append(f"columnKind {run.get('columnKind')!r} is not admitted")
    for index, result in enumerate(results):
        problems.extend(
            f"results[{index}]: {problem}"
            for problem in _result_violations(result, name, described, producer)
        )
    return problems


def _rule_descriptors(rules: object, problems: list[str]) -> set[str]:
    """Return the rule identifiers described by the required array `rules`."""
    if not isinstance(rules, list):
        problems.append("tool.driver.rules is no array")
        return set()
    described = set()
    for rule in rules:
        identifier = rule.get("id") if isinstance(rule, Mapping) else None
        if not isinstance(identifier, str):
            problems.append("a rule descriptor holds no id")
            continue
        described.add(identifier)
        summary = rule.get("shortDescription")
        if not isinstance(summary, Mapping) or not isinstance(summary.get("text"), str):
            problems.append(f"rule {identifier} holds no shortDescription.text")
        configuration = rule.get("defaultConfiguration")
        level = configuration.get("level") if isinstance(configuration, Mapping) else None
        if level not in LEVELS:
            problems.append(f"rule {identifier} holds no defaultConfiguration.level")
    return described


def _invocation_violations(invocations: object, producer: bool, problems: list[str]) -> bool:
    """
    Record the violations by `invocations`, and return whether they declare an incomplete run.

    The gate reads a run as incomplete when one invocation holds `executionSuccessful` false or a
    notification of level `error`. A producer writes exactly one invocation when it writes any: a
    failed one with an error notification stating why, or a successful one without such a notice.
    """
    if invocations is None:
        return False
    if not isinstance(invocations, list) or not all(
        isinstance(invocation, Mapping) and isinstance(invocation.get("executionSuccessful"), bool)
        for invocation in invocations
    ):
        problems.append("invocations is not an array of objects holding executionSuccessful")
        return False
    failed, errors = False, []
    for invocation in invocations:
        failed |= invocation["executionSuccessful"] is False
        errors.extend(_notification_errors(invocation, problems))
    if producer:
        if len(invocations) != 1:
            problems.append("invocations does not hold exactly one invocation")
        elif failed and not errors:
            problems.append("a failed invocation holds no notification of level error")
        elif errors and not failed:
            problems.append("a successful invocation holds a notification of level error")
        if any(not isinstance(text, str) for text in errors):
            problems.append("a notification of level error holds no message.text")
    return failed or bool(errors)


def _notification_errors(invocation: Mapping[str, object], problems: list[str]) -> list[object]:
    """Return the `message.text` of each notification of level `error` of `invocation`."""
    notifications = invocation.get("toolExecutionNotifications", [])
    if not isinstance(notifications, list) or not all(
        isinstance(notification, Mapping)
        and notification.get("level", "warning") in NOTIFICATION_LEVELS
        for notification in notifications
    ):
        problems.append("toolExecutionNotifications is not an array of notifications")
        return []
    texts = []
    for notification in notifications:
        if notification.get("level", "warning") == "error":
            message = notification.get("message")
            texts.append(message.get("text") if isinstance(message, Mapping) else None)
    return texts


def _result_violations(
    result: object, driver: str, described: set[str] | None, producer: bool
) -> list[str]:
    """Return the violations of section 4 by one result, or of section 5.6 alone."""
    if not isinstance(result, Mapping):
        return ["the result is no object"]
    problems = []
    rule = result.get("ruleId")
    if not isinstance(rule, str) or not RULE_ID.match(rule):
        problems.append(f"ruleId {rule!r} breaks the form of a rule identifier")
    elif described is not None and rule not in described:
        problems.append(f"ruleId {rule} has no rule descriptor")
    if result.get("level") not in LEVELS:
        problems.append(f"level {result.get('level')!r} is not admitted")
    message = result.get("message")
    if not isinstance(message, Mapping) or not isinstance(message.get("text"), str):
        problems.append("message.text is absent")
    if "suppressions" in result:
        problems.append("suppressions is written, which the gate alone writes")
    fingerprints = result.get("fingerprints", {})
    if isinstance(fingerprints, Mapping) and "elenchos/v1" in fingerprints:
        problems.append("fingerprints holds elenchos/v1, which the gate alone writes")
    problems.extend(_location_violations(result.get("locations"), producer))
    for key in ("partialFingerprints", "fingerprints"):
        problems.extend(_fingerprint_violations(key, result.get(key, {})))
    if producer:
        problems.extend(_producer_result_violations(result, driver))
    return problems


def _producer_result_violations(result: Mapping[str, object], driver: str) -> list[str]:
    """Return the violations of section 4 that the gate does not check, by one result."""
    problems = [f"{key} is written" for key in ABSENT if key in result]
    if "fingerprints" in result:
        problems.append("fingerprints is written by a producer")
    partial = result.get("partialFingerprints", {})
    if isinstance(partial, Mapping):
        if set(partial) - {"discriminator/v1"}:
            problems.append("partialFingerprints holds a key other than discriminator/v1")
        if partial.get("discriminator/v1", None) == "":
            problems.append("partialFingerprints holds an empty discriminator")
    properties = result.get("properties", {})
    if isinstance(properties, Mapping):
        problems.extend(
            f"property {key} does not open on {driver}/"
            for key in properties
            if not str(key).startswith(f"{driver}/")
        )
    return problems


def _location_violations(locations: object, producer: bool) -> list[str]:
    """Return the violations of sections 4.4 and 4.5 by the locations of a result."""
    if not isinstance(locations, list) or len(locations) != 1:
        return ["locations does not hold exactly one location"]
    [location] = locations
    if not isinstance(location, Mapping):
        return ["the location is no object"]
    problems: list[str] = []
    logical = location.get("logicalLocations")
    path = None
    if not isinstance(logical, list) or len(logical) != 1 or not isinstance(logical[0], Mapping):
        problems.append("logicalLocations does not hold exactly one logical location")
    elif not isinstance(logical[0].get("name"), str):
        problems.append("the logical location holds no name")
    else:
        name = logical[0]["name"]
        path = _name_violations(name, problems)
        if producer and logical[0].get("fullyQualifiedName", name) != name:
            problems.append("fullyQualifiedName differs from name")
        if producer and "parentIndex" in logical[0]:
            problems.append("the logical location is not top-level")
    if not producer:
        return problems
    physical = location.get("physicalLocation")
    if physical is not None:
        problems.extend(_physical_violations(physical, path))
    elif path is not None:
        problems.append("a resource path: holds no physicalLocation")
    return problems


def _physical_violations(physical: object, path: str | None) -> list[str]:
    """Return the violations of section 4.4 by a physical location, given the resource path."""
    if not isinstance(physical, Mapping):
        return ["physicalLocation is no object"]
    problems = []
    artifact = physical.get("artifactLocation")
    if not isinstance(artifact, Mapping) or not isinstance(artifact.get("uri"), str):
        return ["physicalLocation.artifactLocation.uri is absent"]
    uri = artifact["uri"]
    relative = not re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", uri)
    if relative and artifact.get("uriBaseId") != "SRCROOT":
        problems.append("a relative URI is not based on SRCROOT")
    if re.search(r"[^A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]|%(?![0-9A-Fa-f]{2})", uri):
        problems.append(f"the URI {uri!r} is not percent-encoded")
    elif relative and path is not None and unquote(uri) != path:
        problems.append(f"the URI {uri!r} does not name the resource path {path!r}")
    region = physical.get("region")
    if region is not None:
        if not isinstance(region, Mapping):
            return [*problems, "region is no object"]
        for key in ("startLine", "startColumn"):
            value = region.get(key, 1)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                problems.append(f"region.{key} is no positive integer")
    return problems


def _name_violations(name: str, problems: list[str]) -> str | None:
    """Record the violations of section 4.5 by a logical name, and return its path, if any."""
    resource, separator, locus = name.partition("#")
    if separator and not locus:
        problems.append(f"the name {name!r} ends with #")
    if re.search(r"%(?!25|23)", resource):
        problems.append(f"the resource {resource!r} holds a % sequence other than %25 and %23")
    decoded = re.sub(r"%(25|23)", lambda match: chr(int(match[1], 16)), resource)
    path = None
    if decoded.startswith("id:"):
        if decoded == "id:":
            problems.append("the identifier of the resource is empty")
    elif decoded.startswith("path:"):
        path = decoded[len("path:") :]
        problems.extend(_path_violations(path))
    else:
        problems.append(f"the resource {resource!r} opens on neither id: nor path:")
    if locus.startswith("/"):
        if re.search(r"~(?![01])", locus):
            problems.append(f"the pointer {locus!r} holds a ~ followed by neither 0 nor 1")
    elif locus:
        kind, colon, _ = locus.partition(":")
        if not colon or kind not in LOCUS_TYPES:
            problems.append(f"the locus {locus!r} is neither a pointer nor a typed locus")
    return path


def _path_violations(path: str) -> list[str]:
    """Return the violations of the form of a repository-relative POSIX path."""
    if path == "./":
        return []
    if path.startswith(("/", "./")):
        return [f"the path {path!r} opens on / or ./"]
    segments = (path[:-1] if path.endswith("/") else path).split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        return [f"the path {path!r} holds an empty, . or .. segment"]
    return []


def _fingerprint_violations(key: str, fingerprints: object) -> list[str]:
    """Return the violations of section 4.6 by `fingerprints` or `partialFingerprints`."""
    if not isinstance(fingerprints, Mapping):
        return [f"{key} is no object"]
    problems = []
    for name, value in fingerprints.items():
        if not isinstance(name, str) or not VERSIONED_KEY.match(name):
            problems.append(f"{key} key {name!r} is no versioned hierarchical string")
        if not isinstance(value, str):
            problems.append(f"{key} value of {name!r} is no string")
    return problems
