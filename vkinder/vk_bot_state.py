import enum


class BotState(enum.Enum):
    active_state = 8
    search_state = 7
    check_bdate = 6
    apply_search_params = 5
    get_age = 4
    get_city = 3
    main_state = 2
    empty_state = 1
