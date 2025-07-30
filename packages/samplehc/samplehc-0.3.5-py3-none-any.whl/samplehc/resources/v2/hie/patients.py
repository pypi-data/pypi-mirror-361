# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v2.hie import patient_retrieve_documents_params
from ....types.v2.hie.patient_retrieve_documents_response import PatientRetrieveDocumentsResponse

__all__ = ["PatientsResource", "AsyncPatientsResource"]


class PatientsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PatientsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return PatientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PatientsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return PatientsResourceWithStreamingResponse(self)

    def retrieve_documents(
        self,
        *,
        address: Iterable[patient_retrieve_documents_params.Address],
        dob: str,
        external_id: str,
        first_name: str,
        gender_at_birth: Literal["M", "F", "O", "U"],
        last_name: str,
        contact: Iterable[patient_retrieve_documents_params.Contact] | NotGiven = NOT_GIVEN,
        personal_identifiers: Iterable[patient_retrieve_documents_params.PersonalIdentifier] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientRetrieveDocumentsResponse:
        """
        Upserts a patient and triggers jobs to get patient FHIR data and documents from
        HIE.

        Args:
          address: An array of Address objects, representing the Patient's current and/or previous
              addresses. May be empty.

          dob: The Patient's date of birth (DOB), formatted `YYYY-MM-DD` as per ISO 8601.

          external_id: An external Patient ID that you store and can use to reference this Patient.

          first_name: The Patient's first name(s).

          gender_at_birth: The Patient's gender at birth, can be one of `M` or `F` or `O` or `U`. Use `O`
              (other) when the patient's gender is known but it is not `M` or `F`, i.e
              intersex or hermaphroditic. Use `U` (unknown) when the patient's gender is not
              known.

          last_name: The Patient's last name(s).

          contact: An array of Contact objects, representing the Patient's current and/or previous
              contact information. May be empty.

          personal_identifiers: An array of the Patient's personal IDs, such as a driver's license or SSN. May
              be empty.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/hie/patient/documents",
            body=maybe_transform(
                {
                    "address": address,
                    "dob": dob,
                    "external_id": external_id,
                    "first_name": first_name,
                    "gender_at_birth": gender_at_birth,
                    "last_name": last_name,
                    "contact": contact,
                    "personal_identifiers": personal_identifiers,
                },
                patient_retrieve_documents_params.PatientRetrieveDocumentsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientRetrieveDocumentsResponse,
        )


class AsyncPatientsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPatientsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPatientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPatientsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncPatientsResourceWithStreamingResponse(self)

    async def retrieve_documents(
        self,
        *,
        address: Iterable[patient_retrieve_documents_params.Address],
        dob: str,
        external_id: str,
        first_name: str,
        gender_at_birth: Literal["M", "F", "O", "U"],
        last_name: str,
        contact: Iterable[patient_retrieve_documents_params.Contact] | NotGiven = NOT_GIVEN,
        personal_identifiers: Iterable[patient_retrieve_documents_params.PersonalIdentifier] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientRetrieveDocumentsResponse:
        """
        Upserts a patient and triggers jobs to get patient FHIR data and documents from
        HIE.

        Args:
          address: An array of Address objects, representing the Patient's current and/or previous
              addresses. May be empty.

          dob: The Patient's date of birth (DOB), formatted `YYYY-MM-DD` as per ISO 8601.

          external_id: An external Patient ID that you store and can use to reference this Patient.

          first_name: The Patient's first name(s).

          gender_at_birth: The Patient's gender at birth, can be one of `M` or `F` or `O` or `U`. Use `O`
              (other) when the patient's gender is known but it is not `M` or `F`, i.e
              intersex or hermaphroditic. Use `U` (unknown) when the patient's gender is not
              known.

          last_name: The Patient's last name(s).

          contact: An array of Contact objects, representing the Patient's current and/or previous
              contact information. May be empty.

          personal_identifiers: An array of the Patient's personal IDs, such as a driver's license or SSN. May
              be empty.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/hie/patient/documents",
            body=await async_maybe_transform(
                {
                    "address": address,
                    "dob": dob,
                    "external_id": external_id,
                    "first_name": first_name,
                    "gender_at_birth": gender_at_birth,
                    "last_name": last_name,
                    "contact": contact,
                    "personal_identifiers": personal_identifiers,
                },
                patient_retrieve_documents_params.PatientRetrieveDocumentsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientRetrieveDocumentsResponse,
        )


class PatientsResourceWithRawResponse:
    def __init__(self, patients: PatientsResource) -> None:
        self._patients = patients

        self.retrieve_documents = to_raw_response_wrapper(
            patients.retrieve_documents,
        )


class AsyncPatientsResourceWithRawResponse:
    def __init__(self, patients: AsyncPatientsResource) -> None:
        self._patients = patients

        self.retrieve_documents = async_to_raw_response_wrapper(
            patients.retrieve_documents,
        )


class PatientsResourceWithStreamingResponse:
    def __init__(self, patients: PatientsResource) -> None:
        self._patients = patients

        self.retrieve_documents = to_streamed_response_wrapper(
            patients.retrieve_documents,
        )


class AsyncPatientsResourceWithStreamingResponse:
    def __init__(self, patients: AsyncPatientsResource) -> None:
        self._patients = patients

        self.retrieve_documents = async_to_streamed_response_wrapper(
            patients.retrieve_documents,
        )
