from typing import List, Optional

from ...types._api_version import ApiVersion
from ...types.api.pipelines_config import GetPipelineConfigResponse
from .._request_handler import RequestHandler
from .base_pipelines_config import BasePipelinesConfig


class PipelinesConfig(BasePipelinesConfig):
    def __init__(self, request_handler: RequestHandler):
        super().__init__(request_handler)

    def get_active_pipelines_ids(
        self, project_id: Optional[str] = None, correlation_id: Optional[str] = None
    ) -> List[str]:
        """
        Retrieve a list of active pipeline IDs.

        This method fetches the IDs of all active pipelines, optionally filtered by project.
        Active pipelines are those that are currently deployed and available for execution.

        Args:
            project_id (str, optional): The unique identifier of the project to filter
                pipelines by. If not provided, returns active pipelines from all projects
                accessible to the authenticated user.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            List[str]: A list of pipeline IDs that are currently active. Returns an
                empty list if no active pipelines are found.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The project_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaClient

            client = AiriaClient(api_key="your_api_key")

            # Get all active pipeline IDs
            pipeline_ids = client.pipelines_config.get_active_pipelines_ids()
            print(f"Found {len(pipeline_ids)} active pipelines")

            # Get active pipeline IDs for a specific project
            project_pipelines = client.pipelines_config.get_active_pipelines_ids(
                project_id="your_project_id"
            )
            print(f"Project has {len(project_pipelines)} active pipelines")
            ```

        Note:
            Only pipelines with active versions are returned. Inactive or archived
            pipelines are not included in the results.
        """
        request_data = self._pre_get_active_pipelines_ids(
            project_id=project_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = self._request_handler.make_request("GET", request_data)

        if "items" not in resp or len(resp["items"]) == 0:
            return []

        pipeline_ids = [r["activeVersion"]["pipelineId"] for r in resp["items"]]

        return pipeline_ids

    def get_pipeline_config(
        self, pipeline_id: str, correlation_id: Optional[str] = None
    ) -> GetPipelineConfigResponse:
        """
        Retrieve configuration details for a specific pipeline.

        This method fetches comprehensive information about a pipeline including its
        deployment details, execution statistics, version information, and metadata.

        Args:
            pipeline_id (str): The unique identifier of the pipeline to retrieve
                configuration for.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            GetPipelineConfigResponse: A response object containing the pipeline
                configuration.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The pipeline_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaClient

            client = AiriaClient(api_key="your_api_key")

            # Get pipeline configuration
            config = client.pipelines_config.get_pipeline_config(
                pipeline_id="your_pipeline_id"
            )

            print(f"Pipeline: {config.agent.name}")
            print(f"Description: {config.agent.agent_description}")
            ```

        Note:
            This method only retrieves configuration information and does not
            execute the pipeline. Use execute_pipeline() to run the pipeline.
        """
        request_data = self._pre_get_pipeline_config(
            pipeline_id=pipeline_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = self._request_handler.make_request("GET", request_data)

        return GetPipelineConfigResponse(**resp)
