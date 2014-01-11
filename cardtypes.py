from enum import enum

CardTypes = enum('Loan', 'Upgrade', 'Action', 'Bonus',
                 'Building', 'Roof', 'Level', 'ConfidenceDecrease')

PlayerAreaCardTypes =[ CardTypes.Loan, CardTypes.Upgrade, CardTypes.Action ]
