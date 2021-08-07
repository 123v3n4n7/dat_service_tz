from django.db.models.expressions import RawSQL


def filter_queryset(lat, long, queryset, max_distance):
    """Фильтр по расстоянию"""
    gcd_formula = "6371 * acos(least(greatest(\
    cos(radians(%s)) * cos(radians(lat)) \
    * cos(radians(long) - radians(%s)) + \
    sin(radians(%s)) * sin(radians(lat)) \
    , -1), 1))"
    distance_raw_sql = RawSQL(
        gcd_formula,
        (lat, long, lat)
    )
    queryset = queryset.annotate(distance=distance_raw_sql).order_by('distance')
    queryset = queryset.filter(distance__lt=max_distance)
    return queryset
