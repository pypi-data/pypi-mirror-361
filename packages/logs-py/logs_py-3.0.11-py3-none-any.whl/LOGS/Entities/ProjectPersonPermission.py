from typing import TYPE_CHECKING, Any, Callable, Optional, Tuple

from LOGS.Auxiliary.MinimalModelGenerator import MinimalFromSingle
from LOGS.Entity.SerializableContent import SerializableContent

if TYPE_CHECKING:
    from LOGS.Entities.PersonMinimal import PersonMinimal
    from LOGS.Entities.ProjectMinimal import ProjectMinimal


class ProjectPersonPermission(SerializableContent):
    _person: Optional["PersonMinimal"] = None
    _project: Optional["ProjectMinimal"] = None
    _administer: Optional[bool] = None
    _edit: Optional[bool] = None
    _add: Optional[bool] = None
    _read: Optional[bool] = None

    def _fromRef(
        self,
        ref,
        selfClass,
        convertOtherType: Tuple[type, Callable[[Any], Any]] | None = None,
    ):
        if isinstance(ref, dict) and "read" in ref:
            self._read = ref["read"]
            del ref["read"]
        return super()._fromRef(ref, selfClass, convertOtherType)

    @property
    def person(self) -> Optional["PersonMinimal"]:
        return self._person

    @person.setter
    def person(self, value):
        self._person = MinimalFromSingle(value, "PersonMinimal", "person")

    @property
    def project(self) -> Optional["ProjectMinimal"]:
        return self._project

    @project.setter
    def project(self, value):
        self._project = MinimalFromSingle(value, "ProjectMinimal", "project")

    @property
    def administer(self) -> Optional[bool]:
        return self._administer

    @administer.setter
    def administer(self, value):
        self._administer = self.checkAndConvertNullable(value, bool, "administer")
        if self._administer:
            self._edit = True
            self._add = True

    @property
    def edit(self) -> Optional[bool]:
        return self._edit

    @edit.setter
    def edit(self, value):
        self._edit = self.checkAndConvertNullable(value, bool, "edit")
        if self._edit:
            self._add = True
        else:
            self._administer = False

    @property
    def add(self) -> Optional[bool]:
        return self._add

    @add.setter
    def add(self, value):
        self._add = self.checkAndConvertNullable(value, bool, "add")
        if not self._add:
            self._edit = False
            self._administer = False

    @property
    def read(self) -> Optional[bool]:
        return self._read

    @read.setter
    def read(self, _):
        raise Exception(
            "Every person added to a project has automatically read permissions."
        )
