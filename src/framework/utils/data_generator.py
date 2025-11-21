from faker import Faker

faker = Faker()

def first_name():
    return faker.first_name()

def last_name():
    return faker.last_name()

def email():
    return faker.email()

def phone_number():
    return ''.join([str(faker.random_digit_not_null()) for _ in range(10)])

def address():
    return faker.address().replace("\n", " ")
