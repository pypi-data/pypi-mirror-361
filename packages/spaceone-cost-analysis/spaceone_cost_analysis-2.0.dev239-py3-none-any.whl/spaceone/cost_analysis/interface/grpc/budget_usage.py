from spaceone.api.cost_analysis.v1 import budget_usage_pb2, budget_usage_pb2_grpc
from spaceone.core.pygrpc import BaseAPI

from spaceone.cost_analysis.service import BudgetUsageService


class BudgetUsage(BaseAPI, budget_usage_pb2_grpc.BudgetUsageServicer):

    pb2 = budget_usage_pb2
    pb2_grpc = budget_usage_pb2_grpc

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        budget_svc = BudgetUsageService(metadata)
        response: dict = budget_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service(
            "BudgetUsageService", metadata
        ) as budget_usage_service:
            return self.locator.get_info(
                "StatisticsInfo", budget_usage_service.stat(params)
            )

    def analyze(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service(
            "BudgetUsageService", metadata
        ) as budget_usage_service:
            return self.locator.get_info(
                "AnalyzeInfo", budget_usage_service.analyze(params)
            )
