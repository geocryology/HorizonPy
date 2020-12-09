###################
# File associations
####################

file_opt = options = {}

# Image files
options['defaultextension'] = '.gif'
options['filetypes'] = [('all files', '.*'),
                        ('ppm files', '.ppm'),
                        ('pgm files', '.pgm'),
                        ('gif files', '.gif'),
                        ('jpg files', '.jpg'),
                        ('jpeg files', '.jpeg')]
options['initialdir'] = '.'

# csv files
csv_opt = csv_options = {}
csv_options['defaultextension'] = '.hpt.csv'
csv_options['filetypes'] = [('all files', '.*'),
                            ('horizon csv files', '.hpt.csv')]

csv_options['initialdir'] = "."

# Azimuth files
azm_opt = azm_options = {}
azm_options['defaultextension'] = '.azm.ini'
azm_options['filetypes'] = [('all files', '.*'),
                            ("Azimuth files", ".azm.ini")]
azm_options['initialdir'] = "."

### 
# Plotting Styles
###

plot_styles = {
    'overhangingpoint': {'fill': 'yellow'},
    'regularpoint': {'fill': 'blue', 'outline': 'pink'},
    'whitepoint': {'fill': 'white'}}
