from datetime import datetime

from database_mysql_local.point import Point
from people_local.people import PeopleLocal


# TOOO Person -> PersonLocal
class Person:
    """person details class"""

    # TODO Adding is_same_person() method which override people.is_same_entity() checking username only
    """
  	is_same_person()
		(one of the verified emails is same)
        OR
        (One of the verified telephones is same)  
    """

    # TODO: is there a way to give a default values for Point? Point(None, None) is not working
    # TODO We prefer not to use Point(0,0) and use NULL in the database
    def __init__(self, *, name: str = None, last_coordinate: Point = Point(0, 0),
                 # TODO birthdat_data_object (unlike birthday_date_str)
                 birthday_date: datetime.date = None, day: int = None,
                 month: int = None, year: int = None, first_name: str = None,
                 last_name: str = None, location_id: int = None,
                 nickname: str = None, gender_id: int = None,
                 father_name: str = None, main_email_address: str = None, main_full_number_normalized: str = None,
                 birthday_original: str = None, is_approved: bool = False,
                 is_identity_confirmed: bool = False, birthday_timestamp: str = None,
                 year_cira: int = None, is_first_name_approved: bool = False,
                 is_last_name_approved: bool = False, is_nickname_approved: bool = False,
                 last_location_id: int = None, is_rip: bool = False, is_test_data: bool = False) -> None:
        if first_name:
            if len(first_name.split()) > 1 and last_name is None:  # TODO: test
                # TODO: We may have to improve it later
                splitted_name_dict = PeopleLocal.split_first_name_field(first_name=first_name)
                first_name = splitted_name_dict.get('first_name')
                last_name = splitted_name_dict.get('last_name')
        self.gender_id = gender_id
        self.last_coordinate = last_coordinate
        self.location_id = location_id
        self.birthday_date = birthday_date
        self.day = day
        self.month = month
        self.year = year
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.father_name = father_name
        self.main_email_address = main_email_address
        self.main_full_number_normalized = main_full_number_normalized
        self.name = name or self.generate_name()
        self.birthday_original = birthday_original
        self.is_approved = is_approved
        self.is_identity_confirmed = is_identity_confirmed
        self.birthday_timestamp = birthday_timestamp
        self.year_cira = year_cira
        self.is_first_name_approved = is_first_name_approved
        self.is_last_name_approved = is_last_name_approved
        self.is_nickname_approved = is_nickname_approved
        self.last_location_id = last_location_id
        self.is_rip = is_rip
        self.is_test_data = is_test_data

    def generate_name(self) -> str:
        # TODO I'm not sure first_name and last_name is enough, we should add full_normalized phone number and email [but we use them here!]
        #  I prefer we'll have pure virtual method in Item class i.e. generate_name() and Person will inherit Item and implement generate_name()
        first_name = self.first_name or ''
        last_name = self.last_name or ''
        # TODO: add comment explaining why we are using main_email_address and main_full_number_normalized as part of the name
        main_email_address = self.main_email_address or ''
        main_full_number_normalized = self.main_full_number_normalized or ''
        name = ' '.join([first_name, last_name, main_email_address, main_full_number_normalized])
        return name.strip().replace('  ', ' ')

    def to_dict(self) -> dict:
        person_dict = {k: v for k, v in self.__dict__.items() if v is not None}
        return person_dict