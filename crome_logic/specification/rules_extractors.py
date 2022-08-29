from specification import Specification
from specification.string_logic import and_, f_, g_, iff_, implies_, not_, or_, x_
from specification.temporal import LTL
from typelement import TypeKind
from typelement.basic import Boolean
from typeset import Typeset


def extract_refinement_rules(
    typeset: Typeset,
    output_list: bool = False,
) -> LTL | tuple[list[str], Typeset]:
    """Extract Refinement rules from the Formula."""

    rules_str = []
    rules_typeset: Typeset = Typeset()

    refinements: dict[Boolean, set[Boolean]] = {}

    for key_type, set_super_types in typeset.super_types.items():
        if isinstance(key_type, Boolean):
            for super_type in set_super_types:
                if super_type in refinements.keys():
                    refinements[super_type].add(key_type)
                else:
                    refinements[super_type] = {key_type}
                rules_typeset += Typeset({key_type})
                rules_typeset += Typeset(set_super_types)
    for super, refined in refinements.items():
        rules_str.append(g_(iff_(super.name, or_([r.name for r in refined]))))

    if output_list:
        return rules_str, rules_typeset

    if len(rules_str) == 0:
        return LTL("TRUE")

    return LTL(
        _init_formula=and_(rules_str, brackets=True),
        _typeset=rules_typeset,
        _kind=Specification.Kind.Rule.REFINEMENT,
    )


def extract_refinement_rules_legacy(
    typeset: Typeset,
    output_list: bool = False,
) -> LTL | tuple[list[str], Typeset]:
    """Extract Refinement rules from the Formula."""

    rules_str = []
    rules_typeset: Typeset = Typeset()

    for key_type, set_super_types in typeset.super_types.items():
        if isinstance(key_type, Boolean):
            for super_type in set_super_types:
                rules_str.append(
                    g_(
                        implies_(
                            key_type.name,
                            super_type.name,
                        ),
                    ),
                )
                rules_typeset += Typeset({key_type})
                rules_typeset += Typeset(set_super_types)

    if output_list:
        return rules_str, rules_typeset

    if len(rules_str) == 0:
        return LTL("TRUE")

    return LTL(
        _init_formula=and_(rules_str, brackets=True),
        _typeset=rules_typeset,
        _kind=Specification.Kind.Rule.REFINEMENT,
    )


def extract_mutex_rules(
    typeset: Typeset,
    output_list: bool = False,
) -> LTL | tuple[list[str], Typeset]:
    """Extract Mutex rules from the Formula."""

    rules_str = []
    rules_typeset: Typeset = Typeset()

    for mutex_group in typeset.mutex_types:
        or_elements = []
        if len(mutex_group) > 1:
            for mutex_type in mutex_group:
                neg_group = mutex_group.symmetric_difference({mutex_type})
                and_elements = [mutex_type.name]
                for elem in neg_group:
                    and_elements.append(not_(elem.name))
                or_elements.append(and_(and_elements, brackets=True))
            rules_str.append(
                g_(or_(or_elements, brackets=False)),
            )
            rules_typeset += Typeset(set(mutex_group))

    if output_list:
        return rules_str, rules_typeset

    if len(rules_str) == 0:
        return LTL("TRUE")

    return LTL(
        _init_formula=and_(rules_str, brackets=True),
        _typeset=rules_typeset,
        _kind=Specification.Kind.Rule.MUTEX,
    )


def extract_adjacency_rules(
    typeset: Typeset,
    output_list: bool = False,
) -> LTL | tuple[list[str], Typeset]:
    """Extract Adjacency rules from the Formula."""

    rules_str = []
    rules_typeset: Typeset = Typeset()

    for key_type, set_adjacent_types in typeset.adjacent_types.items():
        if isinstance(key_type, Boolean):
            # G(a -> X(b | c | d))
            rules_str.append(
                g_(
                    implies_(
                        key_type.name,
                        x_(
                            or_(
                                [e.name for e in set_adjacent_types],
                            ),
                        ),
                    ),
                ),
            )
            rules_typeset += Typeset({key_type})
            rules_typeset += Typeset(set_adjacent_types)

    if output_list:
        return rules_str, rules_typeset

    if len(rules_str) == 0:
        return LTL("TRUE")

    return LTL(
        _init_formula=and_(rules_str, brackets=True),
        _typeset=rules_typeset,
        _kind=Specification.Kind.Rule.ADJACENCY,
    )


def extract_liveness_rules(
    typeset: Typeset,
    output_list: bool = False,
) -> LTL | tuple[list[str], Typeset] | None:
    """Extract Liveness rules from the Formula."""

    rules_str = []
    rules_typeset: Typeset = Typeset()

    sensors, outs = typeset.extract_inputs_outputs()

    for t in sensors:
        if isinstance(t, Boolean):
            if t.kind == TypeKind.SENSOR:
                rules_str.append(g_(f_(t.name)))
            rules_typeset += Typeset({t})

    if output_list:
        return rules_str, rules_typeset

    if len(rules_str) == 0:
        return LTL("TRUE")

    return LTL(
        _init_formula=and_(rules_str, brackets=True),
        _typeset=rules_typeset,
        _kind=Specification.Kind.Rule.LIVENESS,
    )


def context_active_rules(
    typeset: Typeset,
    output_list: bool = False,
) -> LTL | tuple[list[str], Typeset] | None:
    """Extract Liveness rules from the Formula."""

    rules_str = []
    rules_typeset: Typeset = Typeset()

    inputs, outs = typeset.extract_inputs_outputs()

    active_context_types = []
    for t in inputs:
        if isinstance(t, Boolean):
            if t.kind == TypeKind.ACTIVE or t.kind == TypeKind.CONTEXT:
                active_context_types.append(t.name)
            rules_typeset += Typeset({t})

    if len(active_context_types) > 0:
        rules_str.append(g_(and_(active_context_types)))

    if len(rules_str) == 0:
        return None

    if output_list:
        return rules_str, rules_typeset

    return LTL(
        _init_formula=and_(rules_str, brackets=True),
        _typeset=rules_typeset,
        _kind=Specification.Kind.Rule.LIVENESS,
    )
