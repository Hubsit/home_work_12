from collections import UserDict
from datetime import date, datetime
import pickle
import re


class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Name(Field):
    pass


class Phone(Field):
    @Field.value.setter
    def value(self, value):
        pattern = r'\+380\d{9}|\d{10}|\+38(\d{3})\d{7}|\d{3}-\d{3}-\d{2}-\d{2}'
        result = re.fullmatch(pattern, value)
        if not result:
            raise ValueError('Wrong phone number! Try again... ')
        self._value = value


class Birthday(Field):
    @Field.value.setter
    def value(self, value):
        pattern = r'\d{2}\.\d{2}\.\d{4}'
        result = re.fullmatch(pattern, value)
        if not result:
            raise ValueError('Wrong birthday date. Please, input DD.MM.YYYY')
        birthday_date = datetime.strptime(value, '%d.%m.%Y').date()
        if birthday_date > date.today():
            raise ValueError('Birthday must be less than current year and date')
        self._value = value


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def get_info(self):
        phones_info = ''
        birthday_info = ''

        for phone in self.phones:
            phones_info += f'{phone.value}, '

        if self.birthday:
            birthday_info = f' Birthday: {self.birthday.value}'

        return f'{self.name.value} : {phones_info[:-2]}{birthday_info}'

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def delete_phone(self, phone):
        for record_phone in self.phones:
            if record_phone.value == phone:
                self.phones.remove(record_phone)
                return True
        return False

    def edit_phones(self, phones):
        for phone in phones:
            if not self.delete_phone(phone):
                self.add_phone(phone)

    def add_birthday(self, date_birthday):
        self.birthday = Birthday(date_birthday)

    def days_to_birthday(self):
        if not self.birthday:
            raise ValueError('This contact don`t have birthday! Please, add birthday.')
        current_date = date.today()
        birthday = datetime.strptime(self.birthday.value, '%d.%m.%Y').date()
        this_year_birthday = date(year=current_date.year, month=birthday.month, day=birthday.day)
        if current_date > this_year_birthday:
            next_birthday = date(year=this_year_birthday.year + 1, month=birthday.month, day=birthday.day)
        else:
            next_birthday = this_year_birthday
        return (next_birthday - current_date).days


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def get_all_record(self):
        return self.data

    def has_record(self, name):
        return bool(self.data.get(name))

    def get_record(self, name) -> Record:
        return self.data.get(name)

    def remove_record(self, name):
        del self.data[name]

    def search(self, value):
        if self.has_record(value):
            return self.get_record(value)

        for record in self.get_all_record().values():
            for phone in record.phones:
                if phone.value == value:
                    return record

        raise ValueError('Contact with this value does not exist.')

    def save_to_file(self):
        with open('adress_book', 'wb') as file:
            pickle.dump(self.data, file)

    def load_from_file(self):
        with open('adress_book', 'rb') as file:
            data = pickle.load(file)
        self.data.update(data)

    def iterator(self):
        max_record = 3
        record_count = 0
        information = list()

        for record in self.data.values():
            information.append(record)
            record_count += 1
            if record_count == max_record:
                yield information
                record_count = 0
                information = []

        if information:
            yield information
