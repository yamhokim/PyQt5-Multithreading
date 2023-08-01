from scipy.spatial import distance

# Implementing this formula
# (||p2 - p8|| + ||p3 - p7|| + ||p4 - p6||) / (2 * ||p1 - p5||)

def MAR(mouth_coords):
    p1 = mouth_coords[0]
    p2 = mouth_coords[1]
    p3 = mouth_coords[2]
    p4 = mouth_coords[3]
    p5 = mouth_coords[4]
    p6 = mouth_coords[5]
    p7 = mouth_coords[6]
    p8 = mouth_coords[7]

    p2_minus_p8 = abs(distance.euclidean(p2, p8))
    p3_minus_p7 = abs(distance.euclidean(p3, p7))
    p4_minus_p6 = abs(distance.euclidean(p4, p6))
    p1_minus_p5 = abs(distance.euclidean(p1, p5))

    mar = (p2_minus_p8 + p3_minus_p7 + p4_minus_p6) / (2 * p1_minus_p5)

    return mar