from unittest.mock import Mock

from pytest import raises, mark, param

from sl_util.sl_util.str_utils import deterministic_uuid
from slp_tfplan.slp_tfplan.transformers.dataflow.strategies.dataflow_creation_strategy import DataflowCreationStrategy, \
    DataflowCreationStrategyContainer, create_dataflow
from slp_tfplan.tests.util.builders import get_instance_classes


class TestDataflowCreationStrategy:

    def test_get_strategies(self):
        # GIVEN all the subclasses of the DataflowCreationStrategy interface
        dataflow_creation_strategy_subclasses = DataflowCreationStrategy.__subclasses__()

        # AND the DataflowCreationStrategyContainer
        dataflow_creation_strategy_container = DataflowCreationStrategyContainer()

        # AND all the instances for DataflowCreationStrategyContainer strategies
        dataflow_creation_strategy_instances = get_instance_classes(dataflow_creation_strategy_container.strategies)

        # THEN the subclasses and the instances match
        assert dataflow_creation_strategy_subclasses == dataflow_creation_strategy_instances

    def test_interface_instantiated_error(self):
        # GIVEN an instance of the interface itself
        instance = DataflowCreationStrategy()

        # WHEN DataflowCreationStrategy::create_dataflows is called
        # THEN an NotImplementedError is raised
        with raises(NotImplementedError):
            instance.create_dataflows(otm=Mock(), relationships_extractor=Mock(), are_hierarchically_related=Mock())

    @mark.parametrize('source_id,source_name,target_id,target_name,bidirectional', [
        param('1', 'C1', '2', 'C2', False, id='simple dataflow'),
        param('1', 'C1', '2', 'C2', True, id='bidirectional dataflow')
    ])
    def test_create_dataflow(self,
                             source_id: str, source_name: str, target_id: str, target_name: str, bidirectional: bool):
        # GIVEN a source component
        source_component = Mock(id=source_id)
        source_component.name = source_name

        # AND a target component ID and name
        target_component = Mock(id=target_id)
        target_component.name = target_name

        # AND a bidirectional flag

        # WHEN create_dataflow is invoked
        dataflow = create_dataflow(source_component, target_component, bidirectional)

        # THEN a dataflow is created with the right ID
        if bidirectional:
            assert dataflow.id == deterministic_uuid(hash(source_id) + hash(target_id))
        else:
            assert dataflow.id == deterministic_uuid(f'{source_id}-{target_id}')

        # AND its name is right
        assert dataflow.name == f'{source_name} to {target_name}'

        # AND its source_node is the ID of the source component
        assert dataflow.source_node == source_id

        # AND its destination_node node is the ID of the destination_node component
        assert dataflow.destination_node == target_id

        # AND its bidirectional flag is set right
        assert dataflow.bidirectional == bidirectional

    def test_create_dataflow_bidirectional_same_id(self):
        # GIVEN two components
        component_1 = Mock(id='1')
        component_1.name = 'C1'

        component_2 = Mock(id='2')
        component_2.name = 'C2'

        # AND a bidirectional flag set to True
        bidirectional = True

        # WHEN create_dataflow with the components in the two directions
        dataflow_1 = create_dataflow(component_1, component_2, bidirectional)
        dataflow_2 = create_dataflow(component_2, component_1, bidirectional)

        # THEN the ID for the two dataflows is the same
        assert dataflow_1.id == dataflow_2.id
