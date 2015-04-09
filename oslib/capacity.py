class Capacity(object):
    mapping = {
        'Mini':     (1, 0.615, 0.05),
        'Small': (1, 1.7, 0.10),
        'Large': (2, 7.5, 0.40),
        'Memory': (4, 17.1, 0.57),
        'Maxi': (4, 15, 0.75),
        'Power': (8, 7, 0.75),
        'Large Memory': (6, 34.2, 1.15),
        'Maxi Memory': (8, 64, 2,3),
        't1.micro': 'Mini',
        'm1.xlarge': 'Maxi',
        'm1.large': 'Large',
        'm2.xlarge': 'Memory',
        'm2.2xlarge': 'Large Memory',
        'm2.4xlarge': 'Maxi Memory',
        'c1.xlarge': 'Power',
    }