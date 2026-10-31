"""
Validator of a SARIF log against the findings profile of Elenchos, written from the profile text.

The validator implements the requirements that the profile places on a producer: sections 3 and 4
of `elenchos/docs/profile.md`, and the rejected input of its section 5.6. It reports every
violation as a string naming the object at fault. It imports no package of Elenchos, as the profile
requires of a producer.

Functions
---------
profile_violations(log, producer) -> list of str
    Violations of the profile by a log.
"""

import re
from collections.abc import Mapping

DRIVER_NAME = re.compile(r"[a-z][a-z0-9-]*\Z")
RULE_ID = re.compile(r"[a-z0-9][a-z0-9._-]*(/[a-z0-9][a-z0-9._-]*)*\Z")
VERSIONED_KEY = re.compile(r"([^/]+/)*v(0|[1-9][0-9]*)\Z")
LEVELS = {"error", "warning", "note"}
COLUMN_KINDS = {"unicodeCodePoints", "utf16CodeUnits"}
LOCUS_TYPES = {"link", "task", "slot", "term", "symbol"}
GATE_ONLY = ("fingerprints", "suppressions")
ABSENT = ("kind", "baselineState")


def profile_violations(log: object, producer: bool = True) -> list[str]:
    """
    Return the violations of the findings profile by `log`, empty when the log conforms.

    Parameters
    ----------
    log : object
        SARIF log parsed from JSON.
    producer : bool
        Whether the log is written by a producer, which writes no object reserved to the gate.
    """
    if not isinstance(log, Mapping):
        return ["the log is no object"]
    problems = []
    if log.get("version") != "2.1.0":
        problems.append("sarifLog.version is not 2.1.0")
    runs = log.get("runs")
    if not isinstance(runs, list) or not runs:
        return [*problems, "sarifLog.runs holds no run"]
    for index, run in enumerate(runs):
        problems.extend(f"runs[{index}]: {problem}" for problem in _run_violations(run, producer))
    return problems


def _run_violations(run: object, producer: bool) -> list[str]:
    """Return the violations of section 3 and of section 4 by one run."""
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
    if not any(isinstance(driver.get(key), str) for key in ("version", "semanticVersion")):
        problems.append("tool.driver holds neither version nor semanticVersion")
    described = _rule_descriptors(driver.get("rules"), problems)
    results = run.get("results", [])
    if not isinstance(results, list):
        return [*problems, "results is no array"]
    if results and run.get("columnKind") not in COLUMN_KINDS:
        problems.append(f"columnKind {run.get('columnKind')!r} is not admitted")
    for index, result in enumerate(results):
        problems.extend(
            f"results[{index}]: {problem}"
            for problem in _result_violations(result, name, described, producer)
        )
    return problems


def _rule_descriptors(rules: object, problems: list[str]) -> set[str] | None:
    """Return the rule identifiers described by `rules`, or `None` when the run lists no rule."""
    if rules is None:
        return None
    if not isinstance(rules, list):
        problems.append("tool.driver.rules is no array")
        return None
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


def _result_violations(
    result: object, driver: str, described: set[str] | None, producer: bool
) -> list[str]:
    """Return the violations of section 4 by one result."""
    if not isinstance(result, Mapping):
        return ["the result is no object"]
    problems = []
    rule = result.get("ruleId")
    if not isinstance(rule, str) or not RULE_ID.match(rule):
        problems.append(f"ruleId {rule!r} breaks the form of a rule identifier")
    elif described is not None and rule not in described:
        problems.append(f"ruleId {rule} has no rule descriptor")
    problems.extend(f"{key} is written" for key in ABSENT if key in result)
    if producer:
        problems.extend(f"{key} is written by a producer" for key in GATE_ONLY if key in result)
    if result.get("level") not in LEVELS:
        problems.append(f"level {result.get('level')!r} is not admitted")
    message = result.get("message")
    if not isinstance(message, Mapping) or not isinstance(message.get("text"), str):
        problems.append("message.text is absent")
    problems.extend(_location_violations(result.get("locations")))
    for key in ("partialFingerprints", "fingerprints"):
        problems.extend(_fingerprint_violations(key, result.get(key, {})))
    partial = result.get("partialFingerprints", {})
    if producer and isinstance(partial, Mapping):
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


def _location_violations(locations: object) -> list[str]:
    """Return the violations of sections 4.4 and 4.5 by the locations of a result."""
    if not isinstance(locations, list) or len(locations) != 1:
        return ["locations does not hold exactly one location"]
    [location] = locations
    if not isinstance(location, Mapping):
        return ["the location is no object"]
    problems = []
    logical = location.get("logicalLocations")
    if not isinstance(logical, list) or len(logical) != 1 or not isinstance(logical[0], Mapping):
        problems.append("logicalLocations does not hold exactly one logical location")
    else:
        name = logical[0].get("name")
        if not isinstance(name, str):
            problems.append("the logical location holds no name")
        else:
            problems.extend(_name_violations(name))
            qualified = logical[0].get("fullyQualifiedName", name)
            if qualified != name:
                problems.append("fullyQualifiedName differs from name")
        if "parentIndex" in logical[0]:
            problems.append("the logical location is not top-level")
    physical = location.get("physicalLocation")
    if physical is not None:
        problems.extend(_physical_violations(physical))
    return problems


def _physical_violations(physical: object) -> list[str]:
    """Return the violations of section 4.4 by a physical location."""
    if not isinstance(physical, Mapping):
        return ["physicalLocation is no object"]
    problems = []
    artifact = physical.get("artifactLocation")
    if not isinstance(artifact, Mapping) or not isinstance(artifact.get("uri"), str):
        return ["physicalLocation.artifactLocation.uri is absent"]
    uri = artifact["uri"]
    if not re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", uri) and artifact.get("uriBaseId") != "SRCROOT":
        problems.append("a relative URI is not based on SRCROOT")
    if re.search(r"[^A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]|%(?![0-9A-Fa-f]{2})", uri):
        problems.append(f"the URI {uri!r} is not percent-encoded")
    region = physical.get("region")
    if region is not None:
        if not isinstance(region, Mapping):
            return [*problems, "region is no object"]
        for key in ("startLine", "startColumn"):
            value = region.get(key, 1)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                problems.append(f"region.{key} is no positive integer")
    return problems


def _name_violations(name: str) -> list[str]:
    """Return the violations of section 4.5 by the name of a logical location."""
    resource, separator, locus = name.partition("#")
    problems = []
    if separator and not locus:
        problems.append(f"the name {name!r} ends with #")
    if re.search(r"%(?!25|23)", resource):
        problems.append(f"the resource {resource!r} holds a % sequence other than %25 and %23")
    decoded = re.sub(r"%(25|23)", lambda match: chr(int(match[1], 16)), resource)
    if decoded.startswith("id:"):
        if decoded == "id:":
            problems.append("the identifier of the resource is empty")
    elif decoded.startswith("path:"):
        problems.extend(_path_violations(decoded[len("path:") :]))
    else:
        problems.append(f"the resource {resource!r} opens on neither id: nor path:")
    if locus.startswith("/"):
        if re.search(r"~(?![01])", locus):
            problems.append(f"the pointer {locus!r} holds a ~ followed by neither 0 nor 1")
    elif locus:
        kind, colon, _ = locus.partition(":")
        if not colon or kind not in LOCUS_TYPES:
            problems.append(f"the locus {locus!r} is neither a pointer nor a typed locus")
    return problems


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
