from collections import UserDict
from datetime import datetime, timedelta
import pickle
from pathlib import Path
from abc import ABC, abstractmethod


# Абстрактний клас для уявлень
class View(ABC):
    @abstractmethod
    def show_record(self, record):
        pass

    @abstractmethod
    def show_all_records(self, address_book):
        pass

    @abstractmethod
    def show_message(self, message):
        pass


# Реалізація інтерфейсу для консолі
class ConsoleView(View):
    def show_record(self, record):
        print(record)

    def show_all_records(self, address_book):
        print("All contacts:")
        print(address_book)

    def show_message(self, message):
        print(message)


# Базовий клас для полів запису
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                return
        raise ValueError("Old phone number not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                if 0 <= (birthday_this_year - today).days <= 7:
                    upcoming_birthdays.append(
                        {
                            "name": record.name.value,
                            "birthday": birthday_this_year.strftime("%d.%m.%Y"),
                        }
                    )
        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)

    return inner


@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise ValueError("Usage: add-birthday [name] [birthday]")
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Added birthday {birthday} for {name}"
    return f"Contact {name} not found"


@input_error
def show_birthday(args, book):
    if len(args) != 1:
        raise ValueError("Usage: show-birthday [name]")
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is {record.birthday}"
    return f"Contact {name} not found or no birthday set"


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        return "\n".join([f"{item['name']}: {item['birthday']}" for item in upcoming])
    return "No upcoming birthdays"


commands = {
    "add": lambda args, book: book.add_record(Record(args[0])),
    "change": lambda args, book: book.find(args[0]).edit_phone(args[1], args[2]),
    "phone": lambda args, book: str(book.find(args[0])),
    "all": lambda args, book: str(book),
    "add-birthday": add_birthday,
    "show-birthday": show_birthday,
    "birthdays": birthdays,
    "hello": lambda args, book: "Hello! How can I assist you?",
    "close": lambda args, book: "Goodbye!",
    "exit": lambda args, book: "Goodbye!",
}


def parse_input(user_input):
    parts = user_input.split()
    command = parts[0]
    args = parts[1:]
    return command, args


def handle_command(command, args, book, view):
    if command in commands:
        result = commands[command](args, book)
        view.show_message(result)
    else:
        view.show_message("Unknown command")


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()
    view = ConsoleView()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            view.show_message("Goodbye!")
            save_data(book)
            break

        handle_command(command, args, book, view)


if __name__ == "__main__":
    main()
