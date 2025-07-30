from typing import List, Optional, Dict, Union, Any
from pydantic import BaseModel, model_validator
from .shared_models import Address

class Customer(BaseModel):
    id: Optional[int] = None
    code: Optional[str] = None
    customerNo: Optional[str] = None
    name: Optional[str] = None
    foregroundColor: Optional[int] = None
    backgroundColor: Optional[int] = None
    hold: Optional[bool] = None
    status: Optional[str] = None
    reference: Optional[str] = None
    address: Optional[Address] = None
    shippingAddresses: Optional[List[Address]] = None
    paymentTerms: Optional[Dict[str, Any]] = None
    applyFinanceCharges: Optional[bool] = None
    statementType: Optional[str] = None
    creditType: Optional[int] = None
    creditLimit: Optional[str] = None
    creditBalance: Optional[str] = None
    creditApprovedBy: Optional[str] = None
    creditApprovedDate: Optional[str] = None
    currency: Optional[str] = None 
    userDef1: Optional[str] = None
    userDef2: Optional[str] = None
    discount: Optional[str] = None
    receivableAccount: Optional[str] = None
    defaultShipTo: Optional[str] = None
    specialCode: Optional[str] = None
    upload: Optional[bool] = None
    lastModified: Optional[str] = None
    paymentProviderId: Optional[int] = None
    udf: Optional[Dict[str, Any]] = None
    createdBy: Optional[str] = None
    modifiedBy: Optional[str] = None
    created: Optional[str] = None
    modified: Optional[str] = None
    links: Optional[Dict[str, str]] = None