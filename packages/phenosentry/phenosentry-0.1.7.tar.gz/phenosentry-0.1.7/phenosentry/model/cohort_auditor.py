import abc

from stairval import Auditor
from phenopackets.schema.v2.phenopackets_pb2 import Cohort

class CohortAuditor(Auditor[Cohort], metaclass=abc.ABCMeta):
    """
        Abstract base class for auditing cohorts.

        This class extends the `Auditor` class with a generic type of `Cohort`
        and uses the `abc.ABCMeta` metaclass to enforce the implementation of abstract methods.

        Methods:
            id() -> str: Abstract method to return the unique identifier for the cohort auditor.
    """
    @abc.abstractmethod
    def id(self) -> str:
        return "default_cohort_auditor"
