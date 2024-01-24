import os
from typing import Optional

import bcrypt
import pwinput
from colorama import Fore

from supersecret import happyfuntime


class Account:
    def __init__(self, name: str, pw: bytes, salt: bytes, mod: bool, admin: bool):
        self.username = name
        self.password = pw
        self.salt = salt
        self.is_moderator = mod
        self.is_admin = admin


class Car:
    def __init__(
        self,
        make: str,
        model: str,
        year: int,
        cost_price: int,
        selling_price: int,
        color: str,
    ):
        self.make = make
        self.model = model
        self.year = year
        self.cost_price = cost_price
        self.selling_price = selling_price
        self.color = color


###==={Password Hashing}===###
def HashPassword(password: str, salt=None) -> tuple:
    bytepassword = password.encode()  # Standard encode to ASCII
    salt = bcrypt.gensalt() if salt == None else salt
    hashed = bcrypt.hashpw(bytepassword, salt)

    return (hashed, salt)


###==={Create an Account}===###
def add_account(profiles: list[Account]) -> Account:
    currentusers = []
    for user in profiles:
        currentusers.append(user.username)
    Invalid_account = True

    while Invalid_account:
        while True:
            name = input("Username: ").strip().lower()
            if len(name.split()) == 1:
                break
            else:
                print("Spaces are not a valid character.")
        while True:
            password = input("Password: ").strip()
            if len(password) < 8:
                print("Password must be at least 8 characters.")
            else:
                break

        if name in currentusers:
            print("That username is already taken, please enter a valid one!")
        else:
            Invalid_account = False

    Hashed = HashPassword(password)

    is_admin = False if len(profiles) != 0 else True

    try:
        with open("userlog.txt", "a") as f:
            f.write(f"{name}, {Hashed[0]}, {Hashed[1]}, {is_admin}, {is_admin}\n")
    except FileNotFoundError:
        with open("userlog.txt", "w") as f:
            f.write(f"{name}, {Hashed[0]}, {Hashed[1]}, {is_admin}, {is_admin}\n")

    return Account(name, Hashed[0], Hashed[1], is_admin, is_admin)


###==={Pull Users from Files}===###
def pullnames() -> list[Account]:
    with open("userlog.txt", "r") as f:
        userlist = f.readlines()
        # Removes the '\n' and splits each entry into Name, Password, and Salt
        for index, user in enumerate(userlist):
            userlist[index] = user[:-1].split(", ")
        # Removes the "b''" to convert the string to bytes properly
        for x, user in enumerate(userlist):
            for i, portion in enumerate(user):
                if portion != user[0] and portion != user[3] and portion != user[4]:
                    userlist[x][i] = portion[2:-1]
    return [
        Account(
            i[0],
            bytes(i[1], "utf-8"),
            bytes(i[2], "utf-8"),
            i[3] == "True",
            i[4] == "True",
        )
        for i in userlist
    ]


# ==={Log In to Account}===###
def login(userlist: list[Account]) -> Optional[Account]:
    username = input("Username: ").lower().strip()
    password = pwinput.pwinput(prompt="Password: ").strip()
    for user in userlist:
        if user.username == username:
            testhash = HashPassword(password, salt=user.salt)[0]
            if testhash == user.password:
                return user
    return None


###==={Search for Users}===###
def searchUser(userlist: list[Account]) -> None:
    searchfor = (
        input("Enter the name of the account you want to search for: ").lower().strip()
    )
    print()
    for user in userlist:
        if searchfor in user.username:
            print(
                f'{user.username}: {Fore.BLUE}{"Customer" if not user.is_moderator and not user.is_admin else "Admin" if user.is_admin else "Moderator"}{Fore.RESET}'
            )


####==={Search for Cars by Price}===###
def sort_cars_by_price(car_list: list[Car]) -> list[Car]:
    sorted_cars = sorted(car_list, key=lambda x: x.selling_price)
    return sorted_cars


###==={Format Price to USD}===###
def price_format(price: int) -> str:
    return "${:,.2f}".format(price)


###==={Sort Cars by Color}===###
def sort_cars_by_colors(car_list: list[Car]) -> dict[str, Car]:
    color_dict = {}
    for car in car_list:
        color = car.color.lower()
        if color in color_dict:
            color_dict[color].append(car)
        else:
            color_dict[color] = [car]
    return color_dict


###==={Delete Account from Database}===###
def delete_account(username: str) -> None:
    userlist = pullnames()
    for user in userlist:
        if user.username == username:
            userlist.remove(user)
    with open("userlog.txt", "w") as f:
        for user in userlist:
            f.write(f"{user.username}, {user.password}, {user.salt}\n")


###==={Pull Current Stock of Cars}===###
def pullcars() -> list[Car]:
    try:
        with open("carlog.txt", "r") as f:
            carlist = f.readlines()

            for index, car in enumerate(carlist):
                carlist[index] = car[:-1].split(", ")

    except FileNotFoundError:
        print("File Not Found")

    return [Car(i[0], i[1], int(i[2]), int(i[3]), int(i[4]), i[5]) for i in carlist]


###==={Add Car to Car Catalog}===###
def AddCar() -> Optional[Car]:
    while True:
        inputModel = input("Model Name: ").title().strip()
        if inputModel != "Back":
            while True:
                inputYear = input("Production Year: ").strip()
                if inputYear.isdigit():
                    inputYear = int(inputYear)
                    break
                else:
                    print("Please enter a valid year.")
            while True:
                inputCost = input("Cost: ").strip()
                if inputCost.isdigit():
                    inputCost = int(inputCost)
                    break
                else:
                    print("Please enter a valid cost.")
            while True:
                inputSell = input("Selling Price: ").strip()
                if inputSell.isdigit():
                    inputSell = int(inputSell)
                    break
                else:
                    print("Please enter a valid price.")
            while True:
                inputColor = input("Color: ").strip().lower()
                if not inputColor.isdigit():
                    break
                else:
                    print("Please enter a valid color.")
        else:
            return None

        return Car(
            "Solksvagen", inputModel, inputYear, inputCost, inputSell, inputColor
        )


###==={Remove Car from Stock/Catalog}===###
def RemoveCar(car_list) -> Optional[Car]:
    cartodelete = ""
    while cartodelete != "back":
        print("Which car would you like to remove?\n")
        for index, car in enumerate(car_list):
            print(
                f"{index + 1}. {car.year} {car.model} - {Fore.BLUE}{price_format(car.selling_price)}{Fore.RESET}"
            )

        cartodelete = input(
            "\nEnter the number of the car you would like to remove or [Back].\n> "
        )
        if cartodelete.isdigit():
            if 0 < int(cartodelete) <= len(car_list):
                cartodelete = int(cartodelete) - 1
                removed_car = car_list.pop(cartodelete)
                print(
                    f"\nRemoved {removed_car.year} {removed_car.model} from the inventory."
                )
                return removed_car
            else:
                print("\nInvalid car number\n")

        elif cartodelete != "back":
            print("\nInvalid input.\n")

    return None


###==={Add Car to Current Stock}===###
def AddCarFromCatalog(car_list) -> Optional[Car]:
    cartoadd = ""
    while cartoadd != "back":
        print("Which car would you like to add?\n")
        for index, car in enumerate(car_list):
            print(
                f"{index + 1}. {car.year} {car.model} - {Fore.BLUE}{price_format(car.selling_price)}{Fore.RESET}"
            )

        cartoadd = input(
            "\nEnter the number of the car you would like to add or [Back].\n> "
        )
        if cartoadd != "back":
            if cartoadd.isdigit():
                if 0 < int(cartoadd) <= len(car_list):
                    cartoadd = int(cartoadd) - 1
                    removed_car = car_list[cartoadd]

                    return removed_car
                else:
                    print("\nInvalid car number\n")

            elif cartoadd != "back":
                print("\nInvalid input.\n")

    return None


###==={Pull Cars from Car Catalog}===###
def pullcatalog() -> list[Car]:
    try:
        with open("catalog.txt", "r") as f:
            carlist = f.readlines()

            for index, car in enumerate(carlist):
                carlist[index] = car[:-1].split(", ")

    except FileNotFoundError:
        print("File Not Found")

    return [Car(i[0], i[1], int(i[2]), int(i[3]), int(i[4]), i[5]) for i in carlist]


def main():
    running = True
    state = "start"
    current_user = None

    while running:
        AllCurrentUsers = pullnames()
        car_list = pullcars()
        car_catalog = pullcatalog()

        ###==={Login Screen}===###
        if state == "start":
            os.system("clear")
            while current_user is None and running:
                print(
                    "Welcome! Would you like to [Log in], [Create] an account, or [Quit]."
                )
                choice = input("> ").lower().strip()
                print()

                ###==={Log In}===###
                if choice in ["log in", "login"]:
                    current_user = login(AllCurrentUsers)
                    if current_user is None:
                        print(
                            "\nThe username or password you entered is not correct, please try again.\n"
                        )

                ###==={Create Account}===###
                elif choice == "create":
                    current_user = add_account(AllCurrentUsers)

                ###==={Close Program}===###
                elif choice == "quit":
                    running = False

                ###==={Input Validation/FailProofing}===###
                if choice not in ["log in", "login", "create", "quit"]:
                    print("Please enter a valid input\n")
                elif current_user is not None:
                    state = "browse" if not current_user.is_moderator else "manage"
                    os.system("clear")

        ###==={Customer View}===###
        elif state == "browse":
            print(
                f"Hello {Fore.BLUE}{current_user.username}{Fore.RESET}, Welcome to the Solkvwagen™ Sales Management System, what would you like to do?"
            )
            choice = (
                input(
                    f"Browse vehicles by [Year], [Price], [Color], {'[Manage], ' if current_user.is_admin or current_user.is_moderator else ''}or [Logout]?\n> "
                )
                .strip()
                .lower()
            )
            print()

            ###==={Sort by Price}===###
            if choice == "price":
                sorted_cars = sort_cars_by_price(car_list)
                for car in sorted_cars:
                    formatted_price = price_format(car.selling_price)
                    print(f"{car.model} - {Fore.BLUE}{formatted_price}{Fore.RESET}")
                print()

            ###==={Sort by Year}===###
            elif choice == "year":
                sorted_cars = sorted(car_list, key=lambda x: x.year)
                for car in sorted_cars:
                    print(f"{car.model} - {Fore.BLUE}{car.year}{Fore.RESET}")
                print()

            ###==={Sort by Color}===}###
            elif choice == "color":
                color_cars = sort_cars_by_colors(car_list)
                for color, cars in color_cars.items():
                    print(f"{color.capitalize()} Cars:")
                    for car in cars:
                        formatted_price = price_format(car.selling_price)
                        print(
                            f"  {car.model} - {Fore.BLUE}{formatted_price}{Fore.RESET}"
                        )
                print()

            ###==={Back to Manage (Admin/Manager)}===###
            elif choice == "manage" and (
                current_user.is_moderator or current_user.is_admin
            ):
                state = "manage"
                os.system("clear")

            ###==={Logout}===###
            elif choice == "logout":
                state = "start"
                current_user = None

            ###==={Input Validation}===###
            else:
                print("Please enter a valid choice\n")

        ###==={Manager  View}===###
        elif state == "manage":
            print(f"Hello {Fore.BLUE}{current_user.username}{Fore.RESET}, What would you like to do today?\nManage [Users], Manage [Stock], {'Manage [Catalog], ' if current_user.is_admin else ''}[Logout], or View as [Customer]")  # type: ignore
            choice = input("> ").lower().strip()
            print()
            ###==={Manage Users}===###
            if choice == "users":
                while choice != "back":
                    print(
                        f"Current total users: {Fore.BLUE}{len(AllCurrentUsers)}{Fore.RESET}"
                    )
                    print(
                        f"Would you like to [Search] for a user, [Display] all users, {'[Promote] a user, [Demote] a user, ' if current_user.is_admin else ''}[Delete] a user, or [Back]."
                    )

                    choice = input("> ").lower().strip()
                    print()

                    ###==={Search for Users}===###
                    if choice == "search":
                        searchUser(AllCurrentUsers)
                        print()

                    ###==={Display All Users}===###
                    elif choice == "display":
                        sorted_users = sorted(
                            AllCurrentUsers, key=lambda x: not x.is_moderator
                        )
                        sortedagain = sorted(sorted_users, key=lambda x: not x.is_admin)
                        for user in sortedagain:
                            print(
                                f'{user.username}: {Fore.BLUE}{"Customer" if not user.is_moderator and not user.is_admin else "Admin" if user.is_admin else "Moderator"}{Fore.RESET}'
                            )
                        print()

                    ###==={Promote Users (Admin)}===###
                    elif choice == "promote" and current_user.is_admin:
                        promotables = [
                            user
                            for user in AllCurrentUsers
                            if not user.is_moderator and not user.is_admin
                        ]
                        if len(promotables) != 0:
                            print("Who would you like to promote?\n")
                            for user in AllCurrentUsers:
                                if not user.is_moderator and not user.is_admin:
                                    print(user.username)

                            NameToPromote = input("> ").lower().strip()

                            for i, user in enumerate(AllCurrentUsers):
                                if user.username == NameToPromote:
                                    AllCurrentUsers[i].is_moderator = True
                        else:
                            print("There are currently no customers to promote.")  # type: ignore
                        print()

                    ###==={Demote Users (Admin)}===###
                    elif choice == "demote" and current_user.is_admin:  # type: ignore
                        demotables = [
                            user
                            for user in AllCurrentUsers
                            if user.is_moderator and not user.is_admin
                        ]
                        if len(demotables) != 0:
                            print("Who would you like to demote?\n")

                            for user in AllCurrentUsers:
                                if user.is_moderator and not user.is_admin:
                                    print(user.username)

                            NameToDemote = input("> ").lower().strip()

                            for i, user in enumerate(AllCurrentUsers):
                                if user.username == NameToDemote and not user.is_admin:
                                    AllCurrentUsers[i].is_moderator = False
                        else:
                            print("There are currently no moderators to demote.")  # type: ignore
                        print()

                    ###===={Delete Users}===###
                    elif choice == "delete":
                        nonadmin = [i for i in AllCurrentUsers if not i.is_admin]
                        nonmod = [
                            i
                            for i in AllCurrentUsers
                            if not i.is_moderator and not i.is_admin
                        ]

                        if len(nonadmin) != 0 and current_user.is_admin:  # type: ignore
                            print("Which account would you like to Delete?\n")
                            for user in AllCurrentUsers:
                                if not user.is_admin:
                                    print(user.username)
                            WhoToDelete = input("> ").lower().strip()

                            for user in AllCurrentUsers:
                                if not user.is_admin and user.username == WhoToDelete:
                                    AllCurrentUsers.remove(user)

                        elif len(nonmod) != 0 and not current_user.is_admin:
                            print("Which account would you like to Delete?")
                            for user in AllCurrentUsers:
                                if not user.is_admin and not user.is_moderator:
                                    print(user.username)
                            WhoToDelete = input("> ").lower().strip()

                            for user in AllCurrentUsers:
                                if (
                                    not user.is_admin
                                    and not user.is_moderator
                                    and user.username == WhoToDelete
                                ):
                                    AllCurrentUsers.remove(user)
                        else:
                            print("There are no accounts to delete.")
                        print()

                    ###==={Back to Manage}===###
                    elif choice == "back":
                        with open("userlog.txt", "w") as f:
                            for user in AllCurrentUsers:
                                f.write(
                                    f"{user.username}, {user.password}, {user.salt}, {user.is_moderator}, {user.is_admin}\n"
                                )
                        os.system("clear")

                    ###==={Input Validation}===#
                    else:
                        print("Please enter a valid action.\n")

            ###==={Manage Stock}===###
            elif choice == "stock":
                while choice != "back":
                    print(
                        f"Would you like to [View] Cars, [Add] New Cars, [Remove] Cars, or Go [Back]"
                    )
                    choice = input("> ").lower().strip()
                    print()

                    ###==={View Stock}===###
                    if choice == "view":
                        sorted_carlist = sorted(car_list, key=lambda x: x.year)
                        for car in sorted_carlist:
                            print(
                                f"Model: {car.year} {car.model}\nInvoice: ${car.cost_price:,.2f}\nMSRP: ${car.selling_price:,.2f}\n"
                            )

                    ###==={Add Stock}===###
                    elif choice == "add":
                        cartoadd = AddCarFromCatalog(car_catalog)
                        if cartoadd is not None:
                            car_list.append(cartoadd)

                    ###==={Remove Stock}===###
                    elif choice == "remove":
                        RemoveCar(car_list)

                    ###==={Back to Manage}===###
                    elif choice == "back":
                        with open("carlog.txt", "w") as f:
                            for car in car_list:
                                f.write(
                                    f"{car.make}, {car.model}, {car.year}, {car.cost_price}, {car.selling_price}, {car.color}\n"
                                )
                        os.system("clear")

                    ###==={Input Validation}===###
                    else:
                        print("Please enter a valid action.\n")

            ###==={Manage Catalog (Admin)}===###
            elif choice == "catalog" and current_user.is_admin:
                while choice != "back":
                    print(
                        "\nWould you like to [Add] Styles, [Remove] Styles, [Display] All Current Styles, or [Back]"
                    )
                    choice = input("> ").lower().strip()
                    print()

                    ###==={Add Cars to Catalog}===###
                    if choice == "add":
                        CarorNone = AddCar()
                        if CarorNone is not None:
                            car_catalog.append(CarorNone)

                    ###==={Remove Cars from Catalog}===###
                    elif choice == "remove":
                        RemoveCar(car_catalog)

                    ###==={Display Cars in Catalog}===###
                    elif choice == "display":
                        sorted_catalog = sorted(car_catalog, key=lambda x: x.year)
                        for car in sorted_catalog:
                            print(
                                f"Model: {car.year} {car.model}\nInvoice: ${car.cost_price:,.2f}\nMSRP: ${car.selling_price:,.2f}\n"
                            )

                    ###==={Back to Manage}===###
                    elif choice == "back":
                        with open("catalog.txt", "w") as f:
                            for car in car_catalog:
                                f.write(
                                    f"{car.make}, {car.model}, {car.year}, {car.cost_price}, {car.selling_price}, {car.color}\n"
                                )
                        os.system("clear")

                    ###==={Input Validation}===###
                    else:
                        print("Invalid Action.")

            ###==={Logout as Manager}===###
            elif choice == "logout":
                state = "start"
                current_user = None

            ###==={View as Customer}===###
            elif choice == "customer":
                state = "browse"
                os.system("clear")

            ###==={Kevin James}===###
            elif choice == "supersecret":
                happyfuntime()
                running = False

            else:
                print("Invalid Action\n")


if __name__ == "__main__":
    main()
