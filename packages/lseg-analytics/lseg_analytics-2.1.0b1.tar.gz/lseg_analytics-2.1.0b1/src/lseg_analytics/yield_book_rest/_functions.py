import copy
import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from lseg_analytics._client.client import Client
from lseg_analytics.common._resource_base import ResourceBase
from lseg_analytics.exceptions import (
    LibraryException,
    ResourceNotFound,
    check_and_raise,
    check_exception_and_raise,
    check_id,
)
from lseg_analytics_basic_client._types import JobStoreInputData
from lseg_analytics_basic_client.models import (
    ApimCurveShift,
    ApimError,
    Balloon,
    BondIndicRequest,
    BulkCompact,
    BulkComposite,
    BulkDefaultSettings,
    BulkGlobalSettings,
    BulkJsonInputItem,
    BulkMeta,
    BulkResultItem,
    BulkResultRequest,
    BulkTemplateDataSource,
    CapVolatility,
    CapVolItem,
    CashflowFloaterSettings,
    CashFlowGlobalSettings,
    CashFlowInput,
    CashflowMbsSettings,
    CashflowPrepaySettings,
    CashFlowRequestData,
    CashflowVolatility,
    CloSettings,
    CmbsPrepayment,
    CmbsSettings,
    CMOModification,
    ColumnDetail,
    ConvertiblePricing,
    CurveDetailsRequest,
    CurveMultiShift,
    CurvePoint,
    CurveSearch,
    CurveTypeAndCurrency,
    CustomScenario,
    DataTable,
    DataTableColumnDetail,
    DefaultDials,
    Distribution,
    ExtraSettings,
    FloaterSettings,
    HecmSettings,
    HorizonInfo,
    IdentifierInfo,
    IdTypeEnum,
    IndexLinkerSettings,
    IndexProjection,
    InterpolationTypeAndVector,
    JobCreationRequest,
    JobResponse,
    JobResubmissionRequest,
    JobStatusResponse,
    JobTimelineEntry,
    JsonRef,
    JsonScenRef,
    LookbackSettings,
    LookupDetails,
    LossSettings,
    MappedResponseRefData,
    MarketSettingsRequest,
    MarketSettingsRequestInfo,
    MbsSettings,
    ModifyClass,
    ModifyCollateral,
    MonthRatePair,
    MuniSettings,
    OptionModel,
    OriginChannel,
    Partials,
    PrepayDialsInput,
    PrepayDialsSettings,
    PrepayModelSeller,
    PrepayModelServicer,
    PricingScenario,
    PyCalcGlobalSettings,
    PyCalcInput,
    PyCalcRequest,
    RefDataMeta,
    RequestId,
    RestPrepaySettings,
    ResultResponseBulkResultItem,
    Results,
    ReturnAttributionCurveTypeAndCurrency,
    ReturnAttributionGlobalSettings,
    ReturnAttributionInput,
    ReturnAttributionRequest,
    ScalarAndVector,
    ScalarAndVectorWithCollateral,
    ScenAbsoluteCurvePoint,
    Scenario,
    ScenarioCalcFloaterSettings,
    ScenarioCalcGlobalSettings,
    ScenarioCalcInput,
    ScenarioCalcRequest,
    ScenarioDefinition,
    ScenarioSettlement,
    ScenarioVolatility,
    ScenCalcExtraSettings,
    ScheduleItem,
    SensitivityShocks,
    SettlementInfo,
    SqlSettings,
    StateHomePriceAppreciation,
    StoreType,
    StructureNote,
    Summary,
    SwaptionVolatility,
    SwaptionVolItem,
    SystemScenario,
    TermAndValue,
    TermRatePair,
    UDIExtension,
    UserCurve,
    UserScenario,
    UserScenarioCurve,
    UserScenarioInput,
    UserScenCurveDefinition,
    UserVol,
    Vector,
    Visible,
    Volatility,
    VolItem,
    YBPortUserBond,
    YbRestCurveType,
)

from ._logger import logger

__all__ = [
    "ApimCurveShift",
    "ApimError",
    "Balloon",
    "BulkDefaultSettings",
    "BulkGlobalSettings",
    "BulkJsonInputItem",
    "BulkMeta",
    "BulkResultItem",
    "BulkTemplateDataSource",
    "CMOModification",
    "CapVolItem",
    "CapVolatility",
    "CashFlowGlobalSettings",
    "CashFlowInput",
    "CashflowFloaterSettings",
    "CashflowMbsSettings",
    "CashflowPrepaySettings",
    "CashflowVolatility",
    "CloSettings",
    "CmbsPrepayment",
    "CmbsSettings",
    "ColumnDetail",
    "ConvertiblePricing",
    "CurveMultiShift",
    "CurvePoint",
    "CurveSearch",
    "CurveTypeAndCurrency",
    "CustomScenario",
    "DataTable",
    "DataTableColumnDetail",
    "DefaultDials",
    "Distribution",
    "ExtraSettings",
    "FloaterSettings",
    "HecmSettings",
    "HorizonInfo",
    "IdTypeEnum",
    "IdentifierInfo",
    "IndexLinkerSettings",
    "IndexProjection",
    "InterpolationTypeAndVector",
    "JobResponse",
    "JobStatusResponse",
    "JobStoreInputData",
    "JobTimelineEntry",
    "JsonRef",
    "JsonScenRef",
    "LookbackSettings",
    "LookupDetails",
    "LossSettings",
    "MappedResponseRefData",
    "MarketSettingsRequestInfo",
    "MbsSettings",
    "ModifyClass",
    "ModifyCollateral",
    "MonthRatePair",
    "MuniSettings",
    "OptionModel",
    "OriginChannel",
    "Partials",
    "PrepayDialsInput",
    "PrepayDialsSettings",
    "PrepayModelSeller",
    "PrepayModelServicer",
    "PricingScenario",
    "PyCalcGlobalSettings",
    "PyCalcInput",
    "RefDataMeta",
    "RequestId",
    "RestPrepaySettings",
    "ResultResponseBulkResultItem",
    "Results",
    "ReturnAttributionCurveTypeAndCurrency",
    "ReturnAttributionGlobalSettings",
    "ReturnAttributionInput",
    "ScalarAndVector",
    "ScalarAndVectorWithCollateral",
    "ScenAbsoluteCurvePoint",
    "ScenCalcExtraSettings",
    "Scenario",
    "ScenarioCalcFloaterSettings",
    "ScenarioCalcGlobalSettings",
    "ScenarioCalcInput",
    "ScenarioDefinition",
    "ScenarioSettlement",
    "ScenarioVolatility",
    "ScheduleItem",
    "SensitivityShocks",
    "SettlementInfo",
    "SqlSettings",
    "StateHomePriceAppreciation",
    "StoreType",
    "StructureNote",
    "Summary",
    "SwaptionVolItem",
    "SwaptionVolatility",
    "SystemScenario",
    "TermAndValue",
    "TermRatePair",
    "UDIExtension",
    "UserCurve",
    "UserScenCurveDefinition",
    "UserScenario",
    "UserScenarioCurve",
    "UserScenarioInput",
    "UserVol",
    "Vector",
    "Visible",
    "VolItem",
    "Volatility",
    "YBPortUserBond",
    "YbRestCurveType",
    "abort_job",
    "bulk_compact_request",
    "bulk_composite_request",
    "bulk_yb_port_udi_request",
    "bulk_zip_request",
    "close_job",
    "create_job",
    "get_cash_flow_async",
    "get_cash_flow_sync",
    "get_csv_bulk_result",
    "get_formatted_result",
    "get_job",
    "get_job_data",
    "get_job_object_meta",
    "get_job_status",
    "get_json_result",
    "get_result",
    "get_tba_pricing_sync",
    "post_cash_flow_async",
    "post_cash_flow_sync",
    "post_csv_bulk_results_sync",
    "post_json_bulk_request_sync",
    "post_market_setting_sync",
    "request_bond_indic_async",
    "request_bond_indic_async_get",
    "request_bond_indic_sync",
    "request_bond_indic_sync_get",
    "request_curve_async",
    "request_curve_sync",
    "request_curves_async",
    "request_curves_sync",
    "request_get_scen_calc_sys_scen_async",
    "request_get_scen_calc_sys_scen_sync",
    "request_py_calculation_async",
    "request_py_calculation_async_by_id",
    "request_py_calculation_sync",
    "request_py_calculation_sync_by_id",
    "request_return_attribution_async",
    "request_return_attribution_sync",
    "request_scenario_calculation_async",
    "request_scenario_calculation_sync",
    "request_volatility_async",
    "request_volatility_sync",
    "resubmit_job",
    "upload_csv_job_data_async",
    "upload_csv_job_data_sync",
    "upload_csv_job_data_with_name_async",
    "upload_csv_job_data_with_name_sync",
    "upload_json_job_data_async",
    "upload_json_job_data_sync",
    "upload_json_job_data_with_name_async",
    "upload_json_job_data_with_name_sync",
    "upload_text_job_data_async",
    "upload_text_job_data_sync",
    "upload_text_job_data_with_name_async",
    "upload_text_job_data_with_name_sync",
]


def abort_job(*, job_ref: str) -> JobResponse:
    """
    Abort a job

    Parameters
    ----------
    job_ref : str
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    JobResponse


    Examples
    --------
    >>> # abort job
    >>> response = abort_job(job_ref="myJob")
    >>> print(response)
    {'id': 'J-20413', 'sequence': 0, 'asOf': '2025-03-10', 'closed': True, 'onHold': True, 'aborted': True, 'exitStatus': 'NEVER_STARTED', 'actualHold': True, 'name': 'myJob', 'chain': 'string', 'description': 'string', 'priority': 0, 'order': 'FAST', 'requestCount': 0, 'pendingCount': 0, 'runningCount': 0, 'okCount': 0, 'errorCount': 0, 'abortedCount': 0, 'skipCount': 0, 'startAfter': '2025-03-03T10:10:15Z', 'stopAfter': '2025-03-10T20:10:15Z', 'createdAt': '2025-03-07T03:02:13.964Z', 'updatedAt': '2025-03-07T03:02:24.016Z'}

    """

    try:
        logger.info("Calling abort_job")

        response = check_and_raise(Client().yield_book_rest.abort_job(job_ref=job_ref))

        output = response
        logger.info("Called abort_job")

        return output
    except Exception as err:
        logger.error(f"Error abort_job. {err}")
        check_exception_and_raise(err)


def bulk_compact_request(
    *,
    path: Optional[str] = None,
    name_expr: Optional[str] = None,
    body: Optional[str] = None,
    requests: Optional[List[Dict[str, Any]]] = None,
    data_source: Optional[BulkTemplateDataSource] = None,
    params: Optional[Dict[str, Any]] = None,
    create_job: Optional[bool] = None,
    chain_job: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> ResultResponseBulkResultItem:
    """
    Bulk compact request.

    Parameters
    ----------
    path : str, optional
        URL to which each individual request should be posted.i.e "/bond/py" for PY calculation.
    name_expr : str, optional
        Name of each request. This can be a valid JSON path expression, i.e "concat($.CUSIP,"_PY")" will give each request the name CUSIP_PY. Name should be unique within a single job.
    body : str, optional
        POST body associated with the calculation. This is specific to each request type. Refer to individual calculation section for more details.
    requests : List[Dict[str, Any]], optional
        List of key value pairs. This values provided will be used to update corresponding variables in the body of the request.
    data_source : BulkTemplateDataSource, optional

    params : Dict[str, Any], optional

    create_job : bool, optional
        Boolean with `true` and `false` values.
    chain_job : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    ResultResponseBulkResultItem


    Examples
    --------


    """

    try:
        logger.info("Calling bulk_compact_request")

        response = check_and_raise(
            Client().yield_book_rest.bulk_compact_request(
                body=BulkCompact(
                    path=path,
                    name_expr=name_expr,
                    body=body,
                    requests=requests,
                    data_source=data_source,
                    params=params,
                ),
                create_job=create_job,
                chain_job=chain_job,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
                content_type="application/json",
            )
        )

        output = response
        logger.info("Called bulk_compact_request")

        return output
    except Exception as err:
        logger.error(f"Error bulk_compact_request. {err}")
        check_exception_and_raise(err)


def bulk_composite_request(
    *,
    requests: Optional[List[BulkJsonInputItem]] = None,
    create_job: Optional[bool] = None,
    chain_job: Optional[str] = None,
    partial: Optional[bool] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> ResultResponseBulkResultItem:
    """
    Bulk composite request.

    Parameters
    ----------
    requests : List[BulkJsonInputItem], optional

    create_job : bool, optional
        Boolean with `true` and `false` values.
    chain_job : str, optional
        A sequence of textual characters.
    partial : bool, optional
        Boolean with `true` and `false` values.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    ResultResponseBulkResultItem


    Examples
    --------


    """

    try:
        logger.info("Calling bulk_composite_request")

        response = check_and_raise(
            Client().yield_book_rest.bulk_composite_request(
                body=BulkComposite(requests=requests),
                create_job=create_job,
                chain_job=chain_job,
                partial=partial,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
                content_type="application/json",
            )
        )

        output = response
        logger.info("Called bulk_composite_request")

        return output
    except Exception as err:
        logger.error(f"Error bulk_composite_request. {err}")
        check_exception_and_raise(err)


def bulk_yb_port_udi_request(
    *,
    data: str,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    create_job: Optional[bool] = None,
    chain_job: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> ResultResponseBulkResultItem:
    """
    Bulk YB Port UDI request.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    prefix : str, optional
        A sequence of textual characters.
    suffix : str, optional
        A sequence of textual characters.
    create_job : bool, optional
        Boolean with `true` and `false` values.
    chain_job : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    ResultResponseBulkResultItem


    Examples
    --------


    """

    try:
        logger.info("Calling bulk_yb_port_udi_request")

        response = check_and_raise(
            Client().yield_book_rest.bulk_yb_port_udi_request(
                prefix=prefix,
                suffix=suffix,
                create_job=create_job,
                chain_job=chain_job,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
                content_type="text/plain",
                data=data,
            )
        )

        output = response
        logger.info("Called bulk_yb_port_udi_request")

        return output
    except Exception as err:
        logger.error(f"Error bulk_yb_port_udi_request. {err}")
        check_exception_and_raise(err)


def bulk_zip_request(
    *,
    data: bytes,
    default_target: Optional[str] = None,
    create_job: Optional[bool] = None,
    chain_job: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> ResultResponseBulkResultItem:
    """
    Bulk zip request.

    Parameters
    ----------
    data : bytes
        Represent a byte array
    default_target : str, optional
        A sequence of textual characters.
    create_job : bool, optional
        Boolean with `true` and `false` values.
    chain_job : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    ResultResponseBulkResultItem


    Examples
    --------


    """

    try:
        logger.info("Calling bulk_zip_request")

        response = check_and_raise(
            Client().yield_book_rest.bulk_zip_request(
                default_target=default_target,
                create_job=create_job,
                chain_job=chain_job,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
                content_type="application/zip",
                data=data,
            )
        )

        output = response
        logger.info("Called bulk_zip_request")

        return output
    except Exception as err:
        logger.error(f"Error bulk_zip_request. {err}")
        check_exception_and_raise(err)


def close_job(*, job_ref: str) -> JobResponse:
    """
    Close a job

    Parameters
    ----------
    job_ref : str
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    JobResponse


    Examples
    --------
    >>> # close job
    >>> response = close_job(job_ref="myJob")
    >>> print(response)
    {'id': 'J-20413', 'sequence': 0, 'asOf': '2025-03-10', 'closed': True, 'onHold': True, 'aborted': False, 'exitStatus': 'NEVER_STARTED', 'actualHold': True, 'name': 'myJob', 'chain': 'string', 'description': 'string', 'priority': 0, 'order': 'FAST', 'requestCount': 0, 'pendingCount': 0, 'runningCount': 0, 'okCount': 0, 'errorCount': 0, 'abortedCount': 0, 'skipCount': 0, 'startAfter': '2025-03-03T10:10:15Z', 'stopAfter': '2025-03-10T20:10:15Z', 'createdAt': '2025-03-07T03:02:13.964Z', 'updatedAt': '2025-03-07T03:02:24.016Z'}

    """

    try:
        logger.info("Calling close_job")

        response = check_and_raise(Client().yield_book_rest.close_job(job_ref=job_ref))

        output = response
        logger.info("Called close_job")

        return output
    except Exception as err:
        logger.error(f"Error close_job. {err}")
        check_exception_and_raise(err)


def create_job(
    *,
    priority: Optional[int] = None,
    hold: Optional[bool] = None,
    start_after: Optional[datetime.datetime] = None,
    stop_after: Optional[datetime.datetime] = None,
    name: Optional[str] = None,
    asof: Optional[Union[str, datetime.date]] = None,
    order: Optional[Literal["FAST", "FIFO", "NONE"]] = None,
    chain: Optional[str] = None,
    desc: Optional[str] = None,
) -> JobResponse:
    """
    Create a new job

    Parameters
    ----------
    priority : int, optional
        Control priority of job. Requests within jobs of higher priority are processed prior to jobs with lower priority.
    hold : bool, optional
        When set to true, suspends the excution of all requests in the job, processing resumes only after the job is updated and the value is set to false.
    start_after : datetime.datetime, optional
        An instant in coordinated universal time (UTC)"
    stop_after : datetime.datetime, optional
        An instant in coordinated universal time (UTC)"
    name : str, optional
        Optional. Unique name associated with a job. There can only be one active job with this name. Job name can be used for all future job references. If a previously open job exists with the same name, the older job is closed before a new job is created.
    asof : Union[str, datetime.date], optional
        A date on a calendar without a time zone, e.g. "April 10th"
    order : Literal["FAST","FIFO","NONE"], optional

    chain : str, optional
        A sequence of textual characters.
    desc : str, optional
        User defined description of the job.

    Returns
    --------
    JobResponse


    Examples
    --------
    >>> # create job
    >>> job_response = create_job(
    >>>     priority=0,
    >>>     hold=True,
    >>>     start_after=datetime(2025, 3, 3, 10, 10, 15, 263),
    >>>     stop_after=datetime(2025, 3, 10, 20, 10, 15, 263),
    >>>     name="myJob",
    >>>     asof="2025-03-10",
    >>>     order="FAST",
    >>>     chain="string",
    >>>     desc="string",
    >>> )
    >>>
    >>> print(job_response)
    {'id': 'J-31887', 'sequence': 0, 'asOf': '2025-03-10', 'closed': True, 'onHold': True, 'aborted': True, 'exitStatus': 'NEVER_STARTED', 'actualHold': True, 'name': 'myJob', 'chain': 'string', 'description': 'string', 'priority': 0, 'order': 'FAST', 'requestCount': 0, 'pendingCount': 0, 'runningCount': 0, 'okCount': 0, 'errorCount': 0, 'abortedCount': 0, 'skipCount': 0, 'startAfter': '2025-03-03T10:10:15Z', 'stopAfter': '2025-03-10T20:10:15Z', 'createdAt': '2025-06-27T09:41:07.534Z', 'updatedAt': '2025-06-27T09:41:07.534Z'}

    """

    try:
        logger.info("Calling create_job")

        response = check_and_raise(
            Client().yield_book_rest.create_job(
                body=JobCreationRequest(
                    priority=priority,
                    hold=hold,
                    start_after=start_after,
                    stop_after=stop_after,
                    name=name,
                    asof=asof,
                    order=order,
                    chain=chain,
                    desc=desc,
                )
            )
        )

        output = response
        logger.info("Called create_job")

        return output
    except Exception as err:
        logger.error(f"Error create_job. {err}")
        check_exception_and_raise(err)


def get_cash_flow_async(
    *,
    id: str,
    id_type: Optional[str] = None,
    pricing_date: Optional[str] = None,
    par_amount: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Get cash flow request async.

    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    pricing_date : str, optional
        A sequence of textual characters.
    par_amount : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling get_cash_flow_async")

        response = check_and_raise(
            Client().yield_book_rest.get_cash_flow_async(
                id=id,
                id_type=id_type,
                pricing_date=pricing_date,
                par_amount=par_amount,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called get_cash_flow_async")

        return output
    except Exception as err:
        logger.error(f"Error get_cash_flow_async. {err}")
        check_exception_and_raise(err)


def get_cash_flow_sync(
    *,
    id: str,
    id_type: Optional[str] = None,
    pricing_date: Optional[str] = None,
    par_amount: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Get cash flow sync.

    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    pricing_date : str, optional
        A sequence of textual characters.
    par_amount : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling get_cash_flow_sync")

        response = check_and_raise(
            Client().yield_book_rest.get_cash_flow_sync(
                id=id,
                id_type=id_type,
                pricing_date=pricing_date,
                par_amount=par_amount,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called get_cash_flow_sync")

        return output
    except Exception as err:
        logger.error(f"Error get_cash_flow_sync. {err}")
        check_exception_and_raise(err)


def get_csv_bulk_result(*, ids: List[str], fields: List[str], job: Optional[str] = None) -> str:
    """
    Retrieve bulk results with multiple request id or request name.

    Parameters
    ----------
    ids : List[str]
          Ids can be provided comma separated. Different formats for id are:
          1) RequestId R-number
          2) Request name R:name. In this case also provide jobid (J-number) or jobname (J:name)
          3) Jobid J-number
          4) Job name J:name - only 1 active job with the jobname
          5) Tag name T:name. In this case also provide jobid (J-number) or jobname (J:name)
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    fields : List[str]


    Returns
    --------
    str
        A sequence of textual characters.

    Examples
    --------


    """

    try:
        logger.info("Calling get_csv_bulk_result")

        response = check_and_raise(Client().yield_book_rest.get_csv_bulk_result(ids=ids, job=job, fields=fields))

        output = response
        logger.info("Called get_csv_bulk_result")

        return output
    except Exception as err:
        logger.error(f"Error get_csv_bulk_result. {err}")
        check_exception_and_raise(err)


def get_formatted_result(*, request_id_parameter: str, format: str, job: Optional[str] = None) -> Any:
    """
    Retrieve single formatted result using request id or request name.

    Parameters
    ----------
    request_id_parameter : str
        Unique request id. This can be of the format R-number or request name. If request name is used, corresponding job information should be passed in the query parameter.
    format : str
        Only "html" format supported for now.
    job : str, optional
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    Any


    Examples
    --------
    >>> # get formatted result
    >>> response = get_formatted_result(request_id_parameter="R-1475071", format="html")
    >>> print(response)


    <!DOCTYPE HTML>
    <html>
       <head>
          <style>
             html,
    body {
        font-family: Arial, sans-serif;
        font-size: 11px;
    }

    html,
    body,
    div,
    span {
        box-sizing: content-box;
    }
    * {
        box-sizing: border-box;
    }
    *:before {
        box-sizing: border-box;
    }
    *:after {
        box-sizing: border-box;
    }

    button,
    input[type="button"] {
        font-size: 11px;
        cursor: pointer;
        outline: 0;
        border: none;
        border-radius: 3px;
        padding: 0 10px;
    }

    textarea {
        font-family: Arial, sans-serif;
        font-size: 11px;
        color: #5b6974;
        padding-left: 5px;
        padding-right: 5px;
    }
             .main-container {
        padding: 5px;
        margin: 0 auto;
    }
    .main-container .root-container {
        display: flex;
    }
    .main-container .section-container {
        display: flex;
        flex-direction: row;
        width: 1375px;
        flex-wrap: wrap;
        margin: 0 auto;
    }

    .section-container .json-group {
        margin: 5px 10px 15px 5px;
        padding: 15px 20px 15px 15px;
        border: solid #e9ebec;
        overflow: auto;
        width: 1315px;
    }

    .main-container .section-column-container {
        display: flex;
        flex-direction: column;
    }

    .main-container .top-info {
        padding-left: 10px;
        width: 1375px;
        margin: 0 auto;
    }
    .main-container .top-info label {
        font-size: 12px;
        font-weight: bold;
        margin-right: 5px;
    }
    .section-container .section-group {
        margin: 5px 10px 15px 5px;
        padding: 15px 20px 15px 15px;
        border: solid #e9ebec;
        overflow: auto;
        min-width: 400px;
    }
    .section-container .section-group .header {
        padding: 5px;
        padding-top: 1px;
        font-weight: bold;
        /* text-transform: uppercase; */
    }
    .section-container .section-group table {
        width: 100%;
        font-size: 11px;
    }
    .section-container .section-group table td {
        padding: 3px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    }
    .section-container .key-value-table td:nth-child(1) {
        width: 60%;
    }
    .section-container .key-value-table td:nth-child(1) span:nth-child(2) {
        background-color: #f3df9d;
    }
    .section-container .key-value-table td:nth-child(2) {
        width: 40%;
        text-align: right;
    }

    .section-container .partial-table td:nth-child(1),
    .section-container .partial-table th:nth-child(1) {
        width: 20%;
        text-align: center;
    }
    .section-container .partial-table th span:nth-child(3) {
        background-color: #f3df9d;
    }
    .section-container .partial-table td:nth-child(2),
    .section-container .partial-table td:nth-child(3),
    .section-container .partial-table th:nth-child(2),
    .section-container .partial-table th:nth-child(3) {
        width: 40%;
        text-align: right;
    }

    .section-container .regular-table th {
        text-align: right;
    }
    .section-container .regular-table th:nth-child(1) {
        text-align: left;
    }
    .section-container .regular-table td {
        padding: 3px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.08);
        text-align: right;
    }
    .section-container .regular-table th span:nth-child(3) {
        background-color: #f3df9d;
    }
    .section-container .regular-table td:nth-child(1) {
        text-align: left;
    }
    .section-container .prepayment-model-projection-table {
        width: calc(66.66% - 55px);
    }
    .section-container .prepayment-model-projection-table td {
        width: 16%;
    }
    .section-container .prepayment-model-projection-table td:nth-child(1) {
        width: 20%;
    }

    .section-container .flat-table table,
    .section-container .flat-table table th,
    .section-container .flat-table table td {
        padding: 10px;
        border: 1px solid rgba(0, 0, 0, 0.25);
        border-collapse: collapse;
        text-align: center;
    }

    /* Indic Layoyut*/
    .section-container .indic-bond-description {
        min-height: 436px;
    }
    .section-container .indic-bond-row {
        min-height: 190px;
    }

    .section-container .indic-mort-collatral {
        min-height: 532px;
    }
    .section-container .indic-mort-row {
        min-height: 140px;
    }

          </style>
       </head>
       <body>
          <div class="main-container">

    <div class="root-container">
      <div class="section-container section-column-container">
        <div class="section-group key-value-table indic-mort-collatral">
          <div class="header">COLLATERAL</div>
          <table>
            <tbody>
              <tr>
                <td>Ticker</td>
                <td>GNMA</td>
              </tr>
              <tr>
                <td>Original Term</td>
                <td>360</td>
              </tr>
              <tr>
                <td>Issue Date</td>
                <td>2013-05-01</td>
              </tr>
              <tr>
                <td>Gross WAC</td>
                <td>4.0000</td>
              </tr>
              <tr>
                <td>Coupon</td>
                <td>3.500000</td>
              </tr>
              <tr>
                <td>Credit Score</td>
                <td>692</td>
              </tr>
              <tr>
                <td>Original LTV</td>
                <td>90.0000</td>
              </tr>
              <tr>
                <td>Current LTV</td>
                <td>28.7000</td>
              </tr>
              <tr>
                <td>Original TPO</td>
                <td></td>
              </tr>
              <tr>
                <td>Current TPO</td>
                <td></td>
              </tr>
              <tr>
                <td>SATO</td>
                <td>22.4000</td>
              </tr>
              <tr>
                <td>Security Type</td>
                <td>MORT</td>
              </tr>
              <tr>
                <td>Security Sub Type</td>
                <td>MPGNMA</td>
              </tr>
              <tr>
                <td>Maturity</td>
                <td>2041-12-01</td>
              </tr>
              <tr>
                <td>WAM</td>
                <td>201</td>
              </tr>
              <tr>
                <td>WALA</td>
                <td>142</td>
              </tr>
              <tr>
                <td>Weighted Avg Loan Size</td>
                <td>104140.0000</td>
              </tr>
              <tr>
                <td>Weighted Average Original Loan Size</td>
                <td></td>
              </tr>
              <tr>
                <td>Current Loan Size</td>
                <td></td>
              </tr>
              <tr>
                <td>Original Loan Size</td>
                <td>182010.000000</td>
              </tr>
              <tr>
                <td>Servicer</td>
                <td></td>
              </tr>
              <tr>
                <td>Delay</td>
                <td>44</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="section-container section-column-container">
        <div class="section-group key-value-table indic-mort-row">
          <div class="header">DISCLOSURE INFORMATION</div>
          <table>
            <tbody>
              <tr>
                <td>Credit Score</td>
                <td>MORT</td>
              </tr>
              <tr>
                <td>LTV</td>
                <td>692</td>
              </tr>
              <tr>
                <td>Load Size</td>
                <td></td>
              </tr>
              <tr>
                <td>% Refinance</td>
                <td></td>
              </tr>
              <tr>
                <td>% Refinance</td>
                <td>0.0000</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="section-group key-value-table indic-mort-row">
          <div class="header">Ratings</div>
          <table>
            <tbody>

              <tr>
                <td>Moody's</td>
                <td>Aaa</td>
              </tr>


            </tbody>
          </table>
        </div>
        <div class="section-group key-value-table indic-mort-row">
          <div class="header">Sector</div>
          <table>
            <tbody>
              <tr>
                <td>GLIC Code</td>
                <td>MBS</td>
              </tr>
              <tr>
                <td>COBS Code</td>
                <td>MTGE</td>
              </tr>
              <tr>
                <td>Market Type</td>
                <td>DOMC</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="section-container section-column-container">
        <div class="section-group partial-table indic-mort-collatral">
          <div class="header">PREPAY HISTORY</div>

          <h4>PSA</h4>
          <table>
            <tbody>
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Value</th>
                </tr>
              </thead>

              <tr>
                <td>1</td>
                <td>106.2137</td>
              </tr>

              <tr>
                <td>3</td>
                <td>106.9769</td>
              </tr>

              <tr>
                <td>6</td>
                <td>103.0327</td>
              </tr>

              <tr>
                <td>12</td>
                <td>100.2010</td>
              </tr>

              <tr>
                <td>24</td>
                <td>0.0000</td>
              </tr>

            </tbody>
          </table>

          <h4>CPR</h4>
          <table>
            <tbody>
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Value</th>
                </tr>
              </thead>

              <tr>
                <td>1</td>
                <td>6.3728</td>
              </tr>

              <tr>
                <td>3</td>
                <td>6.4186</td>
              </tr>

              <tr>
                <td>6</td>
                <td>6.1820</td>
              </tr>

              <tr>
                <td>12</td>
                <td>6.0121</td>
              </tr>

              <tr>
                <td>24</td>
                <td>0.0000</td>
              </tr>

            </tbody>
          </table>

        </div>
      </div>
    </div>

          </div>
          <div style="page-break-before: always;">
             <div class="main-container">
                <div class="section-container">
                   <details>
                      <summary>Show json</summary>
                      <div class="json-group">
                         <pre>{
      &quot;meta&quot; : {
        &quot;status&quot; : &quot;DONE&quot;,
        &quot;requestId&quot; : &quot;R-1475071&quot;,
        &quot;timeStamp&quot; : &quot;2025-03-06T21:54:34Z&quot;,
        &quot;responseType&quot; : &quot;BOND_INDIC&quot;,
        &quot;resultsStatus&quot; : &quot;ALL&quot;
      },
      &quot;results&quot; : [ {
        &quot;cusip&quot; : &quot;999818YT8&quot;,
        &quot;indic&quot; : {
          &quot;ltv&quot; : 90.0000,
          &quot;wam&quot; : 201,
          &quot;figi&quot; : &quot;BBG0033WXBV4&quot;,
          &quot;cusip&quot; : &quot;999818YT8&quot;,
          &quot;moody&quot; : [ {
            &quot;value&quot; : &quot;Aaa&quot;
          } ],
          &quot;source&quot; : &quot;CITI&quot;,
          &quot;ticker&quot; : &quot;GNMA&quot;,
          &quot;country&quot; : &quot;US&quot;,
          &quot;loanAge&quot; : 142,
          &quot;lockout&quot; : 0,
          &quot;putFlag&quot; : false,
          &quot;callFlag&quot; : false,
          &quot;cobsCode&quot; : &quot;MTGE&quot;,
          &quot;country2&quot; : &quot;US&quot;,
          &quot;country3&quot; : &quot;USA&quot;,
          &quot;currency&quot; : &quot;USD&quot;,
          &quot;dayCount&quot; : &quot;30/360 eom&quot;,
          &quot;glicCode&quot; : &quot;MBS&quot;,
          &quot;grossWAC&quot; : 4.0000,
          &quot;ioPeriod&quot; : 0,
          &quot;poolCode&quot; : &quot;NA&quot;,
          &quot;sinkFlag&quot; : false,
          &quot;cmaTicker&quot; : &quot;N/A&quot;,
          &quot;datedDate&quot; : &quot;2013-05-01&quot;,
          &quot;gnma2Flag&quot; : false,
          &quot;percentVA&quot; : 10.980,
          &quot;currentLTV&quot; : 28.7000,
          &quot;extendFlag&quot; : &quot;N&quot;,
          &quot;isoCountry&quot; : &quot;US&quot;,
          &quot;marketType&quot; : &quot;DOMC&quot;,
          &quot;percentDTI&quot; : 33.900000,
          &quot;percentFHA&quot; : 81.060,
          &quot;percentInv&quot; : 0.0000,
          &quot;percentPIH&quot; : 0.140,
          &quot;percentRHS&quot; : 7.810,
          &quot;securityID&quot; : &quot;999818YT&quot;,
          &quot;serviceFee&quot; : 0.5000,
          &quot;vPointType&quot; : &quot;MPGNMA&quot;,
          &quot;adjustedLTV&quot; : 28.7000,
          &quot;combinedLTV&quot; : 90.600000,
          &quot;creditScore&quot; : 692,
          &quot;description&quot; : &quot;30-YR GNMA-2013 PROD&quot;,
          &quot;esgBondFlag&quot; : false,
          &quot;indexRating&quot; : &quot;AA+&quot;,
          &quot;issueAmount&quot; : 8597.24000000,
          &quot;lowerRating&quot; : &quot;AA+&quot;,
          &quot;paymentFreq&quot; : 12,
          &quot;percentHARP&quot; : 0.000,
          &quot;percentRefi&quot; : 64.0000,
          &quot;tierCapital&quot; : &quot;NA&quot;,
          &quot;balloonMonth&quot; : 0,
          &quot;deliveryFlag&quot; : &quot;N&quot;,
          &quot;indexCountry&quot; : &quot;US&quot;,
          &quot;industryCode&quot; : &quot;MT&quot;,
          &quot;issuerTicker&quot; : &quot;GNMA&quot;,
          &quot;lowestRating&quot; : &quot;AA+&quot;,
          &quot;maturityDate&quot; : &quot;2041-12-01&quot;,
          &quot;middleRating&quot; : &quot;AA+&quot;,
          &quot;modifiedDate&quot; : &quot;2025-02-13&quot;,
          &quot;originalTerm&quot; : 360,
          &quot;parentTicker&quot; : &quot;GNMA&quot;,
          &quot;percentHARP2&quot; : 0.000,
          &quot;percentJumbo&quot; : 0.000,
          &quot;securityType&quot; : &quot;MORT&quot;,
          &quot;currentCoupon&quot; : 3.500000,
          &quot;dataStateList&quot; : [ {
            &quot;state&quot; : &quot;PR&quot;,
            &quot;percent&quot; : 16.9000
          }, {
            &quot;state&quot; : &quot;TX&quot;,
            &quot;percent&quot; : 10.1100
          }, {
            &quot;state&quot; : &quot;FL&quot;,
            &quot;percent&quot; : 5.7100
          }, {
            &quot;state&quot; : &quot;CA&quot;,
            &quot;percent&quot; : 4.8700
          }, {
            &quot;state&quot; : &quot;OH&quot;,
            &quot;percent&quot; : 4.8200
          }, {
            &quot;state&quot; : &quot;NY&quot;,
            &quot;percent&quot; : 4.7800
          }, {
            &quot;state&quot; : &quot;GA&quot;,
            &quot;percent&quot; : 4.4300
          }, {
            &quot;state&quot; : &quot;PA&quot;,
            &quot;percent&quot; : 3.3500
          }, {
            &quot;state&quot; : &quot;MI&quot;,
            &quot;percent&quot; : 3.1000
          }, {
            &quot;state&quot; : &quot;NC&quot;,
            &quot;percent&quot; : 2.7200
          }, {
            &quot;state&quot; : &quot;VA&quot;,
            &quot;percent&quot; : 2.6900
          }, {
            &quot;state&quot; : &quot;IL&quot;,
            &quot;percent&quot; : 2.6700
          }, {
            &quot;state&quot; : &quot;IN&quot;,
            &quot;percent&quot; : 2.4100
          }, {
            &quot;state&quot; : &quot;NJ&quot;,
            &quot;percent&quot; : 2.4000
          }, {
            &quot;state&quot; : &quot;MD&quot;,
            &quot;percent&quot; : 2.2600
          }, {
            &quot;state&quot; : &quot;MO&quot;,
            &quot;percent&quot; : 2.0900
          }, {
            &quot;state&quot; : &quot;AZ&quot;,
            &quot;percent&quot; : 1.7300
          }, {
            &quot;state&quot; : &quot;TN&quot;,
            &quot;percent&quot; : 1.6900
          }, {
            &quot;state&quot; : &quot;WA&quot;,
            &quot;percent&quot; : 1.5000
          }, {
            &quot;state&quot; : &quot;AL&quot;,
            &quot;percent&quot; : 1.4800
          }, {
            &quot;state&quot; : &quot;OK&quot;,
            &quot;percent&quot; : 1.2400
          }, {
            &quot;state&quot; : &quot;LA&quot;,
            &quot;percent&quot; : 1.2000
          }, {
            &quot;state&quot; : &quot;MN&quot;,
            &quot;percent&quot; : 1.1900
          }, {
            &quot;state&quot; : &quot;SC&quot;,
            &quot;percent&quot; : 1.1200
          }, {
            &quot;state&quot; : &quot;CT&quot;,
            &quot;percent&quot; : 1.0700
          }, {
            &quot;state&quot; : &quot;CO&quot;,
            &quot;percent&quot; : 1.0400
          }, {
            &quot;state&quot; : &quot;KY&quot;,
            &quot;percent&quot; : 1.0200
          }, {
            &quot;state&quot; : &quot;WI&quot;,
            &quot;percent&quot; : 1.0100
          }, {
            &quot;state&quot; : &quot;MS&quot;,
            &quot;percent&quot; : 0.9500
          }, {
            &quot;state&quot; : &quot;NM&quot;,
            &quot;percent&quot; : 0.9400
          }, {
            &quot;state&quot; : &quot;OR&quot;,
            &quot;percent&quot; : 0.8900
          }, {
            &quot;state&quot; : &quot;AR&quot;,
            &quot;percent&quot; : 0.7500
          }, {
            &quot;state&quot; : &quot;NV&quot;,
            &quot;percent&quot; : 0.6900
          }, {
            &quot;state&quot; : &quot;MA&quot;,
            &quot;percent&quot; : 0.6700
          }, {
            &quot;state&quot; : &quot;IA&quot;,
            &quot;percent&quot; : 0.6400
          }, {
            &quot;state&quot; : &quot;KS&quot;,
            &quot;percent&quot; : 0.6000
          }, {
            &quot;state&quot; : &quot;UT&quot;,
            &quot;percent&quot; : 0.5900
          }, {
            &quot;state&quot; : &quot;DE&quot;,
            &quot;percent&quot; : 0.4400
          }, {
            &quot;state&quot; : &quot;ID&quot;,
            &quot;percent&quot; : 0.3900
          }, {
            &quot;state&quot; : &quot;NE&quot;,
            &quot;percent&quot; : 0.3900
          }, {
            &quot;state&quot; : &quot;WV&quot;,
            &quot;percent&quot; : 0.2800
          }, {
            &quot;state&quot; : &quot;ME&quot;,
            &quot;percent&quot; : 0.2000
          }, {
            &quot;state&quot; : &quot;NH&quot;,
            &quot;percent&quot; : 0.1600
          }, {
            &quot;state&quot; : &quot;HI&quot;,
            &quot;percent&quot; : 0.1500
          }, {
            &quot;state&quot; : &quot;MT&quot;,
            &quot;percent&quot; : 0.1300
          }, {
            &quot;state&quot; : &quot;AK&quot;,
            &quot;percent&quot; : 0.1200
          }, {
            &quot;state&quot; : &quot;RI&quot;,
            &quot;percent&quot; : 0.1200
          }, {
            &quot;state&quot; : &quot;WY&quot;,
            &quot;percent&quot; : 0.1000
          }, {
            &quot;state&quot; : &quot;SD&quot;,
            &quot;percent&quot; : 0.0700
          }, {
            &quot;state&quot; : &quot;VT&quot;,
            &quot;percent&quot; : 0.0600
          }, {
            &quot;state&quot; : &quot;DC&quot;,
            &quot;percent&quot; : 0.0500
          }, {
            &quot;state&quot; : &quot;ND&quot;,
            &quot;percent&quot; : 0.0400
          } ],
          &quot;delinquencies&quot; : {
            &quot;del30Days&quot; : {
              &quot;percent&quot; : 2.1200
            },
            &quot;del60Days&quot; : {
              &quot;percent&quot; : 0.6100
            },
            &quot;del90Days&quot; : {
              &quot;percent&quot; : 0.1500
            },
            &quot;del90PlusDays&quot; : {
              &quot;percent&quot; : 0.7300
            },
            &quot;del120PlusDays&quot; : {
              &quot;percent&quot; : 0.5800
            }
          },
          &quot;greenBondFlag&quot; : false,
          &quot;highestRating&quot; : &quot;AAA&quot;,
          &quot;incomeCountry&quot; : &quot;US&quot;,
          &quot;issuerCountry&quot; : &quot;US&quot;,
          &quot;percentSecond&quot; : 0.000,
          &quot;poolAgeMethod&quot; : &quot;Calculated&quot;,
          &quot;prepayEffDate&quot; : &quot;2025-01-01&quot;,
          &quot;seniorityType&quot; : &quot;NA&quot;,
          &quot;assetClassCode&quot; : &quot;CO&quot;,
          &quot;cgmiSectorCode&quot; : &quot;MTGE&quot;,
          &quot;collateralType&quot; : &quot;GNMA&quot;,
          &quot;fullPledgeFlag&quot; : false,
          &quot;gpmPercentStep&quot; : 0.0000,
          &quot;incomeCountry3&quot; : &quot;USA&quot;,
          &quot;instrumentType&quot; : &quot;NA&quot;,
          &quot;issuerCountry2&quot; : &quot;US&quot;,
          &quot;issuerCountry3&quot; : &quot;USA&quot;,
          &quot;lowestRatingNF&quot; : &quot;AA+&quot;,
          &quot;poolIssuerName&quot; : &quot;NA&quot;,
          &quot;vPointCategory&quot; : &quot;RP&quot;,
          &quot;amortizedFHALTV&quot; : 63.9000,
          &quot;bloombergTicker&quot; : &quot;GNSF 3.5 2013&quot;,
          &quot;industrySubCode&quot; : &quot;MT&quot;,
          &quot;originationDate&quot; : &quot;2013-05-01&quot;,
          &quot;originationYear&quot; : 2013,
          &quot;percent2To4Unit&quot; : 2.7000,
          &quot;percentHAMPMods&quot; : 0.900000,
          &quot;percentPurchase&quot; : 31.7000,
          &quot;percentStateHFA&quot; : 0.500000,
          &quot;poolOriginalWAM&quot; : 0,
          &quot;preliminaryFlag&quot; : false,
          &quot;redemptionValue&quot; : 100.0000,
          &quot;securitySubType&quot; : &quot;MPGNMA&quot;,
          &quot;dataQuartileList&quot; : [ {
            &quot;ltvlow&quot; : 17.000,
            &quot;ltvhigh&quot; : 87.000,
            &quot;loanSizeLow&quot; : 22000.000,
            &quot;loanSizeHigh&quot; : 101000.000,
            &quot;percentDTILow&quot; : 10.000,
            &quot;creditScoreLow&quot; : 300.000,
            &quot;percentDTIHigh&quot; : 24.400,
            &quot;creditScoreHigh&quot; : 655.000,
            &quot;originalLoanAgeLow&quot; : 0,
            &quot;originationYearLow&quot; : 20101101,
            &quot;originalLoanAgeHigh&quot; : 0,
            &quot;originationYearHigh&quot; : 20130401
          }, {
            &quot;ltvlow&quot; : 87.000,
            &quot;ltvhigh&quot; : 93.000,
            &quot;loanSizeLow&quot; : 101000.000,
            &quot;loanSizeHigh&quot; : 132000.000,
            &quot;percentDTILow&quot; : 24.400,
            &quot;creditScoreLow&quot; : 655.000,
            &quot;percentDTIHigh&quot; : 34.900,
            &quot;creditScoreHigh&quot; : 691.000,
            &quot;originalLoanAgeLow&quot; : 0,
            &quot;originationYearLow&quot; : 20130401,
            &quot;originalLoanAgeHigh&quot; : 0,
            &quot;originationYearHigh&quot; : 20130501
          }, {
            &quot;ltvlow&quot; : 93.000,
            &quot;ltvhigh&quot; : 97.000,
            &quot;loanSizeLow&quot; : 132000.000,
            &quot;loanSizeHigh&quot; : 183000.000,
            &quot;percentDTILow&quot; : 34.900,
            &quot;creditScoreLow&quot; : 691.000,
            &quot;percentDTIHigh&quot; : 43.500,
            &quot;creditScoreHigh&quot; : 739.000,
            &quot;originalLoanAgeLow&quot; : 0,
            &quot;originationYearLow&quot; : 20130501,
            &quot;originalLoanAgeHigh&quot; : 1,
            &quot;originationYearHigh&quot; : 20130701
          }, {
            &quot;ltvlow&quot; : 97.000,
            &quot;ltvhigh&quot; : 118.000,
            &quot;loanSizeLow&quot; : 183000.000,
            &quot;loanSizeHigh&quot; : 743000.000,
            &quot;percentDTILow&quot; : 43.500,
            &quot;creditScoreLow&quot; : 739.000,
            &quot;percentDTIHigh&quot; : 65.000,
            &quot;creditScoreHigh&quot; : 832.000,
            &quot;originalLoanAgeLow&quot; : 1,
            &quot;originationYearLow&quot; : 20130701,
            &quot;originalLoanAgeHigh&quot; : 43,
            &quot;originationYearHigh&quot; : 20141101
          } ],
          &quot;gpmNumberOfSteps&quot; : 0,
          &quot;percentHARPOwner&quot; : 0.000,
          &quot;percentPrincipal&quot; : 100.0000,
          &quot;securityCalcType&quot; : &quot;GNMA&quot;,
          &quot;assetClassSubCode&quot; : &quot;MBS&quot;,
          &quot;forbearanceAmount&quot; : 0.000000,
          &quot;modifiedTimeStamp&quot; : &quot;2025-02-13T20:06:00Z&quot;,
          &quot;outstandingAmount&quot; : 1139.67000000,
          &quot;parentDescription&quot; : &quot;NA&quot;,
          &quot;poolIsBalloonFlag&quot; : false,
          &quot;prepaymentOptions&quot; : {
            &quot;prepayType&quot; : [ &quot;CPR&quot;, &quot;PSA&quot;, &quot;VEC&quot; ]
          },
          &quot;reperformerMonths&quot; : 1,
          &quot;dataPPMHistoryList&quot; : [ {
            &quot;prepayType&quot; : &quot;PSA&quot;,
            &quot;dataPPMHistoryDetailList&quot; : [ {
              &quot;month&quot; : &quot;1&quot;,
              &quot;prepayRate&quot; : 106.2137
            }, {
              &quot;month&quot; : &quot;3&quot;,
              &quot;prepayRate&quot; : 106.9769
            }, {
              &quot;month&quot; : &quot;6&quot;,
              &quot;prepayRate&quot; : 103.0327
            }, {
              &quot;month&quot; : &quot;12&quot;,
              &quot;prepayRate&quot; : 100.2010
            }, {
              &quot;month&quot; : &quot;24&quot;,
              &quot;prepayRate&quot; : 0.0000
            } ]
          }, {
            &quot;prepayType&quot; : &quot;CPR&quot;,
            &quot;dataPPMHistoryDetailList&quot; : [ {
              &quot;month&quot; : &quot;1&quot;,
              &quot;prepayRate&quot; : 6.3728
            }, {
              &quot;month&quot; : &quot;3&quot;,
              &quot;prepayRate&quot; : 6.4186
            }, {
              &quot;month&quot; : &quot;6&quot;,
              &quot;prepayRate&quot; : 6.1820
            }, {
              &quot;month&quot; : &quot;12&quot;,
              &quot;prepayRate&quot; : 6.0121
            }, {
              &quot;month&quot; : &quot;24&quot;,
              &quot;prepayRate&quot; : 0.0000
            } ]
          } ],
          &quot;daysToFirstPayment&quot; : 44,
          &quot;issuerLowestRating&quot; : &quot;NA&quot;,
          &quot;issuerMiddleRating&quot; : &quot;NA&quot;,
          &quot;newCurrentLoanSize&quot; : 104140.000,
          &quot;originationChannel&quot; : {
            &quot;broker&quot; : 4.620,
            &quot;retail&quot; : 62.120,
            &quot;unknown&quot; : 0.000,
            &quot;unspecified&quot; : 0.000,
            &quot;correspondence&quot; : 33.240
          },
          &quot;percentMultiFamily&quot; : 2.700000,
          &quot;percentRefiCashout&quot; : 5.8000,
          &quot;percentRegularMods&quot; : 3.500000,
          &quot;percentReperformer&quot; : 0.500000,
          &quot;relocationLoanFlag&quot; : false,
          &quot;socialDensityScore&quot; : 0.000,
          &quot;umbsfhlgPercentage&quot; : 0.00,
          &quot;umbsfnmaPercentage&quot; : 0.00,
          &quot;industryDescription&quot; : &quot;Mortgage&quot;,
          &quot;issuerHighestRating&quot; : &quot;NA&quot;,
          &quot;newOriginalLoanSize&quot; : 182010.000,
          &quot;socialCriteriaShare&quot; : 0.000,
          &quot;spreadAtOrigination&quot; : 22.4000,
          &quot;weightedAvgLoanSize&quot; : 104140.0000,
          &quot;poolOriginalLoanSize&quot; : 182010.000000,
          &quot;cgmiSectorDescription&quot; : &quot;Mortgage&quot;,
          &quot;expModelAvailableFlag&quot; : true,
          &quot;fhfaImpliedCurrentLTV&quot; : 28.7000,
          &quot;percentRefiNonCashout&quot; : 58.2000,
          &quot;prepayPenaltySchedule&quot; : &quot;0.000&quot;,
          &quot;defaultHorizonPYMethod&quot; : &quot;OAS Change&quot;,
          &quot;industrySubDescription&quot; : &quot;Mortgage Asset Backed&quot;,
          &quot;actualPrepayHistoryList&quot; : {
            &quot;date&quot; : &quot;2025-04-01&quot;,
            &quot;genericValue&quot; : 0.790700
          },
          &quot;adjustedCurrentLoanSize&quot; : 104140.00,
          &quot;forbearanceModification&quot; : 0.000000,
          &quot;percentTwoPlusBorrowers&quot; : 44.100,
          &quot;poolAvgOriginalLoanTerm&quot; : 0,
          &quot;adjustedOriginalLoanSize&quot; : 181999.00,
          &quot;assetClassSubDescription&quot; : &quot;Collateralized Asset Backed - Mortgage&quot;,
          &quot;mortgageInsurancePremium&quot; : {
            &quot;annual&quot; : {
              &quot;va&quot; : 0.000,
              &quot;fha&quot; : 0.793,
              &quot;pih&quot; : 0.000,
              &quot;rhs&quot; : 0.399
            },
            &quot;upfront&quot; : {
              &quot;va&quot; : 0.500,
              &quot;fha&quot; : 0.689,
              &quot;pih&quot; : 1.000,
              &quot;rhs&quot; : 1.996
            }
          },
          &quot;percentReperformerAndMod&quot; : 0.100,
          &quot;reperformerMonthsForMods&quot; : 2,
          &quot;dataPrepayModelSellerList&quot; : [ {
            &quot;seller&quot; : &quot;HFAL&quot;,
            &quot;percent&quot; : 0.0800
          }, {
            &quot;seller&quot; : &quot;HFUSM&quot;,
            &quot;percent&quot; : 0.0600
          }, {
            &quot;seller&quot; : &quot;HFWA&quot;,
            &quot;percent&quot; : 0.0200
          } ],
          &quot;originalLoanSizeRemaining&quot; : 150707.000,
          &quot;percentFirstTimeHomeBuyer&quot; : 20.700000,
          &quot;current3rdPartyOrigination&quot; : 37.870,
          &quot;adjustedSpreadAtOrigination&quot; : 22.4000,
          &quot;dataPrepayModelServicerList&quot; : [ {
            &quot;percent&quot; : 27.0800,
            &quot;servicer&quot; : &quot;WELLS&quot;
          }, {
            &quot;percent&quot; : 10.9800,
            &quot;servicer&quot; : &quot;BCPOP&quot;
          }, {
            &quot;percent&quot; : 7.5700,
            &quot;servicer&quot; : &quot;NSTAR&quot;
          }, {
            &quot;percent&quot; : 7.3100,
            &quot;servicer&quot; : &quot;QUICK&quot;
          }, {
            &quot;percent&quot; : 7.1400,
            &quot;servicer&quot; : &quot;PENNY&quot;
          }, {
            &quot;percent&quot; : 6.2200,
            &quot;servicer&quot; : &quot;CARRG&quot;
          }, {
            &quot;percent&quot; : 5.9900,
            &quot;servicer&quot; : &quot;LAKEV&quot;
          }, {
            &quot;percent&quot; : 5.5000,
            &quot;servicer&quot; : &quot;USB&quot;
          }, {
            &quot;percent&quot; : 4.2400,
            &quot;servicer&quot; : &quot;FREE&quot;
          }, {
            &quot;percent&quot; : 2.4000,
            &quot;servicer&quot; : &quot;PNC&quot;
          }, {
            &quot;percent&quot; : 1.3300,
            &quot;servicer&quot; : &quot;MNTBK&quot;
          }, {
            &quot;percent&quot; : 1.1900,
            &quot;servicer&quot; : &quot;NWRES&quot;
          }, {
            &quot;percent&quot; : 0.9500,
            &quot;servicer&quot; : &quot;FIFTH&quot;
          }, {
            &quot;percent&quot; : 0.7700,
            &quot;servicer&quot; : &quot;DEPOT&quot;
          }, {
            &quot;percent&quot; : 0.6200,
            &quot;servicer&quot; : &quot;HOMBR&quot;
          }, {
            &quot;percent&quot; : 0.5900,
            &quot;servicer&quot; : &quot;BOKF&quot;
          }, {
            &quot;percent&quot; : 0.5200,
            &quot;servicer&quot; : &quot;JPM&quot;
          }, {
            &quot;percent&quot; : 0.4800,
            &quot;servicer&quot; : &quot;TRUIS&quot;
          }, {
            &quot;percent&quot; : 0.4200,
            &quot;servicer&quot; : &quot;CITI&quot;
          }, {
            &quot;percent&quot; : 0.3700,
            &quot;servicer&quot; : &quot;GUILD&quot;
          }, {
            &quot;percent&quot; : 0.2100,
            &quot;servicer&quot; : &quot;REGNS&quot;
          }, {
            &quot;percent&quot; : 0.2000,
            &quot;servicer&quot; : &quot;CNTRL&quot;
          }, {
            &quot;percent&quot; : 0.1000,
            &quot;servicer&quot; : &quot;MNSRC&quot;
          }, {
            &quot;percent&quot; : 0.0900,
            &quot;servicer&quot; : &quot;COLNL&quot;
          }, {
            &quot;percent&quot; : 0.0800,
            &quot;servicer&quot; : &quot;HFAGY&quot;
          } ],
          &quot;nonWeightedOriginalLoanSize&quot; : 0.000,
          &quot;original3rdPartyOrigination&quot; : 0.000,
          &quot;percentHARPDec2010Extension&quot; : 0.000,
          &quot;percentHARPOneYearExtension&quot; : 0.000,
          &quot;percentDownPaymentAssistance&quot; : 5.600,
          &quot;percentAmortizedFHALTVUnder78&quot; : 95.40,
          &quot;loanPerformanceImpliedCurrentLTV&quot; : 46.2000,
          &quot;reperformerMonthsForReperformers&quot; : 28
        },
        &quot;ticker&quot; : &quot;GNMA&quot;,
        &quot;country&quot; : &quot;US&quot;,
        &quot;currency&quot; : &quot;USD&quot;,
        &quot;identifier&quot; : &quot;999818YT&quot;,
        &quot;description&quot; : &quot;30-YR GNMA-2013 PROD&quot;,
        &quot;issuerTicker&quot; : &quot;GNMA&quot;,
        &quot;maturityDate&quot; : &quot;2041-12-01&quot;,
        &quot;securityType&quot; : &quot;MORT&quot;,
        &quot;currentCoupon&quot; : 3.500000,
        &quot;securitySubType&quot; : &quot;MPGNMA&quot;
      } ]
    }</pre>
                      </div>
                   </details>
                </div>
             </div>
          </div>
       </body>
    </html>

    """

    try:
        logger.info("Calling get_formatted_result")

        response = check_and_raise(
            Client().yield_book_rest.get_formatted_result(
                request_id_parameter=request_id_parameter, format=format, job=job
            )
        )

        output = response
        logger.info("Called get_formatted_result")

        return output
    except Exception as err:
        logger.error(f"Error get_formatted_result. {err}")
        check_exception_and_raise(err)


def get_job(*, job_ref: str) -> JobResponse:
    """
    Get job details

    Parameters
    ----------
    job_ref : str
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    JobResponse


    Examples
    --------
    >>> # get job
    >>> response = get_job(job_ref='myJob')
    >>> print(response)
    {'id': 'J-31887', 'sequence': 0, 'asOf': '2025-03-10', 'closed': True, 'onHold': True, 'aborted': True, 'exitStatus': 'NEVER_STARTED', 'actualHold': True, 'name': 'myJob', 'chain': 'string', 'description': 'string', 'priority': 0, 'order': 'FAST', 'requestCount': 0, 'pendingCount': 0, 'runningCount': 0, 'okCount': 0, 'errorCount': 0, 'abortedCount': 0, 'skipCount': 0, 'startAfter': '2025-03-03T10:10:15Z', 'stopAfter': '2025-03-10T20:10:15Z', 'createdAt': '2025-06-27T09:41:07.534Z', 'updatedAt': '2025-06-27T09:41:07.555Z'}

    """

    try:
        logger.info("Calling get_job")

        response = check_and_raise(Client().yield_book_rest.get_job(job_ref=job_ref))

        output = response
        logger.info("Called get_job")

        return output
    except Exception as err:
        logger.error(f"Error get_job. {err}")
        check_exception_and_raise(err)


def get_job_data(*, job: str, store_type: Union[str, StoreType], request_name: str) -> Any:
    """
    Retrieve job data body using request id or request name.

    Parameters
    ----------
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_name : str
        Unique request id. This can be of the format R-number or request name. If request name is used, corresponding job information should be passed in the query parameter.

    Returns
    --------
    Any


    Examples
    --------


    """

    try:
        logger.info("Calling get_job_data")

        response = check_and_raise(
            Client().yield_book_rest.get_job_data(job=job, store_type=store_type, request_name=request_name)
        )

        output = response
        logger.info("Called get_job_data")

        return output
    except Exception as err:
        logger.error(f"Error get_job_data. {err}")
        check_exception_and_raise(err)


def get_job_object_meta(*, job: str, store_type: Union[str, StoreType], request_id_parameter: str) -> Dict[str, Any]:
    """
    Retrieve job object metadata using request id or request name.

    Parameters
    ----------
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_id_parameter : str
        Unique request id. This can be of the format R-number or request name. If request name is used, corresponding job information should be passed in the query parameter.

    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling get_job_object_meta")

        response = check_and_raise(
            Client().yield_book_rest.get_job_object_meta(
                job=job,
                store_type=store_type,
                request_id_parameter=request_id_parameter,
            )
        )

        output = response
        logger.info("Called get_job_object_meta")

        return output
    except Exception as err:
        logger.error(f"Error get_job_object_meta. {err}")
        check_exception_and_raise(err)


def get_job_status(*, job_ref: str) -> JobStatusResponse:
    """
    Get job status

    Parameters
    ----------
    job_ref : str
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    JobStatusResponse


    Examples
    --------
    >>> # get job status
    >>> response = get_job_status(job_ref="myJob")
    >>> print(response)
    {'id': 'J-31887', 'name': 'myJob', 'jobStatus': 'ABORTED', 'requestCount': 0, 'pendingCount': 0, 'runningCount': 0, 'okCount': 0, 'errorCount': 0, 'abortedCount': 0, 'skippedCount': 0}

    """

    try:
        logger.info("Calling get_job_status")

        response = check_and_raise(Client().yield_book_rest.get_job_status(job_ref=job_ref))

        output = response
        logger.info("Called get_job_status")

        return output
    except Exception as err:
        logger.error(f"Error get_job_status. {err}")
        check_exception_and_raise(err)


def get_json_result(
    *,
    ids: List[str],
    job: Optional[str] = None,
    fields: Optional[List[str]] = None,
    format: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve json result using request id or request name.

    Parameters
    ----------
    ids : List[str]
          Ids can be provided comma separated. Different formats for id are:
          1) RequestId R-number
          2) Request name R:name. In this case also provide jobid (J-number) or jobname (J:name)
          3) Jobid J-number
          4) Job name J:name - only 1 active job with the jobname
          5) Tag name T:name. In this case also provide jobid (J-number) or jobname (J:name)
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    fields : List[str], optional

    format : str, optional
        A sequence of textual characters.

    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling get_json_result")

        response = check_and_raise(
            Client().yield_book_rest.get_json_result(ids=ids, job=job, fields=fields, format=format)
        )

        output = response
        logger.info("Called get_json_result")

        return output
    except Exception as err:
        logger.error(f"Error get_json_result. {err}")
        check_exception_and_raise(err)


def get_result(*, request_id_parameter: str, job: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve single result using request id or request name.

    Parameters
    ----------
    request_id_parameter : str
        Unique request id. This can be of the format R-number or request name. If request name is used, corresponding job information should be passed in the query parameter.
    job : str, optional
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    Dict[str, Any]


    Examples
    --------
    >>> # get result
    >>> response = get_result(request_id_parameter="R-1475071")
    >>> print(response)
    {'meta': {'status': 'DONE', 'requestId': 'R-1475071', 'timeStamp': '2025-03-06T21:54:34Z', 'responseType': 'BOND_INDIC', 'resultsStatus': 'ALL'}, 'results': [{'cusip': '999818YT8', 'indic': {'ltv': 90.0, 'wam': 201, 'figi': 'BBG0033WXBV4', 'cusip': '999818YT8', 'moody': [{'value': 'Aaa'}], 'source': 'CITI', 'ticker': 'GNMA', 'country': 'US', 'loanAge': 142, 'lockout': 0, 'putFlag': False, 'callFlag': False, 'cobsCode': 'MTGE', 'country2': 'US', 'country3': 'USA', 'currency': 'USD', 'dayCount': '30/360 eom', 'glicCode': 'MBS', 'grossWAC': 4.0, 'ioPeriod': 0, 'poolCode': 'NA', 'sinkFlag': False, 'cmaTicker': 'N/A', 'datedDate': '2013-05-01', 'gnma2Flag': False, 'percentVA': 10.98, 'currentLTV': 28.7, 'extendFlag': 'N', 'isoCountry': 'US', 'marketType': 'DOMC', 'percentDTI': 33.9, 'percentFHA': 81.06, 'percentInv': 0.0, 'percentPIH': 0.14, 'percentRHS': 7.81, 'securityID': '999818YT', 'serviceFee': 0.5, 'vPointType': 'MPGNMA', 'adjustedLTV': 28.7, 'combinedLTV': 90.6, 'creditScore': 692, 'description': '30-YR GNMA-2013 PROD', 'esgBondFlag': False, 'indexRating': 'AA+', 'issueAmount': 8597.24, 'lowerRating': 'AA+', 'paymentFreq': 12, 'percentHARP': 0.0, 'percentRefi': 64.0, 'tierCapital': 'NA', 'balloonMonth': 0, 'deliveryFlag': 'N', 'indexCountry': 'US', 'industryCode': 'MT', 'issuerTicker': 'GNMA', 'lowestRating': 'AA+', 'maturityDate': '2041-12-01', 'middleRating': 'AA+', 'modifiedDate': '2025-02-13', 'originalTerm': 360, 'parentTicker': 'GNMA', 'percentHARP2': 0.0, 'percentJumbo': 0.0, 'securityType': 'MORT', 'currentCoupon': 3.5, 'dataStateList': [{'state': 'PR', 'percent': 16.9}, {'state': 'TX', 'percent': 10.11}, {'state': 'FL', 'percent': 5.71}, {'state': 'CA', 'percent': 4.87}, {'state': 'OH', 'percent': 4.82}, {'state': 'NY', 'percent': 4.78}, {'state': 'GA', 'percent': 4.43}, {'state': 'PA', 'percent': 3.35}, {'state': 'MI', 'percent': 3.1}, {'state': 'NC', 'percent': 2.72}, {'state': 'VA', 'percent': 2.69}, {'state': 'IL', 'percent': 2.67}, {'state': 'IN', 'percent': 2.41}, {'state': 'NJ', 'percent': 2.4}, {'state': 'MD', 'percent': 2.26}, {'state': 'MO', 'percent': 2.09}, {'state': 'AZ', 'percent': 1.73}, {'state': 'TN', 'percent': 1.69}, {'state': 'WA', 'percent': 1.5}, {'state': 'AL', 'percent': 1.48}, {'state': 'OK', 'percent': 1.24}, {'state': 'LA', 'percent': 1.2}, {'state': 'MN', 'percent': 1.19}, {'state': 'SC', 'percent': 1.12}, {'state': 'CT', 'percent': 1.07}, {'state': 'CO', 'percent': 1.04}, {'state': 'KY', 'percent': 1.02}, {'state': 'WI', 'percent': 1.01}, {'state': 'MS', 'percent': 0.95}, {'state': 'NM', 'percent': 0.94}, {'state': 'OR', 'percent': 0.89}, {'state': 'AR', 'percent': 0.75}, {'state': 'NV', 'percent': 0.69}, {'state': 'MA', 'percent': 0.67}, {'state': 'IA', 'percent': 0.64}, {'state': 'KS', 'percent': 0.6}, {'state': 'UT', 'percent': 0.59}, {'state': 'DE', 'percent': 0.44}, {'state': 'ID', 'percent': 0.39}, {'state': 'NE', 'percent': 0.39}, {'state': 'WV', 'percent': 0.28}, {'state': 'ME', 'percent': 0.2}, {'state': 'NH', 'percent': 0.16}, {'state': 'HI', 'percent': 0.15}, {'state': 'MT', 'percent': 0.13}, {'state': 'AK', 'percent': 0.12}, {'state': 'RI', 'percent': 0.12}, {'state': 'WY', 'percent': 0.1}, {'state': 'SD', 'percent': 0.07}, {'state': 'VT', 'percent': 0.06}, {'state': 'DC', 'percent': 0.05}, {'state': 'ND', 'percent': 0.04}], 'delinquencies': {'del30Days': {'percent': 2.12}, 'del60Days': {'percent': 0.61}, 'del90Days': {'percent': 0.15}, 'del90PlusDays': {'percent': 0.73}, 'del120PlusDays': {'percent': 0.58}}, 'greenBondFlag': False, 'highestRating': 'AAA', 'incomeCountry': 'US', 'issuerCountry': 'US', 'percentSecond': 0.0, 'poolAgeMethod': 'Calculated', 'prepayEffDate': '2025-01-01', 'seniorityType': 'NA', 'assetClassCode': 'CO', 'cgmiSectorCode': 'MTGE', 'collateralType': 'GNMA', 'fullPledgeFlag': False, 'gpmPercentStep': 0.0, 'incomeCountry3': 'USA', 'instrumentType': 'NA', 'issuerCountry2': 'US', 'issuerCountry3': 'USA', 'lowestRatingNF': 'AA+', 'poolIssuerName': 'NA', 'vPointCategory': 'RP', 'amortizedFHALTV': 63.9, 'bloombergTicker': 'GNSF 3.5 2013', 'industrySubCode': 'MT', 'originationDate': '2013-05-01', 'originationYear': 2013, 'percent2To4Unit': 2.7, 'percentHAMPMods': 0.9, 'percentPurchase': 31.7, 'percentStateHFA': 0.5, 'poolOriginalWAM': 0, 'preliminaryFlag': False, 'redemptionValue': 100.0, 'securitySubType': 'MPGNMA', 'dataQuartileList': [{'ltvlow': 17.0, 'ltvhigh': 87.0, 'loanSizeLow': 22000.0, 'loanSizeHigh': 101000.0, 'percentDTILow': 10.0, 'creditScoreLow': 300.0, 'percentDTIHigh': 24.4, 'creditScoreHigh': 655.0, 'originalLoanAgeLow': 0, 'originationYearLow': 20101101, 'originalLoanAgeHigh': 0, 'originationYearHigh': 20130401}, {'ltvlow': 87.0, 'ltvhigh': 93.0, 'loanSizeLow': 101000.0, 'loanSizeHigh': 132000.0, 'percentDTILow': 24.4, 'creditScoreLow': 655.0, 'percentDTIHigh': 34.9, 'creditScoreHigh': 691.0, 'originalLoanAgeLow': 0, 'originationYearLow': 20130401, 'originalLoanAgeHigh': 0, 'originationYearHigh': 20130501}, {'ltvlow': 93.0, 'ltvhigh': 97.0, 'loanSizeLow': 132000.0, 'loanSizeHigh': 183000.0, 'percentDTILow': 34.9, 'creditScoreLow': 691.0, 'percentDTIHigh': 43.5, 'creditScoreHigh': 739.0, 'originalLoanAgeLow': 0, 'originationYearLow': 20130501, 'originalLoanAgeHigh': 1, 'originationYearHigh': 20130701}, {'ltvlow': 97.0, 'ltvhigh': 118.0, 'loanSizeLow': 183000.0, 'loanSizeHigh': 743000.0, 'percentDTILow': 43.5, 'creditScoreLow': 739.0, 'percentDTIHigh': 65.0, 'creditScoreHigh': 832.0, 'originalLoanAgeLow': 1, 'originationYearLow': 20130701, 'originalLoanAgeHigh': 43, 'originationYearHigh': 20141101}], 'gpmNumberOfSteps': 0, 'percentHARPOwner': 0.0, 'percentPrincipal': 100.0, 'securityCalcType': 'GNMA', 'assetClassSubCode': 'MBS', 'forbearanceAmount': 0.0, 'modifiedTimeStamp': '2025-02-13T20:06:00Z', 'outstandingAmount': 1139.67, 'parentDescription': 'NA', 'poolIsBalloonFlag': False, 'prepaymentOptions': {'prepayType': ['CPR', 'PSA', 'VEC']}, 'reperformerMonths': 1, 'dataPPMHistoryList': [{'prepayType': 'PSA', 'dataPPMHistoryDetailList': [{'month': '1', 'prepayRate': 106.2137}, {'month': '3', 'prepayRate': 106.9769}, {'month': '6', 'prepayRate': 103.0327}, {'month': '12', 'prepayRate': 100.201}, {'month': '24', 'prepayRate': 0.0}]}, {'prepayType': 'CPR', 'dataPPMHistoryDetailList': [{'month': '1', 'prepayRate': 6.3728}, {'month': '3', 'prepayRate': 6.4186}, {'month': '6', 'prepayRate': 6.182}, {'month': '12', 'prepayRate': 6.0121}, {'month': '24', 'prepayRate': 0.0}]}], 'daysToFirstPayment': 44, 'issuerLowestRating': 'NA', 'issuerMiddleRating': 'NA', 'newCurrentLoanSize': 104140.0, 'originationChannel': {'broker': 4.62, 'retail': 62.12, 'unknown': 0.0, 'unspecified': 0.0, 'correspondence': 33.24}, 'percentMultiFamily': 2.7, 'percentRefiCashout': 5.8, 'percentRegularMods': 3.5, 'percentReperformer': 0.5, 'relocationLoanFlag': False, 'socialDensityScore': 0.0, 'umbsfhlgPercentage': 0.0, 'umbsfnmaPercentage': 0.0, 'industryDescription': 'Mortgage', 'issuerHighestRating': 'NA', 'newOriginalLoanSize': 182010.0, 'socialCriteriaShare': 0.0, 'spreadAtOrigination': 22.4, 'weightedAvgLoanSize': 104140.0, 'poolOriginalLoanSize': 182010.0, 'cgmiSectorDescription': 'Mortgage', 'expModelAvailableFlag': True, 'fhfaImpliedCurrentLTV': 28.7, 'percentRefiNonCashout': 58.2, 'prepayPenaltySchedule': '0.000', 'defaultHorizonPYMethod': 'OAS Change', 'industrySubDescription': 'Mortgage Asset Backed', 'actualPrepayHistoryList': {'date': '2025-04-01', 'genericValue': 0.7907}, 'adjustedCurrentLoanSize': 104140.0, 'forbearanceModification': 0.0, 'percentTwoPlusBorrowers': 44.1, 'poolAvgOriginalLoanTerm': 0, 'adjustedOriginalLoanSize': 181999.0, 'assetClassSubDescription': 'Collateralized Asset Backed - Mortgage', 'mortgageInsurancePremium': {'annual': {'va': 0.0, 'fha': 0.793, 'pih': 0.0, 'rhs': 0.399}, 'upfront': {'va': 0.5, 'fha': 0.689, 'pih': 1.0, 'rhs': 1.996}}, 'percentReperformerAndMod': 0.1, 'reperformerMonthsForMods': 2, 'dataPrepayModelSellerList': [{'seller': 'HFAL', 'percent': 0.08}, {'seller': 'HFUSM', 'percent': 0.06}, {'seller': 'HFWA', 'percent': 0.02}], 'originalLoanSizeRemaining': 150707.0, 'percentFirstTimeHomeBuyer': 20.7, 'current3rdPartyOrigination': 37.87, 'adjustedSpreadAtOrigination': 22.4, 'dataPrepayModelServicerList': [{'percent': 27.08, 'servicer': 'WELLS'}, {'percent': 10.98, 'servicer': 'BCPOP'}, {'percent': 7.57, 'servicer': 'NSTAR'}, {'percent': 7.31, 'servicer': 'QUICK'}, {'percent': 7.14, 'servicer': 'PENNY'}, {'percent': 6.22, 'servicer': 'CARRG'}, {'percent': 5.99, 'servicer': 'LAKEV'}, {'percent': 5.5, 'servicer': 'USB'}, {'percent': 4.24, 'servicer': 'FREE'}, {'percent': 2.4, 'servicer': 'PNC'}, {'percent': 1.33, 'servicer': 'MNTBK'}, {'percent': 1.19, 'servicer': 'NWRES'}, {'percent': 0.95, 'servicer': 'FIFTH'}, {'percent': 0.77, 'servicer': 'DEPOT'}, {'percent': 0.62, 'servicer': 'HOMBR'}, {'percent': 0.59, 'servicer': 'BOKF'}, {'percent': 0.52, 'servicer': 'JPM'}, {'percent': 0.48, 'servicer': 'TRUIS'}, {'percent': 0.42, 'servicer': 'CITI'}, {'percent': 0.37, 'servicer': 'GUILD'}, {'percent': 0.21, 'servicer': 'REGNS'}, {'percent': 0.2, 'servicer': 'CNTRL'}, {'percent': 0.1, 'servicer': 'MNSRC'}, {'percent': 0.09, 'servicer': 'COLNL'}, {'percent': 0.08, 'servicer': 'HFAGY'}], 'nonWeightedOriginalLoanSize': 0.0, 'original3rdPartyOrigination': 0.0, 'percentHARPDec2010Extension': 0.0, 'percentHARPOneYearExtension': 0.0, 'percentDownPaymentAssistance': 5.6, 'percentAmortizedFHALTVUnder78': 95.4, 'loanPerformanceImpliedCurrentLTV': 46.2, 'reperformerMonthsForReperformers': 28}, 'ticker': 'GNMA', 'country': 'US', 'currency': 'USD', 'identifier': '999818YT', 'description': '30-YR GNMA-2013 PROD', 'issuerTicker': 'GNMA', 'maturityDate': '2041-12-01', 'securityType': 'MORT', 'currentCoupon': 3.5, 'securitySubType': 'MPGNMA'}]}

    """

    try:
        logger.info("Calling get_result")

        response = check_and_raise(
            Client().yield_book_rest.get_result(request_id_parameter=request_id_parameter, job=job)
        )

        output = response
        logger.info("Called get_result")

        return output
    except Exception as err:
        logger.error(f"Error get_result. {err}")
        check_exception_and_raise(err)


def get_tba_pricing_sync(
    *,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    naf: Optional[datetime.datetime] = None,
    dep: Optional[str] = None,
    visible: Optional[Union[str, Visible]] = None,
    parent_req: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Get tba-pricing sync.

    Parameters
    ----------
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    naf : datetime.datetime, optional
        YYYY-MM-DDTHH:MM:SS
    dep : str, optional
        A sequence of textual characters.
    visible : Union[str, Visible], optional

    parent_req : str, optional
        Example: R-1
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling get_tba_pricing_sync")

        response = check_and_raise(
            Client().yield_book_rest.get_tba_pricing_sync(
                job=job,
                name=name,
                pri=pri,
                naf=naf,
                dep=dep,
                visible=visible,
                parent_req=parent_req,
                tags=tags,
            )
        )

        output = response
        logger.info("Called get_tba_pricing_sync")

        return output
    except Exception as err:
        logger.error(f"Error get_tba_pricing_sync. {err}")
        check_exception_and_raise(err)


def post_cash_flow_async(
    *,
    global_settings: Optional[CashFlowGlobalSettings] = None,
    input: Optional[List[CashFlowInput]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Post cash flow request async.

    Parameters
    ----------
    global_settings : CashFlowGlobalSettings, optional

    input : List[CashFlowInput], optional

    keywords : List[str], optional
        Optional. Used to specify the keywords a user will retrieve in the response. All keywords are returned by default.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling post_cash_flow_async")

        response = check_and_raise(
            Client().yield_book_rest.post_cash_flow_async(
                body=CashFlowRequestData(global_settings=global_settings, input=input, keywords=keywords),
                job=job,
                name=name,
                pri=pri,
                tags=tags,
                content_type="application/json",
            )
        )

        output = response
        logger.info("Called post_cash_flow_async")

        return output
    except Exception as err:
        logger.error(f"Error post_cash_flow_async. {err}")
        check_exception_and_raise(err)


def post_cash_flow_sync(
    *,
    global_settings: Optional[CashFlowGlobalSettings] = None,
    input: Optional[List[CashFlowInput]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Post cash flow sync.

    Parameters
    ----------
    global_settings : CashFlowGlobalSettings, optional

    input : List[CashFlowInput], optional

    keywords : List[str], optional
        Optional. Used to specify the keywords a user will retrieve in the response. All keywords are returned by default.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling post_cash_flow_sync")

        response = check_and_raise(
            Client().yield_book_rest.post_cash_flow_sync(
                body=CashFlowRequestData(global_settings=global_settings, input=input, keywords=keywords),
                job=job,
                name=name,
                pri=pri,
                tags=tags,
                content_type="application/json",
            )
        )

        output = response
        logger.info("Called post_cash_flow_sync")

        return output
    except Exception as err:
        logger.error(f"Error post_cash_flow_sync. {err}")
        check_exception_and_raise(err)


def post_csv_bulk_results_sync(
    *,
    ids: List[str],
    default_settings: Optional[BulkDefaultSettings] = None,
    global_settings: Optional[BulkGlobalSettings] = None,
    fields: Optional[List[ColumnDetail]] = None,
    job: Optional[str] = None,
) -> str:
    """
    Retrieve bulk result using request id or request name in csv format.

    Parameters
    ----------
    default_settings : BulkDefaultSettings, optional

    global_settings : BulkGlobalSettings, optional

    fields : List[ColumnDetail], optional

    ids : List[str]
          Ids can be provided comma separated. Different formats for id are:
          1) RequestId R-number
          2) Request name R:name. In this case also provide jobid (J-number) or jobname (J:name)
          3) Jobid J-number
          4) Job name J:name - only 1 active job with the jobname
          5) Tag name T:name. In this case also provide jobid (J-number) or jobname (J:name)
    job : str, optional
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    str
        A sequence of textual characters.

    Examples
    --------


    """

    try:
        logger.info("Calling post_csv_bulk_results_sync")

        response = check_and_raise(
            Client().yield_book_rest.post_csv_bulk_results_sync(
                body=BulkResultRequest(
                    default_settings=default_settings,
                    global_settings=global_settings,
                    fields=fields,
                ),
                ids=ids,
                job=job,
                content_type="application/json",
            )
        )

        output = response
        logger.info("Called post_csv_bulk_results_sync")

        return output
    except Exception as err:
        logger.error(f"Error post_csv_bulk_results_sync. {err}")
        check_exception_and_raise(err)


def post_json_bulk_request_sync(
    *,
    ids: List[str],
    default_settings: Optional[BulkDefaultSettings] = None,
    global_settings: Optional[BulkGlobalSettings] = None,
    fields: Optional[List[ColumnDetail]] = None,
    job: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve bulk json result using request id or request name.

    Parameters
    ----------
    default_settings : BulkDefaultSettings, optional

    global_settings : BulkGlobalSettings, optional

    fields : List[ColumnDetail], optional

    ids : List[str]
          Ids can be provided comma separated. Different formats for id are:
          1) RequestId R-number
          2) Request name R:name. In this case also provide jobid (J-number) or jobname (J:name)
          3) Jobid J-number
          4) Job name J:name - only 1 active job with the jobname
          5) Tag name T:name. In this case also provide jobid (J-number) or jobname (J:name)
    job : str, optional
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling post_json_bulk_request_sync")

        response = check_and_raise(
            Client().yield_book_rest.post_json_bulk_request_sync(
                body=BulkResultRequest(
                    default_settings=default_settings,
                    global_settings=global_settings,
                    fields=fields,
                ),
                ids=ids,
                job=job,
                content_type="application/json",
            )
        )

        output = response
        logger.info("Called post_json_bulk_request_sync")

        return output
    except Exception as err:
        logger.error(f"Error post_json_bulk_request_sync. {err}")
        check_exception_and_raise(err)


def post_market_setting_sync(
    *,
    input: Optional[List[MarketSettingsRequestInfo]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Post Bond market setting.

    Parameters
    ----------
    input : List[MarketSettingsRequestInfo], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling post_market_setting_sync")

        response = check_and_raise(
            Client().yield_book_rest.post_market_setting_sync(
                body=MarketSettingsRequest(input=input),
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called post_market_setting_sync")

        return output
    except Exception as err:
        logger.error(f"Error post_market_setting_sync. {err}")
        check_exception_and_raise(err)


def request_bond_indic_async(
    *,
    input: Optional[List[IdentifierInfo]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Asynchronous Post method to retrieve the contractual information about the reference data of instruments, which will typically not need any further calculations. Retrieve a request ID by which, using subsequent API 'getResult' endpoint, instrument reference data can be obtained given a BondIndicRequest - 'Input' - parameter that includes the information of which security or list of securities to be queried by CUSIP, ISIN, or other identifier type to obtain basic contractual information such as security type, sector,  maturity, credit ratings, coupon, and specific information based on security type like current pool factor if the requested identifier is a mortgage. Recommended and preferred method for high-volume instrument queries (single requsts broken to recommended 100 items, up to 250 max).

    Parameters
    ----------
    input : List[IdentifierInfo], optional
        Single identifier or a list of identifiers to search instruments by.
    keywords : List[str], optional
        List of keywords from the MappedResponseRefData to be exposed in the result data set.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------
    >>> # Request bond indic with async post
    >>> response = request_bond_indic_async(input=[IdentifierInfo(identifier="999818YT")])
    >>>
    >>> # Get results by request_id
    >>> results_response = get_result(request_id_parameter=response.request_id)
    >>>
    >>> # Print results in json format
    >>> print(js.dumps(results_response, indent=4))
    {
        "meta": {
            "status": "DONE",
            "requestId": "R-1475070",
            "timeStamp": "2025-03-06T21:54:33Z",
            "responseType": "BOND_INDIC",
            "resultsStatus": "ALL"
        },
        "results": [
            {
                "cusip": "999818YT8",
                "indic": {
                    "ltv": 90.0,
                    "wam": 201,
                    "figi": "BBG0033WXBV4",
                    "cusip": "999818YT8",
                    "moody": [
                        {
                            "value": "Aaa"
                        }
                    ],
                    "source": "CITI",
                    "ticker": "GNMA",
                    "country": "US",
                    "loanAge": 142,
                    "lockout": 0,
                    "putFlag": false,
                    "callFlag": false,
                    "cobsCode": "MTGE",
                    "country2": "US",
                    "country3": "USA",
                    "currency": "USD",
                    "dayCount": "30/360 eom",
                    "glicCode": "MBS",
                    "grossWAC": 4.0,
                    "ioPeriod": 0,
                    "poolCode": "NA",
                    "sinkFlag": false,
                    "cmaTicker": "N/A",
                    "datedDate": "2013-05-01",
                    "gnma2Flag": false,
                    "percentVA": 10.98,
                    "currentLTV": 28.7,
                    "extendFlag": "N",
                    "isoCountry": "US",
                    "marketType": "DOMC",
                    "percentDTI": 33.9,
                    "percentFHA": 81.06,
                    "percentInv": 0.0,
                    "percentPIH": 0.14,
                    "percentRHS": 7.81,
                    "securityID": "999818YT",
                    "serviceFee": 0.5,
                    "vPointType": "MPGNMA",
                    "adjustedLTV": 28.7,
                    "combinedLTV": 90.6,
                    "creditScore": 692,
                    "description": "30-YR GNMA-2013 PROD",
                    "esgBondFlag": false,
                    "indexRating": "AA+",
                    "issueAmount": 8597.24,
                    "lowerRating": "AA+",
                    "paymentFreq": 12,
                    "percentHARP": 0.0,
                    "percentRefi": 64.0,
                    "tierCapital": "NA",
                    "balloonMonth": 0,
                    "deliveryFlag": "N",
                    "indexCountry": "US",
                    "industryCode": "MT",
                    "issuerTicker": "GNMA",
                    "lowestRating": "AA+",
                    "maturityDate": "2041-12-01",
                    "middleRating": "AA+",
                    "modifiedDate": "2025-02-13",
                    "originalTerm": 360,
                    "parentTicker": "GNMA",
                    "percentHARP2": 0.0,
                    "percentJumbo": 0.0,
                    "securityType": "MORT",
                    "currentCoupon": 3.5,
                    "dataStateList": [
                        {
                            "state": "PR",
                            "percent": 16.9
                        },
                        {
                            "state": "TX",
                            "percent": 10.11
                        },
                        {
                            "state": "FL",
                            "percent": 5.71
                        },
                        {
                            "state": "CA",
                            "percent": 4.87
                        },
                        {
                            "state": "OH",
                            "percent": 4.82
                        },
                        {
                            "state": "NY",
                            "percent": 4.78
                        },
                        {
                            "state": "GA",
                            "percent": 4.43
                        },
                        {
                            "state": "PA",
                            "percent": 3.35
                        },
                        {
                            "state": "MI",
                            "percent": 3.1
                        },
                        {
                            "state": "NC",
                            "percent": 2.72
                        },
                        {
                            "state": "VA",
                            "percent": 2.69
                        },
                        {
                            "state": "IL",
                            "percent": 2.67
                        },
                        {
                            "state": "IN",
                            "percent": 2.41
                        },
                        {
                            "state": "NJ",
                            "percent": 2.4
                        },
                        {
                            "state": "MD",
                            "percent": 2.26
                        },
                        {
                            "state": "MO",
                            "percent": 2.09
                        },
                        {
                            "state": "AZ",
                            "percent": 1.73
                        },
                        {
                            "state": "TN",
                            "percent": 1.69
                        },
                        {
                            "state": "WA",
                            "percent": 1.5
                        },
                        {
                            "state": "AL",
                            "percent": 1.48
                        },
                        {
                            "state": "OK",
                            "percent": 1.24
                        },
                        {
                            "state": "LA",
                            "percent": 1.2
                        },
                        {
                            "state": "MN",
                            "percent": 1.19
                        },
                        {
                            "state": "SC",
                            "percent": 1.12
                        },
                        {
                            "state": "CT",
                            "percent": 1.07
                        },
                        {
                            "state": "CO",
                            "percent": 1.04
                        },
                        {
                            "state": "KY",
                            "percent": 1.02
                        },
                        {
                            "state": "WI",
                            "percent": 1.01
                        },
                        {
                            "state": "MS",
                            "percent": 0.95
                        },
                        {
                            "state": "NM",
                            "percent": 0.94
                        },
                        {
                            "state": "OR",
                            "percent": 0.89
                        },
                        {
                            "state": "AR",
                            "percent": 0.75
                        },
                        {
                            "state": "NV",
                            "percent": 0.69
                        },
                        {
                            "state": "MA",
                            "percent": 0.67
                        },
                        {
                            "state": "IA",
                            "percent": 0.64
                        },
                        {
                            "state": "KS",
                            "percent": 0.6
                        },
                        {
                            "state": "UT",
                            "percent": 0.59
                        },
                        {
                            "state": "DE",
                            "percent": 0.44
                        },
                        {
                            "state": "ID",
                            "percent": 0.39
                        },
                        {
                            "state": "NE",
                            "percent": 0.39
                        },
                        {
                            "state": "WV",
                            "percent": 0.28
                        },
                        {
                            "state": "ME",
                            "percent": 0.2
                        },
                        {
                            "state": "NH",
                            "percent": 0.16
                        },
                        {
                            "state": "HI",
                            "percent": 0.15
                        },
                        {
                            "state": "MT",
                            "percent": 0.13
                        },
                        {
                            "state": "AK",
                            "percent": 0.12
                        },
                        {
                            "state": "RI",
                            "percent": 0.12
                        },
                        {
                            "state": "WY",
                            "percent": 0.1
                        },
                        {
                            "state": "SD",
                            "percent": 0.07
                        },
                        {
                            "state": "VT",
                            "percent": 0.06
                        },
                        {
                            "state": "DC",
                            "percent": 0.05
                        },
                        {
                            "state": "ND",
                            "percent": 0.04
                        }
                    ],
                    "delinquencies": {
                        "del30Days": {
                            "percent": 2.12
                        },
                        "del60Days": {
                            "percent": 0.61
                        },
                        "del90Days": {
                            "percent": 0.15
                        },
                        "del90PlusDays": {
                            "percent": 0.73
                        },
                        "del120PlusDays": {
                            "percent": 0.58
                        }
                    },
                    "greenBondFlag": false,
                    "highestRating": "AAA",
                    "incomeCountry": "US",
                    "issuerCountry": "US",
                    "percentSecond": 0.0,
                    "poolAgeMethod": "Calculated",
                    "prepayEffDate": "2025-01-01",
                    "seniorityType": "NA",
                    "assetClassCode": "CO",
                    "cgmiSectorCode": "MTGE",
                    "collateralType": "GNMA",
                    "fullPledgeFlag": false,
                    "gpmPercentStep": 0.0,
                    "incomeCountry3": "USA",
                    "instrumentType": "NA",
                    "issuerCountry2": "US",
                    "issuerCountry3": "USA",
                    "lowestRatingNF": "AA+",
                    "poolIssuerName": "NA",
                    "vPointCategory": "RP",
                    "amortizedFHALTV": 63.9,
                    "bloombergTicker": "GNSF 3.5 2013",
                    "industrySubCode": "MT",
                    "originationDate": "2013-05-01",
                    "originationYear": 2013,
                    "percent2To4Unit": 2.7,
                    "percentHAMPMods": 0.9,
                    "percentPurchase": 31.7,
                    "percentStateHFA": 0.5,
                    "poolOriginalWAM": 0,
                    "preliminaryFlag": false,
                    "redemptionValue": 100.0,
                    "securitySubType": "MPGNMA",
                    "dataQuartileList": [
                        {
                            "ltvlow": 17.0,
                            "ltvhigh": 87.0,
                            "loanSizeLow": 22000.0,
                            "loanSizeHigh": 101000.0,
                            "percentDTILow": 10.0,
                            "creditScoreLow": 300.0,
                            "percentDTIHigh": 24.4,
                            "creditScoreHigh": 655.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20101101,
                            "originalLoanAgeHigh": 0,
                            "originationYearHigh": 20130401
                        },
                        {
                            "ltvlow": 87.0,
                            "ltvhigh": 93.0,
                            "loanSizeLow": 101000.0,
                            "loanSizeHigh": 132000.0,
                            "percentDTILow": 24.4,
                            "creditScoreLow": 655.0,
                            "percentDTIHigh": 34.9,
                            "creditScoreHigh": 691.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20130401,
                            "originalLoanAgeHigh": 0,
                            "originationYearHigh": 20130501
                        },
                        {
                            "ltvlow": 93.0,
                            "ltvhigh": 97.0,
                            "loanSizeLow": 132000.0,
                            "loanSizeHigh": 183000.0,
                            "percentDTILow": 34.9,
                            "creditScoreLow": 691.0,
                            "percentDTIHigh": 43.5,
                            "creditScoreHigh": 739.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20130501,
                            "originalLoanAgeHigh": 1,
                            "originationYearHigh": 20130701
                        },
                        {
                            "ltvlow": 97.0,
                            "ltvhigh": 118.0,
                            "loanSizeLow": 183000.0,
                            "loanSizeHigh": 743000.0,
                            "percentDTILow": 43.5,
                            "creditScoreLow": 739.0,
                            "percentDTIHigh": 65.0,
                            "creditScoreHigh": 832.0,
                            "originalLoanAgeLow": 1,
                            "originationYearLow": 20130701,
                            "originalLoanAgeHigh": 43,
                            "originationYearHigh": 20141101
                        }
                    ],
                    "gpmNumberOfSteps": 0,
                    "percentHARPOwner": 0.0,
                    "percentPrincipal": 100.0,
                    "securityCalcType": "GNMA",
                    "assetClassSubCode": "MBS",
                    "forbearanceAmount": 0.0,
                    "modifiedTimeStamp": "2025-02-13T20:06:00Z",
                    "outstandingAmount": 1139.67,
                    "parentDescription": "NA",
                    "poolIsBalloonFlag": false,
                    "prepaymentOptions": {
                        "prepayType": [
                            "CPR",
                            "PSA",
                            "VEC"
                        ]
                    },
                    "reperformerMonths": 1,
                    "dataPPMHistoryList": [
                        {
                            "prepayType": "PSA",
                            "dataPPMHistoryDetailList": [
                                {
                                    "month": "1",
                                    "prepayRate": 106.2137
                                },
                                {
                                    "month": "3",
                                    "prepayRate": 106.9769
                                },
                                {
                                    "month": "6",
                                    "prepayRate": 103.0327
                                },
                                {
                                    "month": "12",
                                    "prepayRate": 100.201
                                },
                                {
                                    "month": "24",
                                    "prepayRate": 0.0
                                }
                            ]
                        },
                        {
                            "prepayType": "CPR",
                            "dataPPMHistoryDetailList": [
                                {
                                    "month": "1",
                                    "prepayRate": 6.3728
                                },
                                {
                                    "month": "3",
                                    "prepayRate": 6.4186
                                },
                                {
                                    "month": "6",
                                    "prepayRate": 6.182
                                },
                                {
                                    "month": "12",
                                    "prepayRate": 6.0121
                                },
                                {
                                    "month": "24",
                                    "prepayRate": 0.0
                                }
                            ]
                        }
                    ],
                    "daysToFirstPayment": 44,
                    "issuerLowestRating": "NA",
                    "issuerMiddleRating": "NA",
                    "newCurrentLoanSize": 104140.0,
                    "originationChannel": {
                        "broker": 4.62,
                        "retail": 62.12,
                        "unknown": 0.0,
                        "unspecified": 0.0,
                        "correspondence": 33.24
                    },
                    "percentMultiFamily": 2.7,
                    "percentRefiCashout": 5.8,
                    "percentRegularMods": 3.5,
                    "percentReperformer": 0.5,
                    "relocationLoanFlag": false,
                    "socialDensityScore": 0.0,
                    "umbsfhlgPercentage": 0.0,
                    "umbsfnmaPercentage": 0.0,
                    "industryDescription": "Mortgage",
                    "issuerHighestRating": "NA",
                    "newOriginalLoanSize": 182010.0,
                    "socialCriteriaShare": 0.0,
                    "spreadAtOrigination": 22.4,
                    "weightedAvgLoanSize": 104140.0,
                    "poolOriginalLoanSize": 182010.0,
                    "cgmiSectorDescription": "Mortgage",
                    "expModelAvailableFlag": true,
                    "fhfaImpliedCurrentLTV": 28.7,
                    "percentRefiNonCashout": 58.2,
                    "prepayPenaltySchedule": "0.000",
                    "defaultHorizonPYMethod": "OAS Change",
                    "industrySubDescription": "Mortgage Asset Backed",
                    "actualPrepayHistoryList": {
                        "date": "2025-04-01",
                        "genericValue": 0.7907
                    },
                    "adjustedCurrentLoanSize": 104140.0,
                    "forbearanceModification": 0.0,
                    "percentTwoPlusBorrowers": 44.1,
                    "poolAvgOriginalLoanTerm": 0,
                    "adjustedOriginalLoanSize": 181999.0,
                    "assetClassSubDescription": "Collateralized Asset Backed - Mortgage",
                    "mortgageInsurancePremium": {
                        "annual": {
                            "va": 0.0,
                            "fha": 0.793,
                            "pih": 0.0,
                            "rhs": 0.399
                        },
                        "upfront": {
                            "va": 0.5,
                            "fha": 0.689,
                            "pih": 1.0,
                            "rhs": 1.996
                        }
                    },
                    "percentReperformerAndMod": 0.1,
                    "reperformerMonthsForMods": 2,
                    "dataPrepayModelSellerList": [
                        {
                            "seller": "HFAL",
                            "percent": 0.08
                        },
                        {
                            "seller": "HFUSM",
                            "percent": 0.06
                        },
                        {
                            "seller": "HFWA",
                            "percent": 0.02
                        }
                    ],
                    "originalLoanSizeRemaining": 150707.0,
                    "percentFirstTimeHomeBuyer": 20.7,
                    "current3rdPartyOrigination": 37.87,
                    "adjustedSpreadAtOrigination": 22.4,
                    "dataPrepayModelServicerList": [
                        {
                            "percent": 27.08,
                            "servicer": "WELLS"
                        },
                        {
                            "percent": 10.98,
                            "servicer": "BCPOP"
                        },
                        {
                            "percent": 7.57,
                            "servicer": "NSTAR"
                        },
                        {
                            "percent": 7.31,
                            "servicer": "QUICK"
                        },
                        {
                            "percent": 7.14,
                            "servicer": "PENNY"
                        },
                        {
                            "percent": 6.22,
                            "servicer": "CARRG"
                        },
                        {
                            "percent": 5.99,
                            "servicer": "LAKEV"
                        },
                        {
                            "percent": 5.5,
                            "servicer": "USB"
                        },
                        {
                            "percent": 4.24,
                            "servicer": "FREE"
                        },
                        {
                            "percent": 2.4,
                            "servicer": "PNC"
                        },
                        {
                            "percent": 1.33,
                            "servicer": "MNTBK"
                        },
                        {
                            "percent": 1.19,
                            "servicer": "NWRES"
                        },
                        {
                            "percent": 0.95,
                            "servicer": "FIFTH"
                        },
                        {
                            "percent": 0.77,
                            "servicer": "DEPOT"
                        },
                        {
                            "percent": 0.62,
                            "servicer": "HOMBR"
                        },
                        {
                            "percent": 0.59,
                            "servicer": "BOKF"
                        },
                        {
                            "percent": 0.52,
                            "servicer": "JPM"
                        },
                        {
                            "percent": 0.48,
                            "servicer": "TRUIS"
                        },
                        {
                            "percent": 0.42,
                            "servicer": "CITI"
                        },
                        {
                            "percent": 0.37,
                            "servicer": "GUILD"
                        },
                        {
                            "percent": 0.21,
                            "servicer": "REGNS"
                        },
                        {
                            "percent": 0.2,
                            "servicer": "CNTRL"
                        },
                        {
                            "percent": 0.1,
                            "servicer": "MNSRC"
                        },
                        {
                            "percent": 0.09,
                            "servicer": "COLNL"
                        },
                        {
                            "percent": 0.08,
                            "servicer": "HFAGY"
                        }
                    ],
                    "nonWeightedOriginalLoanSize": 0.0,
                    "original3rdPartyOrigination": 0.0,
                    "percentHARPDec2010Extension": 0.0,
                    "percentHARPOneYearExtension": 0.0,
                    "percentDownPaymentAssistance": 5.6,
                    "percentAmortizedFHALTVUnder78": 95.4,
                    "loanPerformanceImpliedCurrentLTV": 46.2,
                    "reperformerMonthsForReperformers": 28
                },
                "ticker": "GNMA",
                "country": "US",
                "currency": "USD",
                "identifier": "999818YT",
                "description": "30-YR GNMA-2013 PROD",
                "issuerTicker": "GNMA",
                "maturityDate": "2041-12-01",
                "securityType": "MORT",
                "currentCoupon": 3.5,
                "securitySubType": "MPGNMA"
            }
        ]
    }


    >>> # Request bond indic with async post
    >>> response = request_bond_indic_async(input=[IdentifierInfo(identifier="999818YT",
    >>>                                                          id_type="CUSIP",
    >>>                                                          )])
    >>>
    >>> # Get results by request_id
    >>> results_response = get_result(request_id_parameter=response.request_id)
    >>>
    >>> # Print results in json format
    >>> print(js.dumps(results_response, indent=4))
    {
        "meta": {
            "status": "DONE",
            "requestId": "R-1475071",
            "timeStamp": "2025-03-06T21:54:34Z",
            "responseType": "BOND_INDIC",
            "resultsStatus": "ALL"
        },
        "results": [
            {
                "cusip": "999818YT8",
                "indic": {
                    "ltv": 90.0,
                    "wam": 201,
                    "figi": "BBG0033WXBV4",
                    "cusip": "999818YT8",
                    "moody": [
                        {
                            "value": "Aaa"
                        }
                    ],
                    "source": "CITI",
                    "ticker": "GNMA",
                    "country": "US",
                    "loanAge": 142,
                    "lockout": 0,
                    "putFlag": false,
                    "callFlag": false,
                    "cobsCode": "MTGE",
                    "country2": "US",
                    "country3": "USA",
                    "currency": "USD",
                    "dayCount": "30/360 eom",
                    "glicCode": "MBS",
                    "grossWAC": 4.0,
                    "ioPeriod": 0,
                    "poolCode": "NA",
                    "sinkFlag": false,
                    "cmaTicker": "N/A",
                    "datedDate": "2013-05-01",
                    "gnma2Flag": false,
                    "percentVA": 10.98,
                    "currentLTV": 28.7,
                    "extendFlag": "N",
                    "isoCountry": "US",
                    "marketType": "DOMC",
                    "percentDTI": 33.9,
                    "percentFHA": 81.06,
                    "percentInv": 0.0,
                    "percentPIH": 0.14,
                    "percentRHS": 7.81,
                    "securityID": "999818YT",
                    "serviceFee": 0.5,
                    "vPointType": "MPGNMA",
                    "adjustedLTV": 28.7,
                    "combinedLTV": 90.6,
                    "creditScore": 692,
                    "description": "30-YR GNMA-2013 PROD",
                    "esgBondFlag": false,
                    "indexRating": "AA+",
                    "issueAmount": 8597.24,
                    "lowerRating": "AA+",
                    "paymentFreq": 12,
                    "percentHARP": 0.0,
                    "percentRefi": 64.0,
                    "tierCapital": "NA",
                    "balloonMonth": 0,
                    "deliveryFlag": "N",
                    "indexCountry": "US",
                    "industryCode": "MT",
                    "issuerTicker": "GNMA",
                    "lowestRating": "AA+",
                    "maturityDate": "2041-12-01",
                    "middleRating": "AA+",
                    "modifiedDate": "2025-02-13",
                    "originalTerm": 360,
                    "parentTicker": "GNMA",
                    "percentHARP2": 0.0,
                    "percentJumbo": 0.0,
                    "securityType": "MORT",
                    "currentCoupon": 3.5,
                    "dataStateList": [
                        {
                            "state": "PR",
                            "percent": 16.9
                        },
                        {
                            "state": "TX",
                            "percent": 10.11
                        },
                        {
                            "state": "FL",
                            "percent": 5.71
                        },
                        {
                            "state": "CA",
                            "percent": 4.87
                        },
                        {
                            "state": "OH",
                            "percent": 4.82
                        },
                        {
                            "state": "NY",
                            "percent": 4.78
                        },
                        {
                            "state": "GA",
                            "percent": 4.43
                        },
                        {
                            "state": "PA",
                            "percent": 3.35
                        },
                        {
                            "state": "MI",
                            "percent": 3.1
                        },
                        {
                            "state": "NC",
                            "percent": 2.72
                        },
                        {
                            "state": "VA",
                            "percent": 2.69
                        },
                        {
                            "state": "IL",
                            "percent": 2.67
                        },
                        {
                            "state": "IN",
                            "percent": 2.41
                        },
                        {
                            "state": "NJ",
                            "percent": 2.4
                        },
                        {
                            "state": "MD",
                            "percent": 2.26
                        },
                        {
                            "state": "MO",
                            "percent": 2.09
                        },
                        {
                            "state": "AZ",
                            "percent": 1.73
                        },
                        {
                            "state": "TN",
                            "percent": 1.69
                        },
                        {
                            "state": "WA",
                            "percent": 1.5
                        },
                        {
                            "state": "AL",
                            "percent": 1.48
                        },
                        {
                            "state": "OK",
                            "percent": 1.24
                        },
                        {
                            "state": "LA",
                            "percent": 1.2
                        },
                        {
                            "state": "MN",
                            "percent": 1.19
                        },
                        {
                            "state": "SC",
                            "percent": 1.12
                        },
                        {
                            "state": "CT",
                            "percent": 1.07
                        },
                        {
                            "state": "CO",
                            "percent": 1.04
                        },
                        {
                            "state": "KY",
                            "percent": 1.02
                        },
                        {
                            "state": "WI",
                            "percent": 1.01
                        },
                        {
                            "state": "MS",
                            "percent": 0.95
                        },
                        {
                            "state": "NM",
                            "percent": 0.94
                        },
                        {
                            "state": "OR",
                            "percent": 0.89
                        },
                        {
                            "state": "AR",
                            "percent": 0.75
                        },
                        {
                            "state": "NV",
                            "percent": 0.69
                        },
                        {
                            "state": "MA",
                            "percent": 0.67
                        },
                        {
                            "state": "IA",
                            "percent": 0.64
                        },
                        {
                            "state": "KS",
                            "percent": 0.6
                        },
                        {
                            "state": "UT",
                            "percent": 0.59
                        },
                        {
                            "state": "DE",
                            "percent": 0.44
                        },
                        {
                            "state": "ID",
                            "percent": 0.39
                        },
                        {
                            "state": "NE",
                            "percent": 0.39
                        },
                        {
                            "state": "WV",
                            "percent": 0.28
                        },
                        {
                            "state": "ME",
                            "percent": 0.2
                        },
                        {
                            "state": "NH",
                            "percent": 0.16
                        },
                        {
                            "state": "HI",
                            "percent": 0.15
                        },
                        {
                            "state": "MT",
                            "percent": 0.13
                        },
                        {
                            "state": "AK",
                            "percent": 0.12
                        },
                        {
                            "state": "RI",
                            "percent": 0.12
                        },
                        {
                            "state": "WY",
                            "percent": 0.1
                        },
                        {
                            "state": "SD",
                            "percent": 0.07
                        },
                        {
                            "state": "VT",
                            "percent": 0.06
                        },
                        {
                            "state": "DC",
                            "percent": 0.05
                        },
                        {
                            "state": "ND",
                            "percent": 0.04
                        }
                    ],
                    "delinquencies": {
                        "del30Days": {
                            "percent": 2.12
                        },
                        "del60Days": {
                            "percent": 0.61
                        },
                        "del90Days": {
                            "percent": 0.15
                        },
                        "del90PlusDays": {
                            "percent": 0.73
                        },
                        "del120PlusDays": {
                            "percent": 0.58
                        }
                    },
                    "greenBondFlag": false,
                    "highestRating": "AAA",
                    "incomeCountry": "US",
                    "issuerCountry": "US",
                    "percentSecond": 0.0,
                    "poolAgeMethod": "Calculated",
                    "prepayEffDate": "2025-01-01",
                    "seniorityType": "NA",
                    "assetClassCode": "CO",
                    "cgmiSectorCode": "MTGE",
                    "collateralType": "GNMA",
                    "fullPledgeFlag": false,
                    "gpmPercentStep": 0.0,
                    "incomeCountry3": "USA",
                    "instrumentType": "NA",
                    "issuerCountry2": "US",
                    "issuerCountry3": "USA",
                    "lowestRatingNF": "AA+",
                    "poolIssuerName": "NA",
                    "vPointCategory": "RP",
                    "amortizedFHALTV": 63.9,
                    "bloombergTicker": "GNSF 3.5 2013",
                    "industrySubCode": "MT",
                    "originationDate": "2013-05-01",
                    "originationYear": 2013,
                    "percent2To4Unit": 2.7,
                    "percentHAMPMods": 0.9,
                    "percentPurchase": 31.7,
                    "percentStateHFA": 0.5,
                    "poolOriginalWAM": 0,
                    "preliminaryFlag": false,
                    "redemptionValue": 100.0,
                    "securitySubType": "MPGNMA",
                    "dataQuartileList": [
                        {
                            "ltvlow": 17.0,
                            "ltvhigh": 87.0,
                            "loanSizeLow": 22000.0,
                            "loanSizeHigh": 101000.0,
                            "percentDTILow": 10.0,
                            "creditScoreLow": 300.0,
                            "percentDTIHigh": 24.4,
                            "creditScoreHigh": 655.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20101101,
                            "originalLoanAgeHigh": 0,
                            "originationYearHigh": 20130401
                        },
                        {
                            "ltvlow": 87.0,
                            "ltvhigh": 93.0,
                            "loanSizeLow": 101000.0,
                            "loanSizeHigh": 132000.0,
                            "percentDTILow": 24.4,
                            "creditScoreLow": 655.0,
                            "percentDTIHigh": 34.9,
                            "creditScoreHigh": 691.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20130401,
                            "originalLoanAgeHigh": 0,
                            "originationYearHigh": 20130501
                        },
                        {
                            "ltvlow": 93.0,
                            "ltvhigh": 97.0,
                            "loanSizeLow": 132000.0,
                            "loanSizeHigh": 183000.0,
                            "percentDTILow": 34.9,
                            "creditScoreLow": 691.0,
                            "percentDTIHigh": 43.5,
                            "creditScoreHigh": 739.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20130501,
                            "originalLoanAgeHigh": 1,
                            "originationYearHigh": 20130701
                        },
                        {
                            "ltvlow": 97.0,
                            "ltvhigh": 118.0,
                            "loanSizeLow": 183000.0,
                            "loanSizeHigh": 743000.0,
                            "percentDTILow": 43.5,
                            "creditScoreLow": 739.0,
                            "percentDTIHigh": 65.0,
                            "creditScoreHigh": 832.0,
                            "originalLoanAgeLow": 1,
                            "originationYearLow": 20130701,
                            "originalLoanAgeHigh": 43,
                            "originationYearHigh": 20141101
                        }
                    ],
                    "gpmNumberOfSteps": 0,
                    "percentHARPOwner": 0.0,
                    "percentPrincipal": 100.0,
                    "securityCalcType": "GNMA",
                    "assetClassSubCode": "MBS",
                    "forbearanceAmount": 0.0,
                    "modifiedTimeStamp": "2025-02-13T20:06:00Z",
                    "outstandingAmount": 1139.67,
                    "parentDescription": "NA",
                    "poolIsBalloonFlag": false,
                    "prepaymentOptions": {
                        "prepayType": [
                            "CPR",
                            "PSA",
                            "VEC"
                        ]
                    },
                    "reperformerMonths": 1,
                    "dataPPMHistoryList": [
                        {
                            "prepayType": "PSA",
                            "dataPPMHistoryDetailList": [
                                {
                                    "month": "1",
                                    "prepayRate": 106.2137
                                },
                                {
                                    "month": "3",
                                    "prepayRate": 106.9769
                                },
                                {
                                    "month": "6",
                                    "prepayRate": 103.0327
                                },
                                {
                                    "month": "12",
                                    "prepayRate": 100.201
                                },
                                {
                                    "month": "24",
                                    "prepayRate": 0.0
                                }
                            ]
                        },
                        {
                            "prepayType": "CPR",
                            "dataPPMHistoryDetailList": [
                                {
                                    "month": "1",
                                    "prepayRate": 6.3728
                                },
                                {
                                    "month": "3",
                                    "prepayRate": 6.4186
                                },
                                {
                                    "month": "6",
                                    "prepayRate": 6.182
                                },
                                {
                                    "month": "12",
                                    "prepayRate": 6.0121
                                },
                                {
                                    "month": "24",
                                    "prepayRate": 0.0
                                }
                            ]
                        }
                    ],
                    "daysToFirstPayment": 44,
                    "issuerLowestRating": "NA",
                    "issuerMiddleRating": "NA",
                    "newCurrentLoanSize": 104140.0,
                    "originationChannel": {
                        "broker": 4.62,
                        "retail": 62.12,
                        "unknown": 0.0,
                        "unspecified": 0.0,
                        "correspondence": 33.24
                    },
                    "percentMultiFamily": 2.7,
                    "percentRefiCashout": 5.8,
                    "percentRegularMods": 3.5,
                    "percentReperformer": 0.5,
                    "relocationLoanFlag": false,
                    "socialDensityScore": 0.0,
                    "umbsfhlgPercentage": 0.0,
                    "umbsfnmaPercentage": 0.0,
                    "industryDescription": "Mortgage",
                    "issuerHighestRating": "NA",
                    "newOriginalLoanSize": 182010.0,
                    "socialCriteriaShare": 0.0,
                    "spreadAtOrigination": 22.4,
                    "weightedAvgLoanSize": 104140.0,
                    "poolOriginalLoanSize": 182010.0,
                    "cgmiSectorDescription": "Mortgage",
                    "expModelAvailableFlag": true,
                    "fhfaImpliedCurrentLTV": 28.7,
                    "percentRefiNonCashout": 58.2,
                    "prepayPenaltySchedule": "0.000",
                    "defaultHorizonPYMethod": "OAS Change",
                    "industrySubDescription": "Mortgage Asset Backed",
                    "actualPrepayHistoryList": {
                        "date": "2025-04-01",
                        "genericValue": 0.7907
                    },
                    "adjustedCurrentLoanSize": 104140.0,
                    "forbearanceModification": 0.0,
                    "percentTwoPlusBorrowers": 44.1,
                    "poolAvgOriginalLoanTerm": 0,
                    "adjustedOriginalLoanSize": 181999.0,
                    "assetClassSubDescription": "Collateralized Asset Backed - Mortgage",
                    "mortgageInsurancePremium": {
                        "annual": {
                            "va": 0.0,
                            "fha": 0.793,
                            "pih": 0.0,
                            "rhs": 0.399
                        },
                        "upfront": {
                            "va": 0.5,
                            "fha": 0.689,
                            "pih": 1.0,
                            "rhs": 1.996
                        }
                    },
                    "percentReperformerAndMod": 0.1,
                    "reperformerMonthsForMods": 2,
                    "dataPrepayModelSellerList": [
                        {
                            "seller": "HFAL",
                            "percent": 0.08
                        },
                        {
                            "seller": "HFUSM",
                            "percent": 0.06
                        },
                        {
                            "seller": "HFWA",
                            "percent": 0.02
                        }
                    ],
                    "originalLoanSizeRemaining": 150707.0,
                    "percentFirstTimeHomeBuyer": 20.7,
                    "current3rdPartyOrigination": 37.87,
                    "adjustedSpreadAtOrigination": 22.4,
                    "dataPrepayModelServicerList": [
                        {
                            "percent": 27.08,
                            "servicer": "WELLS"
                        },
                        {
                            "percent": 10.98,
                            "servicer": "BCPOP"
                        },
                        {
                            "percent": 7.57,
                            "servicer": "NSTAR"
                        },
                        {
                            "percent": 7.31,
                            "servicer": "QUICK"
                        },
                        {
                            "percent": 7.14,
                            "servicer": "PENNY"
                        },
                        {
                            "percent": 6.22,
                            "servicer": "CARRG"
                        },
                        {
                            "percent": 5.99,
                            "servicer": "LAKEV"
                        },
                        {
                            "percent": 5.5,
                            "servicer": "USB"
                        },
                        {
                            "percent": 4.24,
                            "servicer": "FREE"
                        },
                        {
                            "percent": 2.4,
                            "servicer": "PNC"
                        },
                        {
                            "percent": 1.33,
                            "servicer": "MNTBK"
                        },
                        {
                            "percent": 1.19,
                            "servicer": "NWRES"
                        },
                        {
                            "percent": 0.95,
                            "servicer": "FIFTH"
                        },
                        {
                            "percent": 0.77,
                            "servicer": "DEPOT"
                        },
                        {
                            "percent": 0.62,
                            "servicer": "HOMBR"
                        },
                        {
                            "percent": 0.59,
                            "servicer": "BOKF"
                        },
                        {
                            "percent": 0.52,
                            "servicer": "JPM"
                        },
                        {
                            "percent": 0.48,
                            "servicer": "TRUIS"
                        },
                        {
                            "percent": 0.42,
                            "servicer": "CITI"
                        },
                        {
                            "percent": 0.37,
                            "servicer": "GUILD"
                        },
                        {
                            "percent": 0.21,
                            "servicer": "REGNS"
                        },
                        {
                            "percent": 0.2,
                            "servicer": "CNTRL"
                        },
                        {
                            "percent": 0.1,
                            "servicer": "MNSRC"
                        },
                        {
                            "percent": 0.09,
                            "servicer": "COLNL"
                        },
                        {
                            "percent": 0.08,
                            "servicer": "HFAGY"
                        }
                    ],
                    "nonWeightedOriginalLoanSize": 0.0,
                    "original3rdPartyOrigination": 0.0,
                    "percentHARPDec2010Extension": 0.0,
                    "percentHARPOneYearExtension": 0.0,
                    "percentDownPaymentAssistance": 5.6,
                    "percentAmortizedFHALTVUnder78": 95.4,
                    "loanPerformanceImpliedCurrentLTV": 46.2,
                    "reperformerMonthsForReperformers": 28
                },
                "ticker": "GNMA",
                "country": "US",
                "currency": "USD",
                "identifier": "999818YT",
                "description": "30-YR GNMA-2013 PROD",
                "issuerTicker": "GNMA",
                "maturityDate": "2041-12-01",
                "securityType": "MORT",
                "currentCoupon": 3.5,
                "securitySubType": "MPGNMA"
            }
        ]
    }

    """

    try:
        logger.info("Calling request_bond_indic_async")

        response = check_and_raise(
            Client().yield_book_rest.request_bond_indic_async(
                body=BondIndicRequest(input=input, keywords=keywords),
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called request_bond_indic_async")

        return output
    except Exception as err:
        logger.error(f"Error request_bond_indic_async. {err}")
        check_exception_and_raise(err)


def request_bond_indic_async_get(
    *,
    id: str,
    id_type: Optional[Union[str, IdTypeEnum]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Asynchronous Get method to retrieve the contractual information about the reference data of instruments, which will typically not need any further calculations. Retrieve a request ID by which, using subsequent API 'getResult' endpoint, instrument reference data can be obtained given a BondIndicRequest - 'Input' - parameter that includes the information of which security or list of securities to be queried by CUSIP, ISIN, or other identifier type to obtain basic contractual information such as security type, sector,  maturity, credit ratings, coupon, and specific information based on security type like current pool factor if the requested identifier is a mortgage.

    Parameters
    ----------
    id : str
        A sequence of textual characters.
    id_type : Union[str, IdTypeEnum], optional

    keywords : List[str], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------
    >>> # Request bond indic with async get
    >>> response = request_bond_indic_async_get(id="999818YT", id_type=IdTypeEnum.CUSIP)
    >>>
    >>> # Get results by request_id
    >>> results_response = get_result(request_id_parameter=response.request_id)
    >>>
    >>> # Due to async nature, code Will perform the fetch 10 times, as result is not always ready instantly, with 3 second lapse between attempts
    >>> attempt = 1
    >>>
    >>> if not results_response:
    >>>     while attempt < 10:
    >>>         print(f"Attempt " + str(attempt) + " resulted in error retrieving results from:" + response.request_id)
    >>>
    >>>         time.sleep(10)
    >>>
    >>>         results_response = get_result(request_id_parameter=response.request_id)
    >>>
    >>>         if not results_response:
    >>>             attempt += 1
    >>>         else:
    >>>             break
    >>>
    >>> # Print results in json format
    >>> print(js.dumps(results_response, indent=4))
    {
        "data": {
            "cusip": "999818YT8",
            "indic": {
                "ltv": 90.0,
                "wam": 201,
                "figi": "BBG0033WXBV4",
                "cusip": "999818YT8",
                "moody": [
                    {
                        "value": "Aaa"
                    }
                ],
                "source": "CITI",
                "ticker": "GNMA",
                "country": "US",
                "loanAge": 142,
                "lockout": 0,
                "putFlag": false,
                "callFlag": false,
                "cobsCode": "MTGE",
                "country2": "US",
                "country3": "USA",
                "currency": "USD",
                "dayCount": "30/360 eom",
                "glicCode": "MBS",
                "grossWAC": 4.0,
                "ioPeriod": 0,
                "poolCode": "NA",
                "sinkFlag": false,
                "cmaTicker": "N/A",
                "datedDate": "2013-05-01",
                "gnma2Flag": false,
                "percentVA": 10.98,
                "currentLTV": 28.7,
                "extendFlag": "N",
                "isoCountry": "US",
                "marketType": "DOMC",
                "percentDTI": 33.9,
                "percentFHA": 81.06,
                "percentInv": 0.0,
                "percentPIH": 0.14,
                "percentRHS": 7.81,
                "securityID": "999818YT",
                "serviceFee": 0.5,
                "vPointType": "MPGNMA",
                "adjustedLTV": 28.7,
                "combinedLTV": 90.6,
                "creditScore": 692,
                "description": "30-YR GNMA-2013 PROD",
                "esgBondFlag": false,
                "indexRating": "AA+",
                "issueAmount": 8597.24,
                "lowerRating": "AA+",
                "paymentFreq": 12,
                "percentHARP": 0.0,
                "percentRefi": 64.0,
                "tierCapital": "NA",
                "balloonMonth": 0,
                "deliveryFlag": "N",
                "indexCountry": "US",
                "industryCode": "MT",
                "issuerTicker": "GNMA",
                "lowestRating": "AA+",
                "maturityDate": "2041-12-01",
                "middleRating": "AA+",
                "modifiedDate": "2025-02-13",
                "originalTerm": 360,
                "parentTicker": "GNMA",
                "percentHARP2": 0.0,
                "percentJumbo": 0.0,
                "securityType": "MORT",
                "currentCoupon": 3.5,
                "dataStateList": [
                    {
                        "state": "PR",
                        "percent": 16.9
                    },
                    {
                        "state": "TX",
                        "percent": 10.11
                    },
                    {
                        "state": "FL",
                        "percent": 5.71
                    },
                    {
                        "state": "CA",
                        "percent": 4.87
                    },
                    {
                        "state": "OH",
                        "percent": 4.82
                    },
                    {
                        "state": "NY",
                        "percent": 4.78
                    },
                    {
                        "state": "GA",
                        "percent": 4.43
                    },
                    {
                        "state": "PA",
                        "percent": 3.35
                    },
                    {
                        "state": "MI",
                        "percent": 3.1
                    },
                    {
                        "state": "NC",
                        "percent": 2.72
                    },
                    {
                        "state": "VA",
                        "percent": 2.69
                    },
                    {
                        "state": "IL",
                        "percent": 2.67
                    },
                    {
                        "state": "IN",
                        "percent": 2.41
                    },
                    {
                        "state": "NJ",
                        "percent": 2.4
                    },
                    {
                        "state": "MD",
                        "percent": 2.26
                    },
                    {
                        "state": "MO",
                        "percent": 2.09
                    },
                    {
                        "state": "AZ",
                        "percent": 1.73
                    },
                    {
                        "state": "TN",
                        "percent": 1.69
                    },
                    {
                        "state": "WA",
                        "percent": 1.5
                    },
                    {
                        "state": "AL",
                        "percent": 1.48
                    },
                    {
                        "state": "OK",
                        "percent": 1.24
                    },
                    {
                        "state": "LA",
                        "percent": 1.2
                    },
                    {
                        "state": "MN",
                        "percent": 1.19
                    },
                    {
                        "state": "SC",
                        "percent": 1.12
                    },
                    {
                        "state": "CT",
                        "percent": 1.07
                    },
                    {
                        "state": "CO",
                        "percent": 1.04
                    },
                    {
                        "state": "KY",
                        "percent": 1.02
                    },
                    {
                        "state": "WI",
                        "percent": 1.01
                    },
                    {
                        "state": "MS",
                        "percent": 0.95
                    },
                    {
                        "state": "NM",
                        "percent": 0.94
                    },
                    {
                        "state": "OR",
                        "percent": 0.89
                    },
                    {
                        "state": "AR",
                        "percent": 0.75
                    },
                    {
                        "state": "NV",
                        "percent": 0.69
                    },
                    {
                        "state": "MA",
                        "percent": 0.67
                    },
                    {
                        "state": "IA",
                        "percent": 0.64
                    },
                    {
                        "state": "KS",
                        "percent": 0.6
                    },
                    {
                        "state": "UT",
                        "percent": 0.59
                    },
                    {
                        "state": "DE",
                        "percent": 0.44
                    },
                    {
                        "state": "ID",
                        "percent": 0.39
                    },
                    {
                        "state": "NE",
                        "percent": 0.39
                    },
                    {
                        "state": "WV",
                        "percent": 0.28
                    },
                    {
                        "state": "ME",
                        "percent": 0.2
                    },
                    {
                        "state": "NH",
                        "percent": 0.16
                    },
                    {
                        "state": "HI",
                        "percent": 0.15
                    },
                    {
                        "state": "MT",
                        "percent": 0.13
                    },
                    {
                        "state": "AK",
                        "percent": 0.12
                    },
                    {
                        "state": "RI",
                        "percent": 0.12
                    },
                    {
                        "state": "WY",
                        "percent": 0.1
                    },
                    {
                        "state": "SD",
                        "percent": 0.07
                    },
                    {
                        "state": "VT",
                        "percent": 0.06
                    },
                    {
                        "state": "DC",
                        "percent": 0.05
                    },
                    {
                        "state": "ND",
                        "percent": 0.04
                    }
                ],
                "delinquencies": {
                    "del30Days": {
                        "percent": 2.12
                    },
                    "del60Days": {
                        "percent": 0.61
                    },
                    "del90Days": {
                        "percent": 0.15
                    },
                    "del90PlusDays": {
                        "percent": 0.73
                    },
                    "del120PlusDays": {
                        "percent": 0.58
                    }
                },
                "greenBondFlag": false,
                "highestRating": "AAA",
                "incomeCountry": "US",
                "issuerCountry": "US",
                "percentSecond": 0.0,
                "poolAgeMethod": "Calculated",
                "prepayEffDate": "2025-01-01",
                "seniorityType": "NA",
                "assetClassCode": "CO",
                "cgmiSectorCode": "MTGE",
                "collateralType": "GNMA",
                "fullPledgeFlag": false,
                "gpmPercentStep": 0.0,
                "incomeCountry3": "USA",
                "instrumentType": "NA",
                "issuerCountry2": "US",
                "issuerCountry3": "USA",
                "lowestRatingNF": "AA+",
                "poolIssuerName": "NA",
                "vPointCategory": "RP",
                "amortizedFHALTV": 63.9,
                "bloombergTicker": "GNSF 3.5 2013",
                "industrySubCode": "MT",
                "originationDate": "2013-05-01",
                "originationYear": 2013,
                "percent2To4Unit": 2.7,
                "percentHAMPMods": 0.9,
                "percentPurchase": 31.7,
                "percentStateHFA": 0.5,
                "poolOriginalWAM": 0,
                "preliminaryFlag": false,
                "redemptionValue": 100.0,
                "securitySubType": "MPGNMA",
                "dataQuartileList": [
                    {
                        "ltvlow": 17.0,
                        "ltvhigh": 87.0,
                        "loanSizeLow": 22000.0,
                        "loanSizeHigh": 101000.0,
                        "percentDTILow": 10.0,
                        "creditScoreLow": 300.0,
                        "percentDTIHigh": 24.4,
                        "creditScoreHigh": 655.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20101101,
                        "originalLoanAgeHigh": 0,
                        "originationYearHigh": 20130401
                    },
                    {
                        "ltvlow": 87.0,
                        "ltvhigh": 93.0,
                        "loanSizeLow": 101000.0,
                        "loanSizeHigh": 132000.0,
                        "percentDTILow": 24.4,
                        "creditScoreLow": 655.0,
                        "percentDTIHigh": 34.9,
                        "creditScoreHigh": 691.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20130401,
                        "originalLoanAgeHigh": 0,
                        "originationYearHigh": 20130501
                    },
                    {
                        "ltvlow": 93.0,
                        "ltvhigh": 97.0,
                        "loanSizeLow": 132000.0,
                        "loanSizeHigh": 183000.0,
                        "percentDTILow": 34.9,
                        "creditScoreLow": 691.0,
                        "percentDTIHigh": 43.5,
                        "creditScoreHigh": 739.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20130501,
                        "originalLoanAgeHigh": 1,
                        "originationYearHigh": 20130701
                    },
                    {
                        "ltvlow": 97.0,
                        "ltvhigh": 118.0,
                        "loanSizeLow": 183000.0,
                        "loanSizeHigh": 743000.0,
                        "percentDTILow": 43.5,
                        "creditScoreLow": 739.0,
                        "percentDTIHigh": 65.0,
                        "creditScoreHigh": 832.0,
                        "originalLoanAgeLow": 1,
                        "originationYearLow": 20130701,
                        "originalLoanAgeHigh": 43,
                        "originationYearHigh": 20141101
                    }
                ],
                "gpmNumberOfSteps": 0,
                "percentHARPOwner": 0.0,
                "percentPrincipal": 100.0,
                "securityCalcType": "GNMA",
                "assetClassSubCode": "MBS",
                "forbearanceAmount": 0.0,
                "modifiedTimeStamp": "2025-02-13T20:06:00Z",
                "outstandingAmount": 1139.67,
                "parentDescription": "NA",
                "poolIsBalloonFlag": false,
                "prepaymentOptions": {
                    "prepayType": [
                        "CPR",
                        "PSA",
                        "VEC"
                    ]
                },
                "reperformerMonths": 1,
                "dataPPMHistoryList": [
                    {
                        "prepayType": "PSA",
                        "dataPPMHistoryDetailList": [
                            {
                                "month": "1",
                                "prepayRate": 106.2137
                            },
                            {
                                "month": "3",
                                "prepayRate": 106.9769
                            },
                            {
                                "month": "6",
                                "prepayRate": 103.0327
                            },
                            {
                                "month": "12",
                                "prepayRate": 100.201
                            },
                            {
                                "month": "24",
                                "prepayRate": 0.0
                            }
                        ]
                    },
                    {
                        "prepayType": "CPR",
                        "dataPPMHistoryDetailList": [
                            {
                                "month": "1",
                                "prepayRate": 6.3728
                            },
                            {
                                "month": "3",
                                "prepayRate": 6.4186
                            },
                            {
                                "month": "6",
                                "prepayRate": 6.182
                            },
                            {
                                "month": "12",
                                "prepayRate": 6.0121
                            },
                            {
                                "month": "24",
                                "prepayRate": 0.0
                            }
                        ]
                    }
                ],
                "daysToFirstPayment": 44,
                "issuerLowestRating": "NA",
                "issuerMiddleRating": "NA",
                "newCurrentLoanSize": 104140.0,
                "originationChannel": {
                    "broker": 4.62,
                    "retail": 62.12,
                    "unknown": 0.0,
                    "unspecified": 0.0,
                    "correspondence": 33.24
                },
                "percentMultiFamily": 2.7,
                "percentRefiCashout": 5.8,
                "percentRegularMods": 3.5,
                "percentReperformer": 0.5,
                "relocationLoanFlag": false,
                "socialDensityScore": 0.0,
                "umbsfhlgPercentage": 0.0,
                "umbsfnmaPercentage": 0.0,
                "industryDescription": "Mortgage",
                "issuerHighestRating": "NA",
                "newOriginalLoanSize": 182010.0,
                "socialCriteriaShare": 0.0,
                "spreadAtOrigination": 22.4,
                "weightedAvgLoanSize": 104140.0,
                "poolOriginalLoanSize": 182010.0,
                "cgmiSectorDescription": "Mortgage",
                "expModelAvailableFlag": true,
                "fhfaImpliedCurrentLTV": 28.7,
                "percentRefiNonCashout": 58.2,
                "prepayPenaltySchedule": "0.000",
                "defaultHorizonPYMethod": "OAS Change",
                "industrySubDescription": "Mortgage Asset Backed",
                "actualPrepayHistoryList": {
                    "date": "2025-04-01",
                    "genericValue": 0.7907
                },
                "adjustedCurrentLoanSize": 104140.0,
                "forbearanceModification": 0.0,
                "percentTwoPlusBorrowers": 44.1,
                "poolAvgOriginalLoanTerm": 0,
                "adjustedOriginalLoanSize": 181999.0,
                "assetClassSubDescription": "Collateralized Asset Backed - Mortgage",
                "mortgageInsurancePremium": {
                    "annual": {
                        "va": 0.0,
                        "fha": 0.793,
                        "pih": 0.0,
                        "rhs": 0.399
                    },
                    "upfront": {
                        "va": 0.5,
                        "fha": 0.689,
                        "pih": 1.0,
                        "rhs": 1.996
                    }
                },
                "percentReperformerAndMod": 0.1,
                "reperformerMonthsForMods": 2,
                "dataPrepayModelSellerList": [
                    {
                        "seller": "HFAL",
                        "percent": 0.08
                    },
                    {
                        "seller": "HFUSM",
                        "percent": 0.06
                    },
                    {
                        "seller": "HFWA",
                        "percent": 0.02
                    }
                ],
                "originalLoanSizeRemaining": 150707.0,
                "percentFirstTimeHomeBuyer": 20.7,
                "current3rdPartyOrigination": 37.87,
                "adjustedSpreadAtOrigination": 22.4,
                "dataPrepayModelServicerList": [
                    {
                        "percent": 27.08,
                        "servicer": "WELLS"
                    },
                    {
                        "percent": 10.98,
                        "servicer": "BCPOP"
                    },
                    {
                        "percent": 7.57,
                        "servicer": "NSTAR"
                    },
                    {
                        "percent": 7.31,
                        "servicer": "QUICK"
                    },
                    {
                        "percent": 7.14,
                        "servicer": "PENNY"
                    },
                    {
                        "percent": 6.22,
                        "servicer": "CARRG"
                    },
                    {
                        "percent": 5.99,
                        "servicer": "LAKEV"
                    },
                    {
                        "percent": 5.5,
                        "servicer": "USB"
                    },
                    {
                        "percent": 4.24,
                        "servicer": "FREE"
                    },
                    {
                        "percent": 2.4,
                        "servicer": "PNC"
                    },
                    {
                        "percent": 1.33,
                        "servicer": "MNTBK"
                    },
                    {
                        "percent": 1.19,
                        "servicer": "NWRES"
                    },
                    {
                        "percent": 0.95,
                        "servicer": "FIFTH"
                    },
                    {
                        "percent": 0.77,
                        "servicer": "DEPOT"
                    },
                    {
                        "percent": 0.62,
                        "servicer": "HOMBR"
                    },
                    {
                        "percent": 0.59,
                        "servicer": "BOKF"
                    },
                    {
                        "percent": 0.52,
                        "servicer": "JPM"
                    },
                    {
                        "percent": 0.48,
                        "servicer": "TRUIS"
                    },
                    {
                        "percent": 0.42,
                        "servicer": "CITI"
                    },
                    {
                        "percent": 0.37,
                        "servicer": "GUILD"
                    },
                    {
                        "percent": 0.21,
                        "servicer": "REGNS"
                    },
                    {
                        "percent": 0.2,
                        "servicer": "CNTRL"
                    },
                    {
                        "percent": 0.1,
                        "servicer": "MNSRC"
                    },
                    {
                        "percent": 0.09,
                        "servicer": "COLNL"
                    },
                    {
                        "percent": 0.08,
                        "servicer": "HFAGY"
                    }
                ],
                "nonWeightedOriginalLoanSize": 0.0,
                "original3rdPartyOrigination": 0.0,
                "percentHARPDec2010Extension": 0.0,
                "percentHARPOneYearExtension": 0.0,
                "percentDownPaymentAssistance": 5.6,
                "percentAmortizedFHALTVUnder78": 95.4,
                "loanPerformanceImpliedCurrentLTV": 46.2,
                "reperformerMonthsForReperformers": 28
            },
            "ticker": "GNMA",
            "country": "US",
            "currency": "USD",
            "identifier": "999818YT",
            "description": "30-YR GNMA-2013 PROD",
            "issuerTicker": "GNMA",
            "maturityDate": "2041-12-01",
            "securityType": "MORT",
            "currentCoupon": 3.5,
            "securitySubType": "MPGNMA"
        },
        "meta": {
            "status": "DONE",
            "requestId": "R-1475068",
            "timeStamp": "2025-03-06T21:54:31Z",
            "responseType": "BOND_INDIC"
        }
    }


    >>> # Request bond indic with async get
    >>> response = request_bond_indic_async_get(
    >>>                                     id="999818YT",
    >>>                                     id_type=IdTypeEnum.CUSIP
    >>>                                     )
    >>>
    >>> # Get results by request_id
    >>> results_response = get_result(request_id_parameter=response.request_id)
    >>>
    >>> # Due to async nature, code Will perform the fetch 10 times, as result is not always ready instantly, with 3 second lapse between attempts
    >>> attempt = 1
    >>>
    >>> if not results_response:
    >>>     while attempt < 10:
    >>>         print(f"Attempt " + str(attempt) + " resulted in error retrieving results from:" + response.request_id)
    >>>
    >>>         time.sleep(10)
    >>>
    >>>         results_response = get_result(request_id_parameter=response.request_id)
    >>>
    >>>         if not results_response:
    >>>             attempt += 1
    >>>         else:
    >>>             break
    >>>
    >>> # Print results in json format
    >>> print(js.dumps(results_response, indent=4))
    {
        "data": {
            "cusip": "999818YT8",
            "indic": {
                "ltv": 90.0,
                "wam": 201,
                "figi": "BBG0033WXBV4",
                "cusip": "999818YT8",
                "moody": [
                    {
                        "value": "Aaa"
                    }
                ],
                "source": "CITI",
                "ticker": "GNMA",
                "country": "US",
                "loanAge": 142,
                "lockout": 0,
                "putFlag": false,
                "callFlag": false,
                "cobsCode": "MTGE",
                "country2": "US",
                "country3": "USA",
                "currency": "USD",
                "dayCount": "30/360 eom",
                "glicCode": "MBS",
                "grossWAC": 4.0,
                "ioPeriod": 0,
                "poolCode": "NA",
                "sinkFlag": false,
                "cmaTicker": "N/A",
                "datedDate": "2013-05-01",
                "gnma2Flag": false,
                "percentVA": 10.98,
                "currentLTV": 28.7,
                "extendFlag": "N",
                "isoCountry": "US",
                "marketType": "DOMC",
                "percentDTI": 33.9,
                "percentFHA": 81.06,
                "percentInv": 0.0,
                "percentPIH": 0.14,
                "percentRHS": 7.81,
                "securityID": "999818YT",
                "serviceFee": 0.5,
                "vPointType": "MPGNMA",
                "adjustedLTV": 28.7,
                "combinedLTV": 90.6,
                "creditScore": 692,
                "description": "30-YR GNMA-2013 PROD",
                "esgBondFlag": false,
                "indexRating": "AA+",
                "issueAmount": 8597.24,
                "lowerRating": "AA+",
                "paymentFreq": 12,
                "percentHARP": 0.0,
                "percentRefi": 64.0,
                "tierCapital": "NA",
                "balloonMonth": 0,
                "deliveryFlag": "N",
                "indexCountry": "US",
                "industryCode": "MT",
                "issuerTicker": "GNMA",
                "lowestRating": "AA+",
                "maturityDate": "2041-12-01",
                "middleRating": "AA+",
                "modifiedDate": "2025-02-13",
                "originalTerm": 360,
                "parentTicker": "GNMA",
                "percentHARP2": 0.0,
                "percentJumbo": 0.0,
                "securityType": "MORT",
                "currentCoupon": 3.5,
                "dataStateList": [
                    {
                        "state": "PR",
                        "percent": 16.9
                    },
                    {
                        "state": "TX",
                        "percent": 10.11
                    },
                    {
                        "state": "FL",
                        "percent": 5.71
                    },
                    {
                        "state": "CA",
                        "percent": 4.87
                    },
                    {
                        "state": "OH",
                        "percent": 4.82
                    },
                    {
                        "state": "NY",
                        "percent": 4.78
                    },
                    {
                        "state": "GA",
                        "percent": 4.43
                    },
                    {
                        "state": "PA",
                        "percent": 3.35
                    },
                    {
                        "state": "MI",
                        "percent": 3.1
                    },
                    {
                        "state": "NC",
                        "percent": 2.72
                    },
                    {
                        "state": "VA",
                        "percent": 2.69
                    },
                    {
                        "state": "IL",
                        "percent": 2.67
                    },
                    {
                        "state": "IN",
                        "percent": 2.41
                    },
                    {
                        "state": "NJ",
                        "percent": 2.4
                    },
                    {
                        "state": "MD",
                        "percent": 2.26
                    },
                    {
                        "state": "MO",
                        "percent": 2.09
                    },
                    {
                        "state": "AZ",
                        "percent": 1.73
                    },
                    {
                        "state": "TN",
                        "percent": 1.69
                    },
                    {
                        "state": "WA",
                        "percent": 1.5
                    },
                    {
                        "state": "AL",
                        "percent": 1.48
                    },
                    {
                        "state": "OK",
                        "percent": 1.24
                    },
                    {
                        "state": "LA",
                        "percent": 1.2
                    },
                    {
                        "state": "MN",
                        "percent": 1.19
                    },
                    {
                        "state": "SC",
                        "percent": 1.12
                    },
                    {
                        "state": "CT",
                        "percent": 1.07
                    },
                    {
                        "state": "CO",
                        "percent": 1.04
                    },
                    {
                        "state": "KY",
                        "percent": 1.02
                    },
                    {
                        "state": "WI",
                        "percent": 1.01
                    },
                    {
                        "state": "MS",
                        "percent": 0.95
                    },
                    {
                        "state": "NM",
                        "percent": 0.94
                    },
                    {
                        "state": "OR",
                        "percent": 0.89
                    },
                    {
                        "state": "AR",
                        "percent": 0.75
                    },
                    {
                        "state": "NV",
                        "percent": 0.69
                    },
                    {
                        "state": "MA",
                        "percent": 0.67
                    },
                    {
                        "state": "IA",
                        "percent": 0.64
                    },
                    {
                        "state": "KS",
                        "percent": 0.6
                    },
                    {
                        "state": "UT",
                        "percent": 0.59
                    },
                    {
                        "state": "DE",
                        "percent": 0.44
                    },
                    {
                        "state": "ID",
                        "percent": 0.39
                    },
                    {
                        "state": "NE",
                        "percent": 0.39
                    },
                    {
                        "state": "WV",
                        "percent": 0.28
                    },
                    {
                        "state": "ME",
                        "percent": 0.2
                    },
                    {
                        "state": "NH",
                        "percent": 0.16
                    },
                    {
                        "state": "HI",
                        "percent": 0.15
                    },
                    {
                        "state": "MT",
                        "percent": 0.13
                    },
                    {
                        "state": "AK",
                        "percent": 0.12
                    },
                    {
                        "state": "RI",
                        "percent": 0.12
                    },
                    {
                        "state": "WY",
                        "percent": 0.1
                    },
                    {
                        "state": "SD",
                        "percent": 0.07
                    },
                    {
                        "state": "VT",
                        "percent": 0.06
                    },
                    {
                        "state": "DC",
                        "percent": 0.05
                    },
                    {
                        "state": "ND",
                        "percent": 0.04
                    }
                ],
                "delinquencies": {
                    "del30Days": {
                        "percent": 2.12
                    },
                    "del60Days": {
                        "percent": 0.61
                    },
                    "del90Days": {
                        "percent": 0.15
                    },
                    "del90PlusDays": {
                        "percent": 0.73
                    },
                    "del120PlusDays": {
                        "percent": 0.58
                    }
                },
                "greenBondFlag": false,
                "highestRating": "AAA",
                "incomeCountry": "US",
                "issuerCountry": "US",
                "percentSecond": 0.0,
                "poolAgeMethod": "Calculated",
                "prepayEffDate": "2025-01-01",
                "seniorityType": "NA",
                "assetClassCode": "CO",
                "cgmiSectorCode": "MTGE",
                "collateralType": "GNMA",
                "fullPledgeFlag": false,
                "gpmPercentStep": 0.0,
                "incomeCountry3": "USA",
                "instrumentType": "NA",
                "issuerCountry2": "US",
                "issuerCountry3": "USA",
                "lowestRatingNF": "AA+",
                "poolIssuerName": "NA",
                "vPointCategory": "RP",
                "amortizedFHALTV": 63.9,
                "bloombergTicker": "GNSF 3.5 2013",
                "industrySubCode": "MT",
                "originationDate": "2013-05-01",
                "originationYear": 2013,
                "percent2To4Unit": 2.7,
                "percentHAMPMods": 0.9,
                "percentPurchase": 31.7,
                "percentStateHFA": 0.5,
                "poolOriginalWAM": 0,
                "preliminaryFlag": false,
                "redemptionValue": 100.0,
                "securitySubType": "MPGNMA",
                "dataQuartileList": [
                    {
                        "ltvlow": 17.0,
                        "ltvhigh": 87.0,
                        "loanSizeLow": 22000.0,
                        "loanSizeHigh": 101000.0,
                        "percentDTILow": 10.0,
                        "creditScoreLow": 300.0,
                        "percentDTIHigh": 24.4,
                        "creditScoreHigh": 655.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20101101,
                        "originalLoanAgeHigh": 0,
                        "originationYearHigh": 20130401
                    },
                    {
                        "ltvlow": 87.0,
                        "ltvhigh": 93.0,
                        "loanSizeLow": 101000.0,
                        "loanSizeHigh": 132000.0,
                        "percentDTILow": 24.4,
                        "creditScoreLow": 655.0,
                        "percentDTIHigh": 34.9,
                        "creditScoreHigh": 691.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20130401,
                        "originalLoanAgeHigh": 0,
                        "originationYearHigh": 20130501
                    },
                    {
                        "ltvlow": 93.0,
                        "ltvhigh": 97.0,
                        "loanSizeLow": 132000.0,
                        "loanSizeHigh": 183000.0,
                        "percentDTILow": 34.9,
                        "creditScoreLow": 691.0,
                        "percentDTIHigh": 43.5,
                        "creditScoreHigh": 739.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20130501,
                        "originalLoanAgeHigh": 1,
                        "originationYearHigh": 20130701
                    },
                    {
                        "ltvlow": 97.0,
                        "ltvhigh": 118.0,
                        "loanSizeLow": 183000.0,
                        "loanSizeHigh": 743000.0,
                        "percentDTILow": 43.5,
                        "creditScoreLow": 739.0,
                        "percentDTIHigh": 65.0,
                        "creditScoreHigh": 832.0,
                        "originalLoanAgeLow": 1,
                        "originationYearLow": 20130701,
                        "originalLoanAgeHigh": 43,
                        "originationYearHigh": 20141101
                    }
                ],
                "gpmNumberOfSteps": 0,
                "percentHARPOwner": 0.0,
                "percentPrincipal": 100.0,
                "securityCalcType": "GNMA",
                "assetClassSubCode": "MBS",
                "forbearanceAmount": 0.0,
                "modifiedTimeStamp": "2025-02-13T20:06:00Z",
                "outstandingAmount": 1139.67,
                "parentDescription": "NA",
                "poolIsBalloonFlag": false,
                "prepaymentOptions": {
                    "prepayType": [
                        "CPR",
                        "PSA",
                        "VEC"
                    ]
                },
                "reperformerMonths": 1,
                "dataPPMHistoryList": [
                    {
                        "prepayType": "PSA",
                        "dataPPMHistoryDetailList": [
                            {
                                "month": "1",
                                "prepayRate": 106.2137
                            },
                            {
                                "month": "3",
                                "prepayRate": 106.9769
                            },
                            {
                                "month": "6",
                                "prepayRate": 103.0327
                            },
                            {
                                "month": "12",
                                "prepayRate": 100.201
                            },
                            {
                                "month": "24",
                                "prepayRate": 0.0
                            }
                        ]
                    },
                    {
                        "prepayType": "CPR",
                        "dataPPMHistoryDetailList": [
                            {
                                "month": "1",
                                "prepayRate": 6.3728
                            },
                            {
                                "month": "3",
                                "prepayRate": 6.4186
                            },
                            {
                                "month": "6",
                                "prepayRate": 6.182
                            },
                            {
                                "month": "12",
                                "prepayRate": 6.0121
                            },
                            {
                                "month": "24",
                                "prepayRate": 0.0
                            }
                        ]
                    }
                ],
                "daysToFirstPayment": 44,
                "issuerLowestRating": "NA",
                "issuerMiddleRating": "NA",
                "newCurrentLoanSize": 104140.0,
                "originationChannel": {
                    "broker": 4.62,
                    "retail": 62.12,
                    "unknown": 0.0,
                    "unspecified": 0.0,
                    "correspondence": 33.24
                },
                "percentMultiFamily": 2.7,
                "percentRefiCashout": 5.8,
                "percentRegularMods": 3.5,
                "percentReperformer": 0.5,
                "relocationLoanFlag": false,
                "socialDensityScore": 0.0,
                "umbsfhlgPercentage": 0.0,
                "umbsfnmaPercentage": 0.0,
                "industryDescription": "Mortgage",
                "issuerHighestRating": "NA",
                "newOriginalLoanSize": 182010.0,
                "socialCriteriaShare": 0.0,
                "spreadAtOrigination": 22.4,
                "weightedAvgLoanSize": 104140.0,
                "poolOriginalLoanSize": 182010.0,
                "cgmiSectorDescription": "Mortgage",
                "expModelAvailableFlag": true,
                "fhfaImpliedCurrentLTV": 28.7,
                "percentRefiNonCashout": 58.2,
                "prepayPenaltySchedule": "0.000",
                "defaultHorizonPYMethod": "OAS Change",
                "industrySubDescription": "Mortgage Asset Backed",
                "actualPrepayHistoryList": {
                    "date": "2025-04-01",
                    "genericValue": 0.7907
                },
                "adjustedCurrentLoanSize": 104140.0,
                "forbearanceModification": 0.0,
                "percentTwoPlusBorrowers": 44.1,
                "poolAvgOriginalLoanTerm": 0,
                "adjustedOriginalLoanSize": 181999.0,
                "assetClassSubDescription": "Collateralized Asset Backed - Mortgage",
                "mortgageInsurancePremium": {
                    "annual": {
                        "va": 0.0,
                        "fha": 0.793,
                        "pih": 0.0,
                        "rhs": 0.399
                    },
                    "upfront": {
                        "va": 0.5,
                        "fha": 0.689,
                        "pih": 1.0,
                        "rhs": 1.996
                    }
                },
                "percentReperformerAndMod": 0.1,
                "reperformerMonthsForMods": 2,
                "dataPrepayModelSellerList": [
                    {
                        "seller": "HFAL",
                        "percent": 0.08
                    },
                    {
                        "seller": "HFUSM",
                        "percent": 0.06
                    },
                    {
                        "seller": "HFWA",
                        "percent": 0.02
                    }
                ],
                "originalLoanSizeRemaining": 150707.0,
                "percentFirstTimeHomeBuyer": 20.7,
                "current3rdPartyOrigination": 37.87,
                "adjustedSpreadAtOrigination": 22.4,
                "dataPrepayModelServicerList": [
                    {
                        "percent": 27.08,
                        "servicer": "WELLS"
                    },
                    {
                        "percent": 10.98,
                        "servicer": "BCPOP"
                    },
                    {
                        "percent": 7.57,
                        "servicer": "NSTAR"
                    },
                    {
                        "percent": 7.31,
                        "servicer": "QUICK"
                    },
                    {
                        "percent": 7.14,
                        "servicer": "PENNY"
                    },
                    {
                        "percent": 6.22,
                        "servicer": "CARRG"
                    },
                    {
                        "percent": 5.99,
                        "servicer": "LAKEV"
                    },
                    {
                        "percent": 5.5,
                        "servicer": "USB"
                    },
                    {
                        "percent": 4.24,
                        "servicer": "FREE"
                    },
                    {
                        "percent": 2.4,
                        "servicer": "PNC"
                    },
                    {
                        "percent": 1.33,
                        "servicer": "MNTBK"
                    },
                    {
                        "percent": 1.19,
                        "servicer": "NWRES"
                    },
                    {
                        "percent": 0.95,
                        "servicer": "FIFTH"
                    },
                    {
                        "percent": 0.77,
                        "servicer": "DEPOT"
                    },
                    {
                        "percent": 0.62,
                        "servicer": "HOMBR"
                    },
                    {
                        "percent": 0.59,
                        "servicer": "BOKF"
                    },
                    {
                        "percent": 0.52,
                        "servicer": "JPM"
                    },
                    {
                        "percent": 0.48,
                        "servicer": "TRUIS"
                    },
                    {
                        "percent": 0.42,
                        "servicer": "CITI"
                    },
                    {
                        "percent": 0.37,
                        "servicer": "GUILD"
                    },
                    {
                        "percent": 0.21,
                        "servicer": "REGNS"
                    },
                    {
                        "percent": 0.2,
                        "servicer": "CNTRL"
                    },
                    {
                        "percent": 0.1,
                        "servicer": "MNSRC"
                    },
                    {
                        "percent": 0.09,
                        "servicer": "COLNL"
                    },
                    {
                        "percent": 0.08,
                        "servicer": "HFAGY"
                    }
                ],
                "nonWeightedOriginalLoanSize": 0.0,
                "original3rdPartyOrigination": 0.0,
                "percentHARPDec2010Extension": 0.0,
                "percentHARPOneYearExtension": 0.0,
                "percentDownPaymentAssistance": 5.6,
                "percentAmortizedFHALTVUnder78": 95.4,
                "loanPerformanceImpliedCurrentLTV": 46.2,
                "reperformerMonthsForReperformers": 28
            },
            "ticker": "GNMA",
            "country": "US",
            "currency": "USD",
            "identifier": "999818YT",
            "description": "30-YR GNMA-2013 PROD",
            "issuerTicker": "GNMA",
            "maturityDate": "2041-12-01",
            "securityType": "MORT",
            "currentCoupon": 3.5,
            "securitySubType": "MPGNMA"
        },
        "meta": {
            "status": "DONE",
            "requestId": "R-1475069",
            "timeStamp": "2025-03-06T21:54:32Z",
            "responseType": "BOND_INDIC"
        }
    }

    """

    try:
        logger.info("Calling request_bond_indic_async_get")

        response = check_and_raise(
            Client().yield_book_rest.request_bond_indic_async_get(
                id=id,
                id_type=id_type,
                keywords=keywords,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called request_bond_indic_async_get")

        return output
    except Exception as err:
        logger.error(f"Error request_bond_indic_async_get. {err}")
        check_exception_and_raise(err)


def request_bond_indic_sync(
    *,
    input: Optional[List[IdentifierInfo]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> MappedResponseRefData:
    """
    Synchronous Post method to retrieve the contractual information about the reference data of instruments, which will typically not need any further calculations. Retrieve instrument reference data given a BondIndicRequest - 'Input' - parameter that includes the information of which security or list of securities to be queried by CUSIP, ISIN, or other identifier type to obtain basic contractual information in the MappedResponseRefData such as security type, sector,  maturity, credit ratings, coupon, and specific information based on security type like current pool factor if the requested identifier is a mortgage. Recommended and preferred method for single or low-volume instrument queries (up to 50-70 per request, 250 max).

    Parameters
    ----------
    input : List[IdentifierInfo], optional
        Single identifier or a list of identifiers to search instruments by.
    keywords : List[str], optional
        List of keywords from the MappedResponseRefData to be exposed in the result data set.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    MappedResponseRefData
        Bond indicative response data from the server. It returns a generic container of data contaning a combined dataset of all available instrument types, with only dedicated data filled out. For more information check 'Results' model documentation.

    Examples
    --------
    >>> # Request bond indic with sync post
    >>> response = request_bond_indic_sync(input=[IdentifierInfo(identifier="999818YT")])
    >>>
    >>> # Print results
    >>> print(response)
    {'meta': {'status': 'DONE', 'requestId': 'R-1588912', 'timeStamp': '2025-06-27T05:41:06Z', 'responseType': 'BOND_INDIC', 'resultsStatus': 'ALL'}, 'results': [{'cusip': '999818YT8', 'indic': {'ltv': 90.0, 'wam': 198, 'figi': 'BBG0033WXBV4', 'cusip': '999818YT8', 'moody': [{'value': 'Aaa'}], 'source': 'CITI', 'ticker': 'GNMA', 'country': 'US', 'loanAge': 145, 'lockout': 0, 'putFlag': False, 'callFlag': False, 'cobsCode': 'MTGE', 'country2': 'US', 'country3': 'USA', 'currency': 'USD', 'dayCount': '30/360 eom', 'glicCode': 'MBS', 'grossWAC': 4.0, 'ioPeriod': 0, 'poolCode': 'NA', 'sinkFlag': False, 'cmaTicker': 'N/A', 'datedDate': '2013-05-01', 'gnma2Flag': False, 'percentVA': 11.03, 'currentLTV': 27.9, 'extendFlag': 'N', 'isoCountry': 'US', 'marketType': 'DOMC', 'percentDTI': 34.0, 'percentFHA': 80.96, 'percentInv': 0.0, 'percentPIH': 0.14, 'percentRHS': 7.87, 'securityID': '999818YT', 'serviceFee': 0.5, 'vPointType': 'MPGNMA', 'adjustedLTV': 27.9, 'combinedLTV': 90.7, 'creditScore': 692, 'description': '30-YR GNMA-2013 PROD', 'esgBondFlag': False, 'indexRating': 'AA+', 'issueAmount': 8597.24, 'lowerRating': 'AA+', 'paymentFreq': 12, 'percentHARP': 0.0, 'percentRefi': 63.8, 'tierCapital': 'NA', 'balloonMonth': 0, 'deliveryFlag': 'N', 'indexCountry': 'US', 'industryCode': 'MT', 'issuerTicker': 'GNMA', 'lowestRating': 'AA+', 'maturityDate': '2041-12-01', 'middleRating': 'AA+', 'modifiedDate': '2025-06-12', 'originalTerm': 360, 'parentTicker': 'GNMA', 'percentHARP2': 0.0, 'percentJumbo': 0.0, 'securityType': 'MORT', 'currentCoupon': 3.5, 'dataStateList': [{'state': 'PR', 'percent': 17.05}, {'state': 'TX', 'percent': 10.11}, {'state': 'FL', 'percent': 5.67}, {'state': 'CA', 'percent': 4.91}, {'state': 'OH', 'percent': 4.83}, {'state': 'NY', 'percent': 4.78}, {'state': 'GA', 'percent': 4.4}, {'state': 'PA', 'percent': 3.37}, {'state': 'MI', 'percent': 3.1}, {'state': 'NC', 'percent': 2.73}, {'state': 'IL', 'percent': 2.68}, {'state': 'VA', 'percent': 2.67}, {'state': 'NJ', 'percent': 2.39}, {'state': 'IN', 'percent': 2.37}, {'state': 'MD', 'percent': 2.26}, {'state': 'MO', 'percent': 2.1}, {'state': 'AZ', 'percent': 1.73}, {'state': 'TN', 'percent': 1.67}, {'state': 'AL', 'percent': 1.47}, {'state': 'WA', 'percent': 1.47}, {'state': 'OK', 'percent': 1.22}, {'state': 'LA', 'percent': 1.21}, {'state': 'MN', 'percent': 1.19}, {'state': 'SC', 'percent': 1.11}, {'state': 'CT', 'percent': 1.08}, {'state': 'KY', 'percent': 1.04}, {'state': 'CO', 'percent': 1.03}, {'state': 'WI', 'percent': 1.0}, {'state': 'MS', 'percent': 0.96}, {'state': 'NM', 'percent': 0.95}, {'state': 'OR', 'percent': 0.89}, {'state': 'AR', 'percent': 0.75}, {'state': 'NV', 'percent': 0.7}, {'state': 'MA', 'percent': 0.68}, {'state': 'IA', 'percent': 0.61}, {'state': 'KS', 'percent': 0.59}, {'state': 'UT', 'percent': 0.59}, {'state': 'DE', 'percent': 0.44}, {'state': 'ID', 'percent': 0.39}, {'state': 'NE', 'percent': 0.39}, {'state': 'WV', 'percent': 0.28}, {'state': 'ME', 'percent': 0.19}, {'state': 'NH', 'percent': 0.16}, {'state': 'HI', 'percent': 0.15}, {'state': 'MT', 'percent': 0.13}, {'state': 'AK', 'percent': 0.12}, {'state': 'RI', 'percent': 0.12}, {'state': 'WY', 'percent': 0.08}, {'state': 'SD', 'percent': 0.07}, {'state': 'VT', 'percent': 0.06}, {'state': 'DC', 'percent': 0.04}, {'state': 'ND', 'percent': 0.04}], 'delinquencies': {'del30Days': {'percent': 2.3}, 'del60Days': {'percent': 0.54}, 'del90Days': {'percent': 0.2}, 'del90PlusDays': {'percent': 0.61}, 'del120PlusDays': {'percent': 0.41}}, 'greenBondFlag': False, 'highestRating': 'AAA', 'incomeCountry': 'US', 'issuerCountry': 'US', 'percentSecond': 0.0, 'poolAgeMethod': 'Calculated', 'prepayEffDate': '2025-05-01', 'seniorityType': 'NA', 'assetClassCode': 'CO', 'cgmiSectorCode': 'MTGE', 'collateralType': 'GNMA', 'fullPledgeFlag': False, 'gpmPercentStep': 0.0, 'incomeCountry3': 'USA', 'instrumentType': 'NA', 'issuerCountry2': 'US', 'issuerCountry3': 'USA', 'lowestRatingNF': 'AA+', 'poolIssuerName': 'NA', 'vPointCategory': 'RP', 'amortizedFHALTV': 63.2, 'bloombergTicker': 'GNSF 3.5 2013', 'industrySubCode': 'MT', 'originationDate': '2013-05-01', 'originationYear': 2013, 'percent2To4Unit': 2.7, 'percentHAMPMods': 0.9, 'percentPurchase': 31.8, 'percentStateHFA': 0.4, 'poolOriginalWAM': 0, 'preliminaryFlag': False, 'redemptionValue': 100.0, 'securitySubType': 'MPGNMA', 'dataQuartileList': [{'ltvlow': 17.0, 'ltvhigh': 87.0, 'loanSizeLow': 22000.0, 'loanSizeHigh': 101000.0, 'percentDTILow': 10.0, 'creditScoreLow': 300.0, 'percentDTIHigh': 24.4, 'creditScoreHigh': 656.0, 'originalLoanAgeLow': 0, 'originationYearLow': 20101101, 'originalLoanAgeHigh': 0, 'originationYearHigh': 20130401}, {'ltvlow': 87.0, 'ltvhigh': 93.0, 'loanSizeLow': 101000.0, 'loanSizeHigh': 132000.0, 'percentDTILow': 24.4, 'creditScoreLow': 656.0, 'percentDTIHigh': 34.9, 'creditScoreHigh': 691.0, 'originalLoanAgeLow': 0, 'originationYearLow': 20130401, 'originalLoanAgeHigh': 0, 'originationYearHigh': 20130501}, {'ltvlow': 93.0, 'ltvhigh': 97.0, 'loanSizeLow': 132000.0, 'loanSizeHigh': 183000.0, 'percentDTILow': 34.9, 'creditScoreLow': 691.0, 'percentDTIHigh': 43.6, 'creditScoreHigh': 739.0, 'originalLoanAgeLow': 0, 'originationYearLow': 20130501, 'originalLoanAgeHigh': 1, 'originationYearHigh': 20130701}, {'ltvlow': 97.0, 'ltvhigh': 118.0, 'loanSizeLow': 183000.0, 'loanSizeHigh': 743000.0, 'percentDTILow': 43.6, 'creditScoreLow': 739.0, 'percentDTIHigh': 65.0, 'creditScoreHigh': 832.0, 'originalLoanAgeLow': 1, 'originationYearLow': 20130701, 'originalLoanAgeHigh': 43, 'originationYearHigh': 20141101}], 'gpmNumberOfSteps': 0, 'percentHARPOwner': 0.0, 'percentPrincipal': 100.0, 'securityCalcType': 'GNMA', 'assetClassSubCode': 'MBS', 'forbearanceAmount': 0.0, 'modifiedTimeStamp': '2025-06-12T19:10:00Z', 'outstandingAmount': 1100.37, 'parentDescription': 'NA', 'poolIsBalloonFlag': False, 'prepaymentOptions': {'prepayType': ['CPR', 'PSA', 'VEC']}, 'reperformerMonths': 1, 'dataPPMHistoryList': [{'prepayType': 'PSA', 'dataPPMHistoryDetailList': [{'month': '1', 'prepayRate': 104.2558}, {'month': '3', 'prepayRate': 101.9675}, {'month': '6', 'prepayRate': 101.3512}, {'month': '12', 'prepayRate': 101.4048}, {'month': '24', 'prepayRate': 0.0}]}, {'prepayType': 'CPR', 'dataPPMHistoryDetailList': [{'month': '1', 'prepayRate': 6.2554}, {'month': '3', 'prepayRate': 6.118}, {'month': '6', 'prepayRate': 6.0811}, {'month': '12', 'prepayRate': 6.0843}, {'month': '24', 'prepayRate': 0.0}]}], 'daysToFirstPayment': 44, 'issuerLowestRating': 'NA', 'issuerMiddleRating': 'NA', 'newCurrentLoanSize': 102609.0, 'originationChannel': {'broker': 4.64, 'retail': 62.02, 'unknown': 0.0, 'unspecified': 0.0, 'correspondence': 33.31}, 'percentMultiFamily': 2.7, 'percentRefiCashout': 5.8, 'percentRegularMods': 3.5, 'percentReperformer': 0.5, 'relocationLoanFlag': False, 'socialDensityScore': 0.0, 'umbsfhlgPercentage': 0.0, 'umbsfnmaPercentage': 0.0, 'industryDescription': 'Mortgage', 'issuerHighestRating': 'NA', 'newOriginalLoanSize': 182013.0, 'socialCriteriaShare': 0.0, 'spreadAtOrigination': 22.3, 'weightedAvgLoanSize': 102609.0, 'poolOriginalLoanSize': 182013.0, 'cgmiSectorDescription': 'Mortgage', 'expModelAvailableFlag': True, 'fhfaImpliedCurrentLTV': 27.9, 'newModelAvailableFlag': True, 'percentRefiNonCashout': 58.0, 'prepayPenaltySchedule': '0.000', 'defaultHorizonPYMethod': 'OAS Change', 'industrySubDescription': 'Mortgage Asset Backed', 'actualPrepayHistoryList': {'date': '2025-08-01', 'genericValue': 0.8659}, 'adjustedCurrentLoanSize': 102609.0, 'forbearanceModification': 0.0, 'percentTwoPlusBorrowers': 44.0, 'poolAvgOriginalLoanTerm': 0, 'adjustedOriginalLoanSize': 182003.0, 'assetClassSubDescription': 'Collateralized Asset Backed - Mortgage', 'mortgageInsurancePremium': {'annual': {'va': 0.0, 'fha': 0.797, 'pih': 0.0, 'rhs': 0.399}, 'upfront': {'va': 0.5, 'fha': 0.691, 'pih': 1.0, 'rhs': 1.996}}, 'percentReperformerAndMod': 0.1, 'reperformerMonthsForMods': 2, 'dataPrepayModelSellerList': [{'seller': 'HFUSM', 'percent': 0.07}, {'seller': 'HFAL', 'percent': 0.06}, {'seller': 'HFWA', 'percent': 0.02}], 'originalLoanSizeRemaining': 150810.0, 'percentFirstTimeHomeBuyer': 20.8, 'current3rdPartyOrigination': 37.96, 'adjustedSpreadAtOrigination': 22.3, 'dataPrepayModelServicerList': [{'percent': 23.28, 'servicer': 'WELLS'}, {'percent': 11.33, 'servicer': 'NSTAR'}, {'percent': 11.1, 'servicer': 'BCPOP'}, {'percent': 7.26, 'servicer': 'QUICK'}, {'percent': 7.1, 'servicer': 'PENNY'}, {'percent': 6.56, 'servicer': 'LAKEV'}, {'percent': 6.33, 'servicer': 'CARRG'}, {'percent': 5.5, 'servicer': 'USB'}, {'percent': 4.27, 'servicer': 'FREE'}, {'percent': 2.41, 'servicer': 'PNC'}, {'percent': 1.33, 'servicer': 'MNTBK'}, {'percent': 1.18, 'servicer': 'NWRES'}, {'percent': 0.96, 'servicer': 'FIFTH'}, {'percent': 0.75, 'servicer': 'DEPOT'}, {'percent': 0.6, 'servicer': 'BOKF'}, {'percent': 0.5, 'servicer': 'JPM'}, {'percent': 0.47, 'servicer': 'TRUIS'}, {'percent': 0.42, 'servicer': 'CITI'}, {'percent': 0.38, 'servicer': 'GUILD'}, {'percent': 0.21, 'servicer': 'REGNS'}, {'percent': 0.2, 'servicer': 'CNTRL'}, {'percent': 0.09, 'servicer': 'COLNL'}, {'percent': 0.09, 'servicer': 'MNSRC'}, {'percent': 0.06, 'servicer': 'HFAGY'}, {'percent': 0.03, 'servicer': 'HOMBR'}], 'nonWeightedOriginalLoanSize': 0.0, 'original3rdPartyOrigination': 0.0, 'percentHARPDec2010Extension': 0.0, 'percentHARPOneYearExtension': 0.0, 'percentDownPaymentAssistance': 5.6, 'percentAmortizedFHALTVUnder78': 95.4, 'loanPerformanceImpliedCurrentLTV': 45.1, 'reperformerMonthsForReperformers': 28}, 'ticker': 'GNMA', 'country': 'US', 'currency': 'USD', 'identifier': '999818YT', 'description': '30-YR GNMA-2013 PROD', 'issuerTicker': 'GNMA', 'maturityDate': '2041-12-01', 'securityType': 'MORT', 'currentCoupon': 3.5, 'securitySubType': 'MPGNMA'}]}


    >>> # Request bond indic with sync post
    >>> response = request_bond_indic_sync(input=[IdentifierInfo(identifier="999818YT",
    >>>                                                          id_type="CUSIP",
    >>>                                                          )])
    >>>
    >>> # Print results
    >>> print(response)
    {'meta': {'status': 'DONE', 'requestId': 'R-1588913', 'timeStamp': '2025-06-27T05:41:07Z', 'responseType': 'BOND_INDIC', 'resultsStatus': 'ALL'}, 'results': [{'cusip': '999818YT8', 'indic': {'ltv': 90.0, 'wam': 198, 'figi': 'BBG0033WXBV4', 'cusip': '999818YT8', 'moody': [{'value': 'Aaa'}], 'source': 'CITI', 'ticker': 'GNMA', 'country': 'US', 'loanAge': 145, 'lockout': 0, 'putFlag': False, 'callFlag': False, 'cobsCode': 'MTGE', 'country2': 'US', 'country3': 'USA', 'currency': 'USD', 'dayCount': '30/360 eom', 'glicCode': 'MBS', 'grossWAC': 4.0, 'ioPeriod': 0, 'poolCode': 'NA', 'sinkFlag': False, 'cmaTicker': 'N/A', 'datedDate': '2013-05-01', 'gnma2Flag': False, 'percentVA': 11.03, 'currentLTV': 27.9, 'extendFlag': 'N', 'isoCountry': 'US', 'marketType': 'DOMC', 'percentDTI': 34.0, 'percentFHA': 80.96, 'percentInv': 0.0, 'percentPIH': 0.14, 'percentRHS': 7.87, 'securityID': '999818YT', 'serviceFee': 0.5, 'vPointType': 'MPGNMA', 'adjustedLTV': 27.9, 'combinedLTV': 90.7, 'creditScore': 692, 'description': '30-YR GNMA-2013 PROD', 'esgBondFlag': False, 'indexRating': 'AA+', 'issueAmount': 8597.24, 'lowerRating': 'AA+', 'paymentFreq': 12, 'percentHARP': 0.0, 'percentRefi': 63.8, 'tierCapital': 'NA', 'balloonMonth': 0, 'deliveryFlag': 'N', 'indexCountry': 'US', 'industryCode': 'MT', 'issuerTicker': 'GNMA', 'lowestRating': 'AA+', 'maturityDate': '2041-12-01', 'middleRating': 'AA+', 'modifiedDate': '2025-06-12', 'originalTerm': 360, 'parentTicker': 'GNMA', 'percentHARP2': 0.0, 'percentJumbo': 0.0, 'securityType': 'MORT', 'currentCoupon': 3.5, 'dataStateList': [{'state': 'PR', 'percent': 17.05}, {'state': 'TX', 'percent': 10.11}, {'state': 'FL', 'percent': 5.67}, {'state': 'CA', 'percent': 4.91}, {'state': 'OH', 'percent': 4.83}, {'state': 'NY', 'percent': 4.78}, {'state': 'GA', 'percent': 4.4}, {'state': 'PA', 'percent': 3.37}, {'state': 'MI', 'percent': 3.1}, {'state': 'NC', 'percent': 2.73}, {'state': 'IL', 'percent': 2.68}, {'state': 'VA', 'percent': 2.67}, {'state': 'NJ', 'percent': 2.39}, {'state': 'IN', 'percent': 2.37}, {'state': 'MD', 'percent': 2.26}, {'state': 'MO', 'percent': 2.1}, {'state': 'AZ', 'percent': 1.73}, {'state': 'TN', 'percent': 1.67}, {'state': 'AL', 'percent': 1.47}, {'state': 'WA', 'percent': 1.47}, {'state': 'OK', 'percent': 1.22}, {'state': 'LA', 'percent': 1.21}, {'state': 'MN', 'percent': 1.19}, {'state': 'SC', 'percent': 1.11}, {'state': 'CT', 'percent': 1.08}, {'state': 'KY', 'percent': 1.04}, {'state': 'CO', 'percent': 1.03}, {'state': 'WI', 'percent': 1.0}, {'state': 'MS', 'percent': 0.96}, {'state': 'NM', 'percent': 0.95}, {'state': 'OR', 'percent': 0.89}, {'state': 'AR', 'percent': 0.75}, {'state': 'NV', 'percent': 0.7}, {'state': 'MA', 'percent': 0.68}, {'state': 'IA', 'percent': 0.61}, {'state': 'KS', 'percent': 0.59}, {'state': 'UT', 'percent': 0.59}, {'state': 'DE', 'percent': 0.44}, {'state': 'ID', 'percent': 0.39}, {'state': 'NE', 'percent': 0.39}, {'state': 'WV', 'percent': 0.28}, {'state': 'ME', 'percent': 0.19}, {'state': 'NH', 'percent': 0.16}, {'state': 'HI', 'percent': 0.15}, {'state': 'MT', 'percent': 0.13}, {'state': 'AK', 'percent': 0.12}, {'state': 'RI', 'percent': 0.12}, {'state': 'WY', 'percent': 0.08}, {'state': 'SD', 'percent': 0.07}, {'state': 'VT', 'percent': 0.06}, {'state': 'DC', 'percent': 0.04}, {'state': 'ND', 'percent': 0.04}], 'delinquencies': {'del30Days': {'percent': 2.3}, 'del60Days': {'percent': 0.54}, 'del90Days': {'percent': 0.2}, 'del90PlusDays': {'percent': 0.61}, 'del120PlusDays': {'percent': 0.41}}, 'greenBondFlag': False, 'highestRating': 'AAA', 'incomeCountry': 'US', 'issuerCountry': 'US', 'percentSecond': 0.0, 'poolAgeMethod': 'Calculated', 'prepayEffDate': '2025-05-01', 'seniorityType': 'NA', 'assetClassCode': 'CO', 'cgmiSectorCode': 'MTGE', 'collateralType': 'GNMA', 'fullPledgeFlag': False, 'gpmPercentStep': 0.0, 'incomeCountry3': 'USA', 'instrumentType': 'NA', 'issuerCountry2': 'US', 'issuerCountry3': 'USA', 'lowestRatingNF': 'AA+', 'poolIssuerName': 'NA', 'vPointCategory': 'RP', 'amortizedFHALTV': 63.2, 'bloombergTicker': 'GNSF 3.5 2013', 'industrySubCode': 'MT', 'originationDate': '2013-05-01', 'originationYear': 2013, 'percent2To4Unit': 2.7, 'percentHAMPMods': 0.9, 'percentPurchase': 31.8, 'percentStateHFA': 0.4, 'poolOriginalWAM': 0, 'preliminaryFlag': False, 'redemptionValue': 100.0, 'securitySubType': 'MPGNMA', 'dataQuartileList': [{'ltvlow': 17.0, 'ltvhigh': 87.0, 'loanSizeLow': 22000.0, 'loanSizeHigh': 101000.0, 'percentDTILow': 10.0, 'creditScoreLow': 300.0, 'percentDTIHigh': 24.4, 'creditScoreHigh': 656.0, 'originalLoanAgeLow': 0, 'originationYearLow': 20101101, 'originalLoanAgeHigh': 0, 'originationYearHigh': 20130401}, {'ltvlow': 87.0, 'ltvhigh': 93.0, 'loanSizeLow': 101000.0, 'loanSizeHigh': 132000.0, 'percentDTILow': 24.4, 'creditScoreLow': 656.0, 'percentDTIHigh': 34.9, 'creditScoreHigh': 691.0, 'originalLoanAgeLow': 0, 'originationYearLow': 20130401, 'originalLoanAgeHigh': 0, 'originationYearHigh': 20130501}, {'ltvlow': 93.0, 'ltvhigh': 97.0, 'loanSizeLow': 132000.0, 'loanSizeHigh': 183000.0, 'percentDTILow': 34.9, 'creditScoreLow': 691.0, 'percentDTIHigh': 43.6, 'creditScoreHigh': 739.0, 'originalLoanAgeLow': 0, 'originationYearLow': 20130501, 'originalLoanAgeHigh': 1, 'originationYearHigh': 20130701}, {'ltvlow': 97.0, 'ltvhigh': 118.0, 'loanSizeLow': 183000.0, 'loanSizeHigh': 743000.0, 'percentDTILow': 43.6, 'creditScoreLow': 739.0, 'percentDTIHigh': 65.0, 'creditScoreHigh': 832.0, 'originalLoanAgeLow': 1, 'originationYearLow': 20130701, 'originalLoanAgeHigh': 43, 'originationYearHigh': 20141101}], 'gpmNumberOfSteps': 0, 'percentHARPOwner': 0.0, 'percentPrincipal': 100.0, 'securityCalcType': 'GNMA', 'assetClassSubCode': 'MBS', 'forbearanceAmount': 0.0, 'modifiedTimeStamp': '2025-06-12T19:10:00Z', 'outstandingAmount': 1100.37, 'parentDescription': 'NA', 'poolIsBalloonFlag': False, 'prepaymentOptions': {'prepayType': ['CPR', 'PSA', 'VEC']}, 'reperformerMonths': 1, 'dataPPMHistoryList': [{'prepayType': 'PSA', 'dataPPMHistoryDetailList': [{'month': '1', 'prepayRate': 104.2558}, {'month': '3', 'prepayRate': 101.9675}, {'month': '6', 'prepayRate': 101.3512}, {'month': '12', 'prepayRate': 101.4048}, {'month': '24', 'prepayRate': 0.0}]}, {'prepayType': 'CPR', 'dataPPMHistoryDetailList': [{'month': '1', 'prepayRate': 6.2554}, {'month': '3', 'prepayRate': 6.118}, {'month': '6', 'prepayRate': 6.0811}, {'month': '12', 'prepayRate': 6.0843}, {'month': '24', 'prepayRate': 0.0}]}], 'daysToFirstPayment': 44, 'issuerLowestRating': 'NA', 'issuerMiddleRating': 'NA', 'newCurrentLoanSize': 102609.0, 'originationChannel': {'broker': 4.64, 'retail': 62.02, 'unknown': 0.0, 'unspecified': 0.0, 'correspondence': 33.31}, 'percentMultiFamily': 2.7, 'percentRefiCashout': 5.8, 'percentRegularMods': 3.5, 'percentReperformer': 0.5, 'relocationLoanFlag': False, 'socialDensityScore': 0.0, 'umbsfhlgPercentage': 0.0, 'umbsfnmaPercentage': 0.0, 'industryDescription': 'Mortgage', 'issuerHighestRating': 'NA', 'newOriginalLoanSize': 182013.0, 'socialCriteriaShare': 0.0, 'spreadAtOrigination': 22.3, 'weightedAvgLoanSize': 102609.0, 'poolOriginalLoanSize': 182013.0, 'cgmiSectorDescription': 'Mortgage', 'expModelAvailableFlag': True, 'fhfaImpliedCurrentLTV': 27.9, 'newModelAvailableFlag': True, 'percentRefiNonCashout': 58.0, 'prepayPenaltySchedule': '0.000', 'defaultHorizonPYMethod': 'OAS Change', 'industrySubDescription': 'Mortgage Asset Backed', 'actualPrepayHistoryList': {'date': '2025-08-01', 'genericValue': 0.8659}, 'adjustedCurrentLoanSize': 102609.0, 'forbearanceModification': 0.0, 'percentTwoPlusBorrowers': 44.0, 'poolAvgOriginalLoanTerm': 0, 'adjustedOriginalLoanSize': 182003.0, 'assetClassSubDescription': 'Collateralized Asset Backed - Mortgage', 'mortgageInsurancePremium': {'annual': {'va': 0.0, 'fha': 0.797, 'pih': 0.0, 'rhs': 0.399}, 'upfront': {'va': 0.5, 'fha': 0.691, 'pih': 1.0, 'rhs': 1.996}}, 'percentReperformerAndMod': 0.1, 'reperformerMonthsForMods': 2, 'dataPrepayModelSellerList': [{'seller': 'HFUSM', 'percent': 0.07}, {'seller': 'HFAL', 'percent': 0.06}, {'seller': 'HFWA', 'percent': 0.02}], 'originalLoanSizeRemaining': 150810.0, 'percentFirstTimeHomeBuyer': 20.8, 'current3rdPartyOrigination': 37.96, 'adjustedSpreadAtOrigination': 22.3, 'dataPrepayModelServicerList': [{'percent': 23.28, 'servicer': 'WELLS'}, {'percent': 11.33, 'servicer': 'NSTAR'}, {'percent': 11.1, 'servicer': 'BCPOP'}, {'percent': 7.26, 'servicer': 'QUICK'}, {'percent': 7.1, 'servicer': 'PENNY'}, {'percent': 6.56, 'servicer': 'LAKEV'}, {'percent': 6.33, 'servicer': 'CARRG'}, {'percent': 5.5, 'servicer': 'USB'}, {'percent': 4.27, 'servicer': 'FREE'}, {'percent': 2.41, 'servicer': 'PNC'}, {'percent': 1.33, 'servicer': 'MNTBK'}, {'percent': 1.18, 'servicer': 'NWRES'}, {'percent': 0.96, 'servicer': 'FIFTH'}, {'percent': 0.75, 'servicer': 'DEPOT'}, {'percent': 0.6, 'servicer': 'BOKF'}, {'percent': 0.5, 'servicer': 'JPM'}, {'percent': 0.47, 'servicer': 'TRUIS'}, {'percent': 0.42, 'servicer': 'CITI'}, {'percent': 0.38, 'servicer': 'GUILD'}, {'percent': 0.21, 'servicer': 'REGNS'}, {'percent': 0.2, 'servicer': 'CNTRL'}, {'percent': 0.09, 'servicer': 'COLNL'}, {'percent': 0.09, 'servicer': 'MNSRC'}, {'percent': 0.06, 'servicer': 'HFAGY'}, {'percent': 0.03, 'servicer': 'HOMBR'}], 'nonWeightedOriginalLoanSize': 0.0, 'original3rdPartyOrigination': 0.0, 'percentHARPDec2010Extension': 0.0, 'percentHARPOneYearExtension': 0.0, 'percentDownPaymentAssistance': 5.6, 'percentAmortizedFHALTVUnder78': 95.4, 'loanPerformanceImpliedCurrentLTV': 45.1, 'reperformerMonthsForReperformers': 28}, 'ticker': 'GNMA', 'country': 'US', 'currency': 'USD', 'identifier': '999818YT', 'description': '30-YR GNMA-2013 PROD', 'issuerTicker': 'GNMA', 'maturityDate': '2041-12-01', 'securityType': 'MORT', 'currentCoupon': 3.5, 'securitySubType': 'MPGNMA'}]}

    """

    try:
        logger.info("Calling request_bond_indic_sync")

        response = check_and_raise(
            Client().yield_book_rest.request_bond_indic_sync(
                body=BondIndicRequest(input=input, keywords=keywords),
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called request_bond_indic_sync")

        return output
    except Exception as err:
        logger.error(f"Error request_bond_indic_sync. {err}")
        check_exception_and_raise(err)


def request_bond_indic_sync_get(
    *,
    id: str,
    id_type: Optional[Union[str, IdTypeEnum]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Synchronous Get method to retrieve the contractual information about the reference data of an instrument, which will typically not need any further calculations. Retrieve instrument reference data given an instrument ID and optionaly an ID type as input parameters to obtain basic contractual information in the Record structure with information such as security type, sector,  maturity, credit ratings, coupon, and specific information based on security type like current pool factor if the requested identifier is a mortgage.

    Parameters
    ----------
    id : str
        A sequence of textual characters.
    id_type : Union[str, IdTypeEnum], optional

    keywords : List[str], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------
    >>> # Request bond indic with sync get
    >>> response = request_bond_indic_sync_get(id="999818YT")
    >>>
    >>> # Print results in json format
    >>> print(js.dumps(response, indent=4))
    {
        "data": {
            "cusip": "999818YT8",
            "indic": {
                "ltv": 90.0,
                "wam": 198,
                "figi": "BBG0033WXBV4",
                "cusip": "999818YT8",
                "moody": [
                    {
                        "value": "Aaa"
                    }
                ],
                "source": "CITI",
                "ticker": "GNMA",
                "country": "US",
                "loanAge": 145,
                "lockout": 0,
                "putFlag": false,
                "callFlag": false,
                "cobsCode": "MTGE",
                "country2": "US",
                "country3": "USA",
                "currency": "USD",
                "dayCount": "30/360 eom",
                "glicCode": "MBS",
                "grossWAC": 4.0,
                "ioPeriod": 0,
                "poolCode": "NA",
                "sinkFlag": false,
                "cmaTicker": "N/A",
                "datedDate": "2013-05-01",
                "gnma2Flag": false,
                "percentVA": 11.03,
                "currentLTV": 27.9,
                "extendFlag": "N",
                "isoCountry": "US",
                "marketType": "DOMC",
                "percentDTI": 34.0,
                "percentFHA": 80.96,
                "percentInv": 0.0,
                "percentPIH": 0.14,
                "percentRHS": 7.87,
                "securityID": "999818YT",
                "serviceFee": 0.5,
                "vPointType": "MPGNMA",
                "adjustedLTV": 27.9,
                "combinedLTV": 90.7,
                "creditScore": 692,
                "description": "30-YR GNMA-2013 PROD",
                "esgBondFlag": false,
                "indexRating": "AA+",
                "issueAmount": 8597.24,
                "lowerRating": "AA+",
                "paymentFreq": 12,
                "percentHARP": 0.0,
                "percentRefi": 63.8,
                "tierCapital": "NA",
                "balloonMonth": 0,
                "deliveryFlag": "N",
                "indexCountry": "US",
                "industryCode": "MT",
                "issuerTicker": "GNMA",
                "lowestRating": "AA+",
                "maturityDate": "2041-12-01",
                "middleRating": "AA+",
                "modifiedDate": "2025-06-12",
                "originalTerm": 360,
                "parentTicker": "GNMA",
                "percentHARP2": 0.0,
                "percentJumbo": 0.0,
                "securityType": "MORT",
                "currentCoupon": 3.5,
                "dataStateList": [
                    {
                        "state": "PR",
                        "percent": 17.05
                    },
                    {
                        "state": "TX",
                        "percent": 10.11
                    },
                    {
                        "state": "FL",
                        "percent": 5.67
                    },
                    {
                        "state": "CA",
                        "percent": 4.91
                    },
                    {
                        "state": "OH",
                        "percent": 4.83
                    },
                    {
                        "state": "NY",
                        "percent": 4.78
                    },
                    {
                        "state": "GA",
                        "percent": 4.4
                    },
                    {
                        "state": "PA",
                        "percent": 3.37
                    },
                    {
                        "state": "MI",
                        "percent": 3.1
                    },
                    {
                        "state": "NC",
                        "percent": 2.73
                    },
                    {
                        "state": "IL",
                        "percent": 2.68
                    },
                    {
                        "state": "VA",
                        "percent": 2.67
                    },
                    {
                        "state": "NJ",
                        "percent": 2.39
                    },
                    {
                        "state": "IN",
                        "percent": 2.37
                    },
                    {
                        "state": "MD",
                        "percent": 2.26
                    },
                    {
                        "state": "MO",
                        "percent": 2.1
                    },
                    {
                        "state": "AZ",
                        "percent": 1.73
                    },
                    {
                        "state": "TN",
                        "percent": 1.67
                    },
                    {
                        "state": "AL",
                        "percent": 1.47
                    },
                    {
                        "state": "WA",
                        "percent": 1.47
                    },
                    {
                        "state": "OK",
                        "percent": 1.22
                    },
                    {
                        "state": "LA",
                        "percent": 1.21
                    },
                    {
                        "state": "MN",
                        "percent": 1.19
                    },
                    {
                        "state": "SC",
                        "percent": 1.11
                    },
                    {
                        "state": "CT",
                        "percent": 1.08
                    },
                    {
                        "state": "KY",
                        "percent": 1.04
                    },
                    {
                        "state": "CO",
                        "percent": 1.03
                    },
                    {
                        "state": "WI",
                        "percent": 1.0
                    },
                    {
                        "state": "MS",
                        "percent": 0.96
                    },
                    {
                        "state": "NM",
                        "percent": 0.95
                    },
                    {
                        "state": "OR",
                        "percent": 0.89
                    },
                    {
                        "state": "AR",
                        "percent": 0.75
                    },
                    {
                        "state": "NV",
                        "percent": 0.7
                    },
                    {
                        "state": "MA",
                        "percent": 0.68
                    },
                    {
                        "state": "IA",
                        "percent": 0.61
                    },
                    {
                        "state": "KS",
                        "percent": 0.59
                    },
                    {
                        "state": "UT",
                        "percent": 0.59
                    },
                    {
                        "state": "DE",
                        "percent": 0.44
                    },
                    {
                        "state": "ID",
                        "percent": 0.39
                    },
                    {
                        "state": "NE",
                        "percent": 0.39
                    },
                    {
                        "state": "WV",
                        "percent": 0.28
                    },
                    {
                        "state": "ME",
                        "percent": 0.19
                    },
                    {
                        "state": "NH",
                        "percent": 0.16
                    },
                    {
                        "state": "HI",
                        "percent": 0.15
                    },
                    {
                        "state": "MT",
                        "percent": 0.13
                    },
                    {
                        "state": "AK",
                        "percent": 0.12
                    },
                    {
                        "state": "RI",
                        "percent": 0.12
                    },
                    {
                        "state": "WY",
                        "percent": 0.08
                    },
                    {
                        "state": "SD",
                        "percent": 0.07
                    },
                    {
                        "state": "VT",
                        "percent": 0.06
                    },
                    {
                        "state": "DC",
                        "percent": 0.04
                    },
                    {
                        "state": "ND",
                        "percent": 0.04
                    }
                ],
                "delinquencies": {
                    "del30Days": {
                        "percent": 2.3
                    },
                    "del60Days": {
                        "percent": 0.54
                    },
                    "del90Days": {
                        "percent": 0.2
                    },
                    "del90PlusDays": {
                        "percent": 0.61
                    },
                    "del120PlusDays": {
                        "percent": 0.41
                    }
                },
                "greenBondFlag": false,
                "highestRating": "AAA",
                "incomeCountry": "US",
                "issuerCountry": "US",
                "percentSecond": 0.0,
                "poolAgeMethod": "Calculated",
                "prepayEffDate": "2025-05-01",
                "seniorityType": "NA",
                "assetClassCode": "CO",
                "cgmiSectorCode": "MTGE",
                "collateralType": "GNMA",
                "fullPledgeFlag": false,
                "gpmPercentStep": 0.0,
                "incomeCountry3": "USA",
                "instrumentType": "NA",
                "issuerCountry2": "US",
                "issuerCountry3": "USA",
                "lowestRatingNF": "AA+",
                "poolIssuerName": "NA",
                "vPointCategory": "RP",
                "amortizedFHALTV": 63.2,
                "bloombergTicker": "GNSF 3.5 2013",
                "industrySubCode": "MT",
                "originationDate": "2013-05-01",
                "originationYear": 2013,
                "percent2To4Unit": 2.7,
                "percentHAMPMods": 0.9,
                "percentPurchase": 31.8,
                "percentStateHFA": 0.4,
                "poolOriginalWAM": 0,
                "preliminaryFlag": false,
                "redemptionValue": 100.0,
                "securitySubType": "MPGNMA",
                "dataQuartileList": [
                    {
                        "ltvlow": 17.0,
                        "ltvhigh": 87.0,
                        "loanSizeLow": 22000.0,
                        "loanSizeHigh": 101000.0,
                        "percentDTILow": 10.0,
                        "creditScoreLow": 300.0,
                        "percentDTIHigh": 24.4,
                        "creditScoreHigh": 656.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20101101,
                        "originalLoanAgeHigh": 0,
                        "originationYearHigh": 20130401
                    },
                    {
                        "ltvlow": 87.0,
                        "ltvhigh": 93.0,
                        "loanSizeLow": 101000.0,
                        "loanSizeHigh": 132000.0,
                        "percentDTILow": 24.4,
                        "creditScoreLow": 656.0,
                        "percentDTIHigh": 34.9,
                        "creditScoreHigh": 691.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20130401,
                        "originalLoanAgeHigh": 0,
                        "originationYearHigh": 20130501
                    },
                    {
                        "ltvlow": 93.0,
                        "ltvhigh": 97.0,
                        "loanSizeLow": 132000.0,
                        "loanSizeHigh": 183000.0,
                        "percentDTILow": 34.9,
                        "creditScoreLow": 691.0,
                        "percentDTIHigh": 43.6,
                        "creditScoreHigh": 739.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20130501,
                        "originalLoanAgeHigh": 1,
                        "originationYearHigh": 20130701
                    },
                    {
                        "ltvlow": 97.0,
                        "ltvhigh": 118.0,
                        "loanSizeLow": 183000.0,
                        "loanSizeHigh": 743000.0,
                        "percentDTILow": 43.6,
                        "creditScoreLow": 739.0,
                        "percentDTIHigh": 65.0,
                        "creditScoreHigh": 832.0,
                        "originalLoanAgeLow": 1,
                        "originationYearLow": 20130701,
                        "originalLoanAgeHigh": 43,
                        "originationYearHigh": 20141101
                    }
                ],
                "gpmNumberOfSteps": 0,
                "percentHARPOwner": 0.0,
                "percentPrincipal": 100.0,
                "securityCalcType": "GNMA",
                "assetClassSubCode": "MBS",
                "forbearanceAmount": 0.0,
                "modifiedTimeStamp": "2025-06-12T19:10:00Z",
                "outstandingAmount": 1100.37,
                "parentDescription": "NA",
                "poolIsBalloonFlag": false,
                "prepaymentOptions": {
                    "prepayType": [
                        "CPR",
                        "PSA",
                        "VEC"
                    ]
                },
                "reperformerMonths": 1,
                "dataPPMHistoryList": [
                    {
                        "prepayType": "PSA",
                        "dataPPMHistoryDetailList": [
                            {
                                "month": "1",
                                "prepayRate": 104.2558
                            },
                            {
                                "month": "3",
                                "prepayRate": 101.9675
                            },
                            {
                                "month": "6",
                                "prepayRate": 101.3512
                            },
                            {
                                "month": "12",
                                "prepayRate": 101.4048
                            },
                            {
                                "month": "24",
                                "prepayRate": 0.0
                            }
                        ]
                    },
                    {
                        "prepayType": "CPR",
                        "dataPPMHistoryDetailList": [
                            {
                                "month": "1",
                                "prepayRate": 6.2554
                            },
                            {
                                "month": "3",
                                "prepayRate": 6.118
                            },
                            {
                                "month": "6",
                                "prepayRate": 6.0811
                            },
                            {
                                "month": "12",
                                "prepayRate": 6.0843
                            },
                            {
                                "month": "24",
                                "prepayRate": 0.0
                            }
                        ]
                    }
                ],
                "daysToFirstPayment": 44,
                "issuerLowestRating": "NA",
                "issuerMiddleRating": "NA",
                "newCurrentLoanSize": 102609.0,
                "originationChannel": {
                    "broker": 4.64,
                    "retail": 62.02,
                    "unknown": 0.0,
                    "unspecified": 0.0,
                    "correspondence": 33.31
                },
                "percentMultiFamily": 2.7,
                "percentRefiCashout": 5.8,
                "percentRegularMods": 3.5,
                "percentReperformer": 0.5,
                "relocationLoanFlag": false,
                "socialDensityScore": 0.0,
                "umbsfhlgPercentage": 0.0,
                "umbsfnmaPercentage": 0.0,
                "industryDescription": "Mortgage",
                "issuerHighestRating": "NA",
                "newOriginalLoanSize": 182013.0,
                "socialCriteriaShare": 0.0,
                "spreadAtOrigination": 22.3,
                "weightedAvgLoanSize": 102609.0,
                "poolOriginalLoanSize": 182013.0,
                "cgmiSectorDescription": "Mortgage",
                "expModelAvailableFlag": true,
                "fhfaImpliedCurrentLTV": 27.9,
                "newModelAvailableFlag": true,
                "percentRefiNonCashout": 58.0,
                "prepayPenaltySchedule": "0.000",
                "defaultHorizonPYMethod": "OAS Change",
                "industrySubDescription": "Mortgage Asset Backed",
                "actualPrepayHistoryList": {
                    "date": "2025-08-01",
                    "genericValue": 0.8659
                },
                "adjustedCurrentLoanSize": 102609.0,
                "forbearanceModification": 0.0,
                "percentTwoPlusBorrowers": 44.0,
                "poolAvgOriginalLoanTerm": 0,
                "adjustedOriginalLoanSize": 182003.0,
                "assetClassSubDescription": "Collateralized Asset Backed - Mortgage",
                "mortgageInsurancePremium": {
                    "annual": {
                        "va": 0.0,
                        "fha": 0.797,
                        "pih": 0.0,
                        "rhs": 0.399
                    },
                    "upfront": {
                        "va": 0.5,
                        "fha": 0.691,
                        "pih": 1.0,
                        "rhs": 1.996
                    }
                },
                "percentReperformerAndMod": 0.1,
                "reperformerMonthsForMods": 2,
                "dataPrepayModelSellerList": [
                    {
                        "seller": "HFUSM",
                        "percent": 0.07
                    },
                    {
                        "seller": "HFAL",
                        "percent": 0.06
                    },
                    {
                        "seller": "HFWA",
                        "percent": 0.02
                    }
                ],
                "originalLoanSizeRemaining": 150810.0,
                "percentFirstTimeHomeBuyer": 20.8,
                "current3rdPartyOrigination": 37.96,
                "adjustedSpreadAtOrigination": 22.3,
                "dataPrepayModelServicerList": [
                    {
                        "percent": 23.28,
                        "servicer": "WELLS"
                    },
                    {
                        "percent": 11.33,
                        "servicer": "NSTAR"
                    },
                    {
                        "percent": 11.1,
                        "servicer": "BCPOP"
                    },
                    {
                        "percent": 7.26,
                        "servicer": "QUICK"
                    },
                    {
                        "percent": 7.1,
                        "servicer": "PENNY"
                    },
                    {
                        "percent": 6.56,
                        "servicer": "LAKEV"
                    },
                    {
                        "percent": 6.33,
                        "servicer": "CARRG"
                    },
                    {
                        "percent": 5.5,
                        "servicer": "USB"
                    },
                    {
                        "percent": 4.27,
                        "servicer": "FREE"
                    },
                    {
                        "percent": 2.41,
                        "servicer": "PNC"
                    },
                    {
                        "percent": 1.33,
                        "servicer": "MNTBK"
                    },
                    {
                        "percent": 1.18,
                        "servicer": "NWRES"
                    },
                    {
                        "percent": 0.96,
                        "servicer": "FIFTH"
                    },
                    {
                        "percent": 0.75,
                        "servicer": "DEPOT"
                    },
                    {
                        "percent": 0.6,
                        "servicer": "BOKF"
                    },
                    {
                        "percent": 0.5,
                        "servicer": "JPM"
                    },
                    {
                        "percent": 0.47,
                        "servicer": "TRUIS"
                    },
                    {
                        "percent": 0.42,
                        "servicer": "CITI"
                    },
                    {
                        "percent": 0.38,
                        "servicer": "GUILD"
                    },
                    {
                        "percent": 0.21,
                        "servicer": "REGNS"
                    },
                    {
                        "percent": 0.2,
                        "servicer": "CNTRL"
                    },
                    {
                        "percent": 0.09,
                        "servicer": "COLNL"
                    },
                    {
                        "percent": 0.09,
                        "servicer": "MNSRC"
                    },
                    {
                        "percent": 0.06,
                        "servicer": "HFAGY"
                    },
                    {
                        "percent": 0.03,
                        "servicer": "HOMBR"
                    }
                ],
                "nonWeightedOriginalLoanSize": 0.0,
                "original3rdPartyOrigination": 0.0,
                "percentHARPDec2010Extension": 0.0,
                "percentHARPOneYearExtension": 0.0,
                "percentDownPaymentAssistance": 5.6,
                "percentAmortizedFHALTVUnder78": 95.4,
                "loanPerformanceImpliedCurrentLTV": 45.1,
                "reperformerMonthsForReperformers": 28
            },
            "ticker": "GNMA",
            "country": "US",
            "currency": "USD",
            "identifier": "999818YT",
            "description": "30-YR GNMA-2013 PROD",
            "issuerTicker": "GNMA",
            "maturityDate": "2041-12-01",
            "securityType": "MORT",
            "currentCoupon": 3.5,
            "securitySubType": "MPGNMA"
        },
        "meta": {
            "status": "DONE",
            "requestId": "R-1588910",
            "timeStamp": "2025-06-27T05:41:04Z",
            "responseType": "BOND_INDIC"
        }
    }


    >>> # Request bond indic with sync get
    >>> response = request_bond_indic_sync_get(
    >>>                                     id="01F002628",
    >>>                                     id_type=IdTypeEnum.CUSIP,
    >>>                                     keywords=["keyword1", "keyword2"],
    >>>                                     job="JobName",
    >>>                                     name="Name",
    >>>                                     pri=0,
    >>>                                     tags=["tag1", "tag2"]
    >>>                                     )
    >>>
    >>> # Print results in json format
    >>> print(js.dumps(response, indent=4))
    {
        "data": {
            "cusip": "01F002628",
            "indic": {},
            "ticker": "FNMA",
            "country": "US",
            "currency": "USD",
            "identifier": "01F00262",
            "description": "30-YR UMBS-TBA PROD FEB",
            "issuerTicker": "UMBS",
            "maturityDate": "2054-01-01",
            "securityType": "MORT",
            "currentCoupon": 0.5,
            "securitySubType": "FNTBA"
        },
        "meta": {
            "status": "DONE",
            "requestId": "R-1588911",
            "timeStamp": "2025-06-27T05:41:05Z",
            "responseType": "BOND_INDIC"
        }
    }

    """

    try:
        logger.info("Calling request_bond_indic_sync_get")

        response = check_and_raise(
            Client().yield_book_rest.request_bond_indic_sync_get(
                id=id,
                id_type=id_type,
                keywords=keywords,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called request_bond_indic_sync_get")

        return output
    except Exception as err:
        logger.error(f"Error request_bond_indic_sync_get. {err}")
        check_exception_and_raise(err)


def request_curve_async(
    *,
    date: Union[str, datetime.date],
    currency: str,
    curve_type: Union[str, YbRestCurveType],
    cds_ticker: Optional[str] = None,
    expand_curve: Optional[bool] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request curve async.

    Parameters
    ----------
    date : Union[str, datetime.date]
        A date on a calendar without a time zone, e.g. "April 10th"
    currency : str
        A sequence of textual characters.
    curve_type : Union[str, YbRestCurveType]

    cds_ticker : str, optional
        A sequence of textual characters.
    expand_curve : bool, optional
        Boolean with `true` and `false` values.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_curve_async")

        response = check_and_raise(
            Client().yield_book_rest.request_curve_async(
                date=date,
                currency=currency,
                curve_type=curve_type,
                cds_ticker=cds_ticker,
                expand_curve=expand_curve,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called request_curve_async")

        return output
    except Exception as err:
        logger.error(f"Error request_curve_async. {err}")
        check_exception_and_raise(err)


def request_curve_sync(
    *,
    date: Union[str, datetime.date],
    currency: str,
    curve_type: Union[str, YbRestCurveType],
    cds_ticker: Optional[str] = None,
    expand_curve: Optional[bool] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request curve sync.

    Parameters
    ----------
    date : Union[str, datetime.date]
        A date on a calendar without a time zone, e.g. "April 10th"
    currency : str
        A sequence of textual characters.
    curve_type : Union[str, YbRestCurveType]

    cds_ticker : str, optional
        A sequence of textual characters.
    expand_curve : bool, optional
        Boolean with `true` and `false` values.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_curve_sync")

        response = check_and_raise(
            Client().yield_book_rest.request_curve_sync(
                date=date,
                currency=currency,
                curve_type=curve_type,
                cds_ticker=cds_ticker,
                expand_curve=expand_curve,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called request_curve_sync")

        return output
    except Exception as err:
        logger.error(f"Error request_curve_sync. {err}")
        check_exception_and_raise(err)


def request_curves_async(
    *,
    curves: Optional[List[CurveSearch]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request curves async.

    Parameters
    ----------
    curves : List[CurveSearch], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_curves_async")

        response = check_and_raise(
            Client().yield_book_rest.request_curves_async(
                body=CurveDetailsRequest(curves=curves),
                job=job,
                name=name,
                pri=pri,
                tags=tags,
                content_type="application/json",
            )
        )

        output = response
        logger.info("Called request_curves_async")

        return output
    except Exception as err:
        logger.error(f"Error request_curves_async. {err}")
        check_exception_and_raise(err)


def request_curves_sync(
    *,
    curves: Optional[List[CurveSearch]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request curves sync.

    Parameters
    ----------
    curves : List[CurveSearch], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_curves_sync")

        response = check_and_raise(
            Client().yield_book_rest.request_curves_sync(
                body=CurveDetailsRequest(curves=curves),
                job=job,
                name=name,
                pri=pri,
                tags=tags,
                content_type="application/json",
            )
        )

        output = response
        logger.info("Called request_curves_sync")

        return output
    except Exception as err:
        logger.error(f"Error request_curves_sync. {err}")
        check_exception_and_raise(err)


def request_get_scen_calc_sys_scen_async(
    *,
    id: str,
    scenario: str,
    id_type: Optional[str] = None,
    level: Optional[str] = None,
    pricing_date: Optional[str] = None,
    h_days: Optional[int] = None,
    h_months: Optional[int] = None,
    curve_type: Optional[Union[str, YbRestCurveType]] = None,
    currency: Optional[str] = None,
    volatility: Optional[str] = None,
    prepay_type: Optional[str] = None,
    prepay_rate: Optional[float] = None,
    h_level: Optional[str] = None,
    h_py_method: Optional[str] = None,
    h_prepay_rate: Optional[float] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request get scenario calculation system scenario async.

    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    level : str, optional
        A sequence of textual characters.
    pricing_date : str, optional
        A sequence of textual characters.
    h_days : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    h_months : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    curve_type : Union[str, YbRestCurveType], optional

    currency : str, optional
        A sequence of textual characters.
    volatility : str, optional
        A sequence of textual characters.
    prepay_type : str, optional
        A sequence of textual characters.
    prepay_rate : float, optional
        A 32 bit floating point number. (`±1.5 x 10^−45` to `±3.4 x 10^38`)
    h_level : str, optional
        A sequence of textual characters.
    h_py_method : str, optional
        A sequence of textual characters.
    h_prepay_rate : float, optional
        A 32 bit floating point number. (`±1.5 x 10^−45` to `±3.4 x 10^38`)
    scenario : str
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_get_scen_calc_sys_scen_async")

        response = check_and_raise(
            Client().yield_book_rest.request_get_scen_calc_sys_scen_async(
                id=id,
                id_type=id_type,
                level=level,
                pricing_date=pricing_date,
                h_days=h_days,
                h_months=h_months,
                curve_type=curve_type,
                currency=currency,
                volatility=volatility,
                prepay_type=prepay_type,
                prepay_rate=prepay_rate,
                h_level=h_level,
                h_py_method=h_py_method,
                h_prepay_rate=h_prepay_rate,
                scenario=scenario,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called request_get_scen_calc_sys_scen_async")

        return output
    except Exception as err:
        logger.error(f"Error request_get_scen_calc_sys_scen_async. {err}")
        check_exception_and_raise(err)


def request_get_scen_calc_sys_scen_sync(
    *,
    id: str,
    scenario: str,
    id_type: Optional[str] = None,
    level: Optional[str] = None,
    pricing_date: Optional[str] = None,
    h_days: Optional[int] = None,
    h_months: Optional[int] = None,
    curve_type: Optional[Union[str, YbRestCurveType]] = None,
    currency: Optional[str] = None,
    volatility: Optional[str] = None,
    prepay_type: Optional[str] = None,
    prepay_rate: Optional[float] = None,
    h_level: Optional[str] = None,
    h_py_method: Optional[str] = None,
    h_prepay_rate: Optional[float] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request get scenario calculation system scenario sync.

    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    level : str, optional
        A sequence of textual characters.
    pricing_date : str, optional
        A sequence of textual characters.
    h_days : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    h_months : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    curve_type : Union[str, YbRestCurveType], optional

    currency : str, optional
        A sequence of textual characters.
    volatility : str, optional
        A sequence of textual characters.
    prepay_type : str, optional
        A sequence of textual characters.
    prepay_rate : float, optional
        A 32 bit floating point number. (`±1.5 x 10^−45` to `±3.4 x 10^38`)
    h_level : str, optional
        A sequence of textual characters.
    h_py_method : str, optional
        A sequence of textual characters.
    h_prepay_rate : float, optional
        A 32 bit floating point number. (`±1.5 x 10^−45` to `±3.4 x 10^38`)
    scenario : str
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_get_scen_calc_sys_scen_sync")

        response = check_and_raise(
            Client().yield_book_rest.request_get_scen_calc_sys_scen_sync(
                id=id,
                id_type=id_type,
                level=level,
                pricing_date=pricing_date,
                h_days=h_days,
                h_months=h_months,
                curve_type=curve_type,
                currency=currency,
                volatility=volatility,
                prepay_type=prepay_type,
                prepay_rate=prepay_rate,
                h_level=h_level,
                h_py_method=h_py_method,
                h_prepay_rate=h_prepay_rate,
                scenario=scenario,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called request_get_scen_calc_sys_scen_sync")

        return output
    except Exception as err:
        logger.error(f"Error request_get_scen_calc_sys_scen_sync. {err}")
        check_exception_and_raise(err)


def request_py_calculation_async(
    *,
    global_settings: Optional[PyCalcGlobalSettings] = None,
    input: Optional[List[PyCalcInput]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request PY calculation async.

    Parameters
    ----------
    global_settings : PyCalcGlobalSettings, optional

    input : List[PyCalcInput], optional

    keywords : List[str], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_py_calculation_async")

        response = check_and_raise(
            Client().yield_book_rest.request_py_calculation_async(
                body=PyCalcRequest(global_settings=global_settings, input=input, keywords=keywords),
                job=job,
                name=name,
                pri=pri,
                tags=tags,
                content_type="application/json",
            )
        )

        output = response
        logger.info("Called request_py_calculation_async")

        return output
    except Exception as err:
        logger.error(f"Error request_py_calculation_async. {err}")
        check_exception_and_raise(err)


def request_py_calculation_async_by_id(
    *,
    id: str,
    level: str,
    curve_type: Union[str, YbRestCurveType],
    id_type: Optional[str] = None,
    pricing_date: Optional[Union[str, datetime.date]] = None,
    currency: Optional[str] = None,
    prepay_type: Optional[str] = None,
    prepay_rate: Optional[float] = None,
    option_model: Optional[Union[str, OptionModel]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request PY calculation async by ID.

    Parameters
    ----------
    id : str
        A sequence of textual characters.
    id_type : str, optional
        A sequence of textual characters.
    level : str
        A sequence of textual characters.
    pricing_date : Union[str, datetime.date], optional
        A date on a calendar without a time zone, e.g. "April 10th"
    curve_type : Union[str, YbRestCurveType]

    currency : str, optional
        A sequence of textual characters.
    prepay_type : str, optional
        A sequence of textual characters.
    prepay_rate : float, optional
        A 32 bit floating point number. (`±1.5 x 10^−45` to `±3.4 x 10^38`)
    option_model : Union[str, OptionModel], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_py_calculation_async_by_id")

        response = check_and_raise(
            Client().yield_book_rest.request_py_calculation_async_by_id(
                id=id,
                id_type=id_type,
                level=level,
                pricing_date=pricing_date,
                curve_type=curve_type,
                currency=currency,
                prepay_type=prepay_type,
                prepay_rate=prepay_rate,
                option_model=option_model,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called request_py_calculation_async_by_id")

        return output
    except Exception as err:
        logger.error(f"Error request_py_calculation_async_by_id. {err}")
        check_exception_and_raise(err)


def request_py_calculation_sync(
    *,
    global_settings: Optional[PyCalcGlobalSettings] = None,
    input: Optional[List[PyCalcInput]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request PY calculation sync.

    Parameters
    ----------
    global_settings : PyCalcGlobalSettings, optional

    input : List[PyCalcInput], optional

    keywords : List[str], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_py_calculation_sync")

        response = check_and_raise(
            Client().yield_book_rest.request_py_calculation_sync(
                body=PyCalcRequest(global_settings=global_settings, input=input, keywords=keywords),
                job=job,
                name=name,
                pri=pri,
                tags=tags,
                content_type="application/json",
            )
        )

        output = response
        logger.info("Called request_py_calculation_sync")

        return output
    except Exception as err:
        logger.error(f"Error request_py_calculation_sync. {err}")
        check_exception_and_raise(err)


def request_py_calculation_sync_by_id(
    *,
    id: str,
    level: str,
    curve_type: Union[str, YbRestCurveType],
    id_type: Optional[str] = None,
    pricing_date: Optional[Union[str, datetime.date]] = None,
    currency: Optional[str] = None,
    prepay_type: Optional[str] = None,
    prepay_rate: Optional[float] = None,
    option_model: Optional[Union[str, OptionModel]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request PY calculation sync by ID.

    Parameters
    ----------
    id : str
        A sequence of textual characters.
    id_type : str, optional
        A sequence of textual characters.
    level : str
        A sequence of textual characters.
    pricing_date : Union[str, datetime.date], optional
        A date on a calendar without a time zone, e.g. "April 10th"
    curve_type : Union[str, YbRestCurveType]

    currency : str, optional
        A sequence of textual characters.
    prepay_type : str, optional
        A sequence of textual characters.
    prepay_rate : float, optional
        A 32 bit floating point number. (`±1.5 x 10^−45` to `±3.4 x 10^38`)
    option_model : Union[str, OptionModel], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_py_calculation_sync_by_id")

        response = check_and_raise(
            Client().yield_book_rest.request_py_calculation_sync_by_id(
                id=id,
                id_type=id_type,
                level=level,
                pricing_date=pricing_date,
                curve_type=curve_type,
                currency=currency,
                prepay_type=prepay_type,
                prepay_rate=prepay_rate,
                option_model=option_model,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called request_py_calculation_sync_by_id")

        return output
    except Exception as err:
        logger.error(f"Error request_py_calculation_sync_by_id. {err}")
        check_exception_and_raise(err)


def request_return_attribution_async(
    *,
    global_settings: Optional[ReturnAttributionGlobalSettings] = None,
    input: Optional[List[ReturnAttributionInput]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request return attribution async.

    Parameters
    ----------
    global_settings : ReturnAttributionGlobalSettings, optional

    input : List[ReturnAttributionInput], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_return_attribution_async")

        response = check_and_raise(
            Client().yield_book_rest.request_return_attribution_async(
                body=ReturnAttributionRequest(global_settings=global_settings, input=input),
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called request_return_attribution_async")

        return output
    except Exception as err:
        logger.error(f"Error request_return_attribution_async. {err}")
        check_exception_and_raise(err)


def request_return_attribution_sync(
    *,
    global_settings: Optional[ReturnAttributionGlobalSettings] = None,
    input: Optional[List[ReturnAttributionInput]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request return attribution sync.

    Parameters
    ----------
    global_settings : ReturnAttributionGlobalSettings, optional

    input : List[ReturnAttributionInput], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_return_attribution_sync")

        response = check_and_raise(
            Client().yield_book_rest.request_return_attribution_sync(
                body=ReturnAttributionRequest(global_settings=global_settings, input=input),
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called request_return_attribution_sync")

        return output
    except Exception as err:
        logger.error(f"Error request_return_attribution_sync. {err}")
        check_exception_and_raise(err)


def request_scenario_calculation_async(
    *,
    global_settings: Optional[ScenarioCalcGlobalSettings] = None,
    keywords: Optional[List[str]] = None,
    scenarios: Optional[List[Scenario]] = None,
    input: Optional[List[ScenarioCalcInput]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request scenario calculation async.

    Parameters
    ----------
    global_settings : ScenarioCalcGlobalSettings, optional

    keywords : List[str], optional

    scenarios : List[Scenario], optional

    input : List[ScenarioCalcInput], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_scenario_calculation_async")

        response = check_and_raise(
            Client().yield_book_rest.request_scenario_calculation_async(
                body=ScenarioCalcRequest(
                    global_settings=global_settings,
                    keywords=keywords,
                    scenarios=scenarios,
                    input=input,
                ),
                job=job,
                name=name,
                pri=pri,
                tags=tags,
                content_type="application/json",
            )
        )

        output = response
        logger.info("Called request_scenario_calculation_async")

        return output
    except Exception as err:
        logger.error(f"Error request_scenario_calculation_async. {err}")
        check_exception_and_raise(err)


def request_scenario_calculation_sync(
    *,
    global_settings: Optional[ScenarioCalcGlobalSettings] = None,
    keywords: Optional[List[str]] = None,
    scenarios: Optional[List[Scenario]] = None,
    input: Optional[List[ScenarioCalcInput]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request scenario calculation sync.

    Parameters
    ----------
    global_settings : ScenarioCalcGlobalSettings, optional

    keywords : List[str], optional

    scenarios : List[Scenario], optional

    input : List[ScenarioCalcInput], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_scenario_calculation_sync")

        response = check_and_raise(
            Client().yield_book_rest.request_scenario_calculation_sync(
                body=ScenarioCalcRequest(
                    global_settings=global_settings,
                    keywords=keywords,
                    scenarios=scenarios,
                    input=input,
                ),
                job=job,
                name=name,
                pri=pri,
                tags=tags,
                content_type="application/json",
            )
        )

        output = response
        logger.info("Called request_scenario_calculation_sync")

        return output
    except Exception as err:
        logger.error(f"Error request_scenario_calculation_sync. {err}")
        check_exception_and_raise(err)


def request_volatility_async(
    *,
    currency: str,
    date: str,
    quote_type: str,
    vol_model: Optional[str] = None,
    vol_type: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request volatility async.

    Parameters
    ----------
    currency : str
        Currency should be a 3 letter upper case string
    date : str
        A sequence of textual characters.
    quote_type : str
        Should be one of the following - Market, Calibrated, SOFRMarket, LIBORMarket.
    vol_model : str, optional
        A sequence of textual characters.
    vol_type : str, optional
        Should be one of the following - NORM, BLACK
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_volatility_async")

        response = check_and_raise(
            Client().yield_book_rest.request_volatility_async(
                currency=currency,
                date=date,
                quote_type=quote_type,
                vol_model=vol_model,
                vol_type=vol_type,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called request_volatility_async")

        return output
    except Exception as err:
        logger.error(f"Error request_volatility_async. {err}")
        check_exception_and_raise(err)


def request_volatility_sync(
    *,
    currency: str,
    date: str,
    quote_type: str,
    vol_model: Optional[str] = None,
    vol_type: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request volatility sync.

    Parameters
    ----------
    currency : str
        Currency should be a 3 letter upper case string
    date : str
        A sequence of textual characters.
    quote_type : str
        Should be one of the following - Market, Calibrated, SOFRMarket, LIBORMarket.
    vol_model : str, optional
        A sequence of textual characters.
    vol_type : str, optional
        Should be one of the following - NORM, BLACK
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_volatility_sync")

        response = check_and_raise(
            Client().yield_book_rest.request_volatility_sync(
                currency=currency,
                date=date,
                quote_type=quote_type,
                vol_model=vol_model,
                vol_type=vol_type,
                job=job,
                name=name,
                pri=pri,
                tags=tags,
            )
        )

        output = response
        logger.info("Called request_volatility_sync")

        return output
    except Exception as err:
        logger.error(f"Error request_volatility_sync. {err}")
        check_exception_and_raise(err)


def resubmit_job(
    *,
    job_ref: str,
    scope: Optional[Literal["OK", "ERROR", "ABORTED", "FAILED", "ALL"]] = None,
    ids: Optional[List[str]] = None,
) -> JobResponse:
    """
    Resubmit a job

    Parameters
    ----------
    scope : Literal["OK","ERROR","ABORTED","FAILED","ALL"], optional

    ids : List[str], optional

    job_ref : str
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    JobResponse


    Examples
    --------
    >>> # resubmit job
    >>> response = resubmit_job(scope="OK", ids=["J-20413"], job_ref="myJob")
    >>> print(response)
    {'id': 'J-20413', 'sequence': 0, 'asOf': '2025-03-10', 'closed': True, 'onHold': True, 'aborted': True, 'exitStatus': 'DONE', 'actualHold': True, 'name': 'myJob', 'chain': 'string', 'description': 'string', 'priority': 0, 'order': 'FAST', 'requestCount': 0, 'pendingCount': 0, 'runningCount': 0, 'okCount': 0, 'errorCount': 0, 'abortedCount': 0, 'skipCount': 0, 'startAfter': '2024-11-26T07:42:07.695Z', 'stopAfter': '2024-11-26T07:42:07.695Z', 'createdAt': '2024-11-26T07:42:07.695Z', 'updatedAt': '2024-11-26T07:42:07.695Z', 'timeline': [{'ts': '2024-11-26T07:42:07.695Z', 'okCount': 0, 'errorCount': 0, 'interval': 0}]}

    """

    try:
        logger.info("Calling resubmit_job")

        response = check_and_raise(
            Client().yield_book_rest.resubmit_job(body=JobResubmissionRequest(scope=scope, ids=ids), job_ref=job_ref)
        )

        output = response
        logger.info("Called resubmit_job")

        return output
    except Exception as err:
        logger.error(f"Error resubmit_job. {err}")
        check_exception_and_raise(err)


def upload_csv_job_data_async(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Async upload csv job data.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    name : str, optional
        A sequence of textual characters.
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling upload_csv_job_data_async")

        response = check_and_raise(
            Client().yield_book_rest.upload_csv_job_data_async(
                job=job,
                store_type=store_type,
                name=name,
                pri=pri,
                tags=tags,
                content_type="text/csv",
                data=data,
            )
        )

        output = response
        logger.info("Called upload_csv_job_data_async")

        return output
    except Exception as err:
        logger.error(f"Error upload_csv_job_data_async. {err}")
        check_exception_and_raise(err)


def upload_csv_job_data_sync(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Sync upload csv job data.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    name : str, optional
        A sequence of textual characters.
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling upload_csv_job_data_sync")

        response = check_and_raise(
            Client().yield_book_rest.upload_csv_job_data_sync(
                job=job,
                store_type=store_type,
                name=name,
                pri=pri,
                tags=tags,
                content_type="text/csv",
                data=data,
            )
        )

        output = response
        logger.info("Called upload_csv_job_data_sync")

        return output
    except Exception as err:
        logger.error(f"Error upload_csv_job_data_sync. {err}")
        check_exception_and_raise(err)


def upload_csv_job_data_with_name_async(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    request_name: str,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Async upload csv job data with a user-provided name.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_name : str
        User provided name for the request
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling upload_csv_job_data_with_name_async")

        response = check_and_raise(
            Client().yield_book_rest.upload_csv_job_data_with_name_async(
                job=job,
                store_type=store_type,
                request_name=request_name,
                pri=pri,
                tags=tags,
                content_type="text/csv",
                data=data,
            )
        )

        output = response
        logger.info("Called upload_csv_job_data_with_name_async")

        return output
    except Exception as err:
        logger.error(f"Error upload_csv_job_data_with_name_async. {err}")
        check_exception_and_raise(err)


def upload_csv_job_data_with_name_sync(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    request_name: str,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Sync upload csv job with a user-provided name.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_name : str
        User provided name for the request
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling upload_csv_job_data_with_name_sync")

        response = check_and_raise(
            Client().yield_book_rest.upload_csv_job_data_with_name_sync(
                job=job,
                store_type=store_type,
                request_name=request_name,
                pri=pri,
                tags=tags,
                content_type="text/csv",
                data=data,
            )
        )

        output = response
        logger.info("Called upload_csv_job_data_with_name_sync")

        return output
    except Exception as err:
        logger.error(f"Error upload_csv_job_data_with_name_sync. {err}")
        check_exception_and_raise(err)


def upload_json_job_data_async(
    *,
    data: JobStoreInputData,
    job: str,
    store_type: Union[str, StoreType],
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Async upload json job data.

    Parameters
    ----------
    data : JobStoreInputData

    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    name : str, optional
        A sequence of textual characters.
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling upload_json_job_data_async")

        response = check_and_raise(
            Client().yield_book_rest.upload_json_job_data_async(
                job=job,
                store_type=store_type,
                name=name,
                pri=pri,
                tags=tags,
                content_type="application/json",
                data=data,
            )
        )

        output = response
        logger.info("Called upload_json_job_data_async")

        return output
    except Exception as err:
        logger.error(f"Error upload_json_job_data_async. {err}")
        check_exception_and_raise(err)


def upload_json_job_data_sync(
    *,
    data: JobStoreInputData,
    job: str,
    store_type: Union[str, StoreType],
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Sync upload json job data.

    Parameters
    ----------
    data : JobStoreInputData

    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    name : str, optional
        A sequence of textual characters.
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling upload_json_job_data_sync")

        response = check_and_raise(
            Client().yield_book_rest.upload_json_job_data_sync(
                job=job,
                store_type=store_type,
                name=name,
                pri=pri,
                tags=tags,
                content_type="application/json",
                data=data,
            )
        )

        output = response
        logger.info("Called upload_json_job_data_sync")

        return output
    except Exception as err:
        logger.error(f"Error upload_json_job_data_sync. {err}")
        check_exception_and_raise(err)


def upload_json_job_data_with_name_async(
    *,
    data: JobStoreInputData,
    job: str,
    store_type: Union[str, StoreType],
    request_name: str,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Async upload json job data with a user-provided name.

    Parameters
    ----------
    data : JobStoreInputData

    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_name : str
        User provided name for the request
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling upload_json_job_data_with_name_async")

        response = check_and_raise(
            Client().yield_book_rest.upload_json_job_data_with_name_async(
                job=job,
                store_type=store_type,
                request_name=request_name,
                pri=pri,
                tags=tags,
                content_type="application/json",
                data=data,
            )
        )

        output = response
        logger.info("Called upload_json_job_data_with_name_async")

        return output
    except Exception as err:
        logger.error(f"Error upload_json_job_data_with_name_async. {err}")
        check_exception_and_raise(err)


def upload_json_job_data_with_name_sync(
    *,
    data: JobStoreInputData,
    job: str,
    store_type: Union[str, StoreType],
    request_name: str,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Sync upload json job data with a user-provided name.

    Parameters
    ----------
    data : JobStoreInputData

    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_name : str
        User provided name for the request
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling upload_json_job_data_with_name_sync")

        response = check_and_raise(
            Client().yield_book_rest.upload_json_job_data_with_name_sync(
                job=job,
                store_type=store_type,
                request_name=request_name,
                pri=pri,
                tags=tags,
                content_type="application/json",
                data=data,
            )
        )

        output = response
        logger.info("Called upload_json_job_data_with_name_sync")

        return output
    except Exception as err:
        logger.error(f"Error upload_json_job_data_with_name_sync. {err}")
        check_exception_and_raise(err)


def upload_text_job_data_async(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Async upload text job data.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    name : str, optional
        A sequence of textual characters.
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling upload_text_job_data_async")

        response = check_and_raise(
            Client().yield_book_rest.upload_text_job_data_async(
                job=job,
                store_type=store_type,
                name=name,
                pri=pri,
                tags=tags,
                content_type="text/plain",
                data=data,
            )
        )

        output = response
        logger.info("Called upload_text_job_data_async")

        return output
    except Exception as err:
        logger.error(f"Error upload_text_job_data_async. {err}")
        check_exception_and_raise(err)


def upload_text_job_data_sync(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Sync upload text job data.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    name : str, optional
        A sequence of textual characters.
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling upload_text_job_data_sync")

        response = check_and_raise(
            Client().yield_book_rest.upload_text_job_data_sync(
                job=job,
                store_type=store_type,
                name=name,
                pri=pri,
                tags=tags,
                content_type="text/plain",
                data=data,
            )
        )

        output = response
        logger.info("Called upload_text_job_data_sync")

        return output
    except Exception as err:
        logger.error(f"Error upload_text_job_data_sync. {err}")
        check_exception_and_raise(err)


def upload_text_job_data_with_name_async(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    request_name: str,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Async upload text job data with a user-provided name.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_name : str
        User provided name for the request
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling upload_text_job_data_with_name_async")

        response = check_and_raise(
            Client().yield_book_rest.upload_text_job_data_with_name_async(
                job=job,
                store_type=store_type,
                request_name=request_name,
                pri=pri,
                tags=tags,
                content_type="text/plain",
                data=data,
            )
        )

        output = response
        logger.info("Called upload_text_job_data_with_name_async")

        return output
    except Exception as err:
        logger.error(f"Error upload_text_job_data_with_name_async. {err}")
        check_exception_and_raise(err)


def upload_text_job_data_with_name_sync(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    request_name: str,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Sync upload text job data with a user-provided name.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_name : str
        User provided name for the request
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling upload_text_job_data_with_name_sync")

        response = check_and_raise(
            Client().yield_book_rest.upload_text_job_data_with_name_sync(
                job=job,
                store_type=store_type,
                request_name=request_name,
                pri=pri,
                tags=tags,
                content_type="text/plain",
                data=data,
            )
        )

        output = response
        logger.info("Called upload_text_job_data_with_name_sync")

        return output
    except Exception as err:
        logger.error(f"Error upload_text_job_data_with_name_sync. {err}")
        check_exception_and_raise(err)
