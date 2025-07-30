from django_keycloak_sso.sso.authentication import CustomUser


def check_roles_in_data(roles: list, user_roles: list) -> bool:
    data_titles = {item['id'] for item in user_roles}
    return all(role in data_titles for role in roles)


def check_groups(groups: list, user_groups: list) -> bool:
    groups_data = {item['group']['id'] for item in user_groups}
    access_status = all(group in groups_data for group in groups)
    return access_status


def check_groups_in_data(groups: list, roles: list, user_groups: list) -> bool:
    groups_data = {item['group']['id'] for item in user_groups}
    roles_data = {item['role'] for item in user_groups}
    access_status = all(group in groups_data for group in groups) and all(role in roles_data for role in roles)
    return access_status


def check_user_permission_access(
        user: CustomUser,
        role_titles: list[str],
        group_titles: list[str],
        group_roles: list[str],
        match_group_roles: bool = False,
        permissive: bool = False,
) -> bool:
    if not isinstance(user, CustomUser):
        return False

    # Normalize inputs
    role_titles = [r.lower() for r in role_titles]
    group_titles = [g.lower() for g in group_titles]
    group_roles = [r.lower() for r in group_roles]
    user_roles = [r.lower() for r in user.roles]
    user_client_roles = [r.lower() for r in user.client_roles]

    # Parse groups from user.groups (e.g., '/group_1/managers')
    parsed_user_groups = []
    for group_path in user.groups:
        parts = group_path.strip("/").split("/")
        if len(parts) == 2:
            group, role = parts
            role = role[:-1] if role.endswith('s') else role
            parsed_user_groups.append((group.lower(), role.lower()))

    # Rule 1: Must have all required roles
    has_required_roles = all(
        role in user_roles or role in user_client_roles for role in role_titles
    )

    # Rule 2: Must be member of all required groups
    user_group_names = [group for group, _ in parsed_user_groups]
    in_required_groups = all(group in user_group_names for group in group_titles)

    # Rule 3: Must match at least one group-role pair
    matches_group_roles = False
    if group_roles:
        for group, role in parsed_user_groups:
            if match_group_roles:
                if group in group_titles and role in group_roles:
                    matches_group_roles = True
                    break
            else:
                if role in group_roles:
                    matches_group_roles = True
                    break
    else:
        matches_group_roles = True  # No roles to match = skip this check

    # Combine logic
    if permissive:
        return has_required_roles or in_required_groups or matches_group_roles
    else:
        return has_required_roles and in_required_groups and matches_group_roles
