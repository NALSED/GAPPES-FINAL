"""Adaptateurs purs JSON brut -> Observations, et registre par écosystème."""

from __future__ import annotations

import hashlib
import logging
import re
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, ClassVar

from grappes.models import Observation

log = logging.getLogger(__name__)


class FetcherError(Exception):
    """JSON brut inexploitable."""


@dataclass(slots=True)
class RejectReport:
    """Rapport de rejets d'un lot : comptes et motifs, sans interrompre le lot."""

    accepted: int = 0
    duplicates: int = 0
    rejected: list[tuple[int, str]] = field(default_factory=list)  # (index, motif)

    @property
    def n_rejected(self) -> int:
        return len(self.rejected)


class BaseFetcher(ABC):
    ecosystem: ClassVar[str]

    @abstractmethod
    def parse(self, raw: Mapping[str, Any]) -> Iterable[Observation]:
        """Un enregistrement JSON brut -> Observations. Pure, sans I/O."""

    def parse_many(
        self, raws: Iterable[Mapping[str, Any]]
    ) -> tuple[list[Observation], RejectReport]:
        """Tolérant : invalides comptés et journalisés, doublons (même obs_id) écartés."""
        report = RejectReport()
        seen: set[str] = set()
        out: list[Observation] = []
        for i, raw in enumerate(raws):
            try:
                obs_list = list(self.parse(raw))
            except FetcherError as exc:
                report.rejected.append((i, str(exc)))
                log.warning("%s: enregistrement %d rejeté : %s", self.ecosystem, i, exc)
                continue
            except (TypeError, ValueError, KeyError, AttributeError) as exc:
                report.rejected.append((i, f"{type(exc).__name__}: {exc}"))
                log.warning("%s: enregistrement %d invalide : %s", self.ecosystem, i, exc)
                continue
            for obs in obs_list:
                if obs.obs_id in seen:
                    report.duplicates += 1
                    continue
                seen.add(obs.obs_id)
                out.append(obs)
                report.accepted += 1
        return out, report

    def fetch_raw(self, **params) -> Iterable[Mapping[str, Any]]:
        raise NotImplementedError("Hors périmètre v1 : le JSON est fourni de l'extérieur.")


_REGISTRY: dict[str, type[BaseFetcher]] = {}


def register(cls: type[BaseFetcher]) -> type[BaseFetcher]:
    """Décorateur : enregistre un fetcher par `ecosystem`."""
    eco = getattr(cls, "ecosystem", None)
    if not eco:
        raise ValueError(f"{cls.__name__} n'a pas d'attribut `ecosystem`")
    if eco in _REGISTRY and _REGISTRY[eco] is not cls:
        raise ValueError(f"écosystème déjà enregistré : {eco}")
    _REGISTRY[eco] = cls
    return cls


def get_fetcher(ecosystem: str) -> BaseFetcher:
    try:
        return _REGISTRY[ecosystem]()
    except KeyError:
        raise FetcherError(f"écosystème inconnu : {ecosystem}") from None


def registered_ecosystems() -> list[str]:
    return sorted(_REGISTRY)


# --- utilitaires partagés par les fetchers -------------------------------------------------

_HASHTAG_RE = re.compile(r"(?<!\w)#(\w+)", re.UNICODE)
_MENTION_RE = re.compile(r"(?<![\w@])@(\w{1,64})", re.UNICODE)


def make_obs_id(ecosystem: str, native_id: str, text: str) -> str:
    h = hashlib.sha256(f"{ecosystem}\x1f{native_id}\x1f{text}".encode()).hexdigest()
    return h[:24]


def parse_ts(value: Any) -> datetime | None:
    """ISO 8601 ou epoch (s) -> datetime UTC ; None si absent ou illisible."""
    if value is None or value == "":
        return None
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return datetime.fromtimestamp(value, tz=UTC)
        dt = datetime.fromisoformat(str(value).strip())
    except (ValueError, OverflowError, OSError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def extract_hashtags(text: str) -> list[str]:
    return [m.casefold() for m in _HASHTAG_RE.findall(text)]


def extract_mentions(text: str) -> list[str]:
    return [m for m in _MENTION_RE.findall(text)]


def dedup(items: Iterable[Any]) -> tuple[Any, ...]:
    """Déduplication en conservant l'ordre."""
    return tuple(dict.fromkeys(items))


def to_int(value: Any) -> int:
    try:
        return max(int(value), 0)
    except (TypeError, ValueError):
        return 0


Normalizer = Callable[[str], str]
