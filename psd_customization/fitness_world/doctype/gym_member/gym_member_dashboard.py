# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt


def get_data():
    return {
        'fieldname': 'member',
        'non_standard_fieldnames': {
            'Sales Invoice': 'gym_member',
        },
        'transactions': [
            {
                'label': 'Transactions',
                'items': ['Sales Invoice', 'Gym Subscription'],
            },
        ],
    }
