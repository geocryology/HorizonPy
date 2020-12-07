

def find_angle(self, C, P2, P3):

    angle = np.arctan2(P2[1] - C[1], P2[0] - C[0]) - np.arctan2(P3[1] - C[1], P3[0] - C[0])
    angle_in_degrees = np.degrees(angle)

    if angle_in_degrees < 0:
        angle_in_degrees += 360

    return angle_in_degrees

def calculate_true_azimuth(image_azimuth, field_azimuth):
    """ Calculate true azimuth of horizon point from image azimuth 
    
    image_azimuth: float
        azimuth, in degrees, of 
    field_azimuth: float
        azimuth, in degrees, of brass pin on horizon camera gimble
    """
    if field_azimuth == -1:
        return -1
    else:
        return (image_azimuth + field_azimuth) % 360