# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

from airflow.models import Variable


def update_node_path(src_node, new_node):
    """
    Définition du path root et short
    Comportement différent si la cible est un site ou un dossier.

    Ici on ne reprend uniquement le contenaire "documentLibary", le contenu des autres containers links|dataLists|wiki|discussions|surf-config,
    sont copiés pour archive, mais ce ne sera pas utilisable dans Alfresco Share.
    TODO: prévoir de reprendre correctement les autres containers ?
    """
    import re
    short_path = src_node['path']['name']
    target_site = Variable.get("alfresco_export_target_site", default_var=None)
    target_root_uuid = Variable.get("alfresco_target_root_uuid", default_var=None)
    if target_site is not None:
        # si alfresco_export_target_site est présent on injecte dans un site
        # Valeur prioritaire
        new_node['path']['root'] = f"site:{target_site}"

        # If documentLibrary, Remove all path before documentLibrary
        re_prefix_path = re.compile(r"/(Company Home|Espace racine)/Sites/[\w-]*/documentLibrary")
        if re_prefix_path.match(src_node['path']['name']):
            short_path = re_prefix_path.sub("", src_node['path']['name'])
            if len(short_path) < 1:
                short_path = "/"

        # If other container, keep only the container name
        re_prefix_path = re.compile(
            r"/(Company Home|Espace racine)/Sites/[\w-]*/(links|dataLists|wiki|discussions|surf-config)")
        if re_prefix_path.fullmatch(src_node['path']['name']):
            re_prefix_path = re.compile(r"/(Company Home|Espace racine)/Sites/[\w-]*")
            short_path = re_prefix_path.sub("", src_node['path']['name'])

    elif target_root_uuid is not None:
        # si alfresco_target_root_uuid est présent on inject dans un ce dossier
        new_node['path']['root'] = f"node:{target_root_uuid}"

    # Remove some prefix path
    short_path_remove = Variable.get("short_path_remove", default_var=None)
    if short_path_remove is not None:
        new_node['path']['short'] = short_path.replace(short_path_remove, "")
    else:
        new_node['path']['short'] = short_path
