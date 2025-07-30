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
    Description,
    InterestRateCurveCalculationParameters,
    InterestRateCurveInfo,
    IrCurveDataOnResourceResponseData,
    IrCurveDataResponseData,
    IrCurveDefinition,
    IrCurveDefinitionInstrument,
    Location,
    ResourceType,
    SortingOrderEnum,
)

from ._logger import logger


class InterestRateCurve(ResourceBase):
    """
    InterestRateCurve object.

    Contains all the necessary information to identify and define a InterestRateCurve instance.

    Attributes
    ----------
    type : Union[str, ResourceType], optional
        Property defining the type of the resource.
    id : str, optional
        Unique identifier of the InterestRateCurve.
    location : Location
        Object defining the location of the InterestRateCurve in the platform.
    description : Description, optional
        Object defining metadata for the InterestRateCurve.
    definition : IrCurveDefinition
        Object defining the InterestRateCurve.

    See Also
    --------
    InterestRateCurve.calculate : Calculate the points of the interest rate curve that exists in the platform.

    Examples
    --------


    """

    _definition_class = IrCurveDefinition

    def __init__(self, definition: IrCurveDefinition, description: Optional[Description] = None):
        """
        InterestRateCurve constructor

        Parameters
        ----------
        definition : IrCurveDefinition
            Object defining the InterestRateCurve.
        description : Description, optional
            Object defining metadata for the InterestRateCurve.

        Examples
        --------


        """
        self.definition: IrCurveDefinition = definition
        self.type: Optional[Union[str, ResourceType]] = "InterestRateCurve"
        if description is None:
            self.description: Optional[Description] = Description(tags=[])
        else:
            self.description: Optional[Description] = description
        self._location: Location = Location(name="")
        self._id: Optional[str] = None

    @property
    def id(self):
        """
        Returns the InterestRateCurve id

        Parameters
        ----------


        Returns
        --------
        str
            Unique identifier of the InterestRateCurve.

        Examples
        --------


        """
        return self._id

    @id.setter
    def id(self, value):
        raise AttributeError("id is read only")

    @property
    def location(self):
        """
        Returns the InterestRateCurve location

        Parameters
        ----------


        Returns
        --------
        Location
            Object defining the location of the InterestRateCurve in the platform.

        Examples
        --------


        """
        return self._location

    @location.setter
    def location(self, value):
        raise AttributeError("location is read only")

    def calculate(
        self,
        *,
        pricing_preferences: Optional[InterestRateCurveCalculationParameters] = None,
        return_market_data: Optional[bool] = None,
        fields: Optional[str] = None,
    ) -> IrCurveDataOnResourceResponseData:
        """
        Calculate the points of the interest rate curve that exists in the platform.

        Parameters
        ----------
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
        IrCurveDataOnResourceResponseData


        Examples
        --------


        """

        try:
            logger.info("Calling calculate for interestRateCurve with id")
            check_id(self._id)

            response = check_and_raise(
                Client().interest_rate_curve_service.calculate(
                    curve_id=self._id,
                    fields=fields,
                    pricing_preferences=pricing_preferences,
                    return_market_data=return_market_data,
                )
            )

            output = response.data
            logger.info("Called calculate for interestRateCurve with id")

            return output
        except Exception as err:
            logger.error(f"Error calculate for interestRateCurve with id. {err}")
            check_exception_and_raise(err)

    def _create(self, location: Location) -> None:
        """
        Save a new InterestRateCurve in the platform

        Parameters
        ----------
        location : Location
            Object defining the location of the InterestRateCurve in the platform.

        Returns
        --------
        None


        Examples
        --------


        """

        try:
            logger.info("Creating InterestRateCurve")

            response = check_and_raise(
                Client().interest_rate_curves_service.create(
                    location=location,
                    description=self.description,
                    definition=self.definition,
                )
            )

            self._id = response.data.id

            self._location = response.data.location
            logger.info(f"InterestRateCurve created with id: {self._id}")
        except Exception as err:
            logger.error(f"Error creating InterestRateCurve: {err}")
            raise err

    def _overwrite(self) -> None:
        """
        Overwrite a InterestRateCurve that exists in the platform.

        Parameters
        ----------


        Returns
        --------
        None


        Examples
        --------


        """
        logger.info(f"Overwriting InterestRateCurve with id: {self._id}")
        check_and_raise(
            Client().interest_rate_curve_service.overwrite(
                curve_id=self._id,
                location=self._location,
                description=self.description,
                definition=self.definition,
            )
        )

    def save(self, *, name: Optional[str] = None, space: Optional[str] = None) -> bool:
        """
        Save InterestRateCurve instance in the platform store.

        Parameters
        ----------
        name : str, optional
            The InterestRateCurve name. The name parameter must be specified when the object is first created. Thereafter it is optional. For first creation, name must follow the pattern '^[A-Za-z0-9_]{1,50}$'.
        space : str, optional
            The space where the InterestRateCurve is stored. Space is like a namespace where resources are stored. By default there are two spaces:
            LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

        Returns
        --------
        bool, optional
            True, if saved successfully, otherwise None


        Examples
        --------


        """
        try:
            logger.info("Saving InterestRateCurve")
            if self._id:
                if name and name != self._location.name or (space and space != self._location.space):
                    raise LibraryException("When saving an existing resource, you may not change the name or space")
                self._overwrite()
                logger.info("InterestRateCurve saved")
            elif name:
                location = Location(name=name, space=space)
                self._create(location=location)
                logger.info(f"InterestRateCurve saved to space: {self._location.space} name: {self._location.name}")
            else:
                raise LibraryException("When saving for the first time, name must be defined.")
            return True
        except Exception as err:
            logger.info("InterestRateCurve save failed")
            check_exception_and_raise(err)

    def clone(self) -> "InterestRateCurve":
        """
        Return the same object, without id, name and space

        Parameters
        ----------


        Returns
        --------
        InterestRateCurve
            The cloned InterestRateCurve object


        Examples
        --------


        """
        definition = self._definition_class()
        definition._data = copy.deepcopy(self.definition._data)
        description = None
        if self.description:
            description = Description()
            description._data = copy.deepcopy(self.description._data)
        return self.__class__(definition=definition, description=description)
