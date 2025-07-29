from dataclasses import dataclass
from typing import Dict
from codius.domain.model.plan.steps.create_file_step import CreateFileStep
from codius.domain.model.plan.steps.modify_file_step import ModifyFileStep


@dataclass(frozen=True)
class PlanChangesPrompt:
    intents: list
    sources: Dict[str, str]
    project_metadata: dict

    def as_prompt(self) -> str:
        example_steps = [
            CreateFileStep(
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
            ),
            ModifyFileStep(
                path="Domain/Model/Order/Order.cs",
                description="Add SummarizeLines method to Order",
                modification="add_method",
                context={
                    "aggregate_name": "Order",
                    "method": {
                        "name": "SummarizeLines",
                        "parameters": [],
                        "returns": "OrderSummaryDto",
                        "body": "return new OrderSummaryDto(Lines.Count, Lines.Sum(l => l.Price));"
                    },
                    "placement": {
                        "type": "after_method",
                        "reference": "AddLine"
                    }
                }
            )
        ]

        example_blocks = "\n".join(
            f"### {step.description}\n```json\n{step.to_example_json()}\n```"
            for step in example_steps
        )

        sources_section = "\n\n".join(
            f"### File: {path}\n```csharp\n{content.strip()}\n```"
            for path, content in self.sources.items()
        )

        project_context = f"""
Domain path: {self.project_metadata.get('domain_path')}
Application path: {self.project_metadata.get('application_path')}
Infrastructure path: {self.project_metadata.get('infrastructure_path')}
Root namespace: {self.project_metadata.get('root_namespace')}
Persistence provider: {self.project_metadata.get('persistence_provider')}
Database provider: {self.project_metadata.get('database_provider')}
"""

        import json
        intents_json = json.dumps(self.intents, indent=2)

        return f"""
You are a Domain-Driven Design (DDD) planning assistant for OpenDDD.NET.

Your task is to plan the necessary code changes for the following modeling intents based on the current source files.

Each plan step should be a JSON object describing:
- Whether to **create a new file** (using a template) or **modify an existing file**
- What operation to perform (`create_file` or `modify_file`)
- Where to place it (`path`)
- Either:
  - A template name and context for creation
  - A modification type and context for modification
- All C# class and property names must use PascalCase.

Only return a **list of plan steps as valid JSON** — no markdown, no prose, no explanation.

---

## Project Metadata:
{project_context}

## Modeling Intents:

```json
{intents_json}
```

## Source Files:

{sources_section}

## Example Plan Steps:

{example_blocks}
"""
