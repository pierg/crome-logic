from crome_logic.specification import Specification
from crome_logic.specification.string_logic import and_, f_, g_, implies_, not_, or_, x_
from crome_logic.specification.temporal import LTL
from crome_logic.typeset import Typeset
from crome_logic.typesimple import CromeType
from crome_logic.typesimple.subtype.base.boolean import Boolean


def extract_refinement_rules(
    typeset: Typeset,
    output_list: bool = False,
) -> LTL | tuple[list[str], Typeset] | None:
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

    if len(rules_str) == 0:
        return None

    if output_list:
        return rules_str, rules_typeset

    return LTL(
        formula=and_(rules_str, brackets=True),
        typeset=rules_typeset,
        kind=Specification.Kind.Rule.REFINEMENT,
    )


def extract_mutex_rules(
    typeset: Typeset,
    output_list: bool = False,
) -> LTL | tuple[list[str], Typeset] | None:
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

    if len(rules_str) == 0:
        return None

    if output_list:
        return rules_str, rules_typeset

    return LTL(
        formula=and_(rules_str, brackets=True),
        typeset=rules_typeset,
        kind=Specification.Kind.Rule.MUTEX,
    )


def extract_adjacency_rules(
    typeset: Typeset,
    output_list: bool = False,
) -> LTL | tuple[list[str], Typeset] | None:
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

    if len(rules_str) == 0:
        return None

    if output_list:
        return rules_str, rules_typeset

    return LTL(
        formula=and_(rules_str, brackets=True),
        typeset=rules_typeset,
        kind=Specification.Kind.Rule.ADJACENCY,
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
            if t.kind == CromeType.Kind.SENSOR:
                rules_str.append(g_(f_(t.name)))
            rules_typeset += Typeset({t})

    if len(rules_str) == 0:
        return None

    if output_list:
        return rules_str, rules_typeset

    return LTL(
        formula=and_(rules_str, brackets=True),
        typeset=rules_typeset,
        kind=Specification.Kind.Rule.LIVENESS,
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
            if t.kind == CromeType.Kind.ACTIVE or t.kind == CromeType.Kind.CONTEXT:
                active_context_types.append(t.name)
            rules_typeset += Typeset({t})

    if len(active_context_types) > 0:
        rules_str.append(g_(and_(active_context_types)))

    if len(rules_str) == 0:
        return None

    if output_list:
        return rules_str, rules_typeset

    return LTL(
        formula=and_(rules_str, brackets=True),
        typeset=rules_typeset,
        kind=Specification.Kind.Rule.LIVENESS,
    )
