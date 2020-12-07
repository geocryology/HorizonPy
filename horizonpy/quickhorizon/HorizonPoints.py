import csv
import logging

class HorizonPoints:

    def __init__(self):
        self.dots = list()
    
    def import_horizon_csv(self, file):
        del self.dots[:]

        # start canvas with image file
        f = open(file, 'rt')
        try:
            reader = csv.reader(f)
            next(reader)  # skip header row

            for row in reader:
                raw = (int(row[0]), int(row[1]))
                overhang = float(row[2]) > 90
                self._define_new_dot(raw, overhanging=overhang)

        finally:
            f.close()

    def import_geotop_csv(): 
        raise NotImplementedError

    def import_data(self, data_type="horizon"):
        pass

    def __get_import_method(self, data_type):
        pass

    def export_to_geotop():
        pass

    def export_to_horizon_csv(self):
        pass

    def delete_all(self):
        del self.dots[:]

    def add_dot(self):
        pass

    def get_dots(self):
        return self.dots

    def display_dots(self):
        pass

    def any_defined(self):
        if len(self.dots) > 0:
            return True
        else:
            return False