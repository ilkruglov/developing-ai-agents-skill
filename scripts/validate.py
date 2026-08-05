#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

PLUGIN_NAME = "developing-ai-agents"
MARKETPLACE_NAME = "developing-ai-agents-skill"
PLUGIN_DIRECTORY = Path("plugins") / PLUGIN_NAME
PLUGIN_SOURCE = f"./{PLUGIN_DIRECTORY.as_posix()}"
SKILL_DIRECTORY = PLUGIN_DIRECTORY / "skills" / PLUGIN_NAME

REQUIRED_PATHS = (
    ".agents/plugins/marketplace.json",
    ".claude-plugin/marketplace.json",
    str(PLUGIN_DIRECTORY / ".codex-plugin" / "plugin.json"),
    str(PLUGIN_DIRECTORY / ".claude-plugin" / "plugin.json"),
    str(PLUGIN_DIRECTORY / "LICENSE"),
    str(PLUGIN_DIRECTORY / "NOTICE"),
    str(PLUGIN_DIRECTORY / "SOURCE.json"),
    str(PLUGIN_DIRECTORY / "evals" / "benchmark-v2.json"),
    str(PLUGIN_DIRECTORY / "benchmarks" / "v2" / "benchmark.json"),
    str(SKILL_DIRECTORY / "SKILL.md"),
    "README.md",
    "LICENSE",
    "NOTICE",
    "SOURCE.json",
    str(SKILL_DIRECTORY / "agents" / "openai.yaml"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "introduction.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter1.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter2.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter3.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter4.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter5.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter6.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter7.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter8.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter9.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter10.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "afterword.md"),
)
REQUIRED_ATTRIBUTIONS = {
    "README.md": (
        "https://github.com/bojieli",
        "https://github.com/bojieli/ai-agent-book",
        "https://github.com/ilkruglov/ai-agent-book",
    ),
    "NOTICE": (
        "Bojie Li",
        "https://github.com/bojieli",
        "https://github.com/bojieli/ai-agent-book",
        "https://github.com/ilkruglov/ai-agent-book",
    ),
    "SOURCE.json": (
        "Bojie Li",
        "https://github.com/bojieli",
        "https://github.com/bojieli/ai-agent-book",
        "https://github.com/ilkruglov/ai-agent-book",
    ),
    str(PLUGIN_DIRECTORY / "NOTICE"): (
        "Bojie Li",
        "https://github.com/bojieli",
        "https://github.com/bojieli/ai-agent-book",
        "https://github.com/ilkruglov/ai-agent-book",
    ),
    str(PLUGIN_DIRECTORY / "SOURCE.json"): (
        "Bojie Li",
        "https://github.com/bojieli",
        "https://github.com/bojieli/ai-agent-book",
        "https://github.com/ilkruglov/ai-agent-book",
    ),
}
NON_LOCAL_SOURCE_PATH = re.compile(r"(?<![-\w/])book/")
LOCAL_SOURCE_ANCHOR = re.compile(
    r"(?<![-\w/])(?P<path>references/source-book/[A-Za-z0-9._/-]+\.md):"
    r"(?P<start>\d+)(?:-(?P<end>\d+))?"
)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\((?P<target>[^)]+)\)")
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\."
    r"(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
PLUGIN_MANIFEST_FIELDS = {
    "id",
    "name",
    "version",
    "description",
    "skills",
    "apps",
    "mcpServers",
    "interface",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
}
PLUGIN_INTERFACE_FIELDS = {
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "websiteURL",
    "privacyPolicyURL",
    "termsOfServiceURL",
    "brandColor",
    "composerIcon",
    "logo",
    "logoDark",
    "screenshots",
    "defaultPrompt",
    "default_prompt",
}
CLAUDE_MARKETPLACE_SCHEMA = "https://anthropic.com/claude-code/marketplace.schema.json"
CLAUDE_PLUGIN_SCHEMA = "https://json.schemastore.org/claude-code-plugin-manifest.json"
CLAUDE_MARKETPLACE_FIELDS = {
    "$schema",
    "name",
    "description",
    "owner",
    "plugins",
}
CLAUDE_MARKETPLACE_PLUGIN_FIELDS = {
    "name",
    "source",
    "description",
    "version",
    "category",
}
CLAUDE_PLUGIN_MANIFEST_FIELDS = {
    "$schema",
    "name",
    "displayName",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
}
MARKETPLACE_INSTALLATION_POLICIES = {
    "NOT_AVAILABLE",
    "AVAILABLE",
    "INSTALLED_BY_DEFAULT",
}
MARKETPLACE_AUTHENTICATION_POLICIES = {"ON_INSTALL", "ON_USE"}


def parse_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    return unquote(target.split("#", maxsplit=1)[0])


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}

    values: dict[str, str] = {}
    for line in lines[1:]:
        if line == "---":
            return values
        if ":" not in line:
            continue
        key, value = line.split(":", maxsplit=1)
        values[key.strip()] = value.strip()
    return {}


def is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_https_url(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def add_contract_error(errors: list[str], contract: str, detail: str) -> None:
    errors.append(f"invalid {contract}: {detail}")


def iter_markdown_documents(root: Path) -> list[Path]:
    source_root = root / SKILL_DIRECTORY / "references" / "source-book"
    return [
        path
        for path in root.rglob("*.md")
        if source_root not in path.parents
        and ".git" not in path.relative_to(root).parts
        and ".tmp" not in path.relative_to(root).parts
    ]


def iter_source_anchor_documents(root: Path) -> list[Path]:
    documents = iter_markdown_documents(root)
    evals_root = root / PLUGIN_DIRECTORY / "evals"
    if evals_root.is_dir():
        documents.extend(evals_root.rglob("*.json"))
        documents.extend(evals_root.rglob("*.jsonl"))
    return sorted(set(documents))


def validate_marketplace(root: Path, errors: list[str]) -> None:
    marketplace_path = root / ".agents" / "plugins" / "marketplace.json"
    if not marketplace_path.is_file():
        return
    try:
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(marketplace, dict):
        add_contract_error(errors, "marketplace contract", "root must be an object")
        return
    if marketplace.get("name") != MARKETPLACE_NAME:
        errors.append(f"invalid marketplace name: expected {MARKETPLACE_NAME}")

    unknown_fields = set(marketplace) - {"name", "interface", "plugins"}
    if unknown_fields:
        add_contract_error(
            errors,
            "marketplace contract",
            f"unsupported fields: {', '.join(sorted(unknown_fields))}",
        )

    interface = marketplace.get("interface")
    if interface is not None and not isinstance(interface, dict):
        add_contract_error(
            errors,
            "marketplace contract",
            "interface must be an object",
        )
    elif isinstance(interface, dict):
        interface_fields = set(interface)
        if interface_fields - {"displayName"}:
            add_contract_error(
                errors,
                "marketplace contract",
                "interface contains unsupported fields",
            )
        if "displayName" in interface and not is_non_empty_string(
            interface["displayName"]
        ):
            add_contract_error(
                errors,
                "marketplace contract",
                "interface.displayName must be a non-empty string",
            )

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        errors.append("invalid marketplace plugin source: plugins must be an array")
        return

    entry = next(
        (
            value
            for value in plugins
            if isinstance(value, dict) and value.get("name") == PLUGIN_NAME
        ),
        None,
    )
    if entry is None:
        add_contract_error(
            errors,
            "marketplace contract",
            f"missing plugin entry {PLUGIN_NAME}",
        )

    source = entry.get("source") if isinstance(entry, dict) else None
    source_path = source.get("path") if isinstance(source, dict) else None
    resolved_source = root / str(source_path).removeprefix("./")
    if source_path != PLUGIN_SOURCE or not resolved_source.is_dir():
        errors.append(
            "invalid marketplace plugin source: expected "
            f"{PLUGIN_NAME} at {PLUGIN_SOURCE}"
        )

    if not isinstance(entry, dict):
        return
    unknown_entry_fields = set(entry) - {"name", "source", "policy", "category"}
    if unknown_entry_fields:
        add_contract_error(
            errors,
            "marketplace contract",
            f"plugin entry contains unsupported fields: "
            f"{', '.join(sorted(unknown_entry_fields))}",
        )

    if not isinstance(source, dict) or source.get("source") != "local":
        add_contract_error(
            errors,
            "marketplace contract",
            "plugin source.source must be local",
        )
    elif set(source) - {"source", "path"}:
        add_contract_error(
            errors,
            "marketplace contract",
            "plugin source contains unsupported fields",
        )

    policy = entry.get("policy")
    if not isinstance(policy, dict):
        add_contract_error(
            errors,
            "marketplace contract",
            "plugin policy must be an object",
        )
    else:
        unknown_policy_fields = set(policy) - {
            "installation",
            "authentication",
            "products",
        }
        if unknown_policy_fields:
            add_contract_error(
                errors,
                "marketplace contract",
                "plugin policy contains unsupported fields",
            )
        if policy.get("installation") not in MARKETPLACE_INSTALLATION_POLICIES:
            add_contract_error(
                errors,
                "marketplace contract",
                "plugin policy.installation is invalid",
            )
        if policy.get("authentication") not in MARKETPLACE_AUTHENTICATION_POLICIES:
            add_contract_error(
                errors,
                "marketplace contract",
                "plugin policy.authentication is invalid",
            )
        products = policy.get("products")
        if products is not None and (
            not isinstance(products, list)
            or not all(is_non_empty_string(product) for product in products)
        ):
            add_contract_error(
                errors,
                "marketplace contract",
                "plugin policy.products must be an array of strings",
            )

    if not is_non_empty_string(entry.get("category")):
        add_contract_error(
            errors,
            "marketplace contract",
            "plugin category must be a non-empty string",
        )


def validate_plugin_manifest(root: Path, errors: list[str]) -> None:
    manifest_path = root / PLUGIN_DIRECTORY / ".codex-plugin" / "plugin.json"
    if not manifest_path.is_file():
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(manifest, dict):
        add_contract_error(errors, "plugin manifest", "root must be an object")
        return

    unknown_fields = set(manifest) - PLUGIN_MANIFEST_FIELDS
    if unknown_fields:
        add_contract_error(
            errors,
            "plugin manifest",
            f"unsupported fields: {', '.join(sorted(unknown_fields))}",
        )

    if manifest.get("name") != PLUGIN_NAME:
        add_contract_error(
            errors,
            "plugin manifest",
            f"name must be {PLUGIN_NAME}",
        )
    version = manifest.get("version")
    if not isinstance(version, str) or SEMVER.fullmatch(version) is None:
        add_contract_error(errors, "plugin manifest", "version must be strict semver")
    if not is_non_empty_string(manifest.get("description")):
        add_contract_error(
            errors,
            "plugin manifest",
            "description must be a non-empty string",
        )
    if manifest.get("skills") != "./skills/":
        add_contract_error(
            errors,
            "plugin manifest",
            "skills path must be ./skills/",
        )

    author = manifest.get("author")
    if not isinstance(author, dict):
        add_contract_error(errors, "plugin manifest", "author must be an object")
    else:
        if set(author) - {"name", "email", "url"}:
            add_contract_error(
                errors,
                "plugin manifest",
                "author contains unsupported fields",
            )
        if not is_non_empty_string(author.get("name")):
            add_contract_error(
                errors,
                "plugin manifest",
                "author.name must be a non-empty string",
            )
        if "email" in author and not is_non_empty_string(author["email"]):
            add_contract_error(
                errors,
                "plugin manifest",
                "author.email must be a non-empty string",
            )
        if "url" in author and not is_https_url(author["url"]):
            add_contract_error(
                errors,
                "plugin manifest",
                "author.url must be an absolute HTTPS URL",
            )

    for field in ("homepage", "repository"):
        if field in manifest and not is_https_url(manifest[field]):
            add_contract_error(
                errors,
                "plugin manifest",
                f"{field} must be an absolute HTTPS URL",
            )
    if "license" in manifest and not is_non_empty_string(manifest["license"]):
        add_contract_error(
            errors,
            "plugin manifest",
            "license must be a non-empty string",
        )
    keywords = manifest.get("keywords")
    if keywords is not None and (
        not isinstance(keywords, list)
        or not all(is_non_empty_string(keyword) for keyword in keywords)
    ):
        add_contract_error(
            errors,
            "plugin manifest",
            "keywords must be an array of strings",
        )

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        add_contract_error(errors, "plugin manifest", "interface must be an object")
        return
    unknown_interface_fields = set(interface) - PLUGIN_INTERFACE_FIELDS
    if unknown_interface_fields:
        add_contract_error(
            errors,
            "plugin manifest",
            "interface contains unsupported fields: "
            f"{', '.join(sorted(unknown_interface_fields))}",
        )
    for field in (
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
    ):
        if not is_non_empty_string(interface.get(field)):
            add_contract_error(
                errors,
                "plugin manifest",
                f"interface.{field} must be a non-empty string",
            )
    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not all(
        is_non_empty_string(capability) for capability in capabilities
    ):
        add_contract_error(
            errors,
            "plugin manifest",
            "interface.capabilities must be an array of strings",
        )
    default_prompt = interface.get(
        "defaultPrompt",
        interface.get("default_prompt"),
    )
    if not is_non_empty_string(default_prompt) and (
        not isinstance(default_prompt, list)
        or not default_prompt
        or not all(is_non_empty_string(prompt) for prompt in default_prompt)
    ):
        add_contract_error(
            errors,
            "plugin manifest",
            "interface.defaultPrompt must be a string or an array of strings",
        )
    for field in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
        if field in interface and not is_https_url(interface[field]):
            add_contract_error(
                errors,
                "plugin manifest",
                f"interface.{field} must be an absolute HTTPS URL",
            )


def validate_claude_marketplace(root: Path, errors: list[str]) -> None:
    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    if not marketplace_path.is_file():
        return
    try:
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(marketplace, dict):
        add_contract_error(
            errors,
            "Claude marketplace contract",
            "root must be an object",
        )
        return

    unknown_fields = set(marketplace) - CLAUDE_MARKETPLACE_FIELDS
    if unknown_fields:
        add_contract_error(
            errors,
            "Claude marketplace contract",
            f"unsupported fields: {', '.join(sorted(unknown_fields))}",
        )
    if marketplace.get("$schema") != CLAUDE_MARKETPLACE_SCHEMA:
        add_contract_error(
            errors,
            "Claude marketplace contract",
            "unexpected $schema",
        )
    if marketplace.get("name") != MARKETPLACE_NAME:
        add_contract_error(
            errors,
            "Claude marketplace contract",
            f"name must be {MARKETPLACE_NAME}",
        )
    if not is_non_empty_string(marketplace.get("description")):
        add_contract_error(
            errors,
            "Claude marketplace contract",
            "description must be a non-empty string",
        )

    owner = marketplace.get("owner")
    if not isinstance(owner, dict):
        add_contract_error(
            errors,
            "Claude marketplace contract",
            "owner must be an object",
        )
    else:
        if set(owner) - {"name", "email"}:
            add_contract_error(
                errors,
                "Claude marketplace contract",
                "owner contains unsupported fields",
            )
        if not is_non_empty_string(owner.get("name")):
            add_contract_error(
                errors,
                "Claude marketplace contract",
                "owner.name must be a non-empty string",
            )
        if "email" in owner and not is_non_empty_string(owner["email"]):
            add_contract_error(
                errors,
                "Claude marketplace contract",
                "owner.email must be a non-empty string",
            )

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        add_contract_error(
            errors,
            "Claude marketplace contract",
            "plugins must be an array",
        )
        return
    entry = next(
        (
            value
            for value in plugins
            if isinstance(value, dict) and value.get("name") == PLUGIN_NAME
        ),
        None,
    )
    if not isinstance(entry, dict):
        add_contract_error(
            errors,
            "Claude marketplace contract",
            f"missing plugin entry {PLUGIN_NAME}",
        )
        return

    unknown_entry_fields = set(entry) - CLAUDE_MARKETPLACE_PLUGIN_FIELDS
    if unknown_entry_fields:
        add_contract_error(
            errors,
            "Claude marketplace contract",
            "plugin entry contains unsupported fields: "
            f"{', '.join(sorted(unknown_entry_fields))}",
        )
    source = entry.get("source")
    resolved_source = root / str(source).removeprefix("./")
    if source != PLUGIN_SOURCE or not resolved_source.is_dir():
        errors.append(
            "invalid Claude marketplace source: expected "
            f"{PLUGIN_NAME} at {PLUGIN_SOURCE}"
        )
    if not is_non_empty_string(entry.get("description")):
        add_contract_error(
            errors,
            "Claude marketplace contract",
            "plugin description must be a non-empty string",
        )
    version = entry.get("version")
    if not isinstance(version, str) or SEMVER.fullmatch(version) is None:
        add_contract_error(
            errors,
            "Claude marketplace contract",
            "plugin version must be strict semver",
        )
    if not is_non_empty_string(entry.get("category")):
        add_contract_error(
            errors,
            "Claude marketplace contract",
            "plugin category must be a non-empty string",
        )


def validate_claude_plugin_manifest(root: Path, errors: list[str]) -> None:
    manifest_path = root / PLUGIN_DIRECTORY / ".claude-plugin" / "plugin.json"
    if not manifest_path.is_file():
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(manifest, dict):
        add_contract_error(
            errors,
            "Claude plugin manifest",
            "root must be an object",
        )
        return

    unknown_fields = set(manifest) - CLAUDE_PLUGIN_MANIFEST_FIELDS
    if unknown_fields:
        add_contract_error(
            errors,
            "Claude plugin manifest",
            f"unsupported fields: {', '.join(sorted(unknown_fields))}",
        )
    if manifest.get("$schema") != CLAUDE_PLUGIN_SCHEMA:
        add_contract_error(
            errors,
            "Claude plugin manifest",
            "unexpected $schema",
        )
    if manifest.get("name") != PLUGIN_NAME:
        add_contract_error(
            errors,
            "Claude plugin manifest",
            f"name must be {PLUGIN_NAME}",
        )
    for field in ("displayName", "description", "license"):
        if not is_non_empty_string(manifest.get(field)):
            add_contract_error(
                errors,
                "Claude plugin manifest",
                f"{field} must be a non-empty string",
            )
    version = manifest.get("version")
    if not isinstance(version, str) or SEMVER.fullmatch(version) is None:
        add_contract_error(
            errors,
            "Claude plugin manifest",
            "version must be strict semver",
        )

    author = manifest.get("author")
    if not isinstance(author, dict):
        add_contract_error(
            errors,
            "Claude plugin manifest",
            "author must be an object",
        )
    else:
        if set(author) - {"name", "email", "url"}:
            add_contract_error(
                errors,
                "Claude plugin manifest",
                "author contains unsupported fields",
            )
        if not is_non_empty_string(author.get("name")):
            add_contract_error(
                errors,
                "Claude plugin manifest",
                "author.name must be a non-empty string",
            )
        if "email" in author and not is_non_empty_string(author["email"]):
            add_contract_error(
                errors,
                "Claude plugin manifest",
                "author.email must be a non-empty string",
            )
        if "url" in author and not is_https_url(author["url"]):
            add_contract_error(
                errors,
                "Claude plugin manifest",
                "author.url must be an absolute HTTPS URL",
            )

    for field in ("homepage", "repository"):
        if not is_https_url(manifest.get(field)):
            add_contract_error(
                errors,
                "Claude plugin manifest",
                f"{field} must be an absolute HTTPS URL",
            )
    keywords = manifest.get("keywords")
    if not isinstance(keywords, list) or not all(
        is_non_empty_string(keyword) for keyword in keywords
    ):
        add_contract_error(
            errors,
            "Claude plugin manifest",
            "keywords must be an array of strings",
        )


def validate_plugin_versions(root: Path, errors: list[str]) -> None:
    paths = {
        "Codex": root / PLUGIN_DIRECTORY / ".codex-plugin" / "plugin.json",
        "Claude": root / PLUGIN_DIRECTORY / ".claude-plugin" / "plugin.json",
        "Claude marketplace": root / ".claude-plugin" / "marketplace.json",
    }
    versions: dict[str, str] = {}
    for label, path in paths.items():
        if not path.is_file():
            return
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(payload, dict):
            return
        if label == "Claude marketplace":
            plugins = payload.get("plugins")
            if not isinstance(plugins, list):
                return
            entry = next(
                (
                    value
                    for value in plugins
                    if isinstance(value, dict) and value.get("name") == PLUGIN_NAME
                ),
                None,
            )
            version = entry.get("version") if isinstance(entry, dict) else None
        else:
            version = payload.get("version")
        if not isinstance(version, str):
            return
        versions[label] = version

    if len(set(versions.values())) != 1:
        details = ", ".join(f"{label}={version}" for label, version in versions.items())
        errors.append(f"plugin versions differ: {details}")


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    line_counts: dict[Path, int] = {}
    for relative_path in REQUIRED_PATHS:
        if not (root / relative_path).is_file():
            errors.append(f"missing required file: {relative_path}")

    for relative_path, required_values in REQUIRED_ATTRIBUTIONS.items():
        path = root / relative_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for required_value in required_values:
            if required_value not in text:
                errors.append(
                    f"missing attribution in {relative_path}: {required_value}"
                )

    skill_path = root / SKILL_DIRECTORY / "SKILL.md"
    if skill_path.is_file():
        frontmatter = parse_frontmatter(skill_path.read_text(encoding="utf-8"))
        if frontmatter.get("name") != "developing-ai-agents" or not frontmatter.get(
            "description"
        ):
            errors.append(
                "invalid SKILL.md frontmatter: expected name "
                "developing-ai-agents and a non-empty description"
            )

    for json_path in root.rglob("*.json"):
        relative_path = json_path.relative_to(root)
        if ".git" in relative_path.parts or ".tmp" in relative_path.parts:
            continue
        try:
            json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid JSON in {relative_path}: {error}")

    for jsonl_path in root.rglob("*.jsonl"):
        relative_path = jsonl_path.relative_to(root)
        if ".git" in relative_path.parts or ".tmp" in relative_path.parts:
            continue
        for line_number, line in enumerate(
            jsonl_path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as error:
                errors.append(
                    f"invalid JSONL in {relative_path}:{line_number}: {error}"
                )

    validate_marketplace(root, errors)
    validate_plugin_manifest(root, errors)
    validate_claude_marketplace(root, errors)
    validate_claude_plugin_manifest(root, errors)
    validate_plugin_versions(root, errors)

    for document_path in iter_source_anchor_documents(root):
        text = document_path.read_text(encoding="utf-8")
        for match in NON_LOCAL_SOURCE_PATH.finditer(text):
            relative_path = document_path.relative_to(root)
            errors.append(
                f"non-local source anchor in {relative_path}: {match.group(0)}"
            )
        for match in LOCAL_SOURCE_ANCHOR.finditer(text):
            source_path = root / SKILL_DIRECTORY / match.group("path")
            start = int(match.group("start"))
            end = int(match.group("end") or start)
            if not source_path.is_file():
                errors.append(f"source anchor file missing: {match.group('path')}")
                continue
            if source_path not in line_counts:
                line_counts[source_path] = len(
                    source_path.read_text(encoding="utf-8").splitlines()
                )
            maximum = line_counts[source_path]
            if start < 1 or end < start or end > maximum:
                errors.append(
                    "source anchor out of range: "
                    f"{match.group(0)} (file has {maximum} lines)"
                )

    for markdown_path in iter_markdown_documents(root):
        text = markdown_path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = parse_link_target(match.group("target"))
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved_target = (markdown_path.parent / target).resolve()
            if not resolved_target.exists():
                relative_path = markdown_path.relative_to(root)
                errors.append(
                    f"broken Markdown link in {relative_path}: {match.group('target')}"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the developing-ai-agents plugin repository"
    )
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    errors = validate_repository(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
