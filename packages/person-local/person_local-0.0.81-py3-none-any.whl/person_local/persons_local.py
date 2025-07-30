import datetime

from database_mysql_local.to_sql_interface import Concat, TimeUnit
from database_mysql_local.point import Point
from language_remote.lang_code import LangCode
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.MetaLogger import MetaLogger
from people_local.people import PeopleLocal
from user_context_remote.user_context import UserContext

from .person import Person

PERSONS_LOCAL_PYTHON_COMPONENT_ID = 169
PERSONS_LOCAL_PYTHON_COMPONENT_NAME = 'person-local-python'

person_local_code_logger_init_object = {
    'component_id': PERSONS_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': PERSONS_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email": "jenya.b@circ.zone"
}

user_context = UserContext()


class PersonsLocal(PeopleLocal, metaclass=MetaLogger, object=person_local_code_logger_init_object):
    """PersonsLocal class"""

    def __init__(self, *,
                 first_name_original: str = None,
                 last_names_original: list[str] = None,
                 organizations_names_original: list = None,
                 email_addresses: list = None,
                 urls: list = None,
                 is_test_data: bool = False) -> None:
        PeopleLocal.__init__(self,
                             default_schema_name="person", default_table_name="person_table",
                             default_view_table_name="person_view", default_column_name='person_id',
                             first_name_original=first_name_original,
                             last_names_original=last_names_original,
                             organizations_names_original=organizations_names_original,
                             email_addresses=email_addresses,
                             urls=urls, is_test_data=is_test_data)

    def get_person_id_by_email_address_str(self, email_address: str) -> int | None:
        # TODO email_address -> email_address_str
        person_id = self.select_one_value_by_column_and_value(
            column_name='person.main_email_address', column_value=email_address,
            select_clause_value='person_id')
        return person_id

    def insert(self, person: Person) -> int:  # noqa
        data_dict = {
            "gender_id": person.gender_id,
            "last_coordinate": Point(float(person.last_coordinate.longitude), float(person.last_coordinate.latitude)),
            "location_id": person.location_id,
            'birthday_date': person.birthday_date,
            'day': person.day,
            'month': person.month,
            'year': person.year,
            'first_name': self.normalized_first_name if self.normalized_first_name else person.first_name,
            'last_name': self.normalized_last_names[0] if self.normalized_last_names else person.last_name,
            'last_name_original': self.last_names_original[0] if self.last_names_original else person.last_name,
            'nickname': person.nickname,
            'father_name': person.father_name,
            'person.main_email_address': self.email_addresses[0] if self.email_addresses else person.main_email_address,
            'birthday_original': person.birthday_original,
            'is_approved': person.is_approved,
            'is_identity_confirmed': person.is_identity_confirmed,
            'birthday_timestamp': person.birthday_timestamp,
            'year_cira': person.year_cira,
            'is_first_name_approved': person.is_first_name_approved,
            'is_nickname_approved': person.is_nickname_approved,
            'last_location_id': person.last_location_id,
            'is_rip': person.is_rip,
            'name': person.name,
            'main_full_number_normalized': person.main_full_number_normalized,
        }
        person_id = super().insert(data_dict=data_dict)
        return person_id

    # TODO: use crud ml and make person_id optional
    def insert_person_ml(self, *, person_id: int, first_name: str, last_name: str,
                         lang_code: LangCode = None,
                         is_first_name_approved: bool = False,
                         is_last_name_approved: bool = False) -> int:

        lang_code = lang_code or LangCode.detect_lang_code_restricted(
            text=first_name, default_lang_code=LangCode.ENGLISH)
        data_dict = {
            "first_name": self.normalized_first_name if self.normalized_first_name else first_name,
            "last_name": self.normalized_last_names[0] if self.normalized_last_names else last_name,
            "person_id": person_id,
            "lang_code": lang_code.value,
            "is_first_name_approved": is_first_name_approved,
            "is_last_name_approved": is_last_name_approved
        }
        person_ml_id = super().insert(data_dict=data_dict, table_name='person_ml_table', ignore_duplicate=True)
        return person_ml_id

    def insert_if_not_exists(self, person: Person, lang_code: LangCode = None) -> tuple:

        person_id = super().select_one_value_by_column_and_value(
            view_table_name='person_view',
            select_clause_value='person_id',
            column_value=person.name,
            column_name='name'
        )
        if person_id:  # TODO: test this part
            ml_person_id = super().select_one_value_by_column_and_value(
                view_table_name='person_ml_view',
                select_clause_value='person_ml_id',
                column_value=person_id,
                column_name='person_id'
            )

            return person_id, ml_person_id
        lang_code = lang_code or LangCode.detect_lang_code_restricted(
            text=person.first_name, default_lang_code=LangCode.ENGLISH)
        # Insert to person__table
        data_dict = {
            "gender_id": person.gender_id,
            "last_coordinate": person.last_coordinate,
            "location_id": person.location_id,
            'birthday_date': person.birthday_date,
            'day': person.day,
            'month': person.month,
            'year': person.year,
            'first_name':  self.normalized_first_name if self.normalized_first_name else person.first_name,
            'name': person.name,
            'last_name': self.normalized_last_names[0] if self.normalized_last_names else person.last_name,
            'last_name_original': self.last_names_original[0] if self.last_names_original else person.last_name,
            'nickname': person.nickname,
            'father_name': person.father_name,
            'person.main_email_address': person.main_email_address,
            'main_full_number_normalized': person.main_full_number_normalized,
            'birthday_original': person.birthday_original,
            'is_approved': person.is_approved,
            'is_identity_confirmed': person.is_identity_confirmed,
            'birthday_timestamp': person.birthday_timestamp,
            'year_cira': person.year_cira,
            'is_first_name_approved': person.is_first_name_approved,
            'is_nickname_approved': person.is_nickname_approved,
            'last_location_id': person.last_location_id,
            'is_rip': person.is_rip,
        }
        data_compare_dict = {"name": person.name,
                             "person.main_email_address": person.main_email_address,
                             "main_full_number_normalized": person.main_full_number_normalized}
        person_id = super().insert_if_not_exists(data_dict=data_dict, table_name='person_table',
                                                 view_table_name='person_view', data_dict_compare=data_compare_dict)

        # Insert to person_ml_table
        data_dict_ml = {
            "first_name": self.normalized_first_name if self.normalized_first_name else person.first_name,
            "last_name": self.normalized_last_names[0] if self.normalized_last_names else person.last_name,
            "person_id": person_id,
            "lang_code": lang_code.value,
            "is_first_name_approved": person.is_first_name_approved,
            "is_last_name_approved": person.is_last_name_approved
        }
        data_ml_compare_dict = {"person_id": person_id, "lang_code": lang_code.value}
        person_ml_id = super().insert_if_not_exists(table_name="person_ml_table", data_dict=data_dict_ml,
                                                    view_table_name="person_ml_view",
                                                    data_dict_compare=data_ml_compare_dict)

        return person_id, person_ml_id

    def update_birthday_day(self, person_id: int, day: int) -> None:
        """update birthday day"""
        data_dict = {
            "day": day,
            "birthday_date": Concat(TimeUnit(column_name="birthday_date", unit="YEAR"),
                                    "-", TimeUnit(column_name="birthday_date", unit="MONTH"), "-", day)
        }
        super().update_by_column_and_value(column_value=person_id, data_dict=data_dict)

    def update_birthday_month(self, person_id: int, month: int) -> None:
        """update birthday month"""
        data_dict = {
            "month": month,
            "birthday_date": Concat(TimeUnit(column_name="birthday_date", unit="YEAR"),
                                    "-", month, "-", TimeUnit(column_name="birthday_date", unit="DAY"))
        }
        super().update_by_column_and_value(column_value=person_id, data_dict=data_dict)

    def update_birthday_year(self, *, person_id: int, year: int) -> None:
        """update"""
        data_dict = {
            "year": year,
            "birthday_date": Concat(year, "-", TimeUnit(column_name="birthday_date", unit="MONTH"), "-",
                                    TimeUnit(column_name="birthday_date", unit="DAY"))
        }
        super().update_by_column_and_value(column_value=person_id, data_dict=data_dict)

    def update_birthday_date(self, person_id: int, birthday_date: datetime.date) -> None:
        """update birthday date"""

        date = str(birthday_date).split('-')
        person_dict = {
            "person_id": person_id,
            "year": int(date[0]),
            "month": int(date[1]),
            "day": int(date[2]),
            "birthday_date": birthday_date
        }
        self.update_by_column_and_value(column_value=person_id, data_dict=person_dict)

    def update_first_name_by_profile_id(self, profile_id: int, first_name: str) -> None:
        """update first name"""

        person_dict = {
            "person_id": profile_id,
            "first_name": first_name
        }
        self.update_by_column_and_value(column_value=profile_id, data_dict=person_dict)

    def update_person_ml_first_name_by_person_id(
            self, *, person_id: int, first_name: str, lang_code: LangCode = None) -> None:
        """update ml first name"""

        lang_code = lang_code or LangCode.detect_lang_code_restricted(
            text=first_name, default_lang_code=LangCode.ENGLISH)
        data_dict = {
            "first_name": first_name,
            "lang_code": lang_code.value
        }
        super().update_by_column_and_value(column_value=person_id, data_dict=data_dict, table_name='person_ml_table')

    def update_nickname_by_person_id(self, person_id: int, nickname: str) -> None:
        """update nickname"""

        person_dict = {
            "person_id": person_id,
            "nickname": nickname
        }
        self.update_by_column_and_value(column_value=person_id, data_dict=person_dict)

    def update_last_name_by_person_id(self, person_id: int, last_name: str) -> None:
        """update last name"""

        person_dict = {
            "person_id": person_id,
            "last_name": last_name
        }
        self.update_by_column_and_value(column_value=person_id, data_dict=person_dict)

    def update_person_ml_last_name_by_person_id(
            self, *, person_id: int, last_name: str, lang_code: LangCode = None) -> None:
        """update ml last name"""

        # TODO: Do we really want to update lang_code here?
        lang_code = lang_code or LangCode.detect_lang_code_restricted(
            text=last_name, default_lang_code=LangCode.ENGLISH)
        data_dict = {
            "last_name": last_name,
            "lang_code": lang_code.value
        }
        super().update_by_column_and_value(column_value=person_id, data_dict=data_dict, table_name='person_ml_table')

    def delete_by_person_id(self, person_id: int) -> None:
        """delete person"""
        self.delete_by_column_and_value(column_value=person_id)

    # TODO Shall we use ORDER BY person_id ASC LIMIT 1  [why?]
    def get_test_person_id(self, **person_kwargs) -> int:
        test_person_id = super().get_test_entity_id(
            entity_name="person", schema_name="person", view_name="person_view",
            entity_creator=Person, create_kwargs=person_kwargs,
            insert_function=self.insert)
        return test_person_id
