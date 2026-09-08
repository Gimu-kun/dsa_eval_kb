from MetaModel.classes.Concept import Concept
from MetaModel.classes.Attribute import Attribute
from MetaModel.classes.enums.types.ValueType import ValueType
from MetaModel.classes.enums.types.Cardinality import Cardinality

# Khởi tạo Concept Node
node_concept = Concept(
    id="C_NODE",
    name="Node",
    domain="DataStructure",
    subclassOf="",
    attributes=[
        Attribute(
            name="value",
            value_type=ValueType.ANY,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        ), 
        Attribute(
            name="next",
            value_type=ValueType.CONCEPT,
            value_domain=["Node"],
            cardinality=Cardinality.ZERO_ONE,  # Có thể trỏ đến Null (Node cuối)
            constraint=None
        )
    ],
    invariant=[],
    operation=[]
)
