import frappe


def execute():
    for row in _get_names():
        frappe.db.set_value(
            "Trainer Allocation",
            row.get("name"),
            "gym_member_name",
            row.get("gym_member_name"),
        )


def _get_names():
    return frappe.db.sql(
        """
            SELECT ta.name AS name, gm.member_name AS gym_member_name
            FROM `tabTrainer Allocation` AS ta
            LEFT JOIN `tabGym Member` AS gm ON gm.name = ta.gym_member
            WHERE IFNULL(ta.gym_member_name, '') = ''
        """,
        as_dict=1,
    )
