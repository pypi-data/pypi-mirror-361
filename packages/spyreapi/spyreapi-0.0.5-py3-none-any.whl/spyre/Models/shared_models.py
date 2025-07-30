from typing import List, Optional, Dict, Union, Any
from pydantic import BaseModel, model_validator

class PhoneFax(BaseModel):
    number: str
    format: Optional[int] = 1

class Contact(BaseModel):
    id: Optional[int] = None
    contact_type: Optional[dict] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[PhoneFax] = None
    fax: Optional[PhoneFax] = None


class Salesperson(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None

class Territory(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None


class Currency(BaseModel):
    id: Optional[int] = None
    code: Optional[str] = None
    description: Optional[str] = None
    country: Optional[str] = None
    units: Optional[str] = None
    fraction: Optional[str] = None
    symbol: Optional[str] = None
    decimalPlaces: Optional[int] = None
    symbolPosition: Optional[str] = None
    rate: Optional[str] = None
    rateMethod: Optional[str] = None
    glAccountNo: Optional[str] = None
    thousandsSeparator: Optional[str] = None
    lastYearRate: Optional[List[str]] = None
    thisYearRate: Optional[List[str]] = None
    nextYearRate: Optional[List[str]] = None


class Tax(BaseModel):
    code: Optional[int] = None
    name: Optional[str] = None
    shortName: Optional[str] = None
    rate: Optional[Union[str, int]] = None
    exemptNo: Optional[str] = None
    total: Optional[Union[str, int]] = None    


class Address(BaseModel):
    id: Optional[int] = None
    type: Optional[str] = None
    linkTable: Optional[str] = None
    linkType: Optional[str] = None
    linkNo: Optional[str] = None
    shipId: Optional[str] = None
    name: Optional[str] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    line3: Optional[str] = None
    line4: Optional[str] = None
    city: Optional[str] = None
    postalCode: Optional[str] = None
    provState: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[PhoneFax] = None
    fax: Optional[PhoneFax] = None
    email: Optional[str] = None
    website: Optional[str] = None
    shipCode: Optional[str] = None
    shipDescription: Optional[str] = None
    salesperson: Optional[Salesperson] = None
    territory: Optional[Territory] = None
    sellLevel: Optional[int] = None
    glAccount: Optional[str] = None
    defaultWarehouse: Optional[str] = None
    udf: Optional[dict] = None
    created: Optional[str] = None
    modified: Optional[str] = None
    contacts: Optional[List[Contact]] = None
    salesTaxes: Optional[List[Dict[str, Union[int, str]]]] = None
    
    @model_validator(mode="before")
    @classmethod
    def limit_contacts_to_three(cls, data):
        """Limits contacts to 3 per address. The Spire API only allows Creatig/Updating Addresses with contacts."""

        if isinstance(data, dict):
            contacts = data.get('contacts')
            if isinstance(contacts, list) and len(contacts) > 3:
                data['contacts'] = contacts[:3]
        return data

class AssignedTo(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    username: Optional[str] = None
    
class Note(BaseModel):
    id: Optional[int] = None
    linkTable: Optional[str] = None
    linkNo: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    attachment: Optional[Any] = None
    attachmentName: Optional[str] = None
    dueDate: Optional[str] = None
    completedDate: Optional[str] = None
    attention: Optional[str] = None
    type: Optional[str] = None
    displayType: Optional[str] = None
    assignedTo: Optional[AssignedTo] = None
    groupType: Optional[str] = None
    qty: Optional[int] = None
    alert: Optional[Union[str, bool]] = None
    print: Optional[Union[str, bool]] = None
    created: Optional[str] = None
    createdBy: Optional[str] = None
    modified: Optional[str] = None
    modifiedBy: Optional[str] = None
    links: Optional[Dict[str, str]] = None