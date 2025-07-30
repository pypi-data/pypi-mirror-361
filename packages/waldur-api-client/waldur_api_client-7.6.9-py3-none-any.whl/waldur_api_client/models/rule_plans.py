from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rule_plans_attributes import RulePlansAttributes
    from ..models.rule_plans_limits import RulePlansLimits


T = TypeVar("T", bound="RulePlans")


@_attrs_define
class RulePlans:
    """
    Attributes:
        uuid (UUID):
        url (str):
        rule (str):
        plan (str):
        attributes (Union[Unset, RulePlansAttributes]):
        limits (Union[Unset, RulePlansLimits]):
    """

    uuid: UUID
    url: str
    rule: str
    plan: str
    attributes: Union[Unset, "RulePlansAttributes"] = UNSET
    limits: Union[Unset, "RulePlansLimits"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        url = self.url

        rule = self.rule

        plan = self.plan

        attributes: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        limits: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.limits, Unset):
            limits = self.limits.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "url": url,
                "rule": rule,
                "plan": plan,
            }
        )
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if limits is not UNSET:
            field_dict["limits"] = limits

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rule_plans_attributes import RulePlansAttributes
        from ..models.rule_plans_limits import RulePlansLimits

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        url = d.pop("url")

        rule = d.pop("rule")

        plan = d.pop("plan")

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, RulePlansAttributes]
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = RulePlansAttributes.from_dict(_attributes)

        _limits = d.pop("limits", UNSET)
        limits: Union[Unset, RulePlansLimits]
        if isinstance(_limits, Unset):
            limits = UNSET
        else:
            limits = RulePlansLimits.from_dict(_limits)

        rule_plans = cls(
            uuid=uuid,
            url=url,
            rule=rule,
            plan=plan,
            attributes=attributes,
            limits=limits,
        )

        rule_plans.additional_properties = d
        return rule_plans

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
