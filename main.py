
from motherBoard import mother_board



if __name__ == "__main__":
    # 4-17
    program_list = [
    "30F20900000000000000",
    "30F31500000000000000",
    "6123",
    "30F48000000000000000",
    "40436400000000000000",
    "A02F",
    "B00F",
    "734000000000000000",
    "804100000000000000",
    "00",
    "90",
    ]

    board = mother_board()
    start_address = "0"
    program_data = "".join(program_list)
    board.load_data(start_address,program_data)
    board.run()