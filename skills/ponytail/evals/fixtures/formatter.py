from dataclasses import dataclass


def format_tag(tag: str) -> str:
    return f"[{tag[0].upper()}{tag[1:]}]"


@dataclass
class Record:
    name: str
    optional_tag: str | None = None


def format_record(record: Record) -> str:
    tag = "" if record.optional_tag is None else format_tag(record.optional_tag)
    return f"{record.name}{tag}"


def format_search_label(name: str, optional_tag: str | None) -> str:
    suffix = "" if optional_tag is None else format_tag(optional_tag)
    return f"{name}{suffix}"
