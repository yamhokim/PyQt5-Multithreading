from scipy.spatial import distance

# Implementing this formula:
# (abs(p2 - p6) + abs(p3 - p5)) / (2 * abs(p1 - p4))
def EAR(eye_coords):
    p1 = eye_coords[0]
    p2 = eye_coords[1]
    p3 = eye_coords[2]
    p4 = eye_coords[3]
    p5 = eye_coords[4]
    p6 = eye_coords[5]

    p2_minus_p6 = abs(distance.euclidean(p2, p6)) # distance between p2 and p6
    p3_minus_p5 = abs(distance.euclidean(p3, p5)) # distance between p3 and p5
    p1_minus_p4 = abs(distance.euclidean(p1, p4)) # distance between p1 and p4

    ear = (p2_minus_p6 + p3_minus_p5)/(2 * p1_minus_p4) # calculate the eye aspect ratio

    return ear


