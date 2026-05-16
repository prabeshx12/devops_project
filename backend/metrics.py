from prometheus_client import Counter, Histogram, Gauge


INVENTORY_OPERATIONS_TOTAL = Counter(
    "inventory_operations_total",
    "Total inventory operations performed",
    ["operation"],
)

INVENTORY_OPERATION_DURATION_SECONDS = Histogram(
    "inventory_operation_duration_seconds",
    "Inventory operation processing duration in seconds",
    ["operation"],
)

INVENTORY_ITEMS_TOTAL = Gauge(
    "inventory_items_total",
    "Current number of items in inventory",
)

INVENTORY_LOW_STOCK_TOTAL = Gauge(
    "inventory_low_stock_total",
    "Current number of low-stock inventory items",
)

