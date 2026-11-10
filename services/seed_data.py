# RakshakAlert scratch build - Phase 1 seed data.
#
# TOWERS list copied VERBATIM from
# ~/workspace/rakshakalert-scratch-towers-seed.py (2026-11-07).
# All coordinates are SAMPLE demo data (city centres, not real telecom
# sites). Mira Road kept at the old build's exact coords (19.2952, 72.8544).
# 60 towers x 8 citizens = 480 demo citizens. Radius 5.0 km per tower.
# Citizens are fictional, generated deterministically with Random(42).

TOWERS = [
    # Maharashtra (10)
    ("MH-MUM-01", "Mumbai Central", "Mumbai", "Maharashtra", 18.9402, 72.8348),
    ("MH-MIR-02", "Mira Road Station", "Mira Road", "Maharashtra", 19.2952, 72.8544),
    ("MH-NVM-03", "Navi Mumbai Central", "Navi Mumbai", "Maharashtra", 19.0327, 73.0296),
    ("MH-THN-04", "Thane West", "Thane", "Maharashtra", 19.1878, 72.9726),
    ("MH-NSK-05", "Nashik Central", "Nashik", "Maharashtra", 19.9951, 73.7964),
    ("MH-PUN-06", "Pune Shivajinagar", "Pune", "Maharashtra", 18.5042, 73.8529),
    ("MH-NAG-07", "Nagpur Sitabuldi", "Nagpur", "Maharashtra", 21.1569, 79.0820),
    ("MH-SAM-08", "Chhatrapati Sambhajinagar Central", "Chhatrapati Sambhajinagar", "Maharashtra", 19.8702, 75.3460),
    ("MH-KOP-09", "Kolhapur Central", "Kolhapur", "Maharashtra", 16.7045, 74.2415),
    ("MH-STR-10", "Satara Central", "Satara", "Maharashtra", 17.6863, 74.0080),
    # Goa (2)
    ("GA-PAN-11", "Panaji Central", "Panaji", "Goa", 15.4584, 73.8057),
    ("GA-MAR-12", "Margao Central", "Margao", "Goa", 15.2747, 73.9802),
    # Gujarat (5)
    ("GJ-AMD-13", "Ahmedabad Sabarmati", "Ahmedabad", "Gujarat", 23.0278, 72.6003),
    ("GJ-SRT-14", "Surat Ring Road", "Surat", "Gujarat", 21.1859, 72.8366),
    ("GJ-VAD-15", "Vadodara Central", "Vadodara", "Gujarat", 22.3095, 73.1799),
    ("GJ-RJT-16", "Rajkot Central", "Rajkot", "Gujarat", 22.2972, 70.8016),
    ("GJ-VPI-17", "Vapi GIDC", "Vapi", "Gujarat", 20.3717, 72.9091),
    # Karnataka (4)
    ("KA-BLR-18", "Bengaluru Central", "Bengaluru", "Karnataka", 12.9662, 77.5869),
    ("KA-MYS-19", "Mysuru Central", "Mysuru", "Karnataka", 12.3090, 76.6531),
    ("KA-MNG-20", "Mangaluru Central", "Mangaluru", "Karnataka", 12.8979, 74.8454),
    ("KA-HUB-21", "Hubballi Central", "Hubballi", "Karnataka", 15.3505, 75.1374),
    # Tamil Nadu (4)
    ("TN-CHN-22", "Chennai Adyar", "Chennai", "Tamil Nadu", 13.0840, 80.2827),
    ("TN-CBE-23", "Coimbatore RS", "Coimbatore", "Tamil Nadu", 10.9942, 76.9663),
    ("TN-MDU-24", "Madurai Central", "Madurai", "Tamil Nadu", 9.9242, 78.1242),
    ("TN-TRY-25", "Tiruchirappalli Central", "Tiruchirappalli", "Tamil Nadu", 10.8061, 78.6948),
    # Kerala (4)
    ("KL-KOC-26", "Kochi Marine Drive", "Kochi", "Kerala", 9.9360, 76.2614),
    ("KL-TVM-27", "Thiruvananthapuram Central", "Thiruvananthapuram", "Kerala", 8.5053, 76.9514),
    ("KL-KKD-28", "Kozhikode Central", "Kozhikode", "Kerala", 11.2588, 75.7809),
    ("KL-TSR-29", "Thrissur Round", "Thrissur", "Kerala", 10.5109, 76.2112),
    # Telangana / Andhra Pradesh (3)
    ("TS-HYD-30", "Hyderabad Central", "Hyderabad", "Telangana", 17.3949, 78.4708),
    ("AP-VJA-31", "Vijayawada Central", "Vijayawada", "Andhra Pradesh", 16.5026, 80.6398),
    ("AP-VSK-32", "Visakhapatnam Central", "Visakhapatnam", "Andhra Pradesh", 17.7199, 83.2628),
    # North India (11)
    ("DL-NDL-33", "New Delhi Central", "New Delhi", "Delhi", 28.6314, 77.2168),
    ("RJ-JAI-34", "Jaipur Central", "Jaipur", "Rajasthan", 26.9259, 75.8067),
    ("UP-LKO-35", "Lucknow Central", "Lucknow", "Uttar Pradesh", 26.8547, 80.9214),
    ("MP-BPL-36", "Bhopal Central", "Bhopal", "Madhya Pradesh", 23.2647, 77.4052),
    ("MP-IND-37", "Indore Central", "Indore", "Madhya Pradesh", 22.7162, 75.8651),
    ("BR-PAT-38", "Patna Central", "Patna", "Bihar", 25.6013, 85.1375),
    ("WB-KOL-39", "Kolkata Central", "Kolkata", "West Bengal", 22.5706, 88.3713),
    ("OD-BBS-40", "Bhubaneswar Central", "Bhubaneswar", "Odisha", 20.2689, 85.8410),
    ("AS-GHY-41", "Guwahati Central", "Guwahati", "Assam", 26.1772, 91.7541),
    ("UK-DDN-42", "Dehradun Central", "Dehradun", "Uttarakhand", 30.3097, 78.0489),
    ("CH-CHD-43", "Chandigarh Central", "Chandigarh", "Chandigarh", 30.7035, 76.7897),
    # Added 2026-11-07 (Phase 2 refinement): 17 more cities, 1 tower each
    ("MH-AMR-44", "Amravati Central", "Amravati", "Maharashtra", 20.9374, 77.7796),
    ("MH-SOL-45", "Solapur Central", "Solapur", "Maharashtra", 17.6599, 75.9064),
    ("UP-KNP-46", "Kanpur Central", "Kanpur", "Uttar Pradesh", 26.4499, 80.3319),
    ("UP-VNS-47", "Varanasi Central", "Varanasi", "Uttar Pradesh", 25.3176, 82.9739),
    ("UP-AGR-48", "Agra Central", "Agra", "Uttar Pradesh", 27.1767, 78.0081),
    ("GJ-GNR-49", "Gandhinagar Central", "Gandhinagar", "Gujarat", 23.2232, 72.6500),
    ("RJ-UDP-50", "Udaipur Central", "Udaipur", "Rajasthan", 24.5854, 73.7125),
    ("RJ-JDH-51", "Jodhpur Central", "Jodhpur", "Rajasthan", 26.2389, 73.0243),
    ("PB-ASR-52", "Amritsar Central", "Amritsar", "Punjab", 31.6340, 74.8723),
    ("PB-LDH-53", "Ludhiana Central", "Ludhiana", "Punjab", 30.9010, 75.8573),
    ("HR-GUR-54", "Gurugram Central", "Gurugram", "Haryana", 28.4595, 77.0266),
    ("JK-SXR-55", "Srinagar Central", "Srinagar", "Jammu and Kashmir", 34.0837, 74.7973),
    ("HP-SML-56", "Shimla Central", "Shimla", "Himachal Pradesh", 31.1048, 77.1734),
    ("CG-RPR-57", "Raipur Central", "Raipur", "Chhattisgarh", 21.2514, 81.6296),
    ("JH-RNC-58", "Ranchi Central", "Ranchi", "Jharkhand", 23.3441, 85.3096),
    ("JK-JMU-59", "Jammu Central", "Jammu", "Jammu and Kashmir", 32.7266, 74.8570),
    ("HR-FBD-60", "Faridabad Central", "Faridabad", "Haryana", 28.4089, 77.3178),
]

CITIZENS_PER_TOWER = 8
TOWER_RADIUS_KM = 5.0

FIRST_NAMES = [
    "Aarav", "Ananya", "Rohan", "Priya", "Arjun", "Meera", "Vikram", "Kavya",
    "Aditya", "Sneha", "Kiran", "Divya", "Nikhil", "Pooja", "Rahul", "Anita",
    "Sanjay", "Nisha", "Amit", "Ritu", "Manish", "Shreya", "Deepak", "Neha",
    "Varun", "Ishita", "Kunal", "Tanvi", "Rajesh", "Simran", "Harish", "Lata",
]
LAST_NAMES = [
    "Sharma", "Patel", "Iyer", "Reddy", "Khan", "Desai", "Nair", "Gupta",
    "Joshi", "Singh", "Mehta", "Kulkarni", "Chopra", "Menon", "Rao", "Verma",
]


def generate_citizens():
    """Deterministic fictional citizens: 8 per tower, Random(42).

    Returns a list of (name, phone, tower_code) tuples. Phones are
    fictional +91 numbers, unique per citizen.
    """
    import random

    rng = random.Random(42)
    citizens = []
    used_phones = set()
    for code, _name, city, _state, _lat, _lng in TOWERS:
        for _ in range(CITIZENS_PER_TOWER):
            name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            while True:
                phone = "+91 9" + "".join(str(rng.randint(0, 9)) for _ in range(9))
                if phone not in used_phones:
                    used_phones.add(phone)
                    break
            citizens.append((name, phone, code))
    return citizens
