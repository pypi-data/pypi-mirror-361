from typing import List, Dict, Optional, Union
from pydantic import BaseModel



class UPC(BaseModel):
    id: Optional[int] = None
    whse: Optional[str] = None
    partNo: Optional[str] = None
    inventory: Optional[Dict] = None
    uomCode: Optional[str] = None
    upc: Optional[str] = None
    created: Optional[str] = None
    createdBy: Optional[str] = None
    modified: Optional[str] = None
    modifiedBy: Optional[str] = None
    links: Optional[Dict[str, str]] = None

class Vendor(BaseModel):
    id: Optional[int] = None
    vendorNo: Optional[str] = None
    name: Optional[str] = None


class UnitOfMeasure(BaseModel):
    id: Optional[int] = None
    code: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    weight: Optional[str] = None
    buyUOM: Optional[bool] = None
    sellUOM: Optional[bool] = None
    allowFractionalQty: Optional[bool] = None
    quantityFactor: Optional[str] = None
    directFactor: Optional[bool] = None


class Pricing(BaseModel):
    id: Optional[int] = None
    sellPrice: Optional[List[str]] = None
    currMargin: Optional[str] = None
    currMarginPct: Optional[str] = None
    avgMargin: Optional[str] = None
    avgMarginPct: Optional[str] = None


class ItemUDF(BaseModel):
    desc: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    title: Optional[str] = None
    online: Optional[bool] = None
    pk_qty: Optional[str] = None
    volume: Optional[str] = None
    presale: Optional[bool] = None
    sds_url: Optional[str] = None
    tds_url: Optional[str] = None
    features: Optional[str] = None
    includes: Optional[str] = None
    keywords: Optional[str] = None
    op1_name: Optional[str] = None
    op2_name: Optional[str] = None
    op3_name: Optional[str] = None
    op4_name: Optional[str] = None
    asm_depth: Optional[str] = None
    asm_width: Optional[str] = None
    category1: Optional[str] = None
    category2: Optional[str] = None
    category3: Optional[str] = None
    category4: Optional[str] = None
    op1_value: Optional[str] = None
    op2_value: Optional[str] = None
    op3_value: Optional[str] = None
    op4_value: Optional[str] = None
    pkg_depth: Optional[str] = None
    pkg_width: Optional[str] = None
    asm_height: Optional[str] = None
    asm_length: Optional[str] = None
    asm_weight: Optional[str] = None
    html_specs: Optional[str] = None
    image_urls: Optional[str] = None
    is_variant: Optional[bool] = None
    pkg_height: Optional[str] = None
    pkg_length: Optional[str] = None
    pkg_weight: Optional[str] = None
    put_online: Optional[bool] = None
    upc_needed: Optional[bool] = None
    video_urls: Optional[str] = None
    hdr_part_no: Optional[str] = None
    applications: Optional[str] = None
    sell_through: Optional[bool] = None
    unique_title: Optional[str] = None
    alternate_res: Optional[str] = None
    asm_weight_op: Optional[str] = None
    html_includes: Optional[str] = None
    more_info_url: Optional[str] = None
    specsheet_url: Optional[str] = None
    html_desc_feat: Optional[str] = None
    specifications: Optional[str] = None
    html_dimensions: Optional[str] = None
    special_delivery: Optional[bool] = None
    alternate_res_src: Optional[str] = None
    html_applications: Optional[str] = None


class InventoryItem(BaseModel):
    id: Optional[int] = None
    whse: Optional[str] = None
    partNo: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    status: Optional[int] = None
    lotNumbered: Optional[bool] = None
    serialized: Optional[bool] = None
    availableQty: Optional[str] = None
    onHandQty: Optional[str] = None
    committedQty: Optional[str] = None
    backorderQty: Optional[str] = None
    onPurchaseQty: Optional[str] = None
    foregroundColor: Optional[int] = None
    backgroundColor: Optional[int] = None
    primaryVendor: Optional[Vendor] = None
    currentPONo: Optional[str] = None
    poDueDate: Optional[str] = None
    reorderPoint: Optional[str] = None
    minimumBuyQty: Optional[str] = None
    currentCost: Optional[str] = None
    averageCost: Optional[str] = None
    standardCost: Optional[str] = None
    unitOfMeasures: Optional[Dict[str, UnitOfMeasure]] = None
    buyMeasureCode: Optional[str] = None
    stockMeasureCode: Optional[str] = None
    sellMeasureCode: Optional[str] = None
    alternatePartNo: Optional[str] = None
    productCode: Optional[str] = None
    groupNo: Optional[str] = None
    salesDept: Optional[str] = None
    userDef1: Optional[str] = None
    userDef2: Optional[str] = None
    discountable: Optional[bool] = None
    weight: Optional[str] = None
    packSize: Optional[str] = None
    allowBackorders: Optional[bool] = None
    allowReturns: Optional[bool] = None
    dutyPct: Optional[str] = None
    freightPct: Optional[str] = None
    manufactureCountry: Optional[str] = None
    harmonizedCode: Optional[str] = None
    extendedDescription: Optional[str] = None
    pricing: Optional[Union[ Pricing | Dict[str, Pricing]]] = None
    salesTaxFlags: Optional[Dict[str, Union[str, int, float, bool]]] = None
    images: Optional[List[str]] = None
    defaultExpiryDate: Optional[str] = None
    lotConsumeType: Optional[str] = None
    upload: Optional[bool] = None
    showOptions: Optional[bool] = None
    lastModified: Optional[str] = None
    levy: Optional[Union[str | dict]] = None
    udf: Optional[ItemUDF] = None
    createdBy: Optional[str] = None
    modifiedBy: Optional[str] = None
    created: Optional[str] = None
    modified: Optional[str] = None
    links: Optional[Dict[str, Union[str, int, float, bool]]] = None
