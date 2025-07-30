import json

from dataclasses import dataclass
from typing import Dict, Any

from codius.domain.model.plan.steps.plan_step_base import PlanStepBase
from codius.domain.model.plan.steps.plan_step_type import PlanStepType


@dataclass
class ModifyFileStep(PlanStepBase):
    modification: str  # e.g. "add_method", "remove_method", "rename_property"
    context: Dict[str, Any]

    def __init__(self, path: str, description: str, modification: str, context: dict):
        super().__init__(type=PlanStepType.MODIFY_FILE, path=path, description=description)
        self.modification = modification
        self.context = context

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "path": self.path,
            "description": self.description,
            "modification": self.modification,
            "context": self.context,
        }

    @classmethod
    def to_example_json(cls) -> str:
        example = cls(
            path="Domain/Model/Order/Order.cs",
            description="Add SummarizeLines method to Order",
            modification="add_method",
            context={
                "aggregate_name": "Order",
                "method": {
                    "name": "SummarizeLines",
                    "parameters": [],
                    "returns": "OrderSummary",
                    "body": "return new OrderSummary(Lines.Count, Lines.Sum(l => l.Price));"
                },
                "placement": {
                    "type": "after_method",
                    "reference": "AddLine"
                }
            }
        )
        return json.dumps(example.to_dict(), indent=2)
