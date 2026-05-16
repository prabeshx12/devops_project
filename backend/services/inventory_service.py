import csv
import json
import os
import uuid
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from backend.metrics import INVENTORY_ITEMS_TOTAL, INVENTORY_LOW_STOCK_TOTAL


def get_data_file() -> Path:
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "inventory.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_items() -> list[dict[str, Any]]:
    data_file = get_data_file()
    if not data_file.exists():
        data_file.write_text("[]", encoding="utf-8")
        return []
    try:
        return json.loads(data_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Inventory data file is invalid JSON") from exc


def _write_items(items: list[dict[str, Any]]) -> None:
    get_data_file().write_text(json.dumps(items, indent=2), encoding="utf-8")
    refresh_inventory_metrics(items)


def refresh_inventory_metrics(items: list[dict[str, Any]] | None = None) -> None:
    current_items = items if items is not None else _read_items()
    INVENTORY_ITEMS_TOTAL.set(len(current_items))
    INVENTORY_LOW_STOCK_TOTAL.set(sum(1 for item in current_items if item["quantity"] <= item["low_stock_threshold"]))


def list_items(status: str | None = None, low_stock: bool = False) -> list[dict[str, Any]]:
    items = _read_items()
    if status:
        items = [item for item in items if item["status"] == status]
    if low_stock:
        items = [item for item in items if item["quantity"] <= item["low_stock_threshold"]]
    refresh_inventory_metrics(items if not status and not low_stock else None)
    return items


def get_item(item_id: str) -> dict[str, Any]:
    for item in _read_items():
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


def create_item(payload: dict[str, Any]) -> dict[str, Any]:
    items = _read_items()
    timestamp = _now()
    item = {
        "id": str(uuid.uuid4()),
        "name": payload["name"].strip(),
        "category": payload.get("category", "General").strip() or "General",
        "quantity": payload["quantity"],
        "low_stock_threshold": payload.get("low_stock_threshold", 5),
        "location": payload.get("location", "Store Room").strip() or "Store Room",
        "status": payload.get("status", "active"),
        "notes": payload.get("notes", "").strip(),
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    items.append(item)
    _write_items(items)
    return item


def update_item(item_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    items = _read_items()
    for index, item in enumerate(items):
        if item["id"] == item_id:
            updated = {**item, **payload, "updated_at": _now()}
            if "name" in updated:
                updated["name"] = updated["name"].strip()
            if "category" in updated:
                updated["category"] = updated["category"].strip() or "General"
            if "location" in updated:
                updated["location"] = updated["location"].strip() or "Store Room"
            if "notes" in updated:
                updated["notes"] = updated["notes"].strip()
            items[index] = updated
            _write_items(items)
            return updated
    raise HTTPException(status_code=404, detail="Item not found")


def delete_item(item_id: str) -> None:
    items = _read_items()
    remaining = [item for item in items if item["id"] != item_id]
    if len(remaining) == len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    _write_items(remaining)


def export_items_csv() -> str:
    output = StringIO()
    fieldnames = [
        "id",
        "name",
        "category",
        "quantity",
        "low_stock_threshold",
        "location",
        "status",
        "notes",
        "created_at",
        "updated_at",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(_read_items())
    return output.getvalue()

