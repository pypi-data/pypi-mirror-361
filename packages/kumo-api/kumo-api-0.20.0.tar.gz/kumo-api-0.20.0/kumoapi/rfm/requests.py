from typing import Any, Dict, List, Optional

from pydantic.dataclasses import dataclass

from kumoapi.explain import ColumnAnalysisOutput, Subgraph
from kumoapi.graph import GraphDefinition
from kumoapi.rfm import PQueryDefinition


@dataclass
class RFMExplanation:
    summary: str
    subgraphs: Optional[List[Subgraph]] = None
    column_analysis: Optional[List[ColumnAnalysisOutput]] = None


@dataclass
class RFMPredictResponse:
    prediction: dict[str, Any]
    explanation: Optional[RFMExplanation] = None


@dataclass
class RFMEvaluateResponse:
    metrics: Dict[str, float]


@dataclass
class RFMValidateQueryRequest:
    query: str
    graph_definition: GraphDefinition


@dataclass
class RFMValidateQueryResponse:
    query_definition: PQueryDefinition
