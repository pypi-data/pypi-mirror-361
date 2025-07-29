from typing import Any
from carestack.common.enums import HealthInformationTypes
from carestack.document_linking.transformer.op_consultation import (
    OpConsultationTransformer,
)
from carestack.document_linking.transformer.transformer import Transformer
from carestack.base.base_types import ClientConfig


class TransformerFactory:
    """
    Factory for creating transformers.
    """

    def __init__(self, config: ClientConfig):
        self.config = config
        self.transformers: dict[HealthInformationTypes, Transformer[Any, Any, Any]] = {
            HealthInformationTypes.OPConsultation: OpConsultationTransformer(
                self.config
            ),
        }

    def create_transformer(
        self, information_type: HealthInformationTypes
    ) -> Transformer[Any, Any, Any]:
        """
        Creates a transformer for the given information type.

        Args:
            information_type: The type of health information.

        Returns:
            The appropriate transformer.

        Raises:
            ValueError: If no transformer is found for the given information type.
        """
        transformer = self.transformers.get(information_type)
        if not transformer:
            raise ValueError(f"No transformer for {information_type}")
        return transformer
