import pandera as pa
from pandera.typing import Series, String, Float, DateTime
from typing import Optional
import pandas as pd
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class TimeSheetSchema(BrynQPanderaDataFrameModel):
    # core timesheet attributes
    actual_status: Series[String] = pa.Field(coerce=True, description="Actual Status (Y/N)", alias="actualStatus")
    amount: Series[Float] = pa.Field(coerce=True, nullable=False, description="Billed Amount", alias="amount")
    amount_break: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Amount Break (minutes)", alias="amountBreak")
    approval_date: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="Approval Date", alias="approvalDate")
    approval_state: Series[String] = pa.Field(coerce=True, nullable=False, description="Approval State Code", alias="approvalState")
    budget_key: Series[String] = pa.Field(coerce=True, nullable=False, description="Budget Key", alias="budgetKey")
    etc: Series[Float] = pa.Field(coerce=True, nullable=True, description="ETC Value", alias="etc")
    extra: Series[bool] = pa.Field(coerce=True, nullable=False, description="Has Extra Flag", alias="extra")
    extra_time: Series[String] = pa.Field(coerce=True, nullable=True, description="Extra Time Code", alias="extraTime")
    percentage_done: Series[Float] = pa.Field(coerce=True, nullable=True, description="% Complete", alias="percentageDone")
    planning_key: Series[String] = pa.Field(coerce=True, nullable=False, description="Planning Key", alias="planningKey")
    resource_key: Series[String] = pa.Field(coerce=True, nullable=False, description="Resource Key", alias="resourceKey")
    show_on_report_ready: Optional[Series[pd.BooleanDtype]] = pa.Field(coerce=True, nullable=True, description="Visible On Report", alias="showOnReportReady")
    str_extra: Series[String] = pa.Field(coerce=True, nullable=True, description="Extra Time (string)", alias="strExtra")
    tdate: Series[DateTime] = pa.Field(coerce=True, nullable=False, description="Timesheet Date", alias="tdate")
    time_from: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Start Minute of Day", alias="timeFrom")
    time_to: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="End Minute of Day", alias="timeTo")
    timesheet_key: Series[String] = pa.Field(coerce=True, nullable=False, description="Timesheet Entry Key", alias="timesheetKey")
    worktype_key: Series[String] = pa.Field(coerce=True, nullable=False, description="Work Type Key", alias="worktypeKey")

    # project sub-object (flattened)
    project_budget_key: Series[String] = pa.Field(coerce=True, nullable=False, description="Project Budget Key", alias="project_budgetKey")
    project_description: Series[String] = pa.Field(coerce=True, nullable=False, description="Project Description", alias="project_description")
    project_is_parent: Series[bool] = pa.Field(coerce=True, nullable=False, description="Project Is Parent", alias="project_isParent")
    project_planning_exchange_rate: Series[Float] = pa.Field(coerce=True, nullable=False, description="Project Exchange Rate", alias="project_planningExchangeRate")
    project_planning_key: Series[String] = pa.Field(coerce=True, nullable=False, description="Project Planning Key", alias="project_planningKey")
    project_project_key: Series[String] = pa.Field(coerce=True, nullable=False, description="Project Key", alias="project_projectKey")
    project_project_number: Series[String] = pa.Field(coerce=True, nullable=True, description="Project Number", alias="project_projectNumber")
    project_project_type: Series[String] = pa.Field(coerce=True, nullable=False, description="Project Type Code", alias="project_projectType")
    project_schedule_duration: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Scheduled Duration (min)", alias="project_scheduleDuration")
    project_schedule_finish: Series[String] = pa.Field(coerce=True, nullable=True, description="Scheduled Finish", alias="project_scheduleFinish")
    project_schedule_start: Series[String] = pa.Field(coerce=True, nullable=True, description="Scheduled Start", alias="project_scheduleStart")
    project_status: Series[String] = pa.Field(coerce=True, nullable=False, description="Project Status Code", alias="project_status")
    project_type_name: Series[String] = pa.Field(coerce=True, nullable=False, description="Type Name", alias="project_typeName")
    project_user_type: Series[String] = pa.Field(coerce=True, nullable=False, description="User Type Code", alias="project_userType")

    # client sub-object (flattened)
    client_active: Optional[Series[pd.BooleanDtype]] = pa.Field(coerce=True, nullable=True, description="Client Is Active", alias="client_active")
    client_city_address: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Client City", alias="client_cityAddress")
    client_country_code: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Client Country Code", alias="client_countryCodeAddress")
    client_phone1: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Primary Phone", alias="client_phone1")
    client_phone2: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Secondary Phone", alias="client_phone2")
    client_relation_address: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Street Address", alias="client_relationAddress")
    client_relation_id: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Relation ID", alias="client_relationId")
    client_relation_name: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Relation Name", alias="client_relationName")
    client_relation_number: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Relation Number", alias="client_relationNumber")
    client_relation_types: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=True, description="Relation Types", alias="client_relationTypes")
    client_zip_address: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="ZIP Code", alias="client_zipAddress")
    client_country_name: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Country Name", alias="client_countryNameAddress")
    client_business_unit_key: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Business Unit Key", alias="client_businessUnitKey")

    # customFields.item[0].value
    vv_project_uren_locatie: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="VV Project Uren Locatie", alias="customFields_item_0_value")

    # resource sub-object (flattened)
    resource_active: Series[bool] = pa.Field(coerce=True, nullable=False, description="Resource Is Active", alias="resource_active")
    resource_description: Series[String] = pa.Field(coerce=True, nullable=False, description="Resource Description", alias="resource_description")
    resource_key: Series[String] = pa.Field(coerce=True, nullable=False, description="Resource Key", alias="resource_resourceKey")
    resource_number: Series[String] = pa.Field(coerce=True, nullable=False, description="Resource Number", alias="resource_resourceNumber")

    # workType sub-object
    worktype_description: Series[String] = pa.Field(coerce=True, nullable=False, description="Work Type Description", alias="workType_description")
    worktype_code: Series[String] = pa.Field(coerce=True, nullable=False, description="Work Type Code", alias="workType_workTypeCode")

    class Config:
        coerce = True
