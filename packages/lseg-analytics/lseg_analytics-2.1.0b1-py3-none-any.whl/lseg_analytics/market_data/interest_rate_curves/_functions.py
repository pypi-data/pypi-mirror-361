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
    Amount,
    BidAskMidSimpleValues,
    BusinessDayAdjustmentDefinition,
    CityNameEnum,
    CompoundingType,
    ConvexityAdjustment,
    Curve,
    CurveCalculationParameters,
    CurvePointRelatedInstruments,
    DateMovingConvention,
    DayCountBasis,
    DepositConstituentDefinition,
    DepositIrConstituent,
    Description,
    DividendCurve,
    DividendCurvePoint,
    ExtrapolationMode,
    FieldDefinition,
    FieldValue,
    FloatingRateIndexConstituent,
    FloatingRateIndexConstituentDefinition,
    ForwardRateAgreementConstituent,
    ForwardRateAgreementConstituentDefinition,
    FuturesQuotationMode,
    FxForwardCurveCalculationParameters,
    FxForwardCurveCalculationPreferences,
    FxForwardCurveInterpolationMode,
    FxOutrightCurve,
    FxOutrightCurvePoint,
    InnerError,
    InterestRateCurveCalculationParameters,
    InterestRateCurveInfo,
    InterestRateCurveInterpolationMode,
    InterestRateSwapConstituent,
    InterestRateSwapConstituentDefinition,
    IrConstituent,
    IrCurveDataOnResourceResponseData,
    IrCurveDataResponseData,
    IrCurveDataResponseWithError,
    IrCurveDefinition,
    IrCurveDefinitionInstrument,
    IrZcCurve,
    IrZcCurveDescription,
    IrZcCurvePoint,
    Location,
    OvernightIndexSwapConstituent,
    OvernightIndexSwapConstituentDefinition,
    PriceSide,
    Quote,
    QuoteDefinition,
    Rate,
    RoundingDefinition,
    RoundingModeEnum,
    ServiceError,
    SortingOrderEnum,
    StirFutureConstituent,
    StirFutureConstituentDefinition,
    TenorBasisSwapConstituent,
    TenorBasisSwapConstituentDefinition,
    UnitEnum,
    ValuationTime,
    Values,
    YearBasisEnum,
)

from ._interest_rate_curve import InterestRateCurve
from ._logger import logger

__all__ = [
    "Amount",
    "BusinessDayAdjustmentDefinition",
    "CityNameEnum",
    "CompoundingType",
    "ConvexityAdjustment",
    "Curve",
    "CurveCalculationParameters",
    "CurvePointRelatedInstruments",
    "DepositConstituentDefinition",
    "DepositIrConstituent",
    "DividendCurve",
    "DividendCurvePoint",
    "FloatingRateIndexConstituent",
    "FloatingRateIndexConstituentDefinition",
    "ForwardRateAgreementConstituent",
    "ForwardRateAgreementConstituentDefinition",
    "FuturesQuotationMode",
    "FxForwardCurveCalculationParameters",
    "FxForwardCurveCalculationPreferences",
    "FxOutrightCurve",
    "FxOutrightCurvePoint",
    "InterestRateCurve",
    "InterestRateCurveCalculationParameters",
    "InterestRateCurveInfo",
    "InterestRateCurveInterpolationMode",
    "InterestRateSwapConstituent",
    "InterestRateSwapConstituentDefinition",
    "IrConstituent",
    "IrCurveDataOnResourceResponseData",
    "IrCurveDataResponseData",
    "IrCurveDataResponseWithError",
    "IrCurveDefinition",
    "IrCurveDefinitionInstrument",
    "IrZcCurve",
    "IrZcCurveDescription",
    "IrZcCurvePoint",
    "OvernightIndexSwapConstituent",
    "OvernightIndexSwapConstituentDefinition",
    "PriceSide",
    "Rate",
    "RoundingDefinition",
    "RoundingModeEnum",
    "StirFutureConstituent",
    "StirFutureConstituentDefinition",
    "TenorBasisSwapConstituent",
    "TenorBasisSwapConstituentDefinition",
    "UnitEnum",
    "ValuationTime",
    "calculate",
    "delete",
    "load",
    "search",
]


def load(
    *,
    resource_id: Optional[str] = None,
    name: Optional[str] = None,
    space: Optional[str] = None,
):
    """
    Load a InterestRateCurve using its name and space

    Parameters
    ----------
    resource_id : str, optional
        The InterestRateCurve id. Or the combination of the space and name of the resource with a slash, e.g. 'HOME/my_resource'.
        Required if name is not provided.
    name : str, optional
        The InterestRateCurve name.
        Required if resource_id is not provided. The name parameter must be specified when the object is first created. Thereafter it is optional.
    space : str, optional
        The space where the InterestRateCurve is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    InterestRateCurve
        The InterestRateCurve instance.

    Examples
    --------


    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _load_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Load InterestRateCurve {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"InterestRateCurve {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource InterestRateCurve not found by identifier name={name} space={space}")
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
    Delete InterestRateCurve instance from the server.

    Parameters
    ----------
    resource_id : str, optional
        The InterestRateCurve resource ID.
        Required if name is not provided.
    name : str, optional
        The InterestRateCurve name.
        Required if resource_id is not provided.
    space : str, optional
        The space where the InterestRateCurve is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    ServiceErrorResponse, optional
        Error response, if applicable, otherwise None

    Examples
    --------


    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _delete_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Delete InterestRateCurve {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"InterestRateCurve {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource InterestRateCurve not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    return _delete_by_id(result[0].id)


def calculate(
    *,
    definitions: List[IrCurveDefinitionInstrument],
    pricing_preferences: Optional[InterestRateCurveCalculationParameters] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> IrCurveDataResponseData:
    """
    Calculate the points of the interest rate curve by requesting a custom definition (on the fly).

    Parameters
    ----------
    definitions : List[IrCurveDefinitionInstrument]

    pricing_preferences : InterestRateCurveCalculationParameters, optional
        The parameters that control the computation of the analytics.
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
    IrCurveDataResponseData


    Examples
    --------


    """

    try:
        logger.info("Calling calculate")

        response = check_and_raise(
            Client().interest_rate_curves_service.calculate(
                fields=fields,
                definitions=definitions,
                pricing_preferences=pricing_preferences,
                return_market_data=return_market_data,
            )
        )

        output = response.data
        logger.info("Called calculate")

        return output
    except Exception as err:
        logger.error(f"Error calculate. {err}")
        check_exception_and_raise(err)


def _delete_by_id(curve_id: str) -> bool:
    """
    Delete a InterestRateCurve that exists in the platform.

    Parameters
    ----------
    curve_id : str
        The curve identifier.

    Returns
    --------
    bool


    Examples
    --------


    """

    try:
        logger.info(f"Deleting InterestRateCurve with id: {curve_id}")
        check_and_raise(Client().interest_rate_curve_service.delete(curve_id=curve_id))
        logger.info(f"Deleted InterestRateCurve with id: {curve_id}")

        return True
    except Exception as err:
        logger.error(f"Error deleting InterestRateCurve with id: {curve_id}")
        check_exception_and_raise(err)


def _load_by_id(curve_id: str, fields: Optional[str] = None) -> InterestRateCurve:
    """
    Access a InterestRateCurve existing in the platform (read).

    Parameters
    ----------
    curve_id : str
        The curve identifier.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    InterestRateCurve


    Examples
    --------


    """

    try:
        logger.info(f"Opening InterestRateCurve with id: {curve_id}")

        response = check_and_raise(Client().interest_rate_curve_service.read(curve_id=curve_id, fields=fields))

        output = InterestRateCurve(response.data.definition, response.data.description)

        output._id = response.data.id

        output._location = response.data.location

        return output
    except Exception as err:
        logger.error(f"Error opening InterestRateCurve: {err}")
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
) -> List[InterestRateCurveInfo]:
    """
    List the InterestRateCurves existing in the platform (depending on permissions)

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
    List[InterestRateCurveInfo]
        A model template defining the partial description of the resource returned by the GET list service.

    Examples
    --------


    """

    try:
        logger.info("Calling search")

        response = check_and_raise(
            Client().interest_rate_curves_service.list(
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
