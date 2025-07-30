from typing import List, Optional, Dict, Union
from pydantic import BaseModel, model_validator
from .shared_models import Address, Currency, Contact, Tax
from .customers_models import Customer

class Inventory(BaseModel):
    id: Optional[int] = None
    whse: Optional[str] = None
    partNo: Optional[str] = None
    description: Optional[str] = None

class SalesOrderItem(BaseModel):
    id: Optional[int] = None
    orderNo: Optional[str] = None
    sequence: Optional[int] = None
    parentSequence: Optional[int] = None
    inventory: Optional[Inventory] = None
    serials: Optional[List[str]] = None
    whse: Optional[str] = None
    partNo: Optional[str] = None
    description: Optional[str] = None
    comment: Optional[str] = None
    orderQty: Optional[str] = None
    committedQty: Optional[str] = None
    backorderQty: Optional[str] = None
    sellMeasure: Optional[str] = None
    retailPrice: Optional[str] = None
    unitPrice: Optional[str] = None
    userPrice: Optional[bool] = None
    discountable: Optional[bool] = None
    discountPct: Optional[str] = None
    discountAmt: Optional[str] = None
    currentCost: Optional[str] = None
    averageCost: Optional[str] = None
    standardCost: Optional[str] = None
    taxFlags: Optional[List[bool]] = None
    vendor: Optional[str] = None
    inventoryAccountNo: Optional[str] = None
    revenueAccountNo: Optional[str] = None
    costOfGoodsAccountNo: Optional[str] = None
    levyCode: Optional[str] = None
    referenceNo: Optional[str] = None
    requiredDate: Optional[str] = None
    extendedPriceOrdered: Optional[str] = None
    extendedPriceCommitted: Optional[str] = None
    kit: Optional[bool] = None
    suppress: Optional[bool] = None
    udf: Optional[dict] = None


class SalesOrder(BaseModel):
    id: Optional[int] = None
    orderNo: Optional[str] = None
    division: Optional[str] = None
    location: Optional[str] = None
    profitCenter: Optional[str] = None
    invoiceNo: Optional[str] = None
    customer: Optional[Customer] = None
    creditApprovedAmount: Optional[str] = None
    creditApprovedDate: Optional[str] = None
    creditApprovedUser: Optional[str] = None
    currency: Optional[Currency] = None
    status: Optional[str] = None
    type: Optional[str] = None
    hold: Optional[bool] = None
    orderDate: Optional[str] = None
    invoiceDate: Optional[str] = None
    requiredDate: Optional[str] = None
    quoteExpires: Optional[str] = None
    recurrenceRule: Optional[str] = None
    address: Optional[Address] = None
    shippingAddress: Optional[Address] = None
    contact: Optional[Contact] = None
    customerPO: Optional[str] = None
    batchNo: Optional[str] = None
    fob: Optional[str] = None
    incoterms: Optional[str] = None
    incotermsPlace: Optional[str] = None
    referenceNo: Optional[str] = None
    shippingCarrier: Optional[str] = None
    shipDate: Optional[str] = None
    trackingNo: Optional[str] = None
    termsCode: Optional[str] = None
    termsText: Optional[str] = None
    freight: Optional[str] = None
    taxes: Optional[List[Tax]] = None
    subtotal: Optional[str] = None
    subtotalOrdered: Optional[str] = None
    discount: Optional[str] = None
    totalDiscount: Optional[str] = None
    total: Optional[str] = None
    totalOrdered: Optional[str] = None
    totalCostCurrent: Optional[str] = None
    totalCostAverage: Optional[str] = None
    grossProfit: Optional[str] = None
    items: Optional[List[SalesOrderItem]] = None
    payments: Optional[List[dict]] = None
    udf: Optional[dict] = None
    createdBy: Optional[str] = None
    modifiedBy: Optional[str] = None
    created: Optional[str] = None
    modified: Optional[str] = None
    deletedBy: Optional[str] = None
    deleted: Optional[str] = None
    links: Optional[Dict[str, str]] = None
    
    @model_validator(mode="before")
    @classmethod
    def clean_problematic_fields(cls, data: dict) -> dict:
        if data.get("currency") == "":
            data["currency"] = None

        contact = data.get("contact")
        if contact:
            for field in ("phone", "fax"):
                phone_data = contact.get(field)
                if isinstance(phone_data, dict) and phone_data.get("number") is None:
                    phone_data["number"] = ""
        return data

class Invoice(BaseModel):
    id: Optional[int] = None
    invoiceNo: Optional[str] = None
    orderNo: Optional[str] = None
    division: Optional[str] = None
    location: Optional[str] = None
    profitCenter: Optional[str] = None
    customer: Optional['Customer'] = None
    currency: Optional['Currency'] = None
    orderDate: Optional[str] = None
    invoiceDate: Optional[str] = None
    requiredDate: Optional[str] = None
    address: Optional['Address'] = None
    shippingAddress: Optional['Address'] = None
    customerPO: Optional[str] = None
    fob: Optional[str] = None
    incoterms: Optional[str] = None
    incotermsPlace: Optional[str] = None
    referenceNo: Optional[str] = None
    shippingCarrier: Optional[str] = None
    shipDate: Optional[str] = None
    trackingNo: Optional[str] = None
    termsCode: Optional[str] = None
    termsText: Optional[str] = None
    freight: Optional[str] = None
    taxes: Optional[List['Tax']] = None
    subtotal: Optional[str] = None
    total: Optional[str] = None
    items: Optional[List['SalesOrderItem']] = None
    payments: Optional[List[dict]] = None
    udf: Optional[dict] = None
    createdBy: Optional[str] = None
    modifiedBy: Optional[str] = None
    created: Optional[str] = None
    modified: Optional[str] = None
    links: Optional[Dict[str, str]] = None

    @model_validator(mode="before")
    @classmethod
    def clean_problematic_fields(cls, data: dict) -> dict:
        if data.get("currency") == "":
            data["currency"] = None

        contact = data.get("contact")
        if contact:
            for field in ("phone", "fax"):
                phone_data = contact.get(field)
                if isinstance(phone_data, dict) and phone_data.get("number") is None:
                    phone_data["number"] = ""
        return data