from abc import abstractmethod
from typing import List, Callable

from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer

from otm.otm.entity.dataflow import Dataflow
from sl_util.sl_util.str_utils import deterministic_uuid
from slp_tfplan.slp_tfplan.graph.relationships_extractor import RelationshipsExtractor
from slp_tfplan.slp_tfplan.objects.tfplan_objects import TFPlanOTM, TFPlanComponent


def __create_directed_id(source_component_id: str, target_component_id: str):
    return deterministic_uuid(f'{source_component_id}-{target_component_id}')


def __create_undirected_id(source_component_id: str, target_component_id: str):
    return deterministic_uuid(hash(source_component_id) + hash(target_component_id))


def __create_deterministic_id(source_component_id: str, target_component_id: str, bidirectional: bool):
    return __create_undirected_id(source_component_id, target_component_id) if bidirectional \
        else __create_directed_id(source_component_id, target_component_id)


def create_dataflow(source_component: TFPlanComponent, target_component: TFPlanComponent, bidirectional: bool = False):
    return Dataflow(
        dataflow_id=__create_deterministic_id(source_component.id, target_component.id, bidirectional),
        name=f'{source_component.name} to {target_component.name}',
        source_node=source_component.id,
        destination_node=target_component.id,
        bidirectional=bidirectional
    )


class DataflowCreationStrategy:

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
                hasattr(subclass, 'create_dataflows') and callable(subclass.process)
                or NotImplemented)

    @abstractmethod
    def create_dataflows(self,
                         otm: TFPlanOTM,
                         relationships_extractor: RelationshipsExtractor,
                         are_hierarchically_related: Callable) -> List[Dataflow]:
        """
        Common method to build dataflows based on a tfplan OTM and a tfgraph.
        These dataflows can be found in different ways (using the graph, using security groups, etc.).
        Each implementation defines one specific logic to create dataflows.
        :param otm: `TFPlanOTM` object with all the components mapped for a given tfplan.
        :param relationships_extractor: object with methods to find relationships in the tfgraph.
        :param are_hierarchically_related: `Callable` that calculates if there is a hierarchical relationship between
        two components.
        :return: the list of calculated `Dataflow`.
        """
        raise NotImplementedError


class DataflowCreationStrategyContainer(DeclarativeContainer):
    """
    Container with instances for each `DataflowCreationStrategy` implementation to be injected using
    dependency-injector (see https://python-dependency-injector.ets-labs.org/).
    """

    strategies = providers.List()
