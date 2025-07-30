from .Models.sales_models import SalesOrder, Invoice
from typing import TypeVar, Optional, Type, List, Set
from copy import deepcopy
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

# These will always be excluded unless explicitly overridden
DEFAULT_EXCLUDE_FIELDS = {'id', 'linkTable', 'linkType', 'linkNo', 'contact_type'}

# Normalize paths by replacing numeric list indices with '*'
def normalize_path(path: str) -> str:
    return '.'.join('*' if part.isdigit() else part for part in path.split('.'))

# Should exclude based on normalized paths
def should_exclude(field_path: str, exclude_paths: Set[str]) -> bool:
    return field_path in exclude_paths or field_path.split('.')[-1] in exclude_paths

def create_duplicate_record(
    instance: T,
    exclude_fields: Optional[List[str]] = None,
    _prefix: str = ""
) -> T:
    if exclude_fields is None:
        exclude_fields = []

    # Normalize exclude paths so comparisons are wildcard-friendly
    full_exclude_paths = {normalize_path(f) for f in DEFAULT_EXCLUDE_FIELDS.union(set(exclude_fields))}
    cleaned_data = {}

    for field_name, value in instance.model_dump().items():
        full_path = f"{_prefix}.{field_name}" if _prefix else field_name

        if should_exclude(full_path, full_exclude_paths):
            continue

        if isinstance(value, BaseModel):
            cleaned_data[field_name] = create_duplicate_record(value, exclude_fields, _prefix=full_path)

        elif isinstance(value, list):
            cleaned_items = []
            for i, item in enumerate(value):
                if isinstance(item, BaseModel):
                    cleaned_items.append(create_duplicate_record(item, exclude_fields, _prefix=full_path))
                elif isinstance(item, dict):
                    cleaned_dict = {}
                    for k, v in item.items():
                        field_k_path = f"{full_path}.{k}"
                        if isinstance(v, BaseModel):
                            cleaned_dict[k] = create_duplicate_record(v, exclude_fields, _prefix=field_k_path)
                        elif should_exclude(field_k_path, full_exclude_paths):
                            continue
                        else:
                            cleaned_dict[k] = deepcopy(v)
                    cleaned_items.append(cleaned_dict)
                else:
                    cleaned_items.append(deepcopy(item))
            cleaned_data[field_name] = cleaned_items

        elif isinstance(value, dict):
            cleaned_dict = {}
            for k, v in value.items():
                dict_path = f"{full_path}.{k}"
                if isinstance(v, BaseModel):
                    cleaned_dict[k] = create_duplicate_record(v, exclude_fields, _prefix=dict_path)
                elif should_exclude(dict_path, full_exclude_paths):
                    continue
                else:
                    cleaned_dict[k] = deepcopy(v)
            cleaned_data[field_name] = cleaned_dict

        else:
            cleaned_data[field_name] = deepcopy(value)

    return instance.__class__(**cleaned_data)

def create_sales_order_from_invoice(invoice: Invoice) -> SalesOrder:
    """Creates a Sales Order from an Invoice
    
    
    Changes when converting
    freight negative
    backorders
    extendedpriceorderd
    orderqty
    shippingCarrier
    subtotalordered
    taxes : {total}
    total
    totalOrdered
    trackingNo

    """


    return SalesOrder(
        orderNo=invoice.orderNo,
        division=invoice.division,
        location=invoice.location,
        profitCenter=invoice.profitCenter,
        customer=deepcopy(invoice.customer),
        currency=deepcopy(invoice.currency),
        status="O",
        type="O",
        hold=False,
        orderDate=invoice.orderDate,
        address=create_duplicate_record(invoice.address, exclude_fields=["contacts.contact_type"]),
        shippingAddress=create_duplicate_record(invoice.shippingAddress),
        customerPO=invoice.customerPO,
        fob=invoice.fob,
        incoterms=invoice.incoterms,
        incotermsPlace=invoice.incotermsPlace,
        referenceNo=None,
        shippingCarrier=None,
        shipDate=invoice.shipDate,
        trackingNo=None,
        termsCode=invoice.termsCode,
        termsText=invoice.termsText,
        freight=f"-{invoice.freight}",
        subtotal=invoice.subtotal,
        total=invoice.total,
        items = [
            create_duplicate_record(item).model_copy(update={
                "orderQty": f"-{item.orderQty}" if item.orderQty != "0" else item.orderQty ,
                "committedQty": f"-{item.committedQty}" if item.committedQty != "0" else item.committedQty
            })
            for item in invoice.items or []
        ],
        udf=deepcopy(invoice.udf),
    )