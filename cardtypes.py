from enum import enum

CardTypes = enum('Loan', 'Investment', 'Upgrade', 'Action', 'Bonus',
                 'Building', 'Roof', 'Level', 'ConfidenceDecrease')

PlayerAreaCardTypes =[ CardTypes.Loan, CardTypes.Investment, CardTypes.Upgrade,
                       CardTypes.Action ]
