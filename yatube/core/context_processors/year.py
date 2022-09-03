from datetime import date


def year(request):
    actual_year: int = date.today().year
    return {
        'year': actual_year,
    }
