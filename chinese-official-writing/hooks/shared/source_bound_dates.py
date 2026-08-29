#!/usr/bin/env python3
"""Deterministic restoration of one source-bound full date in news drafts."""

from __future__ import annotations

import hashlib
import re
from typing import Any, Final


SCHEMA_VERSION: Final = 1
NEWS_GENRE_RE: Final = re.compile(
    r"(?:新闻稿|新闻消息|快讯|活动新闻(?:稿)?|活动报道|新闻通稿)"
)
EXPLICIT_NEWS_TASK_RE: Final = re.compile(
    r"(?:"
    r"(?:起草|拟写|撰写|写|改写|修改|修订|润色|整理|生成|输出)"
    r"(?:一则|一篇|一份)?[^。；;\n]{0,16}"
    r"(?:新闻稿|新闻消息|快讯|活动新闻(?:稿)?|活动报道|新闻通稿)"
    r"|(?:新闻稿|新闻消息|快讯|活动新闻(?:稿)?|活动报道|新闻通稿)"
    r"(?:请)?(?:改写|修改|修订|润色|压缩)"
    r")"
)
NEGATED_NEWS_RE: Final = re.compile(
    r"(?:不要|不需要|无需|无须|并非|不是|别)(?:再)?[^。；;\n]{0,16}"
    r"(?:写成|改成|整理成|作为|使用)?[^。；;\n]{0,6}"
    r"(?:新闻稿|新闻消息|快讯|活动新闻(?:稿)?|活动报道|新闻通稿)"
)
NEWS_TO_OTHER_GENRE_RE: Final = re.compile(
    r"(?:新闻稿|新闻消息|快讯|活动新闻(?:稿)?|活动报道|新闻通稿)"
    r"[^。；;\n]{0,12}(?:改写|修改|修订|整理|改成|写成|转为|转换为)"
    r"[^。；;\n]{0,8}(?:通知|报告|函|请示|申请|纪要|说明|方案|通报|公告|公示|制度|意见|总结|讲话|致辞)"
)
KEEP_FULL_DATE_RE: Final = re.compile(
    r"(?:不要|不得|不能|不可)[^。；;\n]{0,8}(?:省略|删除|去掉|缩短)"
    r"[^。；;\n]{0,8}(?:年份|完整日期|日期)"
)
OMIT_DATE_RE: Final = re.compile(
    r"(?:"
    r"(?:省略|不写|不要写|无需写|无须写|不必写|删除|去掉|不保留|无需保留|无须保留|不必保留|不要求保留)"
    r"[^。；;\n]{0,10}(?:年份|完整日期|日期)"
    r"|(?:年份|完整日期|日期)[^。；;\n]{0,10}"
    r"(?:省略|不写|不要写|无需写|无须写|不必写|删除|去掉|不保留|无需保留|无须保留|不必保留|不要求保留)"
    r")"
)
ONLY_MONTH_DAY_RE: Final = re.compile(
    r"(?:只|仅)(?:保留|写|写成|使用|采用)"
    r"(?![^。；;\n]{0,8}[12]\d{3}年)"
    r"[^。；;\n]{0,8}(?:月日|(?:0?[1-9]|1[0-2])月(?:0?[1-9]|[12]\d|3[01])日)"
)
FULL_DATE_RE: Final = re.compile(
    r"(?<!\d)(?P<year>[12]\d{3})年"
    r"(?P<month>0?[1-9]|1[0-2])月"
    r"(?P<day>0?[1-9]|[12]\d|3[01])日"
)
ANY_DATE_RE: Final = re.compile(
    r"(?<!\d)(?:(?P<year>[12]\d{3})年)?"
    r"(?P<month>0?[1-9]|1[0-2])月"
    r"(?P<day>0?[1-9]|[12]\d|3[01])日"
)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _result(reason: str, draft: str, output: str | None = None, **extra: Any) -> dict[str, Any]:
    selected = output is not None and output != draft
    final = output if selected else draft
    return {
        "schema_version": SCHEMA_VERSION,
        "selected": selected,
        "reason": reason,
        "original_sha256": _sha256_text(draft),
        "output_sha256": _sha256_text(final),
        "output": final,
        **extra,
    }


def _news_task(request: str) -> bool:
    return bool(
        NEWS_GENRE_RE.search(request)
        and EXPLICIT_NEWS_TASK_RE.search(request)
        and not NEGATED_NEWS_RE.search(request)
        and not NEWS_TO_OTHER_GENRE_RE.search(request)
    )


def _date_omission_requested(request: str) -> bool:
    if KEEP_FULL_DATE_RE.search(request):
        request = KEEP_FULL_DATE_RE.sub("", request)
    return bool(OMIT_DATE_RE.search(request) or ONLY_MONTH_DAY_RE.search(request))


def restore_unique_full_date(request: str, draft: str) -> dict[str, Any]:
    """Return one exact source-bound repair, or the byte-identical draft.

    The function deliberately refuses multiple, conflicting, already-complete,
    or user-suppressed date mappings.  It never supplies a year that is absent
    from the request.
    """

    if not isinstance(request, str) or not isinstance(draft, str) or not draft.strip():
        return _result("invalid_or_empty_input", draft if isinstance(draft, str) else "")
    if not _news_task(request):
        return _result("not_explicit_news_task", draft)
    if _date_omission_requested(request):
        return _result("user_requested_date_omission", draft)

    source_dates: dict[tuple[int, int, int], str] = {}
    for match in FULL_DATE_RE.finditer(request):
        year = int(match.group("year"))
        month = int(match.group("month"))
        day = int(match.group("day"))
        source_dates[(year, month, day)] = match.group(0)
    if not source_dates:
        return _result("request_has_no_full_date", draft)
    if len(source_dates) != 1:
        return _result("request_has_multiple_full_dates", draft)
    (source_key, full_literal), = source_dates.items()
    day_key = source_key[1:]
    request_bare_dates = [
        match
        for match in ANY_DATE_RE.finditer(request)
        if match.group("year") is None
        and (int(match.group("month")), int(match.group("day"))) == day_key
    ]
    if request_bare_dates:
        return _result("request_date_role_ambiguous", draft)

    draft_dates: dict[tuple[int, int], list[re.Match[str]]] = {}
    for match in ANY_DATE_RE.finditer(draft):
        key = (int(match.group("month")), int(match.group("day")))
        draft_dates.setdefault(key, []).append(match)

    matches = draft_dates.get(day_key, [])
    if any(match.group("year") is not None for match in matches):
        return _result("draft_has_full_date_for_same_day", draft)
    short_matches = [match for match in matches if match.group("year") is None]
    if len(short_matches) != 1:
        return _result("no_unique_source_bound_target", draft)

    target = short_matches[0]
    output = draft[: target.start()] + full_literal + draft[target.end() :]
    if output == draft:
        return _result("unchanged_candidate", draft)
    return _result(
        "source_bound_full_date_restored",
        draft,
        output,
        target=target.group(0),
        replacement=full_literal,
        span_start=target.start(),
        span_end=target.end(),
    )
