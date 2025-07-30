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
from lseg_analytics_basic_client.models import (
    AdjustableDate,
    AmortizationDefinition,
    AmortizationTypeEnum,
    Amount,
    BachelierParameters,
    BasePricingParameters,
    BlackScholesEquityParameters,
    BlackScholesFxParameters,
    BlackScholesInterestRateFuture,
    BusinessDayAdjustmentDefinition,
    CapFloorDefinition,
    CapFloorTypeEnum,
    CmdtyOptionVolSurfaceChoice,
    CmdtyVolSurfaceInput,
    CompoundingModeEnum,
    ConvexityAdjustmentMethodEnum,
    CouponReferenceDateEnum,
    CreditCurveChoice,
    CreditCurveInput,
    CrossCurencySwapOverride,
    CurencyBasisSwapOverride,
    CurveDataPoint,
    Date,
    DatedRate,
    DatedValue,
    DateMovingConvention,
    DayCountBasis,
    Description,
    DirectionEnum,
    Dividend,
    DividendTypeEnum,
    EndOfMonthConvention,
    EqOptionVolSurfaceChoice,
    EqVolSurfaceInput,
    FixedRateDefinition,
    FloatingRateDefinition,
    FrequencyEnum,
    FxCurveInput,
    FxForwardCurveChoice,
    FxOptionVolSurfaceChoice,
    FxPricingParameters,
    FxRateTypeEnum,
    FxVolSurfaceInput,
    HestonEquityParameters,
    IndexCompoundingDefinition,
    IndexObservationMethodEnum,
    InnerError,
    IntegrationMethodEnum,
    InterestRateDefinition,
    InterestRateLegDefinition,
    InterestType,
    IrCapVolSurfaceChoice,
    IrConvexityAdjustment,
    IrCurveChoice,
    IrLegDescriptionFields,
    IrLegResponseFields,
    IrLegValuationResponseFields,
    IrMeasure,
    IrPricingParameters,
    IrRiskFields,
    IrSwapAsCollectionItem,
    IrSwapDefinition,
    IrSwapDefinitionInstrument,
    IrSwapInstrumentDescriptionFields,
    IrSwapInstrumentRiskFields,
    IrSwapInstrumentSolveResponseFieldsOnResourceResponseData,
    IrSwapInstrumentSolveResponseFieldsResponseData,
    IrSwapInstrumentSolveResponseFieldsResponseWithError,
    IrSwapInstrumentValuationFields,
    IrSwapInstrumentValuationResponseFieldsOnResourceResponseData,
    IrSwapInstrumentValuationResponseFieldsResponseData,
    IrSwapInstrumentValuationResponseFieldsResponseWithError,
    IrSwapSolvingParameters,
    IrSwapSolvingTarget,
    IrSwapSolvingVariable,
    IrSwaptionVolCubeChoice,
    IrValuationFields,
    IrVolCubeInput,
    IrVolSurfaceInput,
    IrZcCurveInput,
    LoanDefinition,
    LoanInstrumentRiskFields,
    LoanInstrumentValuationFields,
    Location,
    MarketData,
    MarketVolatility,
    Measure,
    ModelParameters,
    NumericalMethodEnum,
    OffsetDefinition,
    OptionPricingParameters,
    OptionSolvingParameters,
    OptionSolvingTarget,
    OptionSolvingVariable,
    OptionSolvingVariableEnum,
    PaidLegEnum,
    PartyEnum,
    PayerReceiverEnum,
    Payment,
    PriceSideWithLastEnum,
    PrincipalDefinition,
    Rate,
    ReferenceDate,
    RelativeAdjustableDate,
    ResetDatesDefinition,
    ScheduleDefinition,
    ServiceError,
    SolvingLegEnum,
    SolvingMethod,
    SolvingMethodEnum,
    SolvingResult,
    SortingOrderEnum,
    Spot,
    SpreadCompoundingModeEnum,
    StepRateDefinition,
    StrikeTypeEnum,
    StubIndexReferences,
    StubRuleEnum,
    SwapSolvingVariableEnum,
    TenorBasisSwapOverride,
    TimeStampEnum,
    UnitEnum,
    VanillaIrsOverride,
    VolatilityTypeEnum,
    VolCubePoint,
    VolModelTypeEnum,
    VolSurfacePoint,
    ZcTypeEnum,
)

from ._ir_swap import IrSwap
from ._logger import logger

__all__ = [
    "AmortizationDefinition",
    "AmortizationTypeEnum",
    "Amount",
    "BachelierParameters",
    "BasePricingParameters",
    "BlackScholesEquityParameters",
    "BlackScholesFxParameters",
    "BlackScholesInterestRateFuture",
    "BusinessDayAdjustmentDefinition",
    "CapFloorDefinition",
    "CapFloorTypeEnum",
    "CmdtyOptionVolSurfaceChoice",
    "CmdtyVolSurfaceInput",
    "CompoundingModeEnum",
    "ConvexityAdjustmentMethodEnum",
    "CouponReferenceDateEnum",
    "CreditCurveChoice",
    "CreditCurveInput",
    "CrossCurencySwapOverride",
    "CurencyBasisSwapOverride",
    "CurveDataPoint",
    "DatedRate",
    "DatedValue",
    "DirectionEnum",
    "Dividend",
    "DividendTypeEnum",
    "EqOptionVolSurfaceChoice",
    "EqVolSurfaceInput",
    "FixedRateDefinition",
    "FloatingRateDefinition",
    "FxCurveInput",
    "FxForwardCurveChoice",
    "FxOptionVolSurfaceChoice",
    "FxPricingParameters",
    "FxRateTypeEnum",
    "FxVolSurfaceInput",
    "HestonEquityParameters",
    "IndexCompoundingDefinition",
    "IndexObservationMethodEnum",
    "IntegrationMethodEnum",
    "InterestRateDefinition",
    "InterestRateLegDefinition",
    "IrCapVolSurfaceChoice",
    "IrConvexityAdjustment",
    "IrCurveChoice",
    "IrLegDescriptionFields",
    "IrLegResponseFields",
    "IrLegValuationResponseFields",
    "IrMeasure",
    "IrPricingParameters",
    "IrRiskFields",
    "IrSwap",
    "IrSwapAsCollectionItem",
    "IrSwapDefinition",
    "IrSwapDefinitionInstrument",
    "IrSwapInstrumentDescriptionFields",
    "IrSwapInstrumentRiskFields",
    "IrSwapInstrumentSolveResponseFieldsOnResourceResponseData",
    "IrSwapInstrumentSolveResponseFieldsResponseData",
    "IrSwapInstrumentSolveResponseFieldsResponseWithError",
    "IrSwapInstrumentValuationFields",
    "IrSwapInstrumentValuationResponseFieldsOnResourceResponseData",
    "IrSwapInstrumentValuationResponseFieldsResponseData",
    "IrSwapInstrumentValuationResponseFieldsResponseWithError",
    "IrSwapSolvingParameters",
    "IrSwapSolvingTarget",
    "IrSwapSolvingVariable",
    "IrSwaptionVolCubeChoice",
    "IrValuationFields",
    "IrVolCubeInput",
    "IrVolSurfaceInput",
    "IrZcCurveInput",
    "LoanDefinition",
    "LoanInstrumentRiskFields",
    "LoanInstrumentValuationFields",
    "MarketData",
    "MarketVolatility",
    "Measure",
    "ModelParameters",
    "NumericalMethodEnum",
    "OffsetDefinition",
    "OptionPricingParameters",
    "OptionSolvingParameters",
    "OptionSolvingTarget",
    "OptionSolvingVariable",
    "OptionSolvingVariableEnum",
    "PartyEnum",
    "Payment",
    "PriceSideWithLastEnum",
    "PrincipalDefinition",
    "Rate",
    "ResetDatesDefinition",
    "ScheduleDefinition",
    "SolvingLegEnum",
    "SolvingMethod",
    "SolvingMethodEnum",
    "SolvingResult",
    "Spot",
    "SpreadCompoundingModeEnum",
    "StepRateDefinition",
    "StrikeTypeEnum",
    "StubIndexReferences",
    "SwapSolvingVariableEnum",
    "TenorBasisSwapOverride",
    "TimeStampEnum",
    "UnitEnum",
    "VanillaIrsOverride",
    "VolCubePoint",
    "VolModelTypeEnum",
    "VolSurfacePoint",
    "VolatilityTypeEnum",
    "ZcTypeEnum",
    "create_from_cbs_template",
    "create_from_ccs_template",
    "create_from_leg_template",
    "create_from_tbs_template",
    "create_from_vanilla_irs_template",
    "delete",
    "load",
    "search",
    "solve",
    "value",
]


def load(
    *,
    resource_id: Optional[str] = None,
    name: Optional[str] = None,
    space: Optional[str] = None,
):
    """
    Load a IrSwap using its name and space

    Parameters
    ----------
    resource_id : str, optional
        The IrSwap id. Or the combination of the space and name of the resource with a slash, e.g. 'HOME/my_resource'.
        Required if name is not provided.
    name : str, optional
        The IrSwap name.
        Required if resource_id is not provided. The name parameter must be specified when the object is first created. Thereafter it is optional.
    space : str, optional
        The space where the IrSwap is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    IrSwap
        The IrSwap instance.

    Examples
    --------
    >>> # execute the search of swap templates
    >>> loaded_template = load(resource_id=swap_templates[0].id)
    >>>
    >>> print(loaded_template)
    <IrSwap space='HOME' name='Dummy_OisSwap_EUR' c594359d‥>

    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _load_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Load IrSwap {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"IrSwap {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource IrSwap not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    elif len(result) > 1:
        logger.warn(f"Found more than one result for name={name!r} and space={space!r}, returning the first one")
    return _load_by_id(result[0].id)


def delete(
    *,
    resource_id: Optional[str] = None,
    name: Optional[str] = None,
    space: Optional[str] = None,
):
    """
    Delete IrSwap instance from the server.

    Parameters
    ----------
    resource_id : str, optional
        The IrSwap resource ID.
        Required if name is not provided.
    name : str, optional
        The IrSwap name.
        Required if resource_id is not provided.
    space : str, optional
        The space where the IrSwap is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    ServiceErrorResponse, optional
        Error response, if applicable, otherwise None

    Examples
    --------
    >>> # Let's delete the instrument we created in HOME space
    >>> from lseg_analytics.instruments.ir_swaps import delete
    >>>
    >>> swap_id = "SOFR_OIS_1Y2Y"
    >>>
    >>> delete(name=swap_id, space="HOME")
    True

    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _delete_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Delete IrSwap {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"IrSwap {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource IrSwap not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    return _delete_by_id(result[0].id)


def create_from_cbs_template(
    *,
    template_reference: str,
    overrides: Optional[CurencyBasisSwapOverride] = None,
    fields: Optional[str] = None,
) -> IrSwap:
    """
    Create an interest rate swap from a currency basis swap template.

    Parameters
    ----------
    template_reference : str
        "The identifier of the currency basis swap template (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    overrides : CurencyBasisSwapOverride, optional
        An object that contains the currency basis swap properties that can be overridden.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    IrSwap
        IrSwap

    Examples
    --------
    >>> swap_from_cbs = create_from_cbs_template(template_reference = "LSEG/GBUSSOSRBS")
    >>> print(swap_from_cbs.definition)
    {'firstLeg': {'rate': {'interestRateType': 'FloatingRate', 'index': 'LSEG/GBP_SONIA_ON_BOE', 'spreadSchedule': [{'rate': {'value': 0.0, 'unit': 'BasisPoint'}}], 'resetDates': {'offset': {'tenor': '0D', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Backward'}}, 'leverage': 1.0}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Quarterly', 'businessDayAdjustment': {'calendars': ['UKG', 'USA'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': ['UKG', 'USA'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_365', 'accrualDayCount': 'Dcb_Actual_365', 'principal': {'currency': 'GBP', 'amount': 10000000.0, 'initialPrincipalExchange': True, 'finalPrincipalExchange': True, 'interimPrincipalExchange': False, 'repaymentCurrency': 'GBP'}, 'payer': 'Party1', 'receiver': 'Party2'}, 'secondLeg': {'rate': {'interestRateType': 'FloatingRate', 'index': 'LSEG/USD_SOFR_ON', 'spreadSchedule': [{'rate': {'value': 0.0, 'unit': 'BasisPoint'}}], 'resetDates': {'offset': {'tenor': '0D', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Backward'}}, 'leverage': 1.0}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Quarterly', 'businessDayAdjustment': {'calendars': ['UKG', 'USA'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': ['UKG', 'USA'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'USD', 'initialPrincipalExchange': True, 'finalPrincipalExchange': True, 'interimPrincipalExchange': False, 'repaymentCurrency': 'USD'}, 'payer': 'Party2', 'receiver': 'Party1'}}

    """

    try:
        logger.info("Calling create_from_cbs_template")

        response = check_and_raise(
            Client().ir_swaps_resource.create_irs_from_cbs_template(
                fields=fields,
                template_reference=template_reference,
                overrides=overrides,
            )
        )

        output = response.data
        logger.info("Called create_from_cbs_template")

        return IrSwap(output)
    except Exception as err:
        logger.error(f"Error create_from_cbs_template {err}")
        check_exception_and_raise(err)


def create_from_ccs_template(
    *,
    template_reference: str,
    overrides: Optional[CrossCurencySwapOverride] = None,
    fields: Optional[str] = None,
) -> IrSwap:
    """
    Create an interest rate swap from a cross currency swap template.

    Parameters
    ----------
    template_reference : str
        "The identifier of the cross currency swap template (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    overrides : CrossCurencySwapOverride, optional
        An object that contains the cross currency swap properties that can be overridden.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    IrSwap
        IrSwap

    Examples
    --------
    >>> swap_from_ccs = create_from_ccs_template(template_reference = "LSEG/CNUSQMSRBS")
    >>> print(swap_from_ccs.definition)
    {'firstLeg': {'rate': {'interestRateType': 'FixedRate', 'rate': {'value': 0.0, 'unit': 'Percentage'}}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Quarterly', 'businessDayAdjustment': {'calendars': ['CHN', 'USA'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': ['CHN', 'USA'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'CNY', 'amount': 10000000.0, 'initialPrincipalExchange': False, 'finalPrincipalExchange': True, 'interimPrincipalExchange': False, 'repaymentCurrency': 'CNY'}, 'payer': 'Party1', 'receiver': 'Party2'}, 'secondLeg': {'rate': {'interestRateType': 'FloatingRate', 'index': 'LSEG/USD_SOFR_ON', 'spreadSchedule': [{'rate': {'value': 0.0, 'unit': 'BasisPoint'}}], 'resetDates': {'offset': {'tenor': '0D', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Backward'}}, 'leverage': 1.0}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Quarterly', 'businessDayAdjustment': {'calendars': ['CHN', 'USA'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': ['CHN', 'USA'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'USD', 'initialPrincipalExchange': False, 'finalPrincipalExchange': True, 'interimPrincipalExchange': False, 'repaymentCurrency': 'USD'}, 'payer': 'Party2', 'receiver': 'Party1'}}

    """

    try:
        logger.info("Calling create_from_ccs_template")

        response = check_and_raise(
            Client().ir_swaps_resource.create_irs_from_ccs_template(
                fields=fields,
                template_reference=template_reference,
                overrides=overrides,
            )
        )

        output = response.data
        logger.info("Called create_from_ccs_template")

        return IrSwap(output)
    except Exception as err:
        logger.error(f"Error create_from_ccs_template {err}")
        check_exception_and_raise(err)


def create_from_leg_template(
    *, first_leg_reference: str, second_leg_reference: str, fields: Optional[str] = None
) -> IrSwap:
    """
    Create an interest rate swap from two interest rate leg templates.

    Parameters
    ----------
    first_leg_reference : str
        The identifier of the template for the instrument's first leg (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    second_leg_reference : str
        The identifier of the template for the instrument's second leg (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    IrSwap
        IrSwap

    Examples
    --------
    >>> swap_from_leg = create_from_leg_template(first_leg_reference = "LSEG/EUR_AB3E_FLT", second_leg_reference = "LSEG/EUR_AB3E_FXD")
    >>> print(swap_from_leg.definition)
    {'firstLeg': {'rate': {'interestRateType': 'FloatingRate', 'index': 'LSEG/EUR_EURIBOR_3M_EMMI', 'spreadSchedule': [{'rate': {'value': 0.0, 'unit': 'BasisPoint'}}], 'resetDates': {'offset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodStartDate', 'direction': 'Backward'}}, 'leverage': 1.0}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Quarterly', 'businessDayAdjustment': {'calendars': ['EMU'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '0D', 'businessDayAdjustment': {'calendars': ['EMU'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'EUR', 'amount': 10000000.0, 'initialPrincipalExchange': False, 'finalPrincipalExchange': False, 'interimPrincipalExchange': False, 'repaymentCurrency': 'EUR'}, 'payer': 'Party2', 'receiver': 'Party1'}, 'secondLeg': {'rate': {'interestRateType': 'FixedRate', 'rate': {'value': 0.0, 'unit': 'Percentage'}}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Annual', 'businessDayAdjustment': {'calendars': ['EMU'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '0D', 'businessDayAdjustment': {'calendars': ['EMU'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_30_360', 'accrualDayCount': 'Dcb_30_360', 'principal': {'currency': 'EUR', 'amount': 10000000.0, 'initialPrincipalExchange': False, 'finalPrincipalExchange': False, 'interimPrincipalExchange': False, 'repaymentCurrency': 'EUR'}, 'payer': 'Party1', 'receiver': 'Party2'}}

    """

    try:
        logger.info("Calling create_from_leg_template")

        response = check_and_raise(
            Client().ir_swaps_resource.create_irs_from_leg_template(
                fields=fields,
                first_leg_reference=first_leg_reference,
                second_leg_reference=second_leg_reference,
            )
        )

        output = response.data
        logger.info("Called create_from_leg_template")

        return IrSwap(output)
    except Exception as err:
        logger.error(f"Error create_from_leg_template {err}")
        check_exception_and_raise(err)


def create_from_tbs_template(
    *,
    template_reference: str,
    overrides: Optional[TenorBasisSwapOverride] = None,
    fields: Optional[str] = None,
) -> IrSwap:
    """
    Create an interest rate swap from a tenor basis swap template.

    Parameters
    ----------
    template_reference : str
        "The identifier of the tenor basis swap template (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    overrides : TenorBasisSwapOverride, optional
        An object that contains the tenor basis swap properties that can be overridden.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    IrSwap
        IrSwap

    Examples
    --------
    >>> swap_from_tbs = create_from_tbs_template(template_reference = "LSEG/CBS_USDSR3LIMM")
    >>> print(swap_from_tbs.definition)
    {'firstLeg': {'rate': {'interestRateType': 'FloatingRate', 'index': 'LSEG/USD_SOFR_ON', 'spreadSchedule': [{'rate': {'value': 0.0, 'unit': 'BasisPoint'}}], 'resetDates': {'offset': {'tenor': '0D', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Backward'}}, 'leverage': 1.0}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Quarterly', 'businessDayAdjustment': {'calendars': ['USA'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': ['USA'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'USD', 'amount': 10000000.0, 'initialPrincipalExchange': False, 'finalPrincipalExchange': False, 'interimPrincipalExchange': False, 'repaymentCurrency': 'USD'}, 'payer': 'Party1', 'receiver': 'Party2'}, 'secondLeg': {'rate': {'interestRateType': 'FloatingRate', 'index': 'LSEG/USD_LIBOR_3M_IBA', 'spreadSchedule': [{'rate': {'value': 0.0, 'unit': 'BasisPoint'}}], 'resetDates': {'offset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodStartDate', 'direction': 'Backward'}}, 'leverage': 1.0}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Quarterly', 'businessDayAdjustment': {'calendars': ['USA'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': ['USA'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'USD', 'amount': 10000000.0, 'initialPrincipalExchange': False, 'finalPrincipalExchange': False, 'interimPrincipalExchange': False, 'repaymentCurrency': 'USD'}, 'payer': 'Party2', 'receiver': 'Party1'}}

    """

    try:
        logger.info("Calling create_from_tbs_template")

        response = check_and_raise(
            Client().ir_swaps_resource.create_irs_from_tbs_template(
                fields=fields,
                template_reference=template_reference,
                overrides=overrides,
            )
        )

        output = response.data
        logger.info("Called create_from_tbs_template")

        return IrSwap(output)
    except Exception as err:
        logger.error(f"Error create_from_tbs_template {err}")
        check_exception_and_raise(err)


def create_from_vanilla_irs_template(
    *,
    template_reference: str,
    overrides: Optional[VanillaIrsOverride] = None,
    fields: Optional[str] = None,
) -> IrSwap:
    """
    Create an interest rate swap from a vanilla irs template.

    Parameters
    ----------
    template_reference : str
        "The identifier of the vanilla interest rate swap template (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    overrides : VanillaIrsOverride, optional
        An object that contains interest rate swap properties that can be overridden.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    IrSwap
        IrSwap

    Examples
    --------
    >>> # build the swap from 'LSEG/OIS_SOFR' template
    >>> fwd_start_sofr = create_from_vanilla_irs_template(template_reference = "LSEG/OIS_SOFR")
    >>>
    >>> fwd_start_sofr_def = IrSwapDefinitionInstrument(definition = fwd_start_sofr.definition)
    >>>
    >>> print(fwd_start_sofr_def)
    {'definition': {'firstLeg': {'rate': {'interestRateType': 'FixedRate', 'rate': {'value': 0.0, 'unit': 'Percentage'}}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Annual', 'businessDayAdjustment': {'calendars': ['USA'], 'convention': 'NextBusinessDay'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': ['USA'], 'convention': 'NextBusinessDay'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'USD', 'amount': 10000000.0, 'initialPrincipalExchange': False, 'finalPrincipalExchange': False, 'interimPrincipalExchange': False, 'repaymentCurrency': 'USD'}, 'payer': 'Party1', 'receiver': 'Party2'}, 'secondLeg': {'rate': {'interestRateType': 'FloatingRate', 'index': 'LSEG/USD_SOFR_ON', 'spreadSchedule': [{'rate': {'value': 0.0, 'unit': 'BasisPoint'}}], 'resetDates': {'offset': {'tenor': '0D', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Backward'}}, 'leverage': 1.0}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Annual', 'businessDayAdjustment': {'calendars': ['USA'], 'convention': 'NextBusinessDay'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': ['USA'], 'convention': 'NextBusinessDay'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'USD', 'amount': 10000000.0, 'initialPrincipalExchange': False, 'finalPrincipalExchange': False, 'interimPrincipalExchange': False, 'repaymentCurrency': 'USD'}, 'payer': 'Party2', 'receiver': 'Party1'}}}

    """

    try:
        logger.info("Calling create_from_vanilla_irs_template")

        response = check_and_raise(
            Client().ir_swaps_resource.create_irs_from_vanilla_irs_template(
                fields=fields,
                template_reference=template_reference,
                overrides=overrides,
            )
        )

        output = response.data
        logger.info("Called create_from_vanilla_irs_template")

        return IrSwap(output)
    except Exception as err:
        logger.error(f"Error create_from_vanilla_irs_template {err}")
        check_exception_and_raise(err)


def _delete_by_id(instrument_id: str) -> bool:
    """
    Delete a IrSwap that exists in the platform.

    Parameters
    ----------
    instrument_id : str
        The instrument identifier.

    Returns
    --------
    bool


    Examples
    --------


    """

    try:
        logger.info(f"Deleting IrSwap with id: {instrument_id}")
        check_and_raise(Client().ir_swap_resource.delete(instrument_id=instrument_id))
        logger.info(f"Deleted IrSwap with id: {instrument_id}")

        return True
    except Exception as err:
        logger.error(f"Error deleting IrSwap with id: {instrument_id}")
        check_exception_and_raise(err)


def _load_by_id(instrument_id: str, fields: Optional[str] = None) -> IrSwap:
    """
    Access a IrSwap existing in the platform (read).

    Parameters
    ----------
    instrument_id : str
        The instrument identifier.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    IrSwap


    Examples
    --------


    """

    try:
        logger.info(f"Opening IrSwap with id: {instrument_id}")

        response = check_and_raise(Client().ir_swap_resource.read(instrument_id=instrument_id, fields=fields))

        output = IrSwap(response.data.definition, response.data.description)

        output._id = response.data.id

        output._location = response.data.location

        return output
    except Exception as err:
        logger.error(f"Error opening IrSwap: {err}")
        check_exception_and_raise(err)


def search(
    *,
    item_per_page: Optional[int] = None,
    page: Optional[int] = None,
    spaces: Optional[List[str]] = None,
    names: Optional[List[str]] = None,
    space_name_sort_order: Optional[Union[str, SortingOrderEnum]] = None,
    tags: Optional[List[str]] = None,
    fields: Optional[str] = None,
) -> List[IrSwapAsCollectionItem]:
    """
    List the IrSwaps existing in the platform (depending on permissions)

    Parameters
    ----------
    item_per_page : int, optional
        A parameter used to select the number of items allowed per page. The valid range is 1-500. If not provided, 50 will be used.
    page : int, optional
        A parameter used to define the page number to display.
    spaces : List[str], optional
        A parameter used to search for platform resources stored in a given space. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space.
        If space is not specified, it will search within all spaces.
    names : List[str], optional
        A parameter used to search for platform resources with given names.
    space_name_sort_order : Union[str, SortingOrderEnum], optional
        A parameter used to sort platform resources by name based on a defined order.
    tags : List[str], optional
        A parameter used to search for platform resources with given tags.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    List[IrSwapAsCollectionItem]
        A model template defining the partial description of the resource returned by the GET list service.

    Examples
    --------
    >>> # execute the search of swap templates
    >>> swap_templates = search()
    >>>
    >>> print(swap_templates)
    [{'type': 0, 'id': 'c594359d-f1ca-472a-af1a-915b6e742b2f', 'location': {'space': 'HOME', 'name': 'Dummy_OisSwap_EUR'}, 'description': {'summary': '', 'tags': []}}, {'type': 0, 'id': '3aafd38f-9aa7-4111-81ea-171dc62033c2', 'location': {'space': 'HOME', 'name': 'TestFxSp17442139226868882'}, 'description': {'summary': 'Test description', 'tags': ['tag1', 'tag2']}}, {'type': 0, 'id': 'bcd2386c-2402-4681-8190-5b1bf6d5eca7', 'location': {'space': 'HOME', 'name': 'TestIrSwap17500707400624428'}, 'description': {'summary': 'Test ir_swap_saved description', 'tags': ['tag1', 'tag2']}}, {'type': 0, 'id': '4f276496-ae11-4ce0-9870-cc3262fae588', 'location': {'space': 'HOME', 'name': 'TestSwapResource3'}, 'description': {'summary': '(overwritten)', 'tags': ['test']}}, {'type': 0, 'id': 'a09cf5b6-9d05-4aea-b7c4-a167e0cfc6e9', 'location': {'space': 'MYSPACE', 'name': 'TestFxSpotClone17442142162523232'}, 'description': {'summary': 'Test ir_swap_saved description', 'tags': ['tag1', 'tag2']}}, {'type': 0, 'id': '13fa9515-47cb-4742-ae92-f83ee8b9bdb6', 'location': {'space': 'MYSPACE', 'name': 'TestFxSpotClone17442143814989772'}, 'description': {'summary': 'Test ir_swap_saved description', 'tags': ['tag1', 'tag2']}}]

    """

    try:
        logger.info("Calling search")

        response = check_and_raise(
            Client().ir_swaps_resource.list(
                item_per_page=item_per_page,
                page=page,
                spaces=spaces,
                names=names,
                space_name_sort_order=space_name_sort_order,
                tags=tags,
                fields=fields,
            )
        )

        output = response.data
        logger.info("Called search")

        return output
    except Exception as err:
        logger.error(f"Error search. {err}")
        check_exception_and_raise(err)


def solve(
    *,
    definitions: List[IrSwapDefinitionInstrument],
    pricing_preferences: Optional[IrPricingParameters] = None,
    market_data: Optional[MarketData] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> IrSwapInstrumentSolveResponseFieldsResponseData:
    """
    Calculate the price of a swap (e.g., fixed rate) provided in the request so that a chosen property (e.g., market value, duration) equals a target value.

    Parameters
    ----------
    definitions : List[IrSwapDefinitionInstrument]

    pricing_preferences : IrPricingParameters, optional
        The parameters that control the computation of the analytics.
    market_data : MarketData, optional
        The market data used to compute the analytics.
    return_market_data : bool, optional
        Boolean property to determine if undelying market data used for calculation should be returned in the response
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    IrSwapInstrumentSolveResponseFieldsResponseData


    Examples
    --------
    >>> # build the swap from 'LSEG/OIS_SOFR' template
    >>> fwd_start_sofr = create_from_vanilla_irs_template(template_reference = "LSEG/OIS_SOFR")
    >>>
    >>> # prepare the Definition Instrument
    >>> fwd_start_sofr_def = IrSwapDefinitionInstrument(definition = fwd_start_sofr.definition)
    >>>
    >>> # set a solving variable between first and second leg and Fixed Rate or Spread
    >>> solving_variable = IrSwapSolvingVariable(leg='FirstLeg', name='FixedRate')
    >>>
    >>> # Apply solving target(s)
    >>> solving_target=IrSwapSolvingTarget(market_value=IrMeasure(value=0.0))
    >>>
    >>> # Setup the solving parameter object
    >>> solving_parameters = IrSwapSolvingParameters(variable=solving_variable, target=solving_target)
    >>>
    >>> # instantiate pricing parameters
    >>> pricing_parameters = IrPricingParameters(solving_parameters=solving_parameters)
    >>>
    >>> # solve the swap par rate
    >>> solving_response_general = solve(
    >>>     definitions=[fwd_start_sofr_def],
    >>>     pricing_preferences=pricing_parameters
    >>>     )
    >>>
    >>> print(solving_response_general)
    {'analytics': [{'solving': {'result': 3.7216567024852716}, 'description': {'instrumentTag': '', 'instrumentDescription': 'Pay USD Annual 3.72% vs Receive USD Annual +0bp SOFR 2035-07-02', 'startDate': '2025-07-01', 'endDate': '2035-07-02', 'tenor': '10Y'}, 'valuation': {'accrued': {'value': 0.0, 'percent': 0.0, 'dealCurrency': {'value': 0.0, 'currency': 'USD'}, 'reportCurrency': {'value': 0.0, 'currency': 'USD'}}, 'marketValue': {'value': -6.61704689264297e-07, 'dealCurrency': {'value': -6.61704689264297e-07, 'currency': 'USD'}, 'reportCurrency': {'value': -6.61704689264297e-07, 'currency': 'USD'}}, 'cleanMarketValue': {'value': -6.61704689264297e-07, 'dealCurrency': {'value': -6.61704689264297e-07, 'currency': 'USD'}, 'reportCurrency': {'value': -6.61704689264297e-07, 'currency': 'USD'}}}, 'risk': {'duration': {'value': -8.50836369545246}, 'modifiedDuration': {'value': -8.19385349862701}, 'benchmarkHedgeNotional': {'value': -9296952.34979707, 'currency': 'USD'}, 'annuity': {'value': -8371.09533760371, 'dealCurrency': {'value': -8371.09533760371, 'currency': 'USD'}, 'reportCurrency': {'value': -8371.09533760371, 'currency': 'USD'}}, 'dv01': {'value': -8188.52452793717, 'bp': -8.18852452793717, 'dealCurrency': {'value': -8188.52452793717, 'currency': 'USD'}, 'reportCurrency': {'value': -8188.52452793717, 'currency': 'USD'}}, 'pv01': {'value': -8188.52452793857, 'bp': -8.18852452793857, 'dealCurrency': {'value': -8188.52452793857, 'currency': 'USD'}, 'reportCurrency': {'value': -8188.52452793857, 'currency': 'USD'}}, 'br01': {'value': 0.0, 'dealCurrency': {'value': 0.0, 'currency': 'USD'}, 'reportCurrency': {'value': 0.0, 'currency': 'USD'}}}, 'firstLeg': {'description': {'legTag': 'PaidLeg', 'legDescription': 'Pay USD Annual 3.72%', 'interestType': 'Fixed', 'currency': 'USD', 'startDate': '2025-07-01', 'endDate': '2035-07-02', 'index': ''}, 'valuation': {'accrued': {'value': 0.0, 'percent': 0.0, 'dealCurrency': {'value': 0.0, 'currency': 'USD'}, 'reportCurrency': {'value': 0.0, 'currency': 'USD'}}, 'marketValue': {'value': 3115434.307033646, 'dealCurrency': {'value': 3115434.307033646, 'currency': 'USD'}, 'reportCurrency': {'value': 3115434.307033646, 'currency': 'USD'}}, 'cleanMarketValue': {'value': 3115434.307033646, 'dealCurrency': {'value': 3115434.307033646, 'currency': 'USD'}, 'reportCurrency': {'value': 3115434.307033646, 'currency': 'USD'}}}, 'risk': {'duration': {'value': 8.508363695452463}, 'modifiedDuration': {'value': 8.209314246370457}, 'benchmarkHedgeNotional': {'value': 0.0, 'currency': 'USD'}, 'annuity': {'value': 8371.095337603707, 'dealCurrency': {'value': 8371.095337603707, 'currency': 'USD'}, 'reportCurrency': {'value': 8371.095337603707, 'currency': 'USD'}}, 'dv01': {'value': 8203.97522059828, 'bp': 8.20397522059828, 'dealCurrency': {'value': 8203.97522059828, 'currency': 'USD'}, 'reportCurrency': {'value': 8203.97522059828, 'currency': 'USD'}}, 'pv01': {'value': 1567.2670857892372, 'bp': 1.5672670857892372, 'dealCurrency': {'value': 1567.2670857892372, 'currency': 'USD'}, 'reportCurrency': {'value': 1567.2670857892372, 'currency': 'USD'}}, 'br01': {'value': 0.0, 'dealCurrency': {'value': 0.0, 'currency': 'USD'}, 'reportCurrency': {'value': 0.0, 'currency': 'USD'}}}}, 'secondLeg': {'description': {'legTag': 'ReceivedLeg', 'legDescription': 'Receive USD Annual +0bp SOFR', 'interestType': 'Float', 'currency': 'USD', 'startDate': '2025-07-01', 'endDate': '2035-07-02', 'index': 'SOFR'}, 'valuation': {'accrued': {'value': 0.0, 'percent': 0.0, 'dealCurrency': {'value': 0.0, 'currency': 'USD'}, 'reportCurrency': {'value': 0.0, 'currency': 'USD'}}, 'marketValue': {'value': 3115434.307032984, 'dealCurrency': {'value': 3115434.307032984, 'currency': 'USD'}, 'reportCurrency': {'value': 3115434.307032984, 'currency': 'USD'}}, 'cleanMarketValue': {'value': 3115434.307032984, 'dealCurrency': {'value': 3115434.307032984, 'currency': 'USD'}, 'reportCurrency': {'value': 3115434.307032984, 'currency': 'USD'}}}, 'risk': {'duration': {'value': 0.0}, 'modifiedDuration': {'value': 0.015460747743442397}, 'benchmarkHedgeNotional': {'value': 0.0, 'currency': 'USD'}, 'annuity': {'value': 0.0, 'dealCurrency': {'value': 0.0, 'currency': 'USD'}, 'reportCurrency': {'value': 0.0, 'currency': 'USD'}}, 'dv01': {'value': 15.450692661106586, 'bp': 0.015450692661106586, 'dealCurrency': {'value': 15.450692661106586, 'currency': 'USD'}, 'reportCurrency': {'value': 15.450692661106586, 'currency': 'USD'}}, 'pv01': {'value': -6621.257442149334, 'bp': -6.621257442149334, 'dealCurrency': {'value': -6621.257442149334, 'currency': 'USD'}, 'reportCurrency': {'value': -6621.257442149334, 'currency': 'USD'}}, 'br01': {'value': 0.0, 'dealCurrency': {'value': 0.0, 'currency': 'USD'}, 'reportCurrency': {'value': 0.0, 'currency': 'USD'}}}}}]}

    """

    try:
        logger.info("Calling solve")

        response = check_and_raise(
            Client().ir_swaps_resource.solve(
                fields=fields,
                definitions=definitions,
                pricing_preferences=pricing_preferences,
                market_data=market_data,
                return_market_data=return_market_data,
            )
        )

        output = response.data
        logger.info("Called solve")

        return output
    except Exception as err:
        logger.error(f"Error solve. {err}")
        check_exception_and_raise(err)


def value(
    *,
    definitions: List[IrSwapDefinitionInstrument],
    pricing_preferences: Optional[IrPricingParameters] = None,
    market_data: Optional[MarketData] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> IrSwapInstrumentValuationResponseFieldsResponseData:
    """
    Calculate the market value of the swaps provided in the request.

    Parameters
    ----------
    definitions : List[IrSwapDefinitionInstrument]

    pricing_preferences : IrPricingParameters, optional
        The parameters that control the computation of the analytics.
    market_data : MarketData, optional
        The market data used to compute the analytics.
    return_market_data : bool, optional
        Boolean property to determine if undelying market data used for calculation should be returned in the response
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    IrSwapInstrumentValuationResponseFieldsResponseData


    Examples
    --------
    >>> # build the swap from 'LSEG/OIS_SOFR' template
    >>> fwd_start_sofr = create_from_vanilla_irs_template(template_reference = "LSEG/OIS_SOFR")
    >>>
    >>> fwd_start_sofr_def = IrSwapDefinitionInstrument(definition = fwd_start_sofr.definition)
    >>>
    >>> # instantiate pricing parameters
    >>> pricing_parameters = IrPricingParameters()
    >>>
    >>> # value the swap
    >>> valuation_response = value(
    >>>     definitions=[fwd_start_sofr_def],
    >>>     pricing_preferences=pricing_parameters
    >>> )
    >>>
    >>> print(valuation_response.analytics[0].valuation)
    {'accrued': {'value': 0.0, 'percent': 0.0, 'dealCurrency': {'value': 0.0, 'currency': 'USD'}, 'reportCurrency': {'value': 0.0, 'currency': 'USD'}}, 'marketValue': {'value': 3115442.42956706, 'dealCurrency': {'value': 3115442.42956706, 'currency': 'USD'}, 'reportCurrency': {'value': 3115442.42956706, 'currency': 'USD'}}, 'cleanMarketValue': {'value': 3115442.42956706, 'dealCurrency': {'value': 3115442.42956706, 'currency': 'USD'}, 'reportCurrency': {'value': 3115442.42956706, 'currency': 'USD'}}}

    """

    try:
        logger.info("Calling value")

        response = check_and_raise(
            Client().ir_swaps_resource.value(
                fields=fields,
                definitions=definitions,
                pricing_preferences=pricing_preferences,
                market_data=market_data,
                return_market_data=return_market_data,
            )
        )

        output = response.data
        logger.info("Called value")

        return output
    except Exception as err:
        logger.error(f"Error value. {err}")
        check_exception_and_raise(err)
