from aiogram.dispatcher.filters.state import State, StatesGroup


class OrderStates(StatesGroup):
    phone_number = State()
    product_name = State()
    product_description = State()
    city = State()


class CaategoryStates(StatesGroup):
    category_list = State()


class AdminAddProductStates(StatesGroup):
    press_buttun_stair = State()
    image = State()
    description = State()
    price = State()


class ComplainStates(StatesGroup):
    phone_number = State()
    image = State()
    description = State()


class CategoryListStates(StatesGroup):
    get_order = State()

    quantity = State()
    description = State()
    phone_number = State()
