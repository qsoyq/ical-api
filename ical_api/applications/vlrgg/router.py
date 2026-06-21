import asyncio
import logging
from datetime import datetime, timedelta, timezone

import dateparser
import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse
from ics import Calendar, Event

from ical_api.core.settings import AppSettings

router = APIRouter(tags=["iCalendar"], prefix="/ics/vlrgg")

logger = logging.getLogger(__file__)

vlrgg_settings = AppSettings().vlrgg
fetch_vlrgg_match_time_semaphore = asyncio.Semaphore(vlrgg_settings.fetch_match_time_semaphore)
vlrgg_fetch_timeout = httpx.Timeout(vlrgg_settings.fetch_timeout)
vlrgg_match_time_memo: dict[str, int] = {}


def parse_vlrgg_event_title(document: BeautifulSoup) -> str:
    for selector in ("h1.event-header-main-title", "h1.wf-title"):
        title = document.select_one(selector)
        if title:
            title_text = title.get_text(" ", strip=True)
            if title_text:
                return title_text
    raise ValueError("can't parse VLR.gg event title")


def parse_vlrgg_match_time(document: BeautifulSoup) -> datetime | None:
    tag = document.select_one("div.moment-tz-convert[data-utc-ts]")
    if not tag:
        return None

    utc_ts = tag.get("data-utc-ts")
    if not isinstance(utc_ts, str):
        return None

    utc_ts = f"{utc_ts} EDT"
    parsed = dateparser.parse(utc_ts)
    return parsed if isinstance(parsed, datetime) else None


def parse_vlrgg_event_matches(document: BeautifulSoup, wf_title: str) -> list[Event]:
    events = []
    for item in document.select("a.wf-module-item.match-item[href]"):
        match_href = item.get("href")
        if not isinstance(match_href, str):
            continue

        teams = []
        for team_text in item.select("div.match-item-vs-team-name div.text-of"):
            team = team_text.get_text(" ", strip=True)
            if team:
                teams.append(team)
        if not teams:
            continue

        e = Event()
        e.name = f"{' vs '.join(teams)}"
        e.description = wf_title
        e.url = match_href if match_href.startswith("https://") else f"https://www.vlr.gg{match_href}"
        events.append(e)
    return events


def get_cached_vlrgg_match_time(url: str) -> datetime | None:
    global vlrgg_match_time_memo

    cached = vlrgg_match_time_memo.get(url)
    if cached:
        cached_match_datetime = datetime.fromtimestamp(cached).astimezone(timezone.utc)
        now = datetime.now().astimezone(timezone.utc)
        max_datetime = now + timedelta(hours=12)
        min_datetime = now - timedelta(hours=3)
        if min_datetime < cached_match_datetime < max_datetime:
            logger.debug(f"[get_cached_vlrgg_match_time]: skip for {url}")
            return None
        else:
            logger.debug(f"[get_cached_vlrgg_match_time]: cache hit for {url}, {cached}")
            return cached_match_datetime
    logger.debug(f"[get_cached_vlrgg_match_time]: cache miss for {url}")
    return None


async def fetch_vlrgg_event_match_time(url: str) -> tuple[str, datetime | None]:
    cached = get_cached_vlrgg_match_time(url)
    if cached:
        return (url, cached)

    async with fetch_vlrgg_match_time_semaphore:
        async with httpx.AsyncClient(timeout=vlrgg_fetch_timeout) as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
            except httpx.HTTPError as error:
                logger.warning(f"can't fetch match time from VLR.gg: {url} - {error}")
                return (url, None)
            document = BeautifulSoup(resp.text, "lxml")
            match_datetime = parse_vlrgg_match_time(document)
            logger.debug(f"[VLRGG Event Match Time]: {match_datetime} - {url}")
            if match_datetime:
                vlrgg_match_time_memo[url] = int(match_datetime.timestamp())
            return (url, match_datetime)


async def add_vlrgg_event_march_time(events: list[Event]):
    url_to_match_time = {}
    results = await asyncio.gather(*[fetch_vlrgg_event_match_time(e.url) for e in events if e.url])
    for result in results:
        url, datetime = result
        url_to_match_time[url] = datetime

    for e in events:
        match_datetime = url_to_match_time.get(e.url) if e.url else None
        if match_datetime:
            e.begin = e.end = match_datetime.astimezone(timezone.utc)
        else:
            logger.warning(f"can't parse match time: {e.name} - {e.url}")
        logger.debug(f"[Valorant Matches]: {e.name} - {e.begin} - {e.end}")


async def vlrgg_event_to_calendar(vlrgg_event: str) -> list[Event]:
    events = []
    async with httpx.AsyncClient(timeout=vlrgg_fetch_timeout) as client:
        url = f"https://www.vlr.gg/event/matches/{vlrgg_event}/"
        resp = await client.get(url)
        resp.raise_for_status()
        document = BeautifulSoup(resp.text, "lxml")
        wf_title = parse_vlrgg_event_title(document)
        events = parse_vlrgg_event_matches(document, wf_title)
    await add_vlrgg_event_march_time(events)
    return events


@router.get("/event/matches", summary="Valorant 赛事订阅", include_in_schema=False)
@router.get("/event/matches.ics", summary="Valorant 赛事订阅")
async def vlrgg(events: list[str] = Query([], description="赛事ID")):
    """赛程数据源自: https://www.vlr.gg/events"""
    results = await asyncio.gather(*[vlrgg_event_to_calendar(event) for event in events])
    c = Calendar()
    for result in results:
        c.events |= set(result)
    return PlainTextResponse(c.serialize())
