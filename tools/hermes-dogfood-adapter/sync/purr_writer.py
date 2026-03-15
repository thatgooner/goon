from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence, TypedDict


class PurrWriterError(RuntimeError):
    """Base error for idempotent Purr ledger writes."""


class PurrWriterConfigurationError(PurrWriterError):
    """Raised when the writer is misconfigured for Supabase access."""


class PurrWriterValidationError(PurrWriterError):
    """Raised when a write request cannot be made retry-safe."""


class SupabaseRequestError(PurrWriterError):
    """Raised when Supabase/PostgREST returns a non-success response."""

    def __init__(self, message: str, *, status_code: int | None = None, body: Any | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class MemoryItemRow(TypedDict, total=False):
    memory_id: str
    owner_id: str
    purr_id: str
    memory_lane: str
    kind: str
    state: str
    review_status: str
    contradiction_status: str
    pack_policy: str
    durability_scope: str
    is_exclusive: bool
    subject_key: str
    dedupe_key: str
    scope_ref: str | None
    episode_id: str | None
    origin_window_id: str | None
    owner_surface: str
    confidence: float
    salience: float
    volatility: float
    freshness_score: float
    last_confirmed_at: str | None
    last_hit_at: str | None
    last_miss_at: str | None
    needs_review_at: str | None
    cooldown_until: str | None
    attempt_count: int
    expires_at: str | None
    supersedes_memory_id: str | None
    payload_json: dict[str, Any]
    created_at: str


class MemoryEventRow(TypedDict, total=False):
    memory_event_id: str
    memory_id: str
    owner_id: str
    purr_id: str
    event_type: str
    event_reason: str | None
    actor_type: str
    from_state: str | None
    to_state: str | None
    intake_batch_key: str | None
    delta_json: dict[str, Any]
    created_at: str


class MemoryEvidenceRefRow(TypedDict, total=False):
    evidence_id: str
    memory_id: str
    owner_id: str
    purr_id: str
    episode_id: str
    window_id: str
    message_id: str
    span_start: int
    span_end: int
    source_type: str
    excerpt_text: str
    excerpt_hash: str
    evidence_weight: float
    explicitness: str
    speaker_role: str
    derived_from_evidence_id: str | None
    captured_at: str


@dataclass(frozen=True, slots=True)
class MemoryWriteBundle:
    memory_item: MemoryItemRow
    evidence_refs: tuple[MemoryEvidenceRefRow, ...]
    memory_events: tuple[MemoryEventRow, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "memory_item", dict(self.memory_item))
        object.__setattr__(self, "evidence_refs", tuple(dict(row) for row in self.evidence_refs))
        object.__setattr__(self, "memory_events", tuple(dict(row) for row in self.memory_events))


@dataclass(frozen=True, slots=True)
class BatchWriteResult:
    table: str
    attempted: int
    submitted: int
    inserted: int | None = None


@dataclass(frozen=True, slots=True)
class MemoryBundleWriteResult:
    memory_id: str
    inserted_memory_item: bool
    inserted_memory_events: int
    inserted_evidence_refs: int


@dataclass(frozen=True, slots=True)
class SupabaseWriterConfig:
    url: str
    service_role_key: str
    timeout_seconds: float = 20.0
    batch_size: int = 200
    memory_bundle_rpc_name: str = "sync_memory_bundle_phase0"
    memory_events_rpc_name: str = "sync_memory_events_phase0"

    @classmethod
    def from_env(
        cls,
        *,
        timeout_seconds: float = 20.0,
        batch_size: int = 200,
        memory_bundle_rpc_name: str = "sync_memory_bundle_phase0",
        memory_events_rpc_name: str = "sync_memory_events_phase0",
    ) -> "SupabaseWriterConfig":
        url = os.environ.get("SUPABASE_URL", "").strip()
        service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        if not url:
            raise PurrWriterConfigurationError("SUPABASE_URL is required")
        if not service_role_key:
            raise PurrWriterConfigurationError("SUPABASE_SERVICE_ROLE_KEY is required")
        return cls(
            url=url,
            service_role_key=service_role_key,
            timeout_seconds=timeout_seconds,
            batch_size=batch_size,
            memory_bundle_rpc_name=memory_bundle_rpc_name,
            memory_events_rpc_name=memory_events_rpc_name,
        )


class PurrWriterBackend(Protocol):
    def upsert_rows(
        self,
        *,
        table: str,
        rows: Sequence[Mapping[str, Any]],
        on_conflict: Sequence[str],
        resolution: str,
    ) -> None: ...

    def call_rpc(
        self,
        *,
        function_name: str,
        payload: Mapping[str, Any],
    ) -> Mapping[str, Any] | None: ...


class SupabaseRestBackend:
    """Small PostgREST client used by the phase-0 writer.

    It only implements the narrow operations the adapter needs:
    idempotent upsert-like inserts via `resolution=ignore-duplicates` and RPC calls.
    """

    def __init__(
        self,
        *,
        url: str,
        service_role_key: str,
        timeout_seconds: float = 20.0,
    ) -> None:
        normalized_url = url.strip().rstrip("/")
        if not normalized_url:
            raise PurrWriterConfigurationError("Supabase URL must be non-empty")
        if normalized_url.endswith("/rest/v1"):
            self._rest_base_url = normalized_url
        else:
            self._rest_base_url = f"{normalized_url}/rest/v1"

        service_role_key = service_role_key.strip()
        if not service_role_key:
            raise PurrWriterConfigurationError("Supabase service role key must be non-empty")

        self._service_role_key = service_role_key
        self._timeout_seconds = timeout_seconds

    def upsert_rows(
        self,
        *,
        table: str,
        rows: Sequence[Mapping[str, Any]],
        on_conflict: Sequence[str],
        resolution: str,
    ) -> None:
        if not rows:
            return
        if resolution not in {"ignore-duplicates", "merge-duplicates"}:
            raise ValueError(f"Unsupported PostgREST resolution mode: {resolution}")
        conflict_target = ",".join(on_conflict)
        query = ""
        if conflict_target:
            encoded = urllib.parse.quote(conflict_target, safe=",")
            query = f"?on_conflict={encoded}"

        self._request_json(
            f"{self._rest_base_url}/{table}{query}",
            payload=list(rows),
            prefer=(f"resolution={resolution}", "return=minimal"),
        )

    def call_rpc(
        self,
        *,
        function_name: str,
        payload: Mapping[str, Any],
    ) -> Mapping[str, Any] | None:
        response = self._request_json(
            f"{self._rest_base_url}/rpc/{function_name}",
            payload=dict(payload),
            prefer=("return=representation",),
        )
        if response is None:
            return None
        if not isinstance(response, Mapping):
            raise SupabaseRequestError(
                f"RPC {function_name!r} returned a non-object payload",
                body=response,
            )
        return response

    def _request_json(
        self,
        url: str,
        *,
        payload: Any,
        prefer: Sequence[str],
    ) -> Any | None:
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={
                "apikey": self._service_role_key,
                "Authorization": f"Bearer {self._service_role_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Prefer": ",".join(prefer),
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                raw_body = response.read()
                if not raw_body:
                    return None
                return json.loads(raw_body.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                parsed_body: Any = json.loads(body) if body else None
            except json.JSONDecodeError:
                parsed_body = body
            raise SupabaseRequestError(
                f"Supabase request failed for {url} with status {exc.code}",
                status_code=exc.code,
                body=parsed_body,
            ) from exc
        except urllib.error.URLError as exc:
            raise SupabaseRequestError(f"Supabase request failed for {url}: {exc.reason}") from exc


class PurrWriter:
    def __init__(
        self,
        backend: PurrWriterBackend,
        *,
        batch_size: int = 200,
        memory_bundle_rpc_name: str = "sync_memory_bundle_phase0",
        memory_events_rpc_name: str = "sync_memory_events_phase0",
    ) -> None:
        if batch_size <= 0:
            raise ValueError(f"batch_size must be > 0, got {batch_size}")
        if not memory_bundle_rpc_name.strip():
            raise ValueError("memory_bundle_rpc_name must be non-empty")
        if not memory_events_rpc_name.strip():
            raise ValueError("memory_events_rpc_name must be non-empty")
        self._backend = backend
        self._batch_size = batch_size
        self._memory_bundle_rpc_name = memory_bundle_rpc_name
        self._memory_events_rpc_name = memory_events_rpc_name

    @classmethod
    def from_env(
        cls,
        *,
        timeout_seconds: float = 20.0,
        batch_size: int = 200,
        memory_bundle_rpc_name: str = "sync_memory_bundle_phase0",
        memory_events_rpc_name: str = "sync_memory_events_phase0",
    ) -> "PurrWriter":
        config = SupabaseWriterConfig.from_env(
            timeout_seconds=timeout_seconds,
            batch_size=batch_size,
            memory_bundle_rpc_name=memory_bundle_rpc_name,
            memory_events_rpc_name=memory_events_rpc_name,
        )
        backend = SupabaseRestBackend(
            url=config.url,
            service_role_key=config.service_role_key,
            timeout_seconds=config.timeout_seconds,
        )
        return cls(
            backend,
            batch_size=config.batch_size,
            memory_bundle_rpc_name=config.memory_bundle_rpc_name,
            memory_events_rpc_name=config.memory_events_rpc_name,
        )

    def upsert_episodes(self, rows: Sequence[Mapping[str, Any]]) -> BatchWriteResult:
        return self._write_simple_table(
            table="episodes",
            rows=rows,
            on_conflict=("episode_id",),
            resolution="merge-duplicates",
            row_key=self._episode_identity,
            sort_key=lambda row: (str(row.get("started_at") or ""), str(row.get("episode_id") or "")),
        )

    def upsert_session_windows(self, rows: Sequence[Mapping[str, Any]]) -> BatchWriteResult:
        return self._write_simple_table(
            table="session_windows",
            rows=rows,
            on_conflict=("window_id",),
            resolution="merge-duplicates",
            row_key=self._window_identity,
            sort_key=lambda row: (str(row.get("opened_at") or ""), str(row.get("window_id") or "")),
        )

    def upsert_message_events(self, rows: Sequence[Mapping[str, Any]]) -> BatchWriteResult:
        return self._write_simple_table(
            table="message_events",
            rows=rows,
            on_conflict=("message_id",),
            resolution="ignore-duplicates",
            row_key=self._message_identity,
            sort_key=lambda row: (str(row.get("created_at") or ""), str(row.get("message_id") or "")),
        )

    def upsert_memory_events(self, rows: Sequence[Mapping[str, Any]]) -> BatchWriteResult:
        normalized_rows = [dict(row) for row in rows]
        for row in normalized_rows:
            self._require_intake_batch_key(row)
        unique_rows = self._dedupe_rows(normalized_rows, self._memory_event_identity)
        ordered_rows = sorted(unique_rows, key=self._memory_event_sort_key)
        response = self._backend.call_rpc(
            function_name=self._memory_events_rpc_name,
            payload={"memory_events": ordered_rows},
        )
        if not isinstance(response, Mapping):
            raise PurrWriterError(
                f"RPC {self._memory_events_rpc_name!r} did not return a response mapping"
            )
        try:
            inserted = int(response.get("inserted_memory_events", 0))
        except (TypeError, ValueError) as exc:
            raise PurrWriterError(
                f"RPC {self._memory_events_rpc_name!r} returned an invalid response: {response!r}"
            ) from exc
        return BatchWriteResult(
            table="memory_events",
            attempted=len(rows),
            submitted=len(ordered_rows),
            inserted=inserted,
        )

    def insert_memory_event_if_absent(self, row: Mapping[str, Any]) -> BatchWriteResult:
        return self.upsert_memory_events([row])

    def upsert_memory_evidence_refs(self, rows: Sequence[Mapping[str, Any]]) -> BatchWriteResult:
        return self._write_simple_table(
            table="memory_evidence_refs",
            rows=rows,
            on_conflict=("memory_id", "message_id", "span_start", "span_end"),
            resolution="ignore-duplicates",
            row_key=self._memory_evidence_identity,
            sort_key=lambda row: (
                str(row.get("memory_id") or ""),
                str(row.get("message_id") or ""),
                int(row.get("span_start") or 0),
                int(row.get("span_end") or 0),
            ),
        )

    def insert_memory_evidence_if_absent(self, row: Mapping[str, Any]) -> BatchWriteResult:
        return self.upsert_memory_evidence_refs([row])

    def write_memory_bundle(
        self,
        memory_item: Mapping[str, Any],
        *,
        evidence_refs: Sequence[Mapping[str, Any]],
        memory_events: Sequence[Mapping[str, Any]] = (),
    ) -> MemoryBundleWriteResult:
        return self.write_memory_bundles(
            [
                MemoryWriteBundle(
                    memory_item=dict(memory_item),
                    evidence_refs=tuple(dict(row) for row in evidence_refs),
                    memory_events=tuple(dict(row) for row in memory_events),
                )
            ]
        )[0]

    def write_memory_bundles(self, bundles: Sequence[MemoryWriteBundle]) -> list[MemoryBundleWriteResult]:
        normalized_bundles = self._normalize_memory_bundles(bundles)
        results: list[MemoryBundleWriteResult] = []
        for bundle in normalized_bundles:
            payload = {
                "memory_item": bundle.memory_item,
                "memory_events": list(bundle.memory_events),
                "evidence_refs": list(bundle.evidence_refs),
            }
            response = self._backend.call_rpc(
                function_name=self._memory_bundle_rpc_name,
                payload=payload,
            )
            if not isinstance(response, Mapping):
                raise PurrWriterError(
                    f"RPC {self._memory_bundle_rpc_name!r} did not return a response mapping"
                )
            try:
                memory_id = str(response["memory_id"])
                inserted_memory_item = bool(response.get("inserted_memory_item", False))
                inserted_memory_events = int(response.get("inserted_memory_events", 0))
                inserted_evidence_refs = int(response.get("inserted_evidence_refs", 0))
            except (KeyError, TypeError, ValueError) as exc:
                raise PurrWriterError(
                    f"RPC {self._memory_bundle_rpc_name!r} returned an invalid response: {response!r}"
                ) from exc

            results.append(
                MemoryBundleWriteResult(
                    memory_id=memory_id,
                    inserted_memory_item=inserted_memory_item,
                    inserted_memory_events=inserted_memory_events,
                    inserted_evidence_refs=inserted_evidence_refs,
                )
            )
        return results

    def _write_simple_table(
        self,
        *,
        table: str,
        rows: Sequence[Mapping[str, Any]],
        on_conflict: Sequence[str],
        resolution: str,
        row_key: Any,
        sort_key: Any,
    ) -> BatchWriteResult:
        normalized_rows = [dict(row) for row in rows]
        unique_rows = self._dedupe_rows(normalized_rows, row_key)
        ordered_rows = sorted(unique_rows, key=sort_key)
        for chunk in _chunked(ordered_rows, self._batch_size):
            self._backend.upsert_rows(
                table=table,
                rows=chunk,
                on_conflict=on_conflict,
                resolution=resolution,
            )
        return BatchWriteResult(table=table, attempted=len(rows), submitted=len(ordered_rows))

    def _normalize_memory_bundles(self, bundles: Sequence[MemoryWriteBundle]) -> list[MemoryWriteBundle]:
        merged: dict[tuple[str, str, str, str, str | None], MemoryWriteBundle] = {}
        ordered_keys: list[tuple[str, str, str, str, str | None]] = []

        for bundle in sorted(bundles, key=self._memory_bundle_sort_key):
            self._validate_memory_bundle(bundle)
            identity = self._memory_item_identity(bundle.memory_item)
            if identity not in merged:
                merged_bundle = MemoryWriteBundle(
                    memory_item=dict(bundle.memory_item),
                    evidence_refs=tuple(self._dedupe_rows(bundle.evidence_refs, self._memory_evidence_identity)),
                    memory_events=tuple(self._dedupe_rows(bundle.memory_events, self._memory_event_identity)),
                )
                merged[identity] = merged_bundle
                ordered_keys.append(identity)
                continue

            current = merged[identity]
            if dict(current.memory_item) != dict(bundle.memory_item):
                raise PurrWriterValidationError(
                    "Conflicting memory_item payloads share the same active-truth identity: "
                    f"{identity!r}"
                )

            merged_evidence = self._dedupe_rows(
                [*current.evidence_refs, *bundle.evidence_refs],
                self._memory_evidence_identity,
            )
            merged_events = self._dedupe_rows(
                [*current.memory_events, *bundle.memory_events],
                self._memory_event_identity,
            )
            merged[identity] = MemoryWriteBundle(
                memory_item=current.memory_item,
                evidence_refs=tuple(sorted(merged_evidence, key=self._memory_evidence_sort_key)),
                memory_events=tuple(sorted(merged_events, key=self._memory_event_sort_key)),
            )

        return [merged[key] for key in ordered_keys]

    def _validate_memory_bundle(self, bundle: MemoryWriteBundle) -> None:
        memory_item = bundle.memory_item
        state = str(memory_item.get("state") or "candidate")
        is_exclusive = bool(memory_item.get("is_exclusive", True))
        if not bundle.evidence_refs:
            raise PurrWriterValidationError("memory bundle must include at least one evidence ref")
        if not is_exclusive or state not in {"candidate", "confirmed"}:
            raise PurrWriterValidationError(
                "phase-0 idempotent memory writes only support exclusive candidate/confirmed memory_items"
            )
        memory_lane = str(memory_item.get("memory_lane") or "")
        if memory_lane != "private_1_1":
            raise PurrWriterValidationError(
                "phase-0 writer only supports memory_lane='private_1_1'"
            )

        owner_id = str(memory_item.get("owner_id") or "")
        purr_id = str(memory_item.get("purr_id") or "")
        if not owner_id or not purr_id:
            raise PurrWriterValidationError("memory_item must include owner_id and purr_id")
        if not str(memory_item.get("dedupe_key") or ""):
            raise PurrWriterValidationError("memory_item must include dedupe_key")
        if not str(memory_item.get("durability_scope") or ""):
            raise PurrWriterValidationError("memory_item must include durability_scope")

        for event in bundle.memory_events:
            if str(event.get("owner_id") or "") != owner_id or str(event.get("purr_id") or "") != purr_id:
                raise PurrWriterValidationError("memory_event owner/purr identity must match memory_item")
            self._require_intake_batch_key(event)

        episode_id = self._optional_text(memory_item.get("episode_id"))
        origin_window_id = self._optional_text(memory_item.get("origin_window_id"))
        for evidence in bundle.evidence_refs:
            if str(evidence.get("owner_id") or "") != owner_id or str(evidence.get("purr_id") or "") != purr_id:
                raise PurrWriterValidationError("memory_evidence_ref owner/purr identity must match memory_item")
            if episode_id is not None and str(evidence.get("episode_id") or "") != episode_id:
                raise PurrWriterValidationError("memory_evidence_ref episode_id must match memory_item episode_id")
            if origin_window_id is not None and str(evidence.get("window_id") or "") != origin_window_id:
                raise PurrWriterValidationError("memory_evidence_ref window_id must match memory_item origin_window_id")

    @staticmethod
    def _dedupe_rows(rows: Sequence[Mapping[str, Any]], key_fn: Any) -> list[dict[str, Any]]:
        seen: dict[Any, dict[str, Any]] = {}
        ordered_keys: list[Any] = []
        for row in rows:
            normalized = dict(row)
            identity = key_fn(normalized)
            if identity in seen:
                if seen[identity] != normalized:
                    raise PurrWriterValidationError(
                        f"Conflicting rows share the same idempotency identity: {identity!r}"
                    )
                continue
            seen[identity] = normalized
            ordered_keys.append(identity)
        return [seen[key] for key in ordered_keys]

    @staticmethod
    def _optional_text(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _require_intake_batch_key(row: Mapping[str, Any]) -> None:
        intake_batch_key = str(row.get("intake_batch_key") or "").strip()
        if not intake_batch_key:
            raise PurrWriterValidationError(
                "memory_events require intake_batch_key for retry-safe idempotency"
            )

    @staticmethod
    def _episode_identity(row: Mapping[str, Any]) -> tuple[str]:
        return (str(row.get("episode_id") or ""),)

    @staticmethod
    def _window_identity(row: Mapping[str, Any]) -> tuple[str]:
        return (str(row.get("window_id") or ""),)

    @staticmethod
    def _message_identity(row: Mapping[str, Any]) -> tuple[str]:
        return (str(row.get("message_id") or ""),)

    def _memory_item_identity(self, row: Mapping[str, Any]) -> tuple[str, str, str, str, str | None]:
        return (
            str(row.get("owner_id") or ""),
            str(row.get("purr_id") or ""),
            str(row.get("dedupe_key") or ""),
            str(row.get("durability_scope") or ""),
            self._optional_text(row.get("scope_ref")),
        )

    def _memory_event_identity(self, row: Mapping[str, Any]) -> tuple[str, str, str]:
        return (
            str(row.get("memory_id") or ""),
            str(row.get("event_type") or ""),
            str(row.get("intake_batch_key") or ""),
        )

    @staticmethod
    def _memory_event_sort_key(row: Mapping[str, Any]) -> tuple[str, str, str]:
        return (
            str(row.get("created_at") or ""),
            str(row.get("event_type") or ""),
            str(row.get("intake_batch_key") or ""),
        )

    @staticmethod
    def _memory_evidence_identity(row: Mapping[str, Any]) -> tuple[str, str, int, int]:
        return (
            str(row.get("memory_id") or ""),
            str(row.get("message_id") or ""),
            int(row.get("span_start") or 0),
            int(row.get("span_end") or 0),
        )

    @staticmethod
    def _memory_evidence_sort_key(row: Mapping[str, Any]) -> tuple[str, str, int, int]:
        return (
            str(row.get("message_id") or ""),
            str(row.get("memory_id") or ""),
            int(row.get("span_start") or 0),
            int(row.get("span_end") or 0),
        )

    def _memory_bundle_sort_key(self, bundle: MemoryWriteBundle) -> tuple[str, str, str, str, str, str]:
        row = bundle.memory_item
        return (
            str(row.get("created_at") or ""),
            str(row.get("owner_id") or ""),
            str(row.get("purr_id") or ""),
            str(row.get("durability_scope") or ""),
            str(row.get("dedupe_key") or ""),
            str(row.get("scope_ref") or ""),
        )


def _chunked(rows: Sequence[Mapping[str, Any]], chunk_size: int) -> list[list[Mapping[str, Any]]]:
    return [list(rows[index : index + chunk_size]) for index in range(0, len(rows), chunk_size)]


__all__ = [
    "BatchWriteResult",
    "MemoryBundleWriteResult",
    "MemoryEventRow",
    "MemoryEvidenceRefRow",
    "MemoryItemRow",
    "MemoryWriteBundle",
    "PurrWriter",
    "PurrWriterConfigurationError",
    "PurrWriterError",
    "PurrWriterValidationError",
    "SupabaseRequestError",
    "SupabaseRestBackend",
    "SupabaseWriterConfig",
]
