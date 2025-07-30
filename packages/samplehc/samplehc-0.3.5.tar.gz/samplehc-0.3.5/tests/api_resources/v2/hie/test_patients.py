# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.hie import PatientRetrieveDocumentsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPatients:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_documents(self, client: SampleHealthcare) -> None:
        patient = client.v2.hie.patients.retrieve_documents(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        )
        assert_matches_type(PatientRetrieveDocumentsResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_documents_with_all_params(self, client: SampleHealthcare) -> None:
        patient = client.v2.hie.patients.retrieve_documents(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                    "address_line2": "addressLine2",
                    "country": "country",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
            contact=[
                {
                    "email": "email",
                    "phone": "phone",
                }
            ],
            personal_identifiers=[
                {
                    "type": "driversLicense",
                    "value": "value",
                    "state": "state",
                }
            ],
        )
        assert_matches_type(PatientRetrieveDocumentsResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_documents(self, client: SampleHealthcare) -> None:
        response = client.v2.hie.patients.with_raw_response.retrieve_documents(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientRetrieveDocumentsResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_documents(self, client: SampleHealthcare) -> None:
        with client.v2.hie.patients.with_streaming_response.retrieve_documents(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientRetrieveDocumentsResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPatients:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_documents(self, async_client: AsyncSampleHealthcare) -> None:
        patient = await async_client.v2.hie.patients.retrieve_documents(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        )
        assert_matches_type(PatientRetrieveDocumentsResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_documents_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        patient = await async_client.v2.hie.patients.retrieve_documents(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                    "address_line2": "addressLine2",
                    "country": "country",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
            contact=[
                {
                    "email": "email",
                    "phone": "phone",
                }
            ],
            personal_identifiers=[
                {
                    "type": "driversLicense",
                    "value": "value",
                    "state": "state",
                }
            ],
        )
        assert_matches_type(PatientRetrieveDocumentsResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_documents(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.hie.patients.with_raw_response.retrieve_documents(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientRetrieveDocumentsResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_documents(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.hie.patients.with_streaming_response.retrieve_documents(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientRetrieveDocumentsResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True
