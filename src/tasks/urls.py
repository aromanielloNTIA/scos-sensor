from django.urls import path

from .views import (
    TaskResultInstanceViewSet,
    TaskResultListViewSet,
    TaskResultsOverviewViewSet,
    task_root,
    upcoming_tasks,
)

urlpatterns = (
    path("", view=task_root, name="task-root"),
    path("upcoming/", view=upcoming_tasks, name="upcoming-tasks"),
    path(
        "completed/",
        view=TaskResultsOverviewViewSet.as_view({"get": "list"}),
        name="task-results-overview",
    ),
    path(
        "completed/<int:schedule_entry_id>/",
        view=TaskResultListViewSet.as_view({"get": "list", "delete": "destroy_all"}),
        name="task-result-list",
    ),
    path(
        "completed/<int:schedule_entry_id>/archive/",
        view=TaskResultListViewSet.as_view({"get": "archive"}),
        name="task-result-list-archive",
    ),
    path(
        "completed/<int:schedule_entry_id>/<int:task_id>/",
        view=TaskResultInstanceViewSet.as_view(
            {"get": "retrieve", "delete": "destroy"}
        ),
        name="task-result-detail",
    ),
    path(
        "completed/<int:schedule_entry_id>/<int:task_id>/archive",
        view=TaskResultInstanceViewSet.as_view({"get": "archive"}),
        name="task-result-archive",
    ),
)
