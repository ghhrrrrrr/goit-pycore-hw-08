import pickle
from collections import UserDict
from datetime import datetime, timedelta


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass
        

class Phone(Field):
    def __init__(self, value):
        if not len(value) == 10 and value.isdigit():
             raise ValueError
        super().__init__(value)

class AddressBook(UserDict):
    def add_record(self, new):
        self.data[new.name.value] = new

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def show_birthday(self, name):
        n = self.data.get(name)
        if n:
            try:
                b  = n.birthday.value.strftime("%d.%m.%Y")
            except ValueError:
                b = None
            return f"Name: {n.name}, Birthday: {b}" 
        else:
            return "Contact doesn't exist"

    def showall(self):
        names = []
        for i in self.data.keys():
            names.append(i)
        return names

class Birthday(Field):
    def __init__(self, value):
        try:
            date_format = "%d.%m.%Y"
            value = datetime.strptime(value, date_format)
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if str(phone) == old_phone:
                self.phones[i] = Phone(new_phone)
                break
    
    def find_phone(self, phone):
        return phone if any(str(p) == phone for p in self.phones) else None
    
    def add_birthday(self, date):
        self.birthday = Birthday(date)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"



def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Something went wrong... Please try again"
        except IndexError:
            return "Enter the argument for the command"
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record:
        record = Record(name)
        book.add_record(record)
        if phone:
            record.add_phone(phone)
    else:
        return "Contact doesn't exist"
    return message

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    return book.find(name)

@input_error
def add_birthday(args, book: AddressBook):
    name, date, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        record.add_birthday(date)
        book.add_record(record)
    else:
        record.add_birthday(date)
        book.add_record(record)
    return 'Contact info updated'


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.show_birthday(name)
    return record

@input_error
def birthdays(book: AddressBook):
    today = datetime.today().date()
    upcoming_birthdays = []

    for _, record in book.data.items():
        birthday = record.birthday.value if record.birthday else None
        if birthday:
            birthday_this_year = birthday.replace(year=today.year).date()
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            
            while birthday_this_year.weekday() >= 5:
                birthday_this_year += timedelta(days=1)

            upcoming_birthdays.append({
                "name": record.name.value,
                "congratulation_date": birthday_this_year.strftime("%Y.%m.%d")
            })

    return upcoming_birthdays



def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(book.showall())

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")


if __name__ == '__main__':
    main()