from django.core.paginator import InvalidPage
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import Http404

from falco.conf import app_settings
from falco.types import HttpRequest


def paginate_queryset(request: HttpRequest, queryset: QuerySet, page_size: int = app_settings.DEFAULT_PAGE_SIZE):
    paginator = Paginator(queryset, page_size)
    page_number = request.GET.get("page") or 1
    try:
        page_number = int(page_number)
    except ValueError as e:
        if page_number == "last":
            page_number = paginator.num_pages
        else:
            msg = "Page is not 'last', nor can it be converted to an int."
            raise Http404(msg) from e

    try:
        return paginator.page(page_number)
    except InvalidPage as exc:
        msg = "Invalid page (%s): %s"
        raise Http404(msg % (page_number, str(exc))) from exc
