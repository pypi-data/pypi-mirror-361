# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..types import project_list_params, project_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, strip_not_given, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.project_list_response import ProjectListResponse
from ..types.project_create_response import ProjectCreateResponse
from ..types.project_delete_response import ProjectDeleteResponse

__all__ = ["ProjectsResource", "AsyncProjectsResource"]


class ProjectsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ProjectsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Trellis-insights/trellis-python-sdk#accessing-raw-response-data-eg-headers
        """
        return ProjectsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProjectsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Trellis-insights/trellis-python-sdk#with_streaming_response
        """
        return ProjectsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProjectCreateResponse:
        """
        Create a new project.

        Args: proj_name (str): The name of the project.

        Args:
          api_version: Pass in an API version to guarantee a consistent response format.

              The latest version should be used for all new API calls. Existing API calls
              should be updated to the latest version when possible.

              **Valid versions:**

              - Latest API version (recommended): `2025-03`

              - Previous API version (maintenance mode): `2025-02`

              If no API version header is included, the response format is considered unstable
              and could change without notice (not recommended).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return self._post(
            "/v1/projects/create",
            body=maybe_transform({"name": name}, project_create_params.ProjectCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProjectCreateResponse,
        )

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        order_by: Literal["updated_at", "created_at", "id"] | NotGiven = NOT_GIVEN,
        proj_ids: List[str] | NotGiven = NOT_GIVEN,
        search_term: str | NotGiven = NOT_GIVEN,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProjectListResponse:
        """
        Retrieve a list of projects.

        Parameters:

        - proj_ids (list[str], optional): A list of project ids. If not provided, all
          projects will be retrieved.

        Returns:

        - dict: A dict containing the status message and the list of project names.

        Args:
          order: An enumeration.

          order_by: An enumeration.

          proj_ids: A list of project ids

          search_term: Search term

          api_version: Pass in an API version to guarantee a consistent response format.

              The latest version should be used for all new API calls. Existing API calls
              should be updated to the latest version when possible.

              **Valid versions:**

              - Latest API version (recommended): `2025-03`

              - Previous API version (maintenance mode): `2025-02`

              If no API version header is included, the response format is considered unstable
              and could change without notice (not recommended).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return self._get(
            "/v1/projects",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                        "order": order,
                        "order_by": order_by,
                        "proj_ids": proj_ids,
                        "search_term": search_term,
                    },
                    project_list_params.ProjectListParams,
                ),
            ),
            cast_to=ProjectListResponse,
        )

    def delete(
        self,
        proj_id: str,
        *,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProjectDeleteResponse:
        """
        Delete a project.

        Parameters:

        - proj_id (str): The id of the project.

        Args:
          api_version: Pass in an API version to guarantee a consistent response format.

              The latest version should be used for all new API calls. Existing API calls
              should be updated to the latest version when possible.

              **Valid versions:**

              - Latest API version (recommended): `2025-03`

              - Previous API version (maintenance mode): `2025-02`

              If no API version header is included, the response format is considered unstable
              and could change without notice (not recommended).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not proj_id:
            raise ValueError(f"Expected a non-empty value for `proj_id` but received {proj_id!r}")
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return self._delete(
            f"/v1/projects/{proj_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProjectDeleteResponse,
        )


class AsyncProjectsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncProjectsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Trellis-insights/trellis-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncProjectsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProjectsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Trellis-insights/trellis-python-sdk#with_streaming_response
        """
        return AsyncProjectsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProjectCreateResponse:
        """
        Create a new project.

        Args: proj_name (str): The name of the project.

        Args:
          api_version: Pass in an API version to guarantee a consistent response format.

              The latest version should be used for all new API calls. Existing API calls
              should be updated to the latest version when possible.

              **Valid versions:**

              - Latest API version (recommended): `2025-03`

              - Previous API version (maintenance mode): `2025-02`

              If no API version header is included, the response format is considered unstable
              and could change without notice (not recommended).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return await self._post(
            "/v1/projects/create",
            body=await async_maybe_transform({"name": name}, project_create_params.ProjectCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProjectCreateResponse,
        )

    async def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        order_by: Literal["updated_at", "created_at", "id"] | NotGiven = NOT_GIVEN,
        proj_ids: List[str] | NotGiven = NOT_GIVEN,
        search_term: str | NotGiven = NOT_GIVEN,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProjectListResponse:
        """
        Retrieve a list of projects.

        Parameters:

        - proj_ids (list[str], optional): A list of project ids. If not provided, all
          projects will be retrieved.

        Returns:

        - dict: A dict containing the status message and the list of project names.

        Args:
          order: An enumeration.

          order_by: An enumeration.

          proj_ids: A list of project ids

          search_term: Search term

          api_version: Pass in an API version to guarantee a consistent response format.

              The latest version should be used for all new API calls. Existing API calls
              should be updated to the latest version when possible.

              **Valid versions:**

              - Latest API version (recommended): `2025-03`

              - Previous API version (maintenance mode): `2025-02`

              If no API version header is included, the response format is considered unstable
              and could change without notice (not recommended).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return await self._get(
            "/v1/projects",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                        "order": order,
                        "order_by": order_by,
                        "proj_ids": proj_ids,
                        "search_term": search_term,
                    },
                    project_list_params.ProjectListParams,
                ),
            ),
            cast_to=ProjectListResponse,
        )

    async def delete(
        self,
        proj_id: str,
        *,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProjectDeleteResponse:
        """
        Delete a project.

        Parameters:

        - proj_id (str): The id of the project.

        Args:
          api_version: Pass in an API version to guarantee a consistent response format.

              The latest version should be used for all new API calls. Existing API calls
              should be updated to the latest version when possible.

              **Valid versions:**

              - Latest API version (recommended): `2025-03`

              - Previous API version (maintenance mode): `2025-02`

              If no API version header is included, the response format is considered unstable
              and could change without notice (not recommended).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not proj_id:
            raise ValueError(f"Expected a non-empty value for `proj_id` but received {proj_id!r}")
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return await self._delete(
            f"/v1/projects/{proj_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProjectDeleteResponse,
        )


class ProjectsResourceWithRawResponse:
    def __init__(self, projects: ProjectsResource) -> None:
        self._projects = projects

        self.create = to_raw_response_wrapper(
            projects.create,
        )
        self.list = to_raw_response_wrapper(
            projects.list,
        )
        self.delete = to_raw_response_wrapper(
            projects.delete,
        )


class AsyncProjectsResourceWithRawResponse:
    def __init__(self, projects: AsyncProjectsResource) -> None:
        self._projects = projects

        self.create = async_to_raw_response_wrapper(
            projects.create,
        )
        self.list = async_to_raw_response_wrapper(
            projects.list,
        )
        self.delete = async_to_raw_response_wrapper(
            projects.delete,
        )


class ProjectsResourceWithStreamingResponse:
    def __init__(self, projects: ProjectsResource) -> None:
        self._projects = projects

        self.create = to_streamed_response_wrapper(
            projects.create,
        )
        self.list = to_streamed_response_wrapper(
            projects.list,
        )
        self.delete = to_streamed_response_wrapper(
            projects.delete,
        )


class AsyncProjectsResourceWithStreamingResponse:
    def __init__(self, projects: AsyncProjectsResource) -> None:
        self._projects = projects

        self.create = async_to_streamed_response_wrapper(
            projects.create,
        )
        self.list = async_to_streamed_response_wrapper(
            projects.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            projects.delete,
        )
