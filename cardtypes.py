from enum import enum

CardTypes = enum('Loan', 'Investment', 'Upgrade', 'Action', 'Bonus',
                'Building', 'Roof', 'Level')

PlayerAreaCardTypes =[ CardTypes.Loan, CardTypes.Investment, CardTypes.Upgrade,
                       CardTypes.Action ]
