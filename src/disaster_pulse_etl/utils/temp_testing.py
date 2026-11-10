# from disaster_pulse_etl.extraction.noaa import (
#     extract_noaa_data,
#     NOAANoDataError,
# )

# try:
#     data = extract_noaa_data("2026-11-07")
#     print("Records:", len(data["results"]))

# except NOAANoDataError as exc:
#     print("NO_DATA:", exc)



from disaster_pulse_etl.utils.noaa_state import (
    load_pending_dates,
    add_pending_date,
    remove_pending_date,
)

test_date = "2000-01-01"

print("Before:", load_pending_dates())

add_pending_date(test_date)

print("After adding:", load_pending_dates())

assert test_date in load_pending_dates()

remove_pending_date(test_date)

print("After removing:", load_pending_dates())

assert test_date not in load_pending_dates()

print("NOAA state management test PASSED")
