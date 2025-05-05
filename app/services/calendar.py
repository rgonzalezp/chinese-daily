import calendar
import datetime

# No dependency on config needed here usually

def month_matrix(year: int, month: int) -> list[list[int]]:
    """Returns the calendar matrix for a given year and month."""
    return calendar.monthcalendar(year, month)

def adjacent_month(year: int, month: int, delta: int = 1) -> tuple[int, int]:
    """Calculates the year and month adjacent (delta months away) from the given one."""
    # Ensure delta is reasonable if needed
    try:
        current_month_start = datetime.date(year, month, 1)
        # Estimate new month by adding/subtracting ~30-31 days per month delta
        # Using slightly more than average days avoids issues around month ends
        estimated_date = current_month_start + datetime.timedelta(days=31 * delta) 
        # A more robust way for large deltas might involve relativedelta or careful loops
        # For +/- 1 month, timedelta works well.
        # For safety with month lengths, let's refine:
        if delta > 0:
            # Go to end of current month, then add delta days to land in target month
            days_in_month = calendar.monthrange(year, month)[1]
            target_date = datetime.date(year, month, days_in_month) + datetime.timedelta(days=delta)
        elif delta < 0:
            # Go to start of current month, then subtract delta days
            target_date = datetime.date(year, month, 1) - datetime.timedelta(days=abs(delta))
        else: # delta == 0
            target_date = current_month_start
            
        return target_date.year, target_date.month
    except ValueError as e:
        # Handle invalid year/month input if necessary
        print(f"Error calculating adjacent month for {year}-{month} with delta {delta}: {e}")
        # Return original year/month or raise error?
        return year, month 