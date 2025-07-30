import json

from dataclasses import dataclass
from typing import Dict

from codius.domain.model.plan.steps.delete_file_step import PlanStepType
from codius.domain.model.plan.steps.plan_step_base import PlanStepBase


@dataclass
class CreateFileStep(PlanStepBase):
    template: str
    context: Dict[str, object]

    def __init__(self, path: str, description: str, template: str, context: dict):
        super().__init__(type=PlanStepType.CREATE_FILE, path=path, description=description)
        self.template = template
        self.context = context

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "template": self.template,
            "context": self.context
        })
        return base

    @classmethod
    def to_example_json(cls) -> str:
        example = cls(
            path="Domain/Model/Order/Order.cs",
            description="Create Order aggregate",
            template="domain/model/aggregate/aggregate_root",
            context={
                "aggregate_name": "Order",
                "namespace": "MyApp.Domain.Model.Order",
                "properties": [],
                "events": [],
                "commands": []
            }
        )
        return json.dumps(example.to_dict(), indent=2)
