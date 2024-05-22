import math


def get_stick(candle_color):
    return candle_color.lower()


def get_solid(candle_color):
    return candle_color.upper()


def get_empty():
    return 'O'


def get_colored_frames(vector, normalized_range):
    candle_columns = 8
    candle_rows = 8
    timestamp_per_frame = round(len(vector) / candle_rows)
    pi_sh_canvas = []
    for candle_index in range(candle_rows):
        sub_vec = vector[candle_index * timestamp_per_frame :
                         (candle_index + 1) * timestamp_per_frame
        ]
        candle_color = 'R' if sub_vec[-1] < sub_vec[0] \
            else 'G' if sub_vec[-1] > sub_vec[0] else 'B'
        candle_min_stick_nom = min(sub_vec)
        pi_sh_candle_min_stick_col = math.floor(
            candle_min_stick_nom / normalized_range * candle_columns
        )
        candle_max_stick_nom = max(sub_vec)
        pi_sh_candle_max_stick_col = math.ceil(
            candle_max_stick_nom / normalized_range * candle_columns
        )
        candle_min_solid_nom = min([sub_vec[0], sub_vec[-1]])
        pi_sh_candle_min_solid_col = math.ceil(
            candle_min_solid_nom / normalized_range * candle_columns
        )
        candle_max_solid_nom = max([sub_vec[0], sub_vec[-1]])
        pi_sh_candle_max_solid_col = math.floor(
            candle_max_solid_nom / normalized_range * candle_columns
        )
        pi_sh_candle_values = [
            get_empty() if x < pi_sh_candle_min_stick_col else
            get_stick(candle_color) if x < pi_sh_candle_min_solid_col else
            get_solid(candle_color) if x <= pi_sh_candle_max_stick_col else
            get_stick(candle_color) if x <= pi_sh_candle_max_solid_col else
            get_empty() for x in range(candle_columns)]
        pi_sh_canvas.extend(pi_sh_candle_values)
    return pi_sh_canvas
