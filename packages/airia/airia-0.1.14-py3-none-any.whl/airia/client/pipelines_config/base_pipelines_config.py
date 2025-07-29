from typing import Optional, Union
from urllib.parse import urljoin

from ...types._api_version import ApiVersion
from .._request_handler import AsyncRequestHandler, RequestHandler


class BasePipelinesConfig:
    def __init__(self, request_handler: Union[RequestHandler, AsyncRequestHandler]):
        self._request_handler = request_handler

    def _pre_get_active_pipelines_ids(
        self,
        project_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for getting active pipelines IDs.

        Args:
            project_id: ID of the project to get configuration for
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the pipeline config endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(self._request_handler.base_url, f"{api_version}/PipelinesConfig")
        params = {"projectId": project_id} if project_id is not None else None
        request_data = self._request_handler.prepare_request(
            url, params=params, correlation_id=correlation_id
        )

        return request_data

    def _pre_get_pipeline_config(
        self,
        pipeline_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for getting pipeline configuration endpoint.

        Args:
            pipeline_id: ID of the pipeline to get configuration for
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the pipeline config endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self._request_handler.base_url,
            f"{api_version}/PipelinesConfig/export/{pipeline_id}",
        )
        request_data = self._request_handler.prepare_request(
            url, correlation_id=correlation_id
        )

        return request_data
