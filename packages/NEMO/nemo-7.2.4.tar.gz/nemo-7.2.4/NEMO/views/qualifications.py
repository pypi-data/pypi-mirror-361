from urllib.parse import urljoin

import requests
from django.conf import settings
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from NEMO.decorators import staff_member_or_tool_staff_required
from NEMO.models import MembershipHistory, Tool, ToolQualificationGroup, User
from NEMO.views.users import get_identity_service


@staff_member_or_tool_staff_required
@require_GET
def qualifications(request):
    """Present a web page to allow staff to qualify or disqualify users on particular tools."""
    users = User.objects.filter(is_active=True)
    tools = Tool.objects.filter(visible=True)
    tool_groups = ToolQualificationGroup.objects.all()
    if not request.user.is_staff:
        # Staff on tools can only use their tools
        tools = tools.filter(_staff__in=[request.user])
        # Staff on tools can only use groups if they are staff for all those
        tool_groups = (
            tool_groups.annotate(num_tools=Count("tools")).filter(tools__in=tools).filter(num_tools=len(tools))
        )
    return render(
        request, "qualifications.html", {"users": users, "tools": list(tools), "tool_groups": list(tool_groups)}
    )


@staff_member_or_tool_staff_required
@require_POST
def modify_qualifications(request):
    """Change the tools that a set of users is qualified to use."""
    action = request.POST.get("action")
    if action != "qualify" and action != "disqualify":
        return HttpResponseBadRequest("You must specify that you are qualifying or disqualifying users.")
    users = request.POST.getlist("chosen_user[]") or request.POST.get("chosen_user") or []
    users = User.objects.in_bulk(users)
    if users == {}:
        return HttpResponseBadRequest("You must specify at least one user.")
    tools = request.POST.getlist("chosen_tool[]") or request.POST.getlist("chosen_tool") or []
    tool_groups = (
        request.POST.getlist("chosen_toolqualificationgroup[]")
        or request.POST.getlist("chosen_toolqualificationgroup")
        or []
    )
    # Add tools from tool group
    tools.extend(
        [
            tool.id
            for tool_group in ToolQualificationGroup.objects.filter(id__in=tool_groups)
            for tool in tool_group.tools.all()
        ]
    )
    tools = Tool.objects.in_bulk(tools)
    if not request.user.is_staff and not set(tools).issubset(
        set(request.user.staff_for_tools.values_list("id", flat=True))
    ):
        return HttpResponseBadRequest("You cannot qualify for a tool you are not staff for.")
    if tools == {}:
        return HttpResponseBadRequest("You must specify at least one tool.")

    for user in users.values():
        original_qualifications = set(user.qualifications.all())
        if action == "qualify":
            user.qualifications.add(*tools)
            original_physical_access_levels = set(user.physical_access_levels.all())
            physical_access_level_automatic_enrollment = list(
                set(
                    [
                        t.grant_physical_access_level_upon_qualification
                        for t in tools.values()
                        if t.grant_physical_access_level_upon_qualification
                    ]
                )
            )
            user.physical_access_levels.add(*physical_access_level_automatic_enrollment)
            current_physical_access_levels = set(user.physical_access_levels.all())
            added_physical_access_levels = set(current_physical_access_levels) - set(original_physical_access_levels)
            for access_level in added_physical_access_levels:
                entry = MembershipHistory()
                entry.authorizer = request.user
                entry.parent_content_object = access_level
                entry.child_content_object = user
                entry.action = entry.Action.ADDED
                entry.save()
            if get_identity_service().get("available", False):
                for t in tools:
                    tool = Tool.objects.get(id=t)
                    if tool.grant_badge_reader_access_upon_qualification:
                        parameters = {
                            "username": user.username,
                            "domain": user.domain,
                            "requested_area": tool.grant_badge_reader_access_upon_qualification,
                        }
                        timeout = settings.IDENTITY_SERVICE.get("timeout", 3)
                        requests.put(
                            urljoin(settings.IDENTITY_SERVICE["url"], "/add/"), data=parameters, timeout=timeout
                        )
        elif action == "disqualify":
            user.qualifications.remove(*tools)
        current_qualifications = set(user.qualifications.all())
        # Record the qualification changes for each tool:
        added_qualifications = set(current_qualifications) - set(original_qualifications)
        for tool in added_qualifications:
            entry = MembershipHistory()
            entry.authorizer = request.user
            entry.parent_content_object = tool
            entry.child_content_object = user
            entry.action = entry.Action.ADDED
            entry.save()
        removed_qualifications = set(original_qualifications) - set(current_qualifications)
        for tool in removed_qualifications:
            entry = MembershipHistory()
            entry.authorizer = request.user
            entry.parent_content_object = tool
            entry.child_content_object = user
            entry.action = entry.Action.REMOVED
            entry.save()

    if request.POST.get("redirect") == "true":
        messages.success(request, "Tool qualifications were successfully modified")
        return redirect("qualifications")
    else:
        return HttpResponse()


@staff_member_or_tool_staff_required
@require_GET
def get_qualified_users(request):
    tool = get_object_or_404(Tool, id=request.GET.get("tool_id"))
    if not request.user.is_staff_on_tool(tool):
        return HttpResponseBadRequest("You do not have permission to view the qualified users for this tool.")
    users = User.objects.filter(is_active=True)
    dictionary = {"tool": tool, "users": users, "expanded": True}
    return render(request, "tool_control/qualified_users.html", dictionary)
