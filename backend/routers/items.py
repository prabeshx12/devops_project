import logging
from time import perf_counter

from fastapi import APIRouter, Query, Response, status
from pydantic import BaseModel, Field

from backend.metrics import INVENTORY_OPERATION_DURATION_SECONDS, INVENTORY_OPERATIONS_TOTAL
from backend.services import inventory_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/items", tags=["inventory"])


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(default="General", max_length=60)
    quantity: int = Field(..., ge=0)
    low_stock_threshold: int = Field(default=5, ge=0)
    location: str = Field(default="Store Room", max_length=80)
    status: str = Field(default="active", pattern="^(active|archived)$")
    notes: str = Field(default="", max_length=300)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, max_length=60)
    quantity: int | None = Field(default=None, ge=0)
    low_stock_threshold: int | None = Field(default=None, ge=0)
    location: str | None = Field(default=None, max_length=80)
    status: str | None = Field(default=None, pattern="^(active|archived)$")
    notes: str | None = Field(default=None, max_length=300)


def _record(operation: str, started_at: float) -> None:
    INVENTORY_OPERATIONS_TOTAL.labels(operation=operation).inc()
    INVENTORY_OPERATION_DURATION_SECONDS.labels(operation=operation).observe(perf_counter() - started_at)


@router.get("")
def list_items(
    status_filter: str | None = Query(default=None, alias="status"),
    low_stock: bool = Query(default=False),
):
    started = perf_counter()
    items = inventory_service.list_items(status=status_filter, low_stock=low_stock)
    _record("list", started)
    return {"items": items, "count": len(items)}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    started = perf_counter()
    created = inventory_service.create_item(item.model_dump())
    logger.info("Created inventory item %s", created["id"])
    _record("create", started)
    return created


@router.get("/export")
def export_items():
    started = perf_counter()
    csv_data = inventory_service.export_items_csv()
    _record("export_csv", started)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory-export.csv"},
    )


@router.get("/{item_id}")
def get_item(item_id: str):
    started = perf_counter()
    item = inventory_service.get_item(item_id)
    _record("get", started)
    return item


@router.put("/{item_id}")
def update_item(item_id: str, item: ItemUpdate):
    started = perf_counter()
    payload = item.model_dump(exclude_unset=True)
    updated = inventory_service.update_item(item_id, payload)
    logger.info("Updated inventory item %s", item_id)
    _record("update", started)
    return updated


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: str):
    started = perf_counter()
    inventory_service.delete_item(item_id)
    logger.info("Deleted inventory item %s", item_id)
    _record("delete", started)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

