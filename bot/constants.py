COOLDOWN = '100 м V1 на выбор'
COOLDOWN_DISTANCE = 100
HELLO = 'Здравствуйте'
MIN_WARMUP_BEGINNER = 200
MAX_WARMUP_BEGINNER = 300
MIN_MAIN_BEGINNER = 500
MAX_MAIN_BEGINNER = 600

MIN_WARMUP_SKILLED = 400
MAX_WARMUP_SKILLED = 500
MIN_MAIN_SKILLED = 700
MAX_MAIN_SKILLED = 1000

MIN_WARMUP_PROFI = 600
MAX_WARMUP_PROFI = 700
MIN_MAIN_PROFI = 1000
MAX_MAIN_PROFI = 1200
LEVEL_PARAMETERS = {
    'Новичок': {
        'min_warmup': MIN_WARMUP_BEGINNER,
        'max_warmup': MAX_WARMUP_BEGINNER,
        'min_main': MIN_MAIN_BEGINNER,
        'max_main': MAX_MAIN_BEGINNER,
    },
    'Опытный': {
        'min_warmup': MIN_WARMUP_SKILLED,
        'max_warmup': MAX_WARMUP_SKILLED,
        'min_main': MIN_MAIN_SKILLED,
        'max_main': MAX_MAIN_SKILLED,
    },
    'Профи': {
        'min_warmup': MIN_WARMUP_PROFI,
        'max_warmup': MAX_WARMUP_PROFI,
        'min_main': MIN_MAIN_PROFI,
        'max_main': MAX_MAIN_PROFI,
    }
}
