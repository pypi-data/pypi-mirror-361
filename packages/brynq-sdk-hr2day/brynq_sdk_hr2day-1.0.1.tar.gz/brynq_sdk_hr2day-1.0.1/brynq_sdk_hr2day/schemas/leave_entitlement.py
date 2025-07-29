from datetime import datetime
from pandera.typing import Series
import pandera as pa
import pandas as pd
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class LeaveEntitlementSchema(BrynQPanderaDataFrameModel):
    """Schema for hr2d__LeaveEntitlement__c entity in HR2Day. Represents leave entitlement records."""

    # Base Salesforce fields
    id: Series[pd.StringDtype] = pa.Field(
        coerce=True,
        description="Record ID",
        alias="Id"
    )
    is_deleted: Series[bool] = pa.Field(
        coerce=True,
        description="Is deleted flag",
        alias="IsDeleted"
    )
    name: Series[pd.StringDtype] = pa.Field(
        coerce=True,
        description="Name of the record",
        alias="Name"
    )
    created_date: Series[datetime] = pa.Field(
        coerce=True,
        description="Created date",
        alias="CreatedDate"
    )
    created_by_id: Series[pd.StringDtype] = pa.Field(
        coerce=True,
        description="Created by ID",
        alias="CreatedById"
    )
    last_modified_date: Series[datetime] = pa.Field(
        coerce=True,
        description="Last modified date",
        alias="LastModifiedDate"
    )
    last_modified_by_id: Series[pd.StringDtype] = pa.Field(
        coerce=True,
        description="Last modified by ID",
        alias="LastModifiedById"
    )
    system_modstamp: Series[datetime] = pa.Field(
        coerce=True,
        description="System modstamp",
        alias="SystemModstamp"
    )
    last_activity_date: Series[datetime] = pa.Field(
        coerce=True,
        description="Last activity date",
        alias="LastActivityDate",
        nullable=True
    )

    # HR2Day specific fields
    employee_id: Series[pd.StringDtype] = pa.Field(
        coerce=True,
        description="Employee ID reference",
        alias="hr2d__Employee__c"
    )
    start_date: Series[datetime] = pa.Field(
        coerce=True,
        description="Start date of entitlement period",
        alias="hr2d__StartDate__c"
    )
    end_date: Series[datetime] = pa.Field(
        coerce=True,
        description="End date of entitlement period",
        alias="hr2d__EndDate__c"
    )
    arbeidsrel_volgnr: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="Employment relationship sequence number",
        alias="hr2d__ArbrelVolgnr__c"
    )
    balance_total: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="Total balance across all leave types",
        alias="hr2d__BalanceTotal__c"
    )

    # L1 Leave Type fields
    l1_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L1 leave balance",
        alias="hr2d__L1_Balance__c"
    )
    l1_correction: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L1 leave correction",
        alias="hr2d__L1_Correction__c",
        nullable=True
    )
    l1_entitlement: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L1 leave entitlement",
        alias="hr2d__L1_Entitlement__c"
    )
    l1_expired: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L1 leave expired",
        alias="hr2d__L1_Expired__c",
        nullable=True
    )
    l1_start_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L1 leave start balance",
        alias="hr2d__L1_StartBalance__c",
        nullable=True
    )
    l1_taken: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L1 leave taken",
        alias="hr2d__L1_Taken__c",
        nullable=True
    )
    l1_accrual: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L1 leave accrual",
        alias="hr2d__L1_Accrual__c"
    )
    l1_pay_buy: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L1 leave pay buy",
        alias="hr2d__L1_PayBuy__c"
    )
    l1_ent_next_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L1 entitlement next calendar year",
        alias="hr2d__L1_EntNextCalYear__c"
    )
    l1_ent_this_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L1 entitlement this calendar year",
        alias="hr2d__L1_EntThisCalYear__c"
    )
    l1_entitlement_fulltime: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L1 entitlement fulltime",
        alias="hr2d__L1_EntitlementFulltime__c",
        nullable=True
    )
    l1_max_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L1 maximum balance",
        alias="hr2d__L1_MaxBalance__c",
        nullable=True
    )

    # L2 Leave Type fields
    l2_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L2 leave balance",
        alias="hr2d__L2_Balance__c"
    )
    l2_correction: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L2 leave correction",
        alias="hr2d__L2_Correction__c",
        nullable=True
    )
    l2_entitlement: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L2 leave entitlement",
        alias="hr2d__L2_Entitlement__c"
    )
    l2_expired: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L2 leave expired",
        alias="hr2d__L2_Expired__c",
        nullable=True
    )
    l2_start_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L2 leave start balance",
        alias="hr2d__L2_StartBalance__c",
        nullable=True
    )
    l2_taken: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L2 leave taken",
        alias="hr2d__L2_Taken__c",
        nullable=True
    )
    l2_accrual: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L2 leave accrual",
        alias="hr2d__L2_Accrual__c"
    )
    l2_pay_buy: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L2 leave pay buy",
        alias="hr2d__L2_PayBuy__c"
    )
    l2_ent_next_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L2 entitlement next calendar year",
        alias="hr2d__L2_EntNextCalYear__c"
    )
    l2_ent_this_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L2 entitlement this calendar year",
        alias="hr2d__L2_EntThisCalYear__c"
    )
    l2_entitlement_fulltime: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L2 entitlement fulltime",
        alias="hr2d__L2_EntitlementFulltime__c",
        nullable=True
    )
    l2_max_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L2 maximum balance",
        alias="hr2d__L2_MaxBalance__c",
        nullable=True
    )

    # L3 Leave Type fields
    l3_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L3 leave balance",
        alias="hr2d__L3_Balance__c"
    )
    l3_correction: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L3 leave correction",
        alias="hr2d__L3_Correction__c",
        nullable=True
    )
    l3_entitlement: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L3 leave entitlement",
        alias="hr2d__L3_Entitlement__c"
    )
    l3_expired: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L3 leave expired",
        alias="hr2d__L3_Expired__c",
        nullable=True
    )
    l3_start_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L3 leave start balance",
        alias="hr2d__L3_StartBalance__c",
        nullable=True
    )
    l3_taken: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L3 leave taken",
        alias="hr2d__L3_Taken__c",
        nullable=True
    )
    l3_accrual: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L3 leave accrual",
        alias="hr2d__L3_Accrual__c"
    )
    l3_pay_buy: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L3 leave pay buy",
        alias="hr2d__L3_PayBuy__c"
    )
    l3_ent_next_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L3 entitlement next calendar year",
        alias="hr2d__L3_EntNextCalYear__c"
    )
    l3_ent_this_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L3 entitlement this calendar year",
        alias="hr2d__L3_EntThisCalYear__c"
    )
    l3_entitlement_fulltime: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L3 entitlement fulltime",
        alias="hr2d__L3_EntitlementFulltime__c",
        nullable=True
    )
    l3_max_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L3 maximum balance",
        alias="hr2d__L3_MaxBalance__c",
        nullable=True
    )

    # L4 Leave Type fields
    l4_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L4 leave balance",
        alias="hr2d__L4_Balance__c"
    )
    l4_correction: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L4 leave correction",
        alias="hr2d__L4_Correction__c",
        nullable=True
    )
    l4_entitlement: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L4 leave entitlement",
        alias="hr2d__L4_Entitlement__c"
    )
    l4_expired: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L4 leave expired",
        alias="hr2d__L4_Expired__c",
        nullable=True
    )
    l4_start_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L4 leave start balance",
        alias="hr2d__L4_StartBalance__c",
        nullable=True
    )
    l4_taken: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L4 leave taken",
        alias="hr2d__L4_Taken__c",
        nullable=True
    )
    l4_accrual: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L4 leave accrual",
        alias="hr2d__L4_Accrual__c"
    )
    l4_pay_buy: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L4 leave pay buy",
        alias="hr2d__L4_PayBuy__c"
    )
    l4_ent_next_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L4 entitlement next calendar year",
        alias="hr2d__L4_EntNextCalYear__c"
    )
    l4_ent_this_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L4 entitlement this calendar year",
        alias="hr2d__L4_EntThisCalYear__c"
    )
    l4_entitlement_fulltime: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L4 entitlement fulltime",
        alias="hr2d__L4_EntitlementFulltime__c",
        nullable=True
    )
    l4_max_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L4 maximum balance",
        alias="hr2d__L4_MaxBalance__c",
        nullable=True
    )

    # L5 Leave Type fields
    l5_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L5 leave balance",
        alias="hr2d__L5_Balance__c"
    )
    l5_correction: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L5 leave correction",
        alias="hr2d__L5_Correction__c",
        nullable=True
    )
    l5_entitlement: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L5 leave entitlement",
        alias="hr2d__L5_Entitlement__c"
    )
    l5_expired: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L5 leave expired",
        alias="hr2d__L5_Expired__c",
        nullable=True
    )
    l5_start_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L5 leave start balance",
        alias="hr2d__L5_StartBalance__c",
        nullable=True
    )
    l5_taken: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L5 leave taken",
        alias="hr2d__L5_Taken__c",
        nullable=True
    )
    l5_accrual: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L5 leave accrual",
        alias="hr2d__L5_Accrual__c"
    )
    l5_pay_buy: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L5 leave pay buy",
        alias="hr2d__L5_PayBuy__c"
    )
    l5_ent_next_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L5 entitlement next calendar year",
        alias="hr2d__L5_EntNextCalYear__c"
    )
    l5_ent_this_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L5 entitlement this calendar year",
        alias="hr2d__L5_EntThisCalYear__c"
    )
    l5_entitlement_fulltime: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L5 entitlement fulltime",
        alias="hr2d__L5_EntitlementFulltime__c",
        nullable=True
    )
    l5_max_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L5 maximum balance",
        alias="hr2d__L5_MaxBalance__c",
        nullable=True
    )

    # L11-L15 Leave Type fields
    l11_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L11 leave balance",
        alias="hr2d__L11_Balance__c"
    )
    l11_correction: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L11 leave correction",
        alias="hr2d__L11_Correction__c",
        nullable=True
    )
    l11_entitlement: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L11 leave entitlement",
        alias="hr2d__L11_Entitlement__c"
    )
    l11_start_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L11 leave start balance",
        alias="hr2d__L11_StartBalance__c",
        nullable=True
    )
    l11_taken: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L11 leave taken",
        alias="hr2d__L11_Taken__c",
        nullable=True
    )
    l11_pay_buy: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L11 leave pay buy",
        alias="hr2d__L11_PayBuy__c"
    )
    l11_ent_next_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L11 entitlement next calendar year",
        alias="hr2d__L11_EntNextCalYear__c"
    )
    l11_ent_this_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L11 entitlement this calendar year",
        alias="hr2d__L11_EntThisCalYear__c"
    )
    l11_entitlement_fulltime: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L11 entitlement fulltime",
        alias="hr2d__L11_EntitlementFulltime__c",
        nullable=True
    )
    l11_max_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L11 maximum balance",
        nullable=True,
        alias="hr2d__L11_MaxBalance__c"
    )

    l12_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L12 leave balance",
        alias="hr2d__L12_Balance__c"
    )
    l12_correction: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L12 leave correction",
        nullable=True,
        alias="hr2d__L12_Correction__c"
    )
    l12_entitlement: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L12 leave entitlement",
        alias="hr2d__L12_Entitlement__c"
    )
    l12_expired: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L12 leave expired",
        nullable=True,
        alias="hr2d__L12_Expired__c"
    )
    l12_start_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L12 leave start balance",
        alias="hr2d__L12_StartBalance__c",
        nullable=True
    )
    l12_taken: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L12 leave taken",
        alias="hr2d__L12_Taken__c",
        nullable=True
    )
    l12_pay_buy: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L12 leave pay buy",
        alias="hr2d__L12_PayBuy__c"
    )
    l12_ent_next_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L12 entitlement next calendar year",
        alias="hr2d__L12_EntNextCalYear__c"
    )
    l12_ent_this_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L12 entitlement this calendar year",
        alias="hr2d__L12_EntThisCalYear__c"
    )
    l12_entitlement_fulltime: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L12 entitlement fulltime",
        alias="hr2d__L12_EntitlementFulltime__c",
        nullable=True
    )
    l12_max_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L12 maximum balance",
        alias="hr2d__L12_MaxBalance__c",
        nullable=True
    )
    l12_expiration_date_overrides: Series[pd.StringDtype] = pa.Field(
        coerce=True,
        description="L12 expiration date overrides",
        alias="hr2d__L12_ExpirationDateOverrides__c",
        nullable=True
    )

    l13_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L13 leave balance",
        alias="hr2d__L13_Balance__c"
    )
    l13_correction: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L13 leave correction",
        nullable=True,
        alias="hr2d__L13_Correction__c"
    )
    l13_entitlement: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L13 leave entitlement",
        alias="hr2d__L13_Entitlement__c"
    )
    l13_expired: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L13 leave expired",
        alias="hr2d__L13_Expired__c",
        nullable=True
    )
    l13_start_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L13 leave start balance",
        alias="hr2d__L13_StartBalance__c",
        nullable=True
    )
    l13_taken: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L13 leave taken",
        nullable=True,
        alias="hr2d__L13_Taken__c"
    )
    l13_pay_buy: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L13 leave pay buy",
        alias="hr2d__L13_PayBuy__c"
    )
    l13_ent_next_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L13 entitlement next calendar year",
        alias="hr2d__L13_EntNextCalYear__c"
    )
    l13_ent_this_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L13 entitlement this calendar year",
        alias="hr2d__L13_EntThisCalYear__c"
    )
    l13_entitlement_fulltime: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L13 entitlement fulltime",
        nullable=True,
        alias="hr2d__L13_EntitlementFulltime__c"
    )
    l13_max_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L13 maximum balance",
        nullable=True,
        alias="hr2d__L13_MaxBalance__c",
    )

    l14_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L14 leave balance",
        alias="hr2d__L14_Balance__c"
    )
    l14_correction: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L14 leave correction",
        nullable=True,
        alias="hr2d__L14_Correction__c"
    )
    l14_entitlement: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L14 leave entitlement",
        alias="hr2d__L14_Entitlement__c"
    )
    l14_expired: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L14 leave expired",
        alias="hr2d__L14_Expired__c",
        nullable=True
    )
    l14_start_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L14 leave start balance",
        alias="hr2d__L14_StartBalance__c",
        nullable=True
    )
    l14_taken: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L14 leave taken",
        alias="hr2d__L14_Taken__c",
        nullable=True
    )
    l14_pay_buy: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L14 leave pay buy",
        alias="hr2d__L14_PayBuy__c"
    )
    l14_ent_next_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L14 entitlement next calendar year",
        alias="hr2d__L14_EntNextCalYear__c"
    )
    l14_ent_this_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L14 entitlement this calendar year",
        alias="hr2d__L14_EntThisCalYear__c"
    )
    l14_entitlement_fulltime: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L14 entitlement fulltime",
        alias="hr2d__L14_EntitlementFulltime__c",
        nullable=True
    )
    l14_max_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L14 maximum balance",
        alias="hr2d__L14_MaxBalance__c",
        nullable=True
    )

    l15_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L15 leave balance",
        alias="hr2d__L15_Balance__c"
    )
    l15_correction: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L15 leave correction",
        alias="hr2d__L15_Correction__c",
        nullable=True
    )
    l15_entitlement: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L15 leave entitlement",
        alias="hr2d__L15_Entitlement__c"
    )
    l15_expired: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L15 leave expired",
        alias="hr2d__L15_Expired__c",
        nullable=True
    )
    l15_start_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L15 leave start balance",
        alias="hr2d__L15_StartBalance__c",
        nullable=True
    )
    l15_taken: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L15 leave taken",
        alias="hr2d__L15_Taken__c",
        nullable=True
    )
    l15_pay_buy: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L15 leave pay buy",
        alias="hr2d__L15_PayBuy__c"
    )
    l15_ent_next_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L15 entitlement next calendar year",
        alias="hr2d__L15_EntNextCalYear__c"
    )
    l15_ent_this_cal_year: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L15 entitlement this calendar year",
        alias="hr2d__L15_EntThisCalYear__c"
    )
    l15_entitlement_fulltime: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L15 entitlement fulltime",
        alias="hr2d__L15_EntitlementFulltime__c",
        nullable=True
    )
    l15_max_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="L15 maximum balance",
        alias="hr2d__L15_MaxBalance__c",
        nullable=True
    )

    # TVT (Time-for-Time) fields
    tvt_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="TVT balance",
        alias="hr2d__Tvt_Balance__c"
    )
    tvt_entitlement: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="TVT entitlement",
        alias="hr2d__Tvt_Entitlement__c",
        nullable=True
    )
    tvt_taken: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="TVT taken",
        nullable=True,
        alias="hr2d__Tvt_Taken__c"
    )
    tvt_correction: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="TVT correction",
        alias="hr2d__Tvt_Correction__c",
        nullable=True
    )
    tvt_start_balance: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="TVT start balance",
        alias="hr2d__Tvt_StartBalance__c",
        nullable=True
    )
    tvt_pay_buy: Series[pd.Float64Dtype] = pa.Field(
        coerce=True,
        description="TVT pay buy",
        alias="hr2d__Tvt_PayBuy__c"
    )

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }
